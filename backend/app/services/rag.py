import json
from pathlib import Path

from app.models.schemas import CaseCategory, LegalSource


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
CATEGORY_TO_DIR = {
    "employment_wages": "employment",
    "property_tenancy": "property_tenancy",
    "womens_protection": "womens_protection",
    "consumer_fraud": "consumer_fraud",
    "police_fir": "police_fir",
}


def _file_for_category(category: CaseCategory) -> Path | None:
    folder = CATEGORY_TO_DIR.get(category)
    if not folder:
        return None
    return DATA_DIR / folder / "acts_and_cases.json"


def load_sources(category: CaseCategory) -> list[dict]:
    file_path = _file_for_category(category)
    if not file_path or not file_path.exists():
        return []
    return json.loads(file_path.read_text(encoding="utf-8"))


def _normalize_place(raw: str | None) -> str:
    if not raw:
        return ""
    return raw.strip().casefold()


def _row_search_blob(row: dict) -> str:
    parts: list[str] = [
        str(row.get("title", "")),
        str(row.get("section", "")),
        str(row.get("snippet", "")),
        str(row.get("district", "")),
        str(row.get("state", "")),
        str(row.get("forum_visited", "")),
        str(row.get("outcome", "")),
        str(row.get("entry_type", "")),
    ]
    docs = row.get("documents_used")
    if isinstance(docs, list):
        parts.extend(str(d) for d in docs)
    return " ".join(parts).lower()


def _dedupe_key(category: CaseCategory, row: dict) -> tuple:
    snip = (row.get("snippet") or "")[:160]
    return (category, row.get("title"), row.get("section"), snip)


def _legal_source_from_row(row: dict, corpus_category: CaseCategory) -> LegalSource:
    payload: dict = {
        "title": row["title"],
        "section": row["section"],
        "snippet": row["snippet"],
        "corpus_category": corpus_category,
    }
    et = row.get("entry_type")
    if et in ("statute", "illustrative_case"):
        payload["entry_type"] = et
    if row.get("district"):
        payload["district"] = str(row["district"])
    if row.get("state"):
        payload["state"] = str(row["state"])
    oc = row.get("outcome")
    if oc in ("won", "lost", "settled", "partial"):
        payload["outcome"] = oc
    if row.get("forum_visited"):
        payload["forum_visited"] = str(row["forum_visited"])
    docs = row.get("documents_used")
    if isinstance(docs, list):
        payload["documents_used"] = [str(x) for x in docs if str(x).strip()]
    return LegalSource(**payload)


def _score_row(
    user_terms: set[str],
    row: dict,
    *,
    district: str | None,
    category: CaseCategory,
    category_hint: CaseCategory | None,
) -> int:
    haystack = _row_search_blob(row)
    score = sum(1 for token in user_terms if len(token) > 2 and token in haystack)
    if category_hint and category == category_hint:
        score += 8
    ud = _normalize_place(district)
    rd = _normalize_place(row.get("district"))
    if ud and rd and ud == rd:
        score += 16
    elif ud and ud in haystack:
        score += 5
    if row.get("entry_type") == "illustrative_case" and ud and rd and ud == rd:
        score += 4
    return score


def _initial_pick(
    scored: list[tuple[int, CaseCategory, dict]],
    limit: int,
) -> list[tuple[int, CaseCategory, dict]]:
    scored_sorted = sorted(scored, key=lambda item: item[0], reverse=True)
    picked: list[tuple[int, CaseCategory, dict]] = []
    keys: set[tuple] = set()
    for item in scored_sorted:
        if len(picked) >= limit:
            break
        _, cat, row = item
        k = _dedupe_key(cat, row)
        if k in keys:
            continue
        keys.add(k)
        picked.append(item)
    return picked


def _has_illustrative_outcome(
    picked: list[tuple[int, CaseCategory, dict]],
    *,
    category: CaseCategory,
    district_norm: str,
    outcome: str,
) -> bool:
    for _, cat, row in picked:
        if cat != category:
            continue
        if row.get("entry_type") != "illustrative_case":
            continue
        if _normalize_place(row.get("district")) != district_norm:
            continue
        if row.get("outcome") == outcome:
            return True
    return False


