import logging
import os
import re
import ffmpeg
import numpy as np
from moviepy import VideoFileClip
import config

logger = logging.getLogger(__name__)


def _find_best_window(clip: VideoFileClip, duration: int) -> float:
    """Return start time (seconds) of the highest-energy audio window."""
    try:
        audio = clip.audio
        if audio is None:
            logger.debug("No audio track — using start of clip")
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

        start_sec = best_start / fps
        logger.debug("Best audio window: start=%.2fs rms=%.4f", start_sec, best_rms)
        return start_sec
    except Exception:
        logger.exception("Audio window detection failed — falling back to 0.0s")
        return 0.0


def extract_clip(video_path: str, video_id: str) -> str | None:
    logger.debug("extract_clip: video_id=%s source=%s duration=%ds", video_id, video_path, config.CLIP_DURATION_SECONDS)
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ValueError(f"Invalid video_id format: {video_id!r}")
    os.makedirs(config.TEMP_DIR, exist_ok=True)
    out_path = os.path.join(config.TEMP_DIR, f"{video_id}_clip.mp4")

    if os.path.exists(out_path):
        logger.info("Cache hit — skipping clip extraction for video_id=%s", video_id)
        return out_path

    logger.info("Extracting clip: video_id=%s source=%s", video_id, video_path)
    try:
        with VideoFileClip(video_path) as clip:
            duration = config.CLIP_DURATION_SECONDS
            if clip.duration <= duration:
                start = 0.0
                logger.debug(
                    "Source duration %.2fs <= clip duration %ds — clipping from start",
                    clip.duration,
                    duration,
                )
            else:
                start = _find_best_window(clip, duration)
                start = min(start, clip.duration - duration)

        # Stream-copy via ffmpeg: no re-encoding, very fast
        (
            ffmpeg
            .input(filename=video_path, ss=start, t=duration)
            .output(filename=out_path, c="copy")
            .run(overwrite_output=True, quiet=True)
        )
        logger.info(
            "Clip extracted: video_id=%s start=%.2fs duration=%ds path=%s",
            video_id,
            start,
            duration,
            out_path,
        )
        return out_path
    except Exception:
        logger.exception("Clip extraction failed for video_id=%s", video_id)
        return None
