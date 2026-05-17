import logging
import os
import re
import shutil
import subprocess
from typing import TYPE_CHECKING

import numpy as np

import config

logger = logging.getLogger(__name__)


def _parse_chapters(description: str | None) -> list[float]:
    if not description:
        return []
    times: list[float] = []
    pattern = re.compile(r"(?m)^(\d+):(\d{2})(?::(\d{2}))?\s+\S")
    for m in pattern.finditer(description):
        h, mm, s = m.group(1), m.group(2), m.group(3)
        if s is not None:
            # hh:mm:ss
            times.append(int(h) * 3600 + int(mm) * 60 + int(s))
        else:
            # mm:ss
            times.append(int(h) * 60 + int(mm))
    return times


def _normalize(arr: np.ndarray) -> np.ndarray:
    mx = arr.max()
    if mx == 0:
        return arr
    return arr / mx


def _compute_audio_signals(video_path: str, step: float) -> tuple[np.ndarray, np.ndarray, float]:
    try:
        import librosa
        y, sr = librosa.load(video_path, sr=22050, mono=True)
        hop = int(sr * step)
        rms = librosa.feature.rms(y=y, hop_length=hop)[0]
        flux = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
        duration = float(len(y) / sr)
        logger.debug("Audio signals computed: duration=%.2fs frames=%d", duration, len(rms))
        return rms, flux, duration
    except Exception:
        logger.exception("Audio signal computation failed for %s", video_path)
        return np.zeros(1), np.zeros(1), 0.0


def _compute_scene_changes(video_path: str, total_frames: int, step: float) -> np.ndarray:
    scene_counts = np.zeros(total_frames)
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-i", video_path,
                "-vf", "select='gt(scene,0.4)',showinfo",
                "-f", "null", "-",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        # showinfo writes to stderr: "pts_time:123.456"
        for line in result.stderr.splitlines():
            if "pts_time:" not in line:
                continue
            for part in line.split():
                if part.startswith("pts_time:"):
                    try:
                        t = float(part.split(":")[1])
                        idx = min(int(t / step), total_frames - 1)
                        scene_counts[idx] += 1
                    except (ValueError, IndexError):
                        pass
        logger.debug("Scene changes detected: %d total cuts", int(scene_counts.sum()))
    except subprocess.TimeoutExpired:
        logger.warning("Scene change detection timed out for %s", video_path)
    except Exception:
        logger.exception("Scene change detection failed for %s", video_path)
    return scene_counts


def _compute_face_density(video_path: str, total_frames: int, step: float) -> np.ndarray:
    face_counts = np.zeros(total_frames)
    try:
        import cv2
    except ImportError:
        logger.debug("opencv-python not installed — face density scoring disabled")
        return face_counts
    try:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(cascade_path)
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.warning("cv2 could not open %s for face detection", video_path)
            return face_counts
        try:
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_idx % 10 == 0:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
                    t = frame_idx / fps
                    bucket = min(int(t / step), total_frames - 1)
                    face_counts[bucket] += len(faces)
                frame_idx += 1
            logger.debug("Face density computed: total face detections=%.0f", face_counts.sum())
        finally:
            cap.release()
    except Exception:
        logger.exception("Face density computation failed for %s", video_path)
    return face_counts


def _score_windows(
    rms: np.ndarray,
    flux: np.ndarray,
    scene: np.ndarray,
    face: np.ndarray,
    chapter_times: list[float],
    step: float,
    seg_dur: int,
) -> list[tuple[float, float]]:
    n = min(len(rms), len(flux), len(scene), len(face))
    rms_n = _normalize(rms[:n])
    flux_n = _normalize(flux[:n])
    scene_n = _normalize(scene[:n])
    face_n = _normalize(face[:n])

    seg_frames = int(seg_dur / step)
    results: list[tuple[float, float]] = []

    for i in range(n - seg_frames):
        start = i * step
        end = start + seg_dur
        # Average signal over window
        score = (
            0.25 * float(rms_n[i:i + seg_frames].mean())
            + 0.35 * float(flux_n[i:i + seg_frames].mean())
            + 0.25 * float(scene_n[i:i + seg_frames].mean())
            + 0.15 * float(face_n[i:i + seg_frames].mean())
        )
        # Chapter bonus
        for ct in chapter_times:
            if start - 2.0 <= ct <= end:
                score += 0.5
                break
        results.append((start, score))

    logger.debug("Scored %d candidate windows", len(results))
    return results


