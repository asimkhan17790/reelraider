from googleapiclient.discovery import build
import config


def filter_safe_videos(videos: list[dict]) -> list[dict]:
    if not videos:
        return []

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
        is_cc = content.get("licensedContent") is False or status.get("license") == "creativeCommon"
        has_restriction = bool(content.get("regionRestriction"))
        if is_cc and not has_restriction:
            safe_ids.add(item["id"])

    safe = [v for v in videos if v["video_id"] in safe_ids]
    return safe[:config.MAX_VIDEOS_PER_RUN]
