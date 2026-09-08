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
     GROQ_API_KEY = "gsk_your-key-here"
     ```
   - Locally: create `.streamlit/secrets.toml` in the project folder:
     ```
     GROQ_API_KEY = "gsk_your-key-here"
     ```

3. Run the app:
   ```
   streamlit run app.py
   ```

## Notes
- Uses the `groq` Python SDK, model `openai/gpt-oss-120b` (Groq deprecated its Llama
  chat models — this is their current recommended general-purpose model). The API
  key is read from `st.secrets["GROQ_API_KEY"]` in `app.py` and exported to the
  environment — it's never hardcoded anywhere. Swap `MODEL_NAME` in `extraction.py` /
  `recommendations.py` if you want a different Groq-hosted model (e.g. the smaller
  `openai/gpt-oss-20b`).
- Supported resume formats: PDF, DOCX, TXT.
- Scoring weights (in `scoring.py`) are adjustable: skills 55%, ATS keywords 25%,
  experience 15%, resume quality 5%.