def _select_segments(
    scored: list[tuple[float, float]],
    n: int,
    seg_dur: int,
    guard: float = 0.5,
) -> list[tuple[float, float]]:
    sorted_windows = sorted(scored, key=lambda x: x[1], reverse=True)
    used: list[tuple[float, float]] = []

    for start, score in sorted_windows:
        end = start + seg_dur
        # Check overlap with guard margin
        overlap = any(
            not (end + guard <= us or start - guard >= ue)
            for us, ue in used
        )
        if not overlap:
            used.append((start, end))
            if len(used) >= n:
                break

    if len(used) < n:
        logger.warning(
            "Only %d/%d non-overlapping segments found (video may be too short or too uniform)",
            len(used),
            n,
        )

    # Sort chronologically
    selected = sorted(used, key=lambda x: x[0])
    logger.debug("Selected %d segments: %s", len(selected), [(f"{s:.1f}s", f"{e:.1f}s") for s, e in selected])
    return selected


def _snap_to_silence(
    rms: np.ndarray, t: float, step: float,
    window: float = 1.5, threshold: float = 0.08,
) -> float:
    lo = max(0, int((t - window) / step))
    hi = min(len(rms) - 1, int((t + window) / step))
    best_t, best_rms = t, float("inf")
    for i in range(lo, hi + 1):
        if rms[i] < best_rms:
            best_rms = rms[i]
            best_t = i * step
    if best_rms > threshold:
        return t
    return best_t


def _extract_segment(video_path: str, start: float, duration: float, out_path: str) -> bool:
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-t", f"{duration:.3f}",
        "-i", video_path,
        "-vf", "crop=ih*9/16:ih:(iw-ih*9/16)/2:0",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "fast",
        "-c:a", "aac",
        "-b:a", "128k",
        out_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        if result.returncode != 0:
            logger.error(
                "ffmpeg segment extraction failed: start=%.2f path=%s stderr=%s",
                start,
                out_path,
                result.stderr.decode(errors="replace")[-500:],
            )
            return False
        logger.debug("Segment extracted: start=%.2fs -> %s", start, out_path)
        return True
    except subprocess.TimeoutExpired:
        logger.error("ffmpeg segment extraction timed out: start=%.2f path=%s", start, out_path)
        return False
    except Exception:
        logger.exception("ffmpeg segment extraction failed unexpectedly: start=%.2f path=%s", start, out_path)
        return False


def _stitch_segments(segment_paths: list[str], out_path: str, transition: float) -> bool:
    if len(segment_paths) == 1:
        shutil.copy2(segment_paths[0], out_path)
        logger.debug("Single segment passthrough -> %s", out_path)
        return True

    seg_dur = config.SHORT_SEGMENT_DURATION
    # Build filter_complex for xfade chain
    inputs = []
    for p in segment_paths:
        inputs += ["-i", p]

    n = len(segment_paths)
    video_filters = []
    audio_filters = []
    # Chain xfades: each offset = accumulated duration - accumulated transitions
    for i in range(n - 1):
        offset = (i + 1) * seg_dur - (i + 1) * transition
        if i == 0:
            v_in, a_in = "[0:v]", "[0:a]"
            v_in2, a_in2 = "[1:v]", "[1:a]"
        else:
            v_in, a_in = f"[v{i}]", f"[a{i}]"
            v_in2, a_in2 = f"[{i+1}:v]", f"[{i+1}:a]"

        v_out = f"[v{i+1}]" if i < n - 2 else "[vout]"
        a_out = f"[a{i+1}]" if i < n - 2 else "[aout]"

        video_filters.append(
            f"{v_in}{v_in2}xfade=transition=fade:duration={transition}:offset={offset:.3f}{v_out}"
        )
        audio_filters.append(
            f"{a_in}{a_in2}acrossfade=d={transition}{a_out}"
        )

    filter_complex = ";".join(video_filters + audio_filters)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "fast",
        "-c:a", "aac",
        "-b:a", "128k",
        out_path,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=180)
        if result.returncode != 0:
            logger.error(
                "ffmpeg stitch failed: stderr=%s",
                result.stderr.decode(errors="replace")[-1000:],
            )
            return False
        logger.info("Stitched %d segments -> %s", n, out_path)
        return True
    except subprocess.TimeoutExpired:
        logger.error("ffmpeg stitch timed out")
        return False
    except Exception:
        logger.exception("ffmpeg stitch failed unexpectedly")
        return False


