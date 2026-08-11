"""
scripts/text_utils.py
---------------------
Shared plain-text helpers (LaTeX stripping, etc.).
"""

from __future__ import annotations

import re


def strip_latex(text: str) -> str:
    """Remove common LaTeX markup so LLMs see readable plain text."""
    text = re.sub(r"\\textbf\{([^}]+)\}", r"\1", text)
    text = re.sub(r"\\textit\{([^}]+)\}", r"\1", text)
    text = re.sub(r"\\emph\{([^}]+)\}", r"\1", text)
    text = re.sub(r"\\texttimes\{\}", "×", text)
    text = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    text = text.replace("\\%", "%").replace("\\&", "&")
    text = text.replace("\\$", "$").replace("\\_", "_")
    text = text.replace("\\#", "#").replace("{", "").replace("}", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()
