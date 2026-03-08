"""
AI summarization adapter for PhishLens.

Accepts a list of incident dicts and returns a structured digest using OpenAI.
Returns None if AI is unavailable, unconfigured, or returns malformed output,
so the caller can fall back to deterministic summarization.
"""

import json
import os


def _get_client():
    """Create an OpenAI client if a key is configured, else return None."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key or api_key == "your_key_here":
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except Exception:
        return None


SYSTEM_PROMPT = (
    "You are a calm, helpful community safety assistant. "
    "Given one or more local incident reports, produce a short digest. "
    "Respond ONLY with valid JSON using exactly these keys:\n"
    '  "summary": a 1-2 sentence digest of the reports,\n'
    '  "explanation": a calm explanation of the likely threat,\n'
    '  "actions": a list of 3-5 recommended next steps (strings),\n'
    '  "confidence_note": a short note about confidence or limitations.\n'
    "Do not add any other keys or text outside the JSON object. "
    "Never claim certainty. Use phrases like 'likely', 'appears to be', "
    "'recommended'. Do not use alarming language."
)


def _build_user_prompt(incidents: list[dict]) -> str:
    """Format incidents into a readable prompt for the model."""
    parts = []
    for inc in incidents:
        parts.append(
            f"- [{inc.get('suspected_category', 'unknown')}] "
            f"{inc.get('title', 'Untitled')}\n"
            f"  Neighborhood: {inc.get('neighborhood', 'Unknown')}\n"
            f"  Description: {inc.get('description', 'No description')}\n"
            f"  Date: {inc.get('timestamp', 'Unknown')}"
        )
    return "Summarize these local incident reports:\n\n" + "\n\n".join(parts)


def _parse_response(text: str) -> dict | None:
    """Parse the model's JSON response into the expected shape.

    Returns None if the response is missing required keys or is not valid JSON.
    """
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None

    required_keys = {"summary", "explanation", "actions", "confidence_note"}
    if not required_keys.issubset(data.keys()):
        return None

    if not isinstance(data["actions"], list):
        return None

    return {
        "summary": str(data["summary"]),
        "explanation": str(data["explanation"]),
        "actions": [str(a) for a in data["actions"]],
        "confidence_note": str(data["confidence_note"]),
    }


def summarize_incidents(incidents: list[dict]) -> dict | None:
    """Generate an AI digest for the given incidents.

    Returns a dict with keys: summary, explanation, actions, confidence_note.
    Returns None if AI is unavailable or fails, so the caller should use
    the deterministic fallback in that case.
    """
    if not incidents:
        return None

    client = _get_client()
    if client is None:
        return None

    provider = os.environ.get("AI_PROVIDER", "openai").lower()
    default_model = "gemini-2.0-flash-lite" if provider == "gemini" else "gpt-4o-mini"
    model = os.environ.get("MODEL_NAME") or default_model

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(incidents)},
            ],
            temperature=0.3,
            max_tokens=512,
        )
        text = response.choices[0].message.content.strip()
        return _parse_response(text)
    except Exception:
        # Any API error — network, auth, rate limit, etc.
        return None
