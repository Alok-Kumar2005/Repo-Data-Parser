import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    TEMP_DIR = "temp_repos"
    VECTOR_DB_PATH = "vector_store"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # supporting files
    SUPPORTED_EXTENSIONS = {'.py', '.cpp', '.cc', '.cxx', '.c++', '.h', '.hpp'}
    
    # model configuration
    GEMINI_MODEL = "gemini-pro"
    TEMPERATURE = 0.3
    MAX_TOKENS = 2048