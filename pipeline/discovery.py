import logging
import re
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import config

logger = logging.getLogger(__name__)

from config import DISCOVERY_KEYWORD


def _safe_int(val, default: int = 0) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def find_viral_videos_by_keyword(keyword: str = DISCOVERY_KEYWORD) -> list[dict]:
    logger.info("Searching YouTube for keyword=%r maxResults=%d", keyword, config.MAX_VIDEOS_PER_RUN * 3)
    youtube = build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)
    search_response = youtube.search().list(  # type: ignore[union-attr]
        q=keyword,
        type="video",
        order="viewCount",
        videoLicense="creativeCommon",
        regionCode=config.REGION_CODE,
        maxResults=config.MAX_VIDEOS_PER_RUN * 3,
        part="id",
    ).execute()

    video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
    if not video_ids:
        logger.warning("Search returned no video IDs for keyword=%r", keyword)
        return []

    logger.debug("Fetching details for %d video IDs", len(video_ids))
    videos_response = youtube.videos().list(  # type: ignore[union-attr]
        id=",".join(video_ids),
        part="snippet,statistics,contentDetails",
    ).execute()

    videos = []
    for item in videos_response.get("items", []):
        video_id = item["id"]
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            logger.warning("Skipping item with invalid video_id format: %r", video_id)
            continue
        stats = item.get("statistics", {})
        snippet = item["snippet"]
        content = item.get("contentDetails", {})

        try:
            transcript_entries = YouTubeTranscriptApi().fetch(video_id)  # type: ignore[attr-defined]
            transcript = " ".join(e.text for e in transcript_entries)
            logger.debug("Fetched transcript for video_id=%s (%d chars)", video_id, len(transcript))
        except Exception:
            logger.debug("No transcript available for video_id=%s", video_id)
            transcript = None

        videos.append({
            "video_id": video_id,
            "title": snippet["title"],
            "description": snippet.get("description", ""),
            "channel": snippet["channelTitle"],
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "published_at": snippet.get("publishedAt", ""),
            "tags": snippet.get("tags", []),
            "view_count": _safe_int(stats.get("viewCount")),
            "like_count": _safe_int(stats.get("likeCount")),
            "comment_count": _safe_int(stats.get("commentCount")),
            "definition": content.get("definition", "sd"),
            "has_caption": content.get("caption", "false") == "true",
            "transcript": transcript,
        })

    logger.info("Built metadata for %d videos", len(videos))
    return videos
