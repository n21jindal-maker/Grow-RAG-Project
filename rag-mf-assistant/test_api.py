import os
from dotenv import load_dotenv

# Try importing the key dependencies to verify installation
try:
    import langchain
    import chromadb
    import google.generativeai as genai
    print("Dependencies successfully installed!")
except ImportError as e:
    print(f"Error importing dependencies: {e}")

# Verify API Keys (if provided in .env)
load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key and gemini_key != "your_gemini_api_key_here":
    print("GEMINI_API_KEY is found in the .env file.")
else:
    print("GEMINI_API_KEY is missing or using the default template value.")
