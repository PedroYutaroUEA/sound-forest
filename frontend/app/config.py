import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    HOST = os.getenv("BACKEND_HOST", "backend")
    PORT = os.getenv("BACKEND_PORT", "5000")
    API_URL = f"http://{HOST}:{PORT}"
