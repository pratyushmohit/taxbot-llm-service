import logging
import os
import dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.getcwd(), ".env")
dotenv.load_dotenv(dotenv_path)

class EnvironmentVariables:
    logging.info("Loading environment variables...")

    # OpenAI Credentials
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # MongoDB Atlas credentials
    DB_URI = os.getenv("MONGO_DB_URI")
    DB_NAME = os.getenv("MONGO_DB_NAME")

    # Tavily Seach API Credentials
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

    # Endpoints
    RETRIEVE_FROM_VECTOR_DATABASE_ENDPOINT = os.getenv("RETRIEVE_FROM_VECTOR_DATABASE_ENDPOINT")
    logging.info("Successfully loaded all environment variables.")