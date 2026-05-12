from googleapiclient.discovery import build
import config


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
