import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]
YOUTUBE_CLIENT_SECRETS = os.getenv("YOUTUBE_CLIENT_SECRETS", "./client_secrets.json")
REGION_CODE = os.getenv("REGION_CODE", "US")
VIDEO_CATEGORY_ID = os.getenv("VIDEO_CATEGORY_ID", "10")
MAX_VIDEOS_PER_RUN = int(os.getenv("MAX_VIDEOS_PER_RUN", "5"))
CLIP_DURATION_SECONDS = int(os.getenv("CLIP_DURATION_SECONDS", "55"))
UPLOAD_PRIVACY = os.getenv("UPLOAD_PRIVACY", "private")
TEMP_DIR = os.getenv("TEMP_DIR", "./tmp")
TOKEN_FILE = "token.json"
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
