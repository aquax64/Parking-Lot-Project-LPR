# =============================
# lpr_engine/utils.py
# =============================
import re

TN_PATTERN_1 = re.compile(r"^[A-Z0-9]{3}[0-9]{4}$")  # ABC1234
TN_PATTERN_2 = re.compile(r"^[0-9]{3}[A-Z0-9]{4}$")  # 123ABCD


def clean_plate_text(text: str) -> str:
    """Fix common OCR confusions (0→O) for TN passenger formats."""
    text = text.replace(" ", "").upper()
    if TN_PATTERN_1.match(text):
        return "".join("O" if c == "0" else c for c in text[:3]) + text[3:]
    if TN_PATTERN_2.match(text):
        return text[:3] + "".join("O" if c == "0" else c for c in text[3:])
    return text