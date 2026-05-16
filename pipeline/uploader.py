import logging
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import config

logger = logging.getLogger(__name__)


def _get_credentials() -> Credentials:
    creds = None
    if os.path.exists(config.TOKEN_FILE):
        logger.debug("Loading credentials from %s", config.TOKEN_FILE)
        creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.YOUTUBE_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired OAuth token")
            creds.refresh(Request())
        else:
            logger.info("No valid token found — launching OAuth flow")
            flow = InstalledAppFlow.from_client_secrets_file(
                config.YOUTUBE_CLIENT_SECRETS, config.YOUTUBE_SCOPES
            )
            creds = flow.run_local_server(port=0)
        fd = os.open(config.TOKEN_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(creds.to_json())
        logger.debug("Credentials saved to %s", config.TOKEN_FILE)

    return creds


def upload_clip(clip_path: str, metadata: dict) -> str | None:
    logger.info("Uploading clip: path=%s title=%r", clip_path, metadata["title"])
    try:
        creds = _get_credentials()
        youtube = build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {
                "title": metadata["title"],
                "description": metadata["description"],
                "tags": metadata["tags"],
                "categoryId": config.VIDEO_CATEGORY_ID,
            },
            "status": {
                "privacyStatus": config.UPLOAD_PRIVACY,
            },
        }

        media = MediaFileUpload(clip_path, mimetype="video/mp4", resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

        response = None
        chunk_count = 0
        while response is None:
            _, response = request.next_chunk()
            chunk_count += 1
            if chunk_count > 100:
                raise RuntimeError("Upload stalled after 100 chunks")

        video_id = response["id"]
        logger.info("Upload complete: https://youtube.com/watch?v=%s", video_id)
        return video_id
    except Exception:
        logger.exception("Upload failed for clip_path=%s", clip_path)
        return None
