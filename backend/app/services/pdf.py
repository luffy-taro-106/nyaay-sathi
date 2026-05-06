from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from app.models.schemas import OrchestrateResponse


_UNICODE_FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
]
_REGISTERED_FONT: str | None = None


def _ensure_unicode_font() -> str:
    """Try to register a Unicode-capable font. Fall back to Helvetica if none found."""
    global _REGISTERED_FONT
    if _REGISTERED_FONT is not None:
        return _REGISTERED_FONT
    for candidate in _UNICODE_FONT_CANDIDATES:
        if Path(candidate).exists():
            try:
                pdfmetrics.registerFont(TTFont("NyaayUnicode", candidate))
                _REGISTERED_FONT = "NyaayUnicode"
                return _REGISTERED_FONT
            except Exception:  # noqa: BLE001
                continue
    _REGISTERED_FONT = "Helvetica"
    return _REGISTERED_FONT


def _draw_wrapped_line(
    pdf: canvas.Canvas,
    text: str,
    x: int,
    y: int,
    width: int,
    line_height: int,
    font_name: str,
    font_size: int,
) -> int:
    if not text:
        return y
    words = text.split()
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if pdf.stringWidth(candidate, font_name, font_size) <= width:
            current = candidate
        else:
            pdf.drawString(x, y, current)
            y -= line_height
            current = word
    if current:
        pdf.drawString(x, y, current)
        y -= line_height
    return y


def _section_title(
    pdf: canvas.Canvas,
    title: str,
    x: int,
    y: int,
    bold_font: str,
    body_font: str,
) -> int:
    pdf.setFont(bold_font, 11)
    pdf.drawString(x, y, title)
    y -= 16
    pdf.setFont(body_font, 10)
    return y


def _ensure_room(
    pdf: canvas.Canvas,
    y: int,
    page_height: int,
    body_font: str,
    min_y: int = 90,
) -> int:
    if y < min_y:
        pdf.showPage()
        pdf.setFont(body_font, 10)
        return int(page_height - 50)
    return y


def build_complaint_pdf(response: OrchestrateResponse) -> bytes:
    body_font = _ensure_unicode_font()
    bold_font = "Helvetica-Bold" if body_font == "Helvetica" else body_font

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    page_width, page_height = A4
    left = 50
    right_width = int(page_width - 100)
    line_height = 14
    y = int(page_height - 50)

    pdf.setFont(bold_font, 14)
    pdf.drawString(left, y, "Nyaay Sathi - Complaint Draft")
    y -= 24

    pdf.setFont(body_font, 10)
    y = _draw_wrapped_line(
        pdf,
        f"Category: {response.category}",
        left,
        y,
        right_width,
        line_height,
        body_font,
        10,
    )
    y = _draw_wrapped_line(
        pdf,
        f"Disclaimer: {response.disclaimer}",
        left,
        y,
        right_width,
        line_height,
        body_font,
        10,
    )
    if response.crisis_detected and response.helplines:
        y = _draw_wrapped_line(
            pdf,
            "Crisis flagged. Helplines: " + "; ".join(response.helplines),
            left,
            y,
            right_width,
            line_height,
            body_font,
            10,
        )
    y -= 8

    y = _ensure_room(pdf, y, int(page_height), body_font)
    y = _section_title(pdf, "Rights summary", left, y, bold_font, body_font)
    y = _draw_wrapped_line(
        pdf,
        response.rights_summary,
        left,
        y,
        right_width,
        line_height,
        body_font,
        10,
    )
    y -= 8

    y = _ensure_room(pdf, y, int(page_height), body_font)
    y = _section_title(pdf, "Complaint Template", left, y, bold_font, body_font)
    for paragraph in response.complaint_template.split("\n"):
        y = _ensure_room(pdf, y, int(page_height), body_font)
        if paragraph.strip():
            y = _draw_wrapped_line(
                pdf, paragraph, left, y, right_width, line_height, body_font, 10
            )
        else:
            y -= 10

    y -= 8
    y = _ensure_room(pdf, y, int(page_height), body_font)
    y = _section_title(pdf, "Suggested Forum", left, y, bold_font, body_font)
    for forum in response.suggested_forum:
        y = _ensure_room(pdf, y, int(page_height), body_font)
        y = _draw_wrapped_line(
            pdf, f"- {forum}", left, y, right_width, line_height, body_font, 10
        )

    if response.required_documents:
        y -= 8
        y = _ensure_room(pdf, y, int(page_height), body_font)
        y = _section_title(pdf, "Required Documents", left, y, bold_font, body_font)
        for doc in response.required_documents:
            y = _ensure_room(pdf, y, int(page_height), body_font)
            y = _draw_wrapped_line(
                pdf, f"- {doc}", left, y, right_width, line_height, body_font, 10
            )

    if response.limitation_hint:
        y -= 8
        y = _ensure_room(pdf, y, int(page_height), body_font)
        y = _section_title(pdf, "Limitation Note", left, y, bold_font, body_font)
        y = _draw_wrapped_line(
            pdf,
            response.limitation_hint,
            left,
            y,
            right_width,
            line_height,
            body_font,
            10,
        )

    if response.free_legal_aid:
        y -= 8
        y = _ensure_room(pdf, y, int(page_height), body_font)
        y = _section_title(pdf, "Free Legal Aid", left, y, bold_font, body_font)
        for aid in response.free_legal_aid:
            y = _ensure_room(pdf, y, int(page_height), body_font)
            y = _draw_wrapped_line(
                pdf, f"- {aid}", left, y, right_width, line_height, body_font, 10
            )

    if response.sources:
        y -= 8
        y = _ensure_room(pdf, y, int(page_height), body_font)
        y = _section_title(pdf, "Sources", left, y, bold_font, body_font)
        for source in response.sources:
            y = _ensure_room(pdf, y, int(page_height), body_font)
            pdf.setFont(bold_font, 10)
            head = f"- {source.title} ({source.section})"
            if getattr(source, "entry_type", "statute") == "illustrative_case":
                meta_bits: list[str] = ["illustrative pattern"]
                if source.district:
                    meta_bits.append(str(source.district))
                if source.outcome:
                    meta_bits.append(str(source.outcome))
                head = f"- {source.title} ({'; '.join(meta_bits)})"
            y = _draw_wrapped_line(
                pdf,
                head,
                left,
                y,
                right_width,
                line_height,
                bold_font,
                10,
            )
            pdf.setFont(body_font, 10)
            y = _draw_wrapped_line(
                pdf,
                f"  {source.snippet}",
                left,
                y,
                right_width,
                line_height,
                body_font,
                10,
            )
            if getattr(source, "entry_type", "statute") == "illustrative_case" and (
                source.forum_visited or source.documents_used
            ):
                extra_lines: list[str] = []
                if source.forum_visited:
                    extra_lines.append(f"Forum (pattern): {source.forum_visited}")
                if source.documents_used:
                    extra_lines.append("Documents (pattern): " + "; ".join(source.documents_used))
                for line in extra_lines:
                    y = _draw_wrapped_line(
                        pdf,
                        f"  {line}",
                        left,
                        y,
                        right_width,
                        line_height,
                        body_font,
                        9,
                    )

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
