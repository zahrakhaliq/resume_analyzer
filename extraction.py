"""
STEP 2: EXTRACTION
--------------------
What it does : Pulls structured data out of unstructured resume_text and jd_text
                (skills, experience, education, titles, required qualifications, keywords).
Gets         : resume_text (str), jd_text (str)
Gives        : resume_data (dict), jd_data (dict)
Uses         : AI (Claude) — understanding unstructured, free-form text needs an LLM,
                not rule-based Python.

NOTE ON API KEY:
The Anthropic client reads the key from the ANTHROPIC_API_KEY environment variable.
In app.py we set this from st.secrets["ANTHROPIC_API_KEY"] at startup, so no key is
ever hardcoded here.
"""

import json
import re
import anthropic

MODEL_NAME = "claude-sonnet-4-5"

RESUME_EXTRACTION_PROMPT = """You are an expert resume parser. Extract structured information
from the resume text below. Return ONLY valid JSON, no other text, no markdown fences.

JSON schema to follow exactly:
{{
  "skills": ["list of technical and soft skills mentioned"],
  "job_titles": ["list of past job titles"],
  "total_experience_years": <number, best estimate, 0 if unclear>,
  "education": ["list of degrees/certifications"],
  "summary_present": <true/false, whether resume has a summary/objective section>,
  "quantified_achievements_count": <number of bullet points that include measurable results, e.g. numbers, %, $>,
  "sections_found": ["list of resume sections detected, e.g. Experience, Education, Skills, Projects"]
}}

Resume text:
---
{resume_text}
---
"""

JD_EXTRACTION_PROMPT = """You are an expert technical recruiter. Extract structured information
from the job description below. Return ONLY valid JSON, no other text, no markdown fences.

JSON schema to follow exactly:
{{
  "required_skills": ["list of hard/technical skills explicitly required"],
  "preferred_skills": ["list of nice-to-have skills, if distinguishable, else empty list"],
  "required_experience_years": <number, best estimate, 0 if unclear>,
  "qualifications": ["list of required education/certifications"],
  "keywords": ["list of important ATS keywords: tools, titles, methodologies, certifications"],
  "seniority_level": "<e.g. Junior, Mid, Senior, Lead, Unclear>"
}}

Job description text:
---
{jd_text}
---
"""


def _get_client() -> anthropic.Anthropic:
    """Creates an Anthropic client using the API key from the environment."""
    return anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env automatically


def _call_claude_for_json(client: anthropic.Anthropic, prompt: str) -> dict:
    """Sends a prompt to Claude and parses the response as JSON."""
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = "".join(
        block.text for block in response.content if block.type == "text"
    )

    # Strip markdown fences if the model added them despite instructions
    cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {e}\nRaw output:\n{raw_text}")


def extract_resume_data(resume_text: str) -> dict:
    """
    Main entry point for Step 2 (resume side).

    Parameters
    ----------
    resume_text : str, cleaned resume text from Step 1

    Returns
    -------
    resume_data : dict matching the schema in RESUME_EXTRACTION_PROMPT
    """
    client = _get_client()
    prompt = RESUME_EXTRACTION_PROMPT.format(resume_text=resume_text)
    data = _call_claude_for_json(client, prompt)

    # Basic safety defaults in case the model omits a field
    data.setdefault("skills", [])
    data.setdefault("job_titles", [])
    data.setdefault("total_experience_years", 0)
    data.setdefault("education", [])
    data.setdefault("summary_present", False)
    data.setdefault("quantified_achievements_count", 0)
    data.setdefault("sections_found", [])

    return data


def extract_jd_data(jd_text: str) -> dict:
    """
    Main entry point for Step 2 (JD side).

    Parameters
    ----------
    jd_text : str, cleaned job description text from Step 1

    Returns
    -------
    jd_data : dict matching the schema in JD_EXTRACTION_PROMPT
    """
    client = _get_client()
    prompt = JD_EXTRACTION_PROMPT.format(jd_text=jd_text)
    data = _call_claude_for_json(client, prompt)

    data.setdefault("required_skills", [])
    data.setdefault("preferred_skills", [])
    data.setdefault("required_experience_years", 0)
    data.setdefault("qualifications", [])
    data.setdefault("keywords", [])
    data.setdefault("seniority_level", "Unclear")

    return data
