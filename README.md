```markdown
# AI-Assisted Geotechnical Engineering App

This is an AI-assisted geotechnical engineering application built with Streamlit and FastAPI. It provides three main functionalities:
- **Expert Chat**: Ask geotechnical questions and get expert advice.
- **Document Analysis**: Upload geotechnical documents (PDFs) to extract key data like soil profiles and hazards.
- **Report Generator**: Generate detailed geotechnical reports based on project details and analyzed documents.

## Prerequisites
- Python 3.8 or higher
- A Google API key for the Gemini model (set in a `.env` file as `GOOGLE_API_KEY`)

## Setup
1. Clone the repository:
   ```
   git clone <your-repo-url>
   cd GEOTECH_APP
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your Google API key:
   ```
   GOOGLE_API_KEY=your-api-key-here
   ```

5. Run the FastAPI server:
   ```
   uvicorn fastapi_app:app --port 8000
   ```

6. In a separate terminal, run the Streamlit app:
   ```
   streamlit run streamlit_app.py
   ```

## Deployment on Streamlit
This app can be deployed on Streamlit Community Cloud. Ensure you have a `requirements.txt` file and set up your secrets (e.g., `GOOGLE_API_KEY`) in the Streamlit dashboard.

## Files
- `streamlit_app.py`: The main Streamlit application.
- `fastapi_app.py`: The FastAPI backend for handling API requests.
- `agents.py`: Contains the agent logic for chat, document extraction, and report generation.
- `models.py`: Defines Pydantic models for data validation.
- `prompts.py`: Contains prompt templates for the AI model.
```