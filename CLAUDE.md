# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install deps (uses uv or pip)
pip install -e .

# Run pipeline once (no scheduler)
python main.py --once

# Run with daily scheduler (09:00)
python main.py
```

## Environment Setup

Copy `.env.example` to `.env` and fill:
- `ANTHROPIC_API_KEY` — required, used by `caption_gen.py`
- `YOUTUBE_API_KEY` — required, YouTube Data API v3
- `YOUTUBE_CLIENT_SECRETS` — path to OAuth2 `client_secrets.json` for upload
- OAuth token auto-saved to `token.json` on first upload

## Architecture

Linear pipeline: `main.py:run_pipeline()` calls each stage in sequence.

```
discovery → copyright_check → downloader → clipper → caption_gen → uploader
```

| Module | Role |
|--------|------|
| `pipeline/discovery.py` | YouTube Data API: fetch `mostPopular` videos filtered to `creativeCommon` license |
| `pipeline/copyright_check.py` | Second API call: verify `licensedContent` flag + no `regionRestriction` |
| `pipeline/downloader.py` | `yt-dlp` downloads video to `TEMP_DIR` |
| `pipeline/clipper.py` | `moviepy` cuts first `CLIP_DURATION_SECONDS` (default 55s) |
| `pipeline/caption_gen.py` | Claude `claude-sonnet-4-6` generates title/description/tags; uses prompt caching on system prompt |
| `pipeline/uploader.py` | YouTube Data API OAuth2 upload; privacy default `private` |
| `scheduler.py` | APScheduler cron at 09:00 daily wrapping `run_pipeline()` |
| `config.py` | Single source of truth for all env vars; fails fast on missing required keys |

All pipeline stage functions take/return plain `dict` with keys: `video_id`, `title`, `description`, `channel`, `url`.

`MAX_VIDEOS_PER_RUN` caps processing; discovery fetches `3×` that count to allow copyright filtering to trim it down.
