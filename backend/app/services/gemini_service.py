import logging
import json
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"


def _get_client():
    try:
        from google import genai
        return genai.Client(api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {e}")
        return None


def _parse_json(text: str) -> dict | list:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


async def extract_task_entities(raw_text: str) -> dict:
    """
    Extract task metadata from raw text using Gemini.
    Returns: {title, impact, urgency, energy_required, is_big_rock}
    Falls back to defaults on error.
    """
    default = {
        "title": raw_text[:100] if raw_text else "Untitled task",
        "impact": 3,
        "urgency": 3,
        "energy_required": 3,
        "is_big_rock": False,
    }

    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set — using default task metadata")
        return default

    try:
        client = _get_client()
        if not client:
            return default

        prompt = f"""Analyze this task/message and extract structured metadata.

Text: "{raw_text[:2000]}"

Return ONLY valid JSON with these exact fields:
{{
  "title": "concise task title (max 100 chars)",
  "impact": <1-5 integer, how impactful is completing this>,
  "urgency": <1-5 integer, how time-sensitive is this>,
  "energy_required": <1-5 integer, how much mental effort does this require>,
  "is_big_rock": <true if energy_required >= 4 AND impact >= 4, else false>
}}

Respond with ONLY the JSON object, no other text."""

        response = client.models.generate_content(model=MODEL, contents=prompt)
        result = _parse_json(response.text)

        return {
            "title": str(result.get("title", default["title"]))[:100],
            "impact": max(1, min(5, int(result.get("impact", 3)))),
            "urgency": max(1, min(5, int(result.get("urgency", 3)))),
            "energy_required": max(1, min(5, int(result.get("energy_required", 3)))),
            "is_big_rock": bool(result.get("is_big_rock", False)),
        }
    except Exception as e:
        logger.error(f"Gemini entity extraction failed: {e}")
        return default


async def generate_task_breakdown(task_title: str, task_description: Optional[str] = None) -> list[str]:
    """
    Generate exactly 3 actionable sub-steps for a task using Gemini.
    Falls back to generic steps on error.
    """
    default_steps = [
        f"Start working on: {task_title[:50]}",
        "Make progress for 15 minutes",
        "Review and decide next action",
    ]

    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set — using default sub-steps")
        return default_steps

    try:
        client = _get_client()
        if not client:
            return default_steps

        context = f"Task: {task_title}"
        if task_description:
            context += f"\nDescription: {task_description[:500]}"

        prompt = f"""{context}

Break this task into EXACTLY 3 small, concrete, actionable sub-steps.
Each step should take 5-15 minutes maximum.
Make them specific and immediately actionable.

Return ONLY valid JSON:
{{"sub_steps": ["step 1", "step 2", "step 3"]}}

No other text."""

        response = client.models.generate_content(model=MODEL, contents=prompt)
        result = _parse_json(response.text)
        steps = result.get("sub_steps", [])

        if len(steps) != 3:
            return default_steps

        return [str(s)[:200] for s in steps[:3]]
    except Exception as e:
        logger.error(f"Gemini task breakdown failed: {e}")
        return default_steps
