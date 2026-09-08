"""
STEP 3: COMPARISON & SCORING
------------------------------
What it does : Compares resume_data vs jd_data. Finds matching/missing skills,
                checks ATS keyword presence, calculates a final match score.
Gets         : resume_data (dict), jd_data (dict)
Gives        : matching_skills (list), missing_skills (list),
                ats_keywords_status (dict), match_score (int, 0-100)
Uses         : Pure Python (rule-based) — kept deterministic and explainable,
                not left to the AI to "guess" a score.
"""

import re

# Weights for the final score. Must sum to 1.0
WEIGHT_SKILLS = 0.55
WEIGHT_KEYWORDS = 0.25
WEIGHT_EXPERIENCE = 0.15
WEIGHT_QUALITY = 0.05  # summary present + quantified achievements


def _normalize(term: str) -> str:
    """Lowercase and strip a skill/keyword string for comparison."""
    return re.sub(r"[^a-z0-9+#. ]", "", term.lower().strip())


def _match_terms(resume_terms: list, target_terms: list) -> tuple:
    """
    Compares two lists of terms (case-insensitive, normalized).

    Returns
    -------
    (matched, missing) : both lists of the ORIGINAL target_terms strings
    """
    normalized_resume = {_normalize(t) for t in resume_terms if t}
    matched, missing = [], []

    for term in target_terms:
        norm = _normalize(term)
        if not norm:
            continue
        # exact match OR substring match (covers "React" vs "React.js", etc.)
        if norm in normalized_resume or any(
            norm in r or r in norm for r in normalized_resume
        ):
            matched.append(term)
        else:
            missing.append(term)

    return matched, missing


def compare_skills(resume_data: dict, jd_data: dict) -> dict:
    """Compares required + preferred JD skills against resume skills."""
    required = jd_data.get("required_skills", [])
    preferred = jd_data.get("preferred_skills", [])
    resume_skills = resume_data.get("skills", [])

    matched_required, missing_required = _match_terms(resume_skills, required)
    matched_preferred, missing_preferred = _match_terms(resume_skills, preferred)

    return {
        "matching_skills": matched_required + matched_preferred,
        "missing_skills": missing_required + missing_preferred,
        "matched_required": matched_required,
        "missing_required": missing_required,
        "matched_preferred": matched_preferred,
        "missing_preferred": missing_preferred,
    }


def check_ats_keywords(resume_data: dict, jd_data: dict) -> dict:
    """Checks which ATS-critical keywords from the JD appear in the resume."""
    keywords = jd_data.get("keywords", [])
    resume_skills = resume_data.get("skills", [])
    resume_titles = resume_data.get("job_titles", [])
    resume_terms = resume_skills + resume_titles

    matched, missing = _match_terms(resume_terms, keywords)

    status = {kw: (kw in matched) for kw in keywords}

    return {
        "ats_keywords_status": status,
        "ats_matched": matched,
        "ats_missing": missing,
    }


def calculate_experience_score(resume_data: dict, jd_data: dict) -> float:
    """Returns a 0-1 score for how experience compares to requirement."""
    required_years = jd_data.get("required_experience_years", 0) or 0
    resume_years = resume_data.get("total_experience_years", 0) or 0

    if required_years <= 0:
        return 1.0  # JD didn't specify, don't penalize

    if resume_years >= required_years:
        return 1.0

    return round(resume_years / required_years, 2)


def calculate_quality_score(resume_data: dict) -> float:
    """Returns a 0-1 score based on resume 'quality' signals."""
    score = 0.0
    if resume_data.get("summary_present"):
        score += 0.4
    quantified = resume_data.get("quantified_achievements_count", 0)
    score += min(quantified / 5, 1.0) * 0.6  # cap benefit at 5+ quantified bullets
    return round(score, 2)


def calculate_match_score(skills_result: dict, ats_result: dict,
                           experience_score: float, quality_score: float,
                           jd_data: dict) -> int:
    """Combines all sub-scores into one final 0-100 match score."""
    total_required = len(skills_result["matched_required"]) + len(skills_result["missing_required"])
    skills_score = (
        len(skills_result["matched_required"]) / total_required
        if total_required > 0 else 1.0
    )

    total_keywords = len(jd_data.get("keywords", []))
    keyword_score = (
        len(ats_result["ats_matched"]) / total_keywords
        if total_keywords > 0 else 1.0
    )

    final = (
        skills_score * WEIGHT_SKILLS
        + keyword_score * WEIGHT_KEYWORDS
        + experience_score * WEIGHT_EXPERIENCE
        + quality_score * WEIGHT_QUALITY
    )

    return round(final * 100)


def run_scoring(resume_data: dict, jd_data: dict) -> dict:
    """
    Main entry point for Step 3.

    Parameters
    ----------
    resume_data : dict from Step 2
    jd_data     : dict from Step 2

    Returns
    -------
    dict with matching_skills, missing_skills, ats_keywords_status, match_score,
    plus sub-scores for transparency.
    """
    skills_result = compare_skills(resume_data, jd_data)
    ats_result = check_ats_keywords(resume_data, jd_data)
    experience_score = calculate_experience_score(resume_data, jd_data)
    quality_score = calculate_quality_score(resume_data)

    match_score = calculate_match_score(
        skills_result, ats_result, experience_score, quality_score, jd_data
    )

    # sanity check: score must be within valid range
    match_score = max(0, min(100, match_score))

    return {
        "matching_skills": skills_result["matching_skills"],
        "missing_skills": skills_result["missing_skills"],
        "ats_keywords_status": ats_result["ats_keywords_status"],
        "match_score": match_score,
        "experience_score": experience_score,
        "quality_score": quality_score,
    }
