# AI Resume Analyzer

## Files
- `input_parsing.py` — Step 1 (Python): reads PDF/DOCX/TXT resume, cleans JD text
- `extraction.py` — Step 2 (AI): extracts structured skills/experience from resume & JD
- `scoring.py` — Step 3 (Python): compares data, computes match score
- `recommendations.py` — Step 4 (AI): generates problems + recommendations
- `output.py` — Step 5 (Python): assembles the final report
- `app.py` — Streamlit UI that runs the full workflow

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Add your API key in Streamlit secrets — **do not put it in code.**
   - On Streamlit Community Cloud: go to your app → Settings → Secrets, and add:
     ```
     ANTHROPIC_API_KEY = "sk-ant-your-key-here"
     ```
   - Locally: create `.streamlit/secrets.toml` in the project folder:
     ```
     ANTHROPIC_API_KEY = "sk-ant-your-key-here"
     ```

3. Run the app:
   ```
   streamlit run app.py
   ```

## Notes
- Uses the `anthropic` Python SDK (Claude). The API key is read from
  `st.secrets["ANTHROPIC_API_KEY"]` in `app.py` and exported to the environment —
  it's never hardcoded anywhere.
- Supported resume formats: PDF, DOCX, TXT.
- Scoring weights (in `scoring.py`) are adjustable: skills 55%, ATS keywords 25%,
  experience 15%, resume quality 5%.
