from googleapiclient.discovery import build
import config


def find_viral_videos() -> list[dict]:
    youtube = build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)

    response = youtube.search().list(
        part="snippet",
        chart="mostPopular",
        regionCode=config.REGION_CODE,
        videoCategoryId=config.VIDEO_CATEGORY_ID,
        videoLicense="creativeCommon",
        type="video",
        maxResults=config.MAX_VIDEOS_PER_RUN * 3,  # fetch extra, filter narrows it down
    ).execute()

    videos = []
    for item in response.get("items", []):
        videos.append({
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "channel": item["snippet"]["channelTitle"],
            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
        })

    return videos
