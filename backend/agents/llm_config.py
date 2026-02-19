# backend/agents/llm_config.py
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Using Gemini 2 Flash for high efficiency and RPM limits
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-001", # Using the Flash model
    temperature=0, # Setting to 0 for maximum determinism and no hallucinations
    google_api_key=os.getenv("GEMINI_API_KEY")
)