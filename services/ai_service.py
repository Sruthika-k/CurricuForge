from __future__ import annotations

import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

_PREFERRED_MODEL = "models/gemini-2.5-flash-lite"
_MAX_WEEKS = 12


def get_available_models() -> list[str]:
    """Return list of model names that support generateContent."""
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    data = response.json()
    return [
        m["name"]
        for m in data.get("models", [])
        if "gemini" in m.get("name", "").lower()
        and "generateContent" in m.get("supportedGenerationMethods", [])
    ]


def _select_model(models: list[str]) -> str:
    """Prefer flash-lite, then flash, then pro, then first available."""
    for keyword in ("flash-lite", "flash", "pro"):
        for m in models:
            if keyword in m:
                return m
    return models[0]


async def generate_curriculum(
    subject: str,
    level: str,
    duration: str,
    goals: str,
) -> str:
    """Generate curriculum using Gemini REST API. Returns clean plain text."""

    # Parse and cap duration
    try:
        weeks = min(int(re.sub(r"[^\d]", "", duration)), _MAX_WEEKS)
    except ValueError:
        weeks = 8

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY not configured."

    # Select model
    try:
        models = get_available_models()
        if not models:
            return "Error: No compatible Gemini model found."
        model = _select_model(models)
        print(f"Using model: {model}")
    except Exception as e:
        return f"Error fetching models: {e}"

    prompt = f"""You are an academic curriculum designer.

Generate a structured syllabus for the following course.

Subject: {subject}
Level: {level}
Duration: {weeks} weeks
Goals:
{goals}

Instructions:
- Return clean plain text only.
- Do not use markdown symbols (#, ##, **, *, ---, backticks).
- Do not use HTML tags.
- Use section headings in UPPERCASE on their own line.
- Separate sections with a single blank line.
- Be concise but structured.
- Limit each week to 4-5 bullet points using a dash (-).
- Keep assignments brief (2-3 lines each).
- Include one capstone project at the end.
- Align content explicitly to the stated goals.

Output these sections in order:
COURSE OVERVIEW
WEEKLY BREAKDOWN (Week 1 to Week {weeks})
ASSIGNMENTS
LEARNING OUTCOMES
ALIGNMENT TO STATED GOALS
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 3000,
        },
    }

    response = requests.post(url, json=payload, timeout=60)

    if response.status_code != 200:
        print("Gemini error:", response.status_code, response.text[:300])
        return f"Gemini API Error {response.status_code}: {response.text}"

    data = response.json()

    if "candidates" not in data:
        print("Unexpected response:", data)
        return f"Gemini Unexpected Response: {data}"

    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]

    # Strip any stray HTML tags or markdown symbols Gemini may still include
    clean_text = re.sub(r"<[^>]+>", "", raw_text)
    clean_text = re.sub(r"[*#`]+", "", clean_text)
    clean_text = re.sub(r"^\s*---+\s*$", "", clean_text, flags=re.MULTILINE)
    clean_text = re.sub(r"\n{3,}", "\n\n", clean_text)

    return clean_text.strip()
