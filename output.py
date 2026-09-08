"""
STEP 5: OUTPUT / FINAL RESULT
--------------------------------
What it does : Combines everything from Steps 3 & 4 into one final, clean
                report structure ready for display in the UI.
Gets         : match_score, matching_skills, missing_skills, ats_keywords_status,
                problems, recommendations
Gives        : final_report (dict) — the single object the UI renders
Uses         : Pure Python — just assembling/formatting data, no intelligence needed.
"""


def build_final_report(scoring_result: dict, recommendation_result: dict) -> dict:
    """
    Main entry point for Step 5.

    Parameters
    ----------
    scoring_result         : dict, output of scoring.run_scoring() (Step 3)
    recommendation_result  : dict, output of recommendations.generate_recommendations() (Step 4)

    Returns
    -------
    final_report : dict, ready to hand to the Streamlit UI

    Raises
    ------
    ValueError if required fields are missing/empty (final sanity check).
    """
    ats_status = scoring_result.get("ats_keywords_status", {})
    ats_matched = [kw for kw, present in ats_status.items() if present]
    ats_missing = [kw for kw, present in ats_status.items() if not present]

    final_report = {
        "match_score": scoring_result.get("match_score"),
        "matching_skills": scoring_result.get("matching_skills", []),
        "missing_skills": scoring_result.get("missing_skills", []),
        "ats_keywords_matched": ats_matched,
        "ats_keywords_missing": ats_missing,
        "problems": recommendation_result.get("problems", []),
        "recommendations": recommendation_result.get("recommendations", []),
    }

    # Final sanity checks before handing off to the UI
    if final_report["match_score"] is None:
        raise ValueError("Final report is missing a match_score.")
    if not (0 <= final_report["match_score"] <= 100):
        raise ValueError(f"match_score out of range: {final_report['match_score']}")

    return final_report


def score_label(match_score: int) -> str:
    """Returns a short human-readable label for a given score, for the UI."""
    if match_score >= 85:
        return "Excellent Match"
    elif match_score >= 70:
        return "Strong Match"
    elif match_score >= 50:
        return "Moderate Match"
    elif match_score >= 30:
        return "Weak Match"
    else:
        return "Poor Match"
