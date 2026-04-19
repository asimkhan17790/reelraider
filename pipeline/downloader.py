import os
import yt_dlp
import config


def download_video(video: dict) -> str | None:
    os.makedirs(config.TEMP_DIR, exist_ok=True)
    out_path = os.path.join(config.TEMP_DIR, f"{video['video_id']}.mp4")

    if os.path.exists(out_path):
        return out_path

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
        return out_path
    except Exception as e:
        print(f"[downloader] failed {video['video_id']}: {e}")
        return None
