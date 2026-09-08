"""
STEP 4: INSIGHT & RECOMMENDATION
-----------------------------------
What it does : Turns the raw gaps/scores from Step 3 into human-readable problems
                and specific, actionable recommendations.
Gets         : matching_skills, missing_skills, ats_keywords_status, match_score,
                resume_text
Gives        : problems (list of str), recommendations (list of str)
Uses         : AI (via Groq API) — natural language generation of specific, useful
                advice is not something rule-based Python can do well.

NOTE ON API KEY:
Same as extraction.py — the Groq client reads GROQ_API_KEY from the
environment, which is set from st.secrets in app.py. No key is hardcoded here.
"""

import json
import re
from groq import Groq

MODEL_NAME = "llama-3.3-70b-versatile"

RECOMMENDATION_PROMPT = """You are an expert resume coach and ATS specialist.
Based on the analysis data below, identify specific PROBLEMS with this resume
(relative to the target job) and give specific, actionable RECOMMENDATIONS to fix them.

Rules:
- Be specific, not generic. Reference actual missing skills/keywords by name.
- Each recommendation should be something the candidate can directly act on.
- Do not repeat the same point in both problems and recommendations.
- Return ONLY valid JSON, no other text, no markdown fences.

JSON schema:
{{
  "problems": ["list of specific issues found, 3-6 items"],
  "recommendations": ["list of specific fixes, 3-6 items, one per problem where possible"]
}}

Analysis data:
- Match score: {match_score}/100
- Matching skills: {matching_skills}
- Missing skills: {missing_skills}
- Missing ATS keywords: {missing_keywords}

Resume text (for context on structure/tone):
---
{resume_text}
---
"""


def _get_client() -> Groq:
    return Groq()  # reads GROQ_API_KEY from env automatically


def generate_recommendations(scoring_result: dict, resume_text: str) -> dict:
    """
    Main entry point for Step 4.

    Parameters
    ----------
    scoring_result : dict, output of scoring.run_scoring() from Step 3
    resume_text    : str, cleaned resume text from Step 1 (for tone/structure context)

    Returns
    -------
    dict with "problems" (list) and "recommendations" (list)
    """
    missing_keywords = [
        kw for kw, present in scoring_result["ats_keywords_status"].items() if not present
    ]

    prompt = RECOMMENDATION_PROMPT.format(
        match_score=scoring_result["match_score"],
        matching_skills=", ".join(scoring_result["matching_skills"]) or "None",
        missing_skills=", ".join(scoring_result["missing_skills"]) or "None",
        missing_keywords=", ".join(missing_keywords) or "None",
        resume_text=resume_text,
    )

    client = _get_client()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.choices[0].message.content
    cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {e}\nRaw output:\n{raw_text}")

    data.setdefault("problems", [])
    data.setdefault("recommendations", [])

    return data