def _find_illustrative(
    full_scored: list[tuple[int, CaseCategory, dict]],
    *,
    category: CaseCategory,
    district_norm: str,
    outcome: str,
    existing_keys: set[tuple],
) -> tuple[int, CaseCategory, dict] | None:
    for item in sorted(full_scored, key=lambda x: x[0], reverse=True):
        _, cat, row = item
        if cat != category:
            continue
        if row.get("entry_type") != "illustrative_case":
            continue
        if _normalize_place(row.get("district")) != district_norm:
            continue
        if row.get("outcome") != outcome:
            continue
        k = _dedupe_key(cat, row)
        if k in existing_keys:
            continue
        return item
    return None


def _inject_won_lost_pair(
    picked: list[tuple[int, CaseCategory, dict]],
    full_scored: list[tuple[int, CaseCategory, dict]],
    *,
    district: str | None,
    category_hint: CaseCategory | None,
    limit: int,
) -> list[tuple[int, CaseCategory, dict]]:
    dn = _normalize_place(district)
    if not dn or not category_hint or category_hint == "general":
        return picked
    picked = list(picked)

    for outcome in ("won", "lost"):
        if _has_illustrative_outcome(picked, category=category_hint, district_norm=dn, outcome=outcome):
            continue
        keys = {_dedupe_key(c, r) for _, c, r in picked}
        cand = _find_illustrative(
            full_scored,
            category=category_hint,
            district_norm=dn,
            outcome=outcome,
            existing_keys=keys,
        )
        if not cand:
            continue
        top_score = max((s for s, _, _ in picked), default=50)
        boosted = (max(top_score, cand[0], 40) + 2, cand[1], cand[2])
        if len(picked) < limit:
            picked.append(boosted)
        else:
            picked.sort(key=lambda x: x[0], reverse=True)
            worst = picked[-1]
            if boosted[0] >= worst[0]:
                picked.remove(worst)
                picked.append(boosted)
        picked.sort(key=lambda x: x[0], reverse=True)

    return picked[:limit]


def retrieve_context(
    category: CaseCategory,
    user_text: str,
    limit: int = 3,
    *,
    district: str | None = None,
) -> list[LegalSource]:
    user_terms = set(user_text.lower().split())
    rows = load_sources(category)
    scored: list[tuple[int, dict]] = []

    for row in rows:
        s = _score_row(user_terms, row, district=district, category=category, category_hint=category)
        scored.append((s, row))

    scored.sort(key=lambda item: item[0], reverse=True)
    if scored and scored[0][0] > 0:
        top = [row for _, row in scored[:limit]]
    elif rows:
        top = rows[:limit]
    else:
        top = []

    return [_legal_source_from_row(item, category) for item in top]


def retrieve_context_all(
    user_text: str,
    limit: int = 6,
    *,
    district: str | None = None,
    category_hint: CaseCategory | None = None,
) -> list[LegalSource]:
    """Score snippets across all pilot corpora; boost user's district and classifier category."""
    user_terms = set(user_text.lower().split())
    scored: list[tuple[int, CaseCategory, dict]] = []

    for category in CATEGORY_TO_DIR:
        rows = load_sources(category)
        for row in rows:
            s = _score_row(
                user_terms,
                row,
                district=district,
                category=category,
                category_hint=category_hint,
            )
            scored.append((s, category, row))

    scored.sort(key=lambda item: item[0], reverse=True)
    positive = [t for t in scored if t[0] > 0]
    if positive:
        picked = _initial_pick(positive, limit)
    else:
        picked_fallback: list[tuple[int, CaseCategory, dict]] = []
        for category in CATEGORY_TO_DIR:
            rows = load_sources(category)
            if rows:
                picked_fallback.append((0, category, rows[0]))
            if len(picked_fallback) >= limit:
                break
        i = 0
        while len(picked_fallback) < limit and i < len(scored):
            score, cat, row = scored[i]
            key = _dedupe_key(cat, row)
            existing = {_dedupe_key(p[1], p[2]) for p in picked_fallback}
            if key not in existing:
                picked_fallback.append((score, cat, row))
            i += 1
        picked = picked_fallback[:limit]

    picked = _inject_won_lost_pair(picked, scored, district=district, category_hint=category_hint, limit=limit)
    picked.sort(key=lambda x: x[0], reverse=True)
    return [_legal_source_from_row(row, cat) for _, cat, row in picked[:limit]]
