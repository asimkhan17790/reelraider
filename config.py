import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]
YOUTUBE_CLIENT_SECRETS = os.getenv("YOUTUBE_CLIENT_SECRETS", "./client_secrets.json")
REGION_CODE = os.getenv("REGION_CODE", "US")
VIDEO_CATEGORY_ID = os.getenv("VIDEO_CATEGORY_ID", "10")
MAX_VIDEOS_PER_RUN = int(os.getenv("MAX_VIDEOS_PER_RUN", "5"))
DISCOVERY_FETCH_MULTIPLIER = int(os.getenv("DISCOVERY_FETCH_MULTIPLIER", "6"))
DISCOVERY_CATEGORY_ID = os.getenv("DISCOVERY_CATEGORY_ID", "")  # empty = no category filter; e.g. "10"=Music, "17"=Sports
CLIP_DURATION_SECONDS = int(os.getenv("CLIP_DURATION_SECONDS", "55"))
SHORT_TOTAL_DURATION = int(os.getenv("SHORT_TOTAL_DURATION", "25"))
SHORT_SEGMENT_DURATION = int(os.getenv("SHORT_SEGMENT_DURATION", "5"))
SHORT_SCORING_STEP = float(os.getenv("SHORT_SCORING_STEP", "0.5"))
if SHORT_SCORING_STEP <= 0:
    raise ValueError(f"SHORT_SCORING_STEP must be > 0, got {SHORT_SCORING_STEP}")
SHORT_CROP_MODE = os.getenv("SHORT_CROP_MODE", "center")
if SHORT_CROP_MODE not in {"center"}:
    raise ValueError(f"Invalid SHORT_CROP_MODE: {SHORT_CROP_MODE!r}. Only 'center' is supported in v1")
SHORT_TRANSITION_DURATION = float(os.getenv("SHORT_TRANSITION_DURATION", "0.3"))
if not (0.0 <= SHORT_TRANSITION_DURATION <= 1.0):
    raise ValueError(f"SHORT_TRANSITION_DURATION must be in [0.0, 1.0], got {SHORT_TRANSITION_DURATION}")
UPLOAD_PRIVACY = os.getenv("UPLOAD_PRIVACY", "private")
if UPLOAD_PRIVACY not in {"private", "unlisted", "public"}:
    raise ValueError(f"Invalid UPLOAD_PRIVACY: {UPLOAD_PRIVACY!r}. Must be one of: private, unlisted, public")
TEMP_DIR = os.getenv("TEMP_DIR", "./tmp")
DISCOVERY_KEYWORD = os.getenv("DISCOVERY_KEYWORD", "Mission Impossible")
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
