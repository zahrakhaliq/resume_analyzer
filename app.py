"""
MAIN APP — Streamlit UI
--------------------------
Ties together all 5 workflow steps:
  1. input_parsing   -> resume_text, jd_text
  2. extraction       -> resume_data, jd_data
  3. scoring          -> matching_skills, missing_skills, ats_keywords_status, match_score
  4. recommendations  -> problems, recommendations
  5. output           -> final_report (displayed here)

API KEY:
This app expects ANTHROPIC_API_KEY to be set in Streamlit secrets
(Settings -> Secrets, or .streamlit/secrets.toml locally):

    ANTHROPIC_API_KEY = "sk-ant-..."

The key is never written in code. We read it from st.secrets and export it to
the environment so extraction.py / recommendations.py (via the anthropic SDK)
can pick it up automatically.
"""

import os
import streamlit as st

# --- Load API key from Streamlit secrets into the environment BEFORE importing
# modules that create an anthropic.Anthropic() client ---
if "ANTHROPIC_API_KEY" in st.secrets:
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]

from input_parsing import parse_resume, parse_job_description, ParsingError
from extraction import extract_resume_data, extract_jd_data
from scoring import run_scoring
from recommendations import generate_recommendations
from output import build_final_report, score_label


st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

st.title("📄 AI Resume Analyzer")
st.caption("Upload your resume and paste a job description to see how well you match.")

if "ANTHROPIC_API_KEY" not in os.environ:
    st.error(
        "No API key found. Please add ANTHROPIC_API_KEY in your Streamlit app's "
        "Secrets before running an analysis."
    )

col1, col2 = st.columns(2)

with col1:
    uploaded_resume = st.file_uploader(
        "Upload your resume", type=["pdf", "docx", "txt"]
    )

with col2:
    jd_input = st.text_area(
        "Paste the job description", height=300,
        placeholder="Paste the full job description here..."
    )

analyze_clicked = st.button("Analyze Match", type="primary", use_container_width=True)

if analyze_clicked:
    if not uploaded_resume:
        st.warning("Please upload a resume file.")
        st.stop()
    if not jd_input or not jd_input.strip():
        st.warning("Please paste a job description.")
        st.stop()
    if "ANTHROPIC_API_KEY" not in os.environ:
        st.stop()

    try:
        # ---------- STEP 1: Input & Parsing (Python) ----------
        with st.spinner("Step 1/5: Reading resume and job description..."):
            resume_text = parse_resume(uploaded_resume)
            jd_text = parse_job_description(jd_input)

        # ---------- STEP 2: Extraction (AI) ----------
        with st.spinner("Step 2/5: Extracting skills and requirements..."):
            resume_data = extract_resume_data(resume_text)
            jd_data = extract_jd_data(jd_text)

        # ---------- STEP 3: Comparison & Scoring (Python) ----------
        with st.spinner("Step 3/5: Comparing resume against job description..."):
            scoring_result = run_scoring(resume_data, jd_data)

        # ---------- STEP 4: Insight & Recommendations (AI) ----------
        with st.spinner("Step 4/5: Generating recommendations..."):
            recommendation_result = generate_recommendations(scoring_result, resume_text)

        # ---------- STEP 5: Output (Python) ----------
        with st.spinner("Step 5/5: Building final report..."):
            final_report = build_final_report(scoring_result, recommendation_result)

        st.success("Analysis complete!")

        # ---------------- DISPLAY RESULTS ----------------
        score = final_report["match_score"]
        st.subheader(f"Match Score: {score}/100 — {score_label(score)}")
        st.progress(score / 100)

        res_col1, res_col2 = st.columns(2)

        with res_col1:
            st.markdown("### ✅ Matching Skills")
            if final_report["matching_skills"]:
                for skill in final_report["matching_skills"]:
                    st.markdown(f"- {skill}")
            else:
                st.markdown("_No matching skills found._")

            st.markdown("### 🔑 ATS Keywords Matched")
            if final_report["ats_keywords_matched"]:
                for kw in final_report["ats_keywords_matched"]:
                    st.markdown(f"- {kw}")
            else:
                st.markdown("_None found._")

        with res_col2:
            st.markdown("### ❌ Missing Skills")
            if final_report["missing_skills"]:
                for skill in final_report["missing_skills"]:
                    st.markdown(f"- {skill}")
            else:
                st.markdown("_No missing skills — great fit!_")

            st.markdown("### 🔑 ATS Keywords Missing")
            if final_report["ats_keywords_missing"]:
                for kw in final_report["ats_keywords_missing"]:
                    st.markdown(f"- {kw}")
            else:
                st.markdown("_None missing._")

        st.markdown("### ⚠️ Problems Found")
        if final_report["problems"]:
            for problem in final_report["problems"]:
                st.markdown(f"- {problem}")
        else:
            st.markdown("_No major problems found._")

        st.markdown("### 💡 Recommendations")
        if final_report["recommendations"]:
            for rec in final_report["recommendations"]:
                st.markdown(f"- {rec}")
        else:
            st.markdown("_No recommendations — resume looks strong._")

    except ParsingError as e:
        st.error(f"Parsing error: {e}")
    except ValueError as e:
        st.error(f"Processing error: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
