import logging
import os
import re
import yt_dlp
import config

logger = logging.getLogger(__name__)


def download_video(video: dict) -> str | None:
    video_id = video["video_id"]
    logger.debug("download_video: video_id=%s url=%s", video_id, video.get("url"))
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ValueError(f"Invalid video_id format: {video_id!r}")
    os.makedirs(config.TEMP_DIR, exist_ok=True)
    out_path = os.path.join(config.TEMP_DIR, f"{video_id}.mp4")

    if os.path.exists(out_path):
        logger.info("Cache hit — skipping download for video_id=%s", video_id)
        return out_path

    logger.info("Downloading video_id=%s url=%s", video_id, video["url"])
    ydl_opts = {
        "format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]",
        "outtmpl": out_path,
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video["url"]])
        logger.info("Download complete: video_id=%s path=%s", video_id, out_path)
        return out_path
    except Exception:
        logger.exception("Download failed for video_id=%s", video_id)
        return None
