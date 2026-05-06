import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
CATEGORY_DIRS = [
    "employment",
    "property_tenancy",
    "womens_protection",
    "consumer_fraud",
    "police_fir",
]


def ingest_category(category_dir: str) -> int:
    seed_file = BASE_DIR / "data" / category_dir / "acts_and_cases.seed.json"
    output_file = BASE_DIR / "data" / category_dir / "acts_and_cases.json"
    rows = json.loads(seed_file.read_text(encoding="utf-8"))
    output_file.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"Ingest complete: {category_dir} -> {len(rows)} rows")
    return len(rows)


def main() -> None:
    total = 0
    for category_dir in CATEGORY_DIRS:
        total += ingest_category(category_dir)
    print(f"All categories ingested: {total} rows total")


if __name__ == "__main__":
    main()
