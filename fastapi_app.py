from fastapi import FastAPI, UploadFile, Body
from agents import chat_agent, extraction_agent, report_agent
import os
import uuid

app = FastAPI() # Fast now!

@app.post("/chat")
async def chat(data: dict = Body(...)):
    query = data["query"]
    chat_history = data["chat_history"]
    result = chat_agent.execute(query, chat_history)
    return {"response": result}

@app.post("/analyze_document")
async def analyze_document(file: UploadFile):
    # Use a unique temporary filename to avoid conflicts
    temp_filename = f"{uuid.uuid4()}_{file.filename}"
    try:
        with open(temp_filename, "wb") as f:
            f.write(file.file.read())
        summary = extraction_agent.execute(temp_filename)
        return summary.dict()
    finally:
        # Ensure the temporary file is removed, even if an error occurs
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

@app.post("/generate_report")
async def generate_report(data: dict = Body(...)):
    report_type = data["report_type"]
    project_info = data["project_info"]
    parameters = data["parameters"]
    doc_summaries = data.get("doc_summaries")  # Optional, use .get() to avoid KeyError
    return report_agent.execute(report_type, project_info, parameters, doc_summaries).dict()