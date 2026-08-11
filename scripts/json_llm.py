"""
scripts/json_llm.py
-------------------
Tolerant JSON extraction/parsing and LLM calls that must return JSON.
"""

from __future__ import annotations

import json
import re

from scripts.llm_provider import complete


def extract_json_blob(raw: str) -> str:
    """Pull the most likely JSON object/array out of a noisy model reply."""
    cleaned = raw.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fence:
        cleaned = fence.group(1).strip()
    starts = [i for i in (cleaned.find("{"), cleaned.find("[")) if i != -1]
    if starts:
        start = min(starts)
        end = max(cleaned.rfind("}"), cleaned.rfind("]"))
        if end > start:
            cleaned = cleaned[start:end + 1]
    return cleaned


def repair_json(text: str) -> str:
    """Fix common model JSON mistakes: trailing commas, smart quotes."""
    text = re.sub(r",\s*([}\]])", r"\1", text)
    for bad, good in (("\u201c", '"'), ("\u201d", '"'),
                      ("\u2018", "'"), ("\u2019", "'")):
        text = text.replace(bad, good)
    return text


def parse_json(raw: str) -> dict | list:
    """Tolerant JSON parse: strip fences/prose, repair, then parse."""
    blob = extract_json_blob(raw)
    try:
        return json.loads(blob)
    except json.JSONDecodeError:
        return json.loads(repair_json(blob))


def validate_keys(data, required_keys: list[str] | None) -> None:
    if not required_keys:
        return
    if not isinstance(data, dict):
        raise ValueError(
            f"Expected a JSON object with keys {required_keys}, got {type(data).__name__}"
        )
    missing = [k for k in required_keys if k not in data]
    if missing:
        raise ValueError(f"JSON missing required keys: {missing}")


def call_json(
    system: str,
    user: str,
    model: str,
    max_tokens: int = 2048,
    required_keys: list[str] | None = None,
    *,
    task: str | None = None,
    use_task_model: bool = False,
) -> dict | list:
    """LLM call that must return JSON. Parses, validates, retries once on failure."""
    try:
        raw = complete(system, user, model, max_tokens, task=task, use_task_model=use_task_model)
    except TypeError:
        raw = complete(system, user, model, max_tokens)
    try:
        data = parse_json(raw)
        validate_keys(data, required_keys)
        return data
    except Exception as first_err:  # noqa: BLE001
        print(f"    [retry] bad JSON ({first_err}); asking model to fix it...")
        corrective = (
            user
            + "\n\nIMPORTANT: Your previous response could NOT be parsed as the required JSON"
            + (f" or was missing keys {required_keys}" if required_keys else "")
            + f". Parser error: {first_err}.\n"
            + "Return ONLY a single valid JSON value — no prose, no markdown fences, "
            + "no trailing commas, all strings double-quoted."
        )
        try:
            raw2 = complete(system, corrective, model, max_tokens, task=task, use_task_model=use_task_model)
        except TypeError:
            raw2 = complete(system, corrective, model, max_tokens)
        data = parse_json(raw2)
        validate_keys(data, required_keys)
        return data
