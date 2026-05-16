from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi # type: ignore[union-attr]
import config

DISCOVERY_KEYWORD = "Technology and Artificial Intelligence"


def find_viral_videos_by_keyword(keyword: str = DISCOVERY_KEYWORD) -> list[dict]:
    youtube = build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)
    search_response = youtube.search().list( # type: ignore[union-attr]
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
        return []

    videos_response = youtube.videos().list(  # type: ignore[union-attr]
        id=",".join(video_ids),
        part="snippet,statistics,contentDetails",
    ).execute()

    videos = []
    for item in videos_response.get("items", []):
        video_id = item["id"]
        stats = item.get("statistics", {})
        snippet = item["snippet"]
        content = item.get("contentDetails", {})

        try:
            transcript_entries = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = " ".join(e["text"] for e in transcript_entries)
        except Exception:
            transcript = None

        videos.append({
            "video_id": video_id,
            "title": snippet["title"],
            "description": snippet.get("description", ""),
            "channel": snippet["channelTitle"],
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "published_at": snippet.get("publishedAt", ""),
            "tags": snippet.get("tags", []),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "definition": content.get("definition", "sd"),
            "has_caption": content.get("caption", "false") == "true",
            "transcript": transcript,
        })

    return videos


def find_viral_videos() -> list[dict]:
    youtube = build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)

    # videos().list supports chart="mostPopular"; search().list does not
    response = youtube.videos().list(
        part="snippet",
        chart="mostPopular",
        regionCode=config.REGION_CODE,
        videoCategoryId=config.VIDEO_CATEGORY_ID,
        maxResults=config.MAX_VIDEOS_PER_RUN * 3,
    ).execute()

    videos = []
    for item in response.get("items", []):
        videos.append({
            "video_id": item["id"],
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "channel": item["snippet"]["channelTitle"],
            "url": f"https://www.youtube.com/watch?v={item['id']}",
        })

    return videos
find_viral_videos_by_keyword()