# ReelRaider

Automated pipeline: finds viral Creative Commons YouTube videos, clips the first 55s, generates AI captions via Claude, and uploads to your channel.

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the full pipeline diagram.

---

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python package manager
- Python 3.11+
- YouTube Data API v3 key
- Anthropic API key
- YouTube OAuth2 `client_secrets.json` — for uploading (download from Google Cloud Console)

---

## Setup

### 1. Clone the repo

```bash
git clone <repo-url>
cd reelraider
```

### 2. Install dependencies

```bash
uv sync
```

Creates `.venv/` and installs all pinned deps from `uv.lock`.

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-...
YOUTUBE_API_KEY=AIza...
YOUTUBE_CLIENT_SECRETS=./client_secrets.json
```

### 4. YouTube OAuth (first upload only)

Place `client_secrets.json` in repo root (or set `YOUTUBE_CLIENT_SECRETS` to its path).
On first upload, a browser window opens for OAuth consent. Token saved to `token.json` — subsequent runs are non-interactive.

---

## Running

### Adhoc — one-shot, no scheduler

```bash
uv run reelraider --once
```

### Daily scheduler (09:00 every day)

```bash
uv run reelraider
```

Runs indefinitely. Press `Ctrl+C` to stop.

### Without script entry point

```bash
uv run python main.py --once   # one-shot
uv run python main.py          # with scheduler
```

---

## Updating dependencies

After pulling changes:

```bash
uv sync
```

Add a new package:

```bash
uv add <package>
```

---

## Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | — | Claude API key for caption generation |
| `YOUTUBE_API_KEY` | Yes | — | YouTube Data API v3 key |
| `YOUTUBE_CLIENT_SECRETS` | Yes | `./client_secrets.json` | Path to OAuth2 secrets file |
| `REGION_CODE` | No | `US` | Region filter for video discovery |
| `VIDEO_CATEGORY_ID` | No | `10` | YouTube category ID (10 = Music) |
| `MAX_VIDEOS_PER_RUN` | No | `5` | Max videos processed per run |
| `CLIP_DURATION_SECONDS` | No | `55` | Length of extracted clip in seconds |
| `UPLOAD_PRIVACY` | No | `private` | Upload privacy: `private`, `unlisted`, `public` |
