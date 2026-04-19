import os
import numpy as np
from moviepy.editor import VideoFileClip
import config


def _find_best_window(clip: VideoFileClip, duration: int) -> float:
    """Return start time of highest-energy audio window."""
    try:
        audio = clip.audio
        if audio is None:
            return 0.0
        fps = 22050
        samples = audio.to_soundarray(fps=fps)
        if samples.ndim > 1:
            samples = samples.mean(axis=1)

        window = int(fps * duration)
        step = int(fps * 5)
        best_start = 0
        best_rms = -1.0

        for i in range(0, len(samples) - window, step):
            rms = float(np.sqrt(np.mean(samples[i:i + window] ** 2)))
            if rms > best_rms:
                best_rms = rms
                best_start = i

        return best_start / fps
    except Exception:
        return 0.0


def extract_clip(video_path: str, video_id: str) -> str | None:
    os.makedirs(config.TEMP_DIR, exist_ok=True)
    out_path = os.path.join(config.TEMP_DIR, f"{video_id}_clip.mp4")

    if os.path.exists(out_path):
        return out_path

    try:
        with VideoFileClip(video_path) as clip:
            duration = config.CLIP_DURATION_SECONDS
            if clip.duration <= duration:
                start = 0.0
            else:
                start = _find_best_window(clip, duration)
                start = min(start, clip.duration - duration)

            subclip = clip.subclip(start, start + duration)
            subclip.write_videofile(out_path, codec="libx264", audio_codec="aac", logger=None)
        return out_path
    except Exception as e:
        print(f"[clipper] failed {video_id}: {e}")
        return None