def extract_clip(video_path: str, video_id: str, metadata: dict | None = None) -> str | None:
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ValueError(f"Invalid video_id format: {video_id!r}")

    os.makedirs(config.TEMP_DIR, exist_ok=True)
    out_path = os.path.join(config.TEMP_DIR, f"{video_id}_clip.mp4")

    if os.path.exists(out_path):
        logger.info("Cache hit — skipping clip extraction for video_id=%s", video_id)
        return out_path

    logger.info("Starting highlight clip extraction: video_id=%s source=%s", video_id, video_path)

    try:
        step = config.SHORT_SCORING_STEP
        seg_dur = config.SHORT_SEGMENT_DURATION
        total_dur = config.SHORT_TOTAL_DURATION
        n_segments = total_dur // seg_dur

        # 1. Compute audio signals and get video duration
        rms, flux, video_duration = _compute_audio_signals(video_path, step)

        if video_duration <= 0:
            logger.error("Could not determine video duration for video_id=%s", video_id)
            return None

        total_frames = max(1, int(video_duration / step))
        logger.info("Source video duration: %.2fs video_id=%s", video_duration, video_id)

        # 2. Short video fallback
        if video_duration <= total_dur:
            logger.debug(
                "Source duration %.2fs <= target %ds — using full video as single segment",
                video_duration,
                total_dur,
            )
            windows = [(0.0, video_duration)]
        else:
            def _resize(arr: np.ndarray, n: int) -> np.ndarray:
                if len(arr) >= n:
                    return arr[:n]
                return np.pad(arr, (0, n - len(arr)))

            rms_f = _resize(rms, total_frames)
            flux_f = _resize(flux, total_frames)

            # 3. Scene changes and face density
            scene = _compute_scene_changes(video_path, total_frames, step)
            face = _compute_face_density(video_path, total_frames, step)

            # 4. Chapter times from metadata description
            description = (metadata or {}).get("description")
            chapter_times = _parse_chapters(description)
            logger.debug("Chapter markers found: %d", len(chapter_times))

            # 5. Score and select
            scored = _score_windows(rms_f, flux_f, scene, face, chapter_times, step, seg_dur)
            if not scored:
                logger.warning("No scoreable windows found — falling back to clip from start")
                windows = [(0.0, float(seg_dur))]
            else:
                windows = _select_segments(scored, n_segments, seg_dur)
                windows = [
                    (_snap_to_silence(rms_f, start, step), end)
                    for start, end in windows
                ]

        # 6. Extract segments with crop
        seg_paths: list[str] = []
        for idx, (start, end) in enumerate(windows):
            duration = end - start
            seg_out = os.path.join(config.TEMP_DIR, f"{video_id}_seg_{idx}.mp4")
            ok = _extract_segment(video_path, start, duration, seg_out)
            if ok:
                seg_paths.append(seg_out)
            else:
                logger.warning("Segment %d extraction failed — skipping", idx)

        if not seg_paths:
            logger.error("All segment extractions failed for video_id=%s", video_id)
            return None

        # 7. Stitch
        ok = _stitch_segments(seg_paths, out_path, config.SHORT_TRANSITION_DURATION)

        if ok:
            # Cleanup temp segments
            for p in seg_paths:
                try:
                    os.remove(p)
                except OSError:
                    logger.debug("Could not remove temp segment %s", p)
            logger.info(
                "Highlight clip complete: video_id=%s segments=%d path=%s",
                video_id,
                len(seg_paths),
                out_path,
            )
            return out_path
        else:
            logger.error(
                "Stitch failed for video_id=%s — temp segments retained at: %s",
                video_id,
                seg_paths,
            )
            return None

    except Exception:
        logger.exception("Clip extraction failed for video_id=%s", video_id)
        return None
