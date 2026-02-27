from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o-mini"
DB_PATH = "commitiq.db"
CHROMA_PATH = "chroma_store"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY