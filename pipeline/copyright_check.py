import logging
from googleapiclient.discovery import build
import config

logger = logging.getLogger(__name__)


def filter_safe_videos(videos: list[dict]) -> list[dict]:
    if not videos:
        return []

    logger.info("Copyright check: evaluating %d videos", len(videos))
    youtube = build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)
    ids = [v["video_id"] for v in videos]

    response = youtube.videos().list(
        part="contentDetails,status",
        id=",".join(ids),
    ).execute()

    safe_ids = set()
    for item in response.get("items", []):
        content = item.get("contentDetails", {})
        status = item.get("status", {})
        is_cc = status.get("license") == "creativeCommon"
        has_restriction = bool(content.get("regionRestriction"))
        if is_cc and not has_restriction:
            safe_ids.add(item["id"])
        else:
            logger.debug(
                "Filtered out video_id=%s is_cc=%s has_restriction=%s",
                item["id"],
                is_cc,
                has_restriction,
            )

    safe = [v for v in videos if v["video_id"] in safe_ids]
    result = safe[:config.MAX_VIDEOS_PER_RUN]
    logger.info("Copyright check complete: %d/%d videos passed", len(result), len(videos))
    return result
