# backend/utils/text_utils.py
import re

def normalize_text(s: str) -> str:
    if not s:
        return s
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s
