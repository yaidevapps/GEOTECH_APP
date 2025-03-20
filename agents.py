import os
import logging
from dotenv import load_dotenv
from pydantic_ai import Agent, Tool
import google.generativeai as genai
from langchain_community.document_loaders import PyPDFLoader
from models import DocumentSummary, Report
from prompts import create_geotech_expert_prompt, create_document_analysis_prompt, create_report_generation_prompt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

# Custom provider-like wrapper for Google Gemini
class GoogleGeminiProvider:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")  # Use a valid model

    def generate(self, prompt: str) -> str:
        return self.model.generate_content(prompt).text

# Initialize the provider with API key from .env
provider = GoogleGeminiProvider(api_key=os.getenv("GOOGLE_API_KEY"))

# Utility function to clean LLM responses
def clean_response(response: str) -> str:
    """Clean the LLM response by removing ```json or ``` markers."""
    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-len("```")].strip()
    return cleaned

class ValidationTool(Tool):
    def __init__(self):
        # Define the validation logic as a standalone function
        def validate(params: dict) -> str:
            ranges = {"cohesion": (0, 50), "bearing_capacity": (100, 300)}  # kPa
            for key, value in params.items():
                if key in ranges and (value < ranges[key][0] or value > ranges[key][1]):
                    return f"Warning: {key} ({value} kPa) outside typical range {ranges[key]}."
            return "Parameters within expected ranges."
        
        # Pass the function to the Tool constructor
        super().__init__(
            name="validate_parameters",
            description="Validates geotechnical parameters against expected ranges.",
            function=validate
        )

class ChatAgent(Agent):
    name = "chat_agent"
    description = "Handles general geotechnical queries."

    def execute(self, query: str, chat_history: str) -> str:
        prompt = create_geotech_expert_prompt(query, chat_history)
        return provider.generate(prompt)

class ExtractionAgent(Agent):
    name = "extraction_agent"
    description = "Extracts data from geotechnical documents."

    def execute(self, file_path: str) -> DocumentSummary:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        content = " ".join([doc.page_content for doc in docs])
        prompt = create_document_analysis_prompt(content)
        response = provider.generate(prompt)
        logger.info(f"Raw LLM response: {response}")
        
        # Clean the response
        cleaned_response = clean_response(response)
        logger.debug(f"Cleaned LLM response: {cleaned_response}")

        try:
            return DocumentSummary.parse_raw(cleaned_response)
        except Exception as e:
            logger.error(f"Error parsing response into DocumentSummary: {e}, Cleaned Response: {cleaned_response}")
            raise

class ReportAgent(Agent):
    name = "report_agent"
    description = "Generates geotechnical reports."
    tools = [ValidationTool()]

    def execute(self, report_type: str, project_info: str, parameters: str, doc_summaries: list = None) -> Report:
        ref_docs = "\n".join([str(summary) for summary in doc_summaries]) if doc_summaries else None
        prompt = create_report_generation_prompt(report_type, project_info, parameters, ref_docs)
        response = provider.generate(prompt)
        logger.info(f"Raw LLM response: {response}")
        
        # Clean the response
        cleaned_response = clean_response(response)
        logger.debug(f"Cleaned LLM response: {cleaned_response}")

        try:
            return Report.parse_raw(cleaned_response)
        except Exception as e:
            logger.error(f"Error parsing response into Report: {e}, Cleaned Response: {cleaned_response}")
            raise

# Initialize agents
chat_agent = ChatAgent()
extraction_agent = ExtractionAgent()
report_agent = ReportAgent()