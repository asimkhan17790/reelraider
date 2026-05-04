# Architecture

## Pipeline Flow

```mermaid
flowchart TD
    A([main.py]) -->|run_pipeline| B[discovery.py]
    B -->|YouTube Data API\nmostPopular + creativeCommon| C[copyright_check.py]
    C -->|licensedContent flag\nno regionRestriction| D[downloader.py]
    D -->|yt-dlp\ndownload to TEMP_DIR| E[clipper.py]
    E -->|moviepy\nfirst N seconds| F[caption_gen.py]
    F -->|Claude claude-sonnet-4-6\ntitle + description + tags| G[uploader.py]
    G -->|YouTube Data API OAuth2\nprivacy: private| H([Done])

    SCH([scheduler.py]) -->|APScheduler cron 09:00| A

    subgraph Config
        CFG[config.py\nenv vars + validation]
    end

    B & C & D & E & F & G --> CFG
```

## Module Responsibilities

| Module | Input | Output | External dependency |
|---|---|---|---|
| `discovery.py` | — | `list[dict]` video candidates | YouTube Data API v3 |
| `copyright_check.py` | `list[dict]` | filtered `list[dict]` | YouTube Data API v3 |
| `downloader.py` | `dict` (video) | local file path | yt-dlp |
| `clipper.py` | file path, video_id | clip file path | moviepy |
| `caption_gen.py` | `dict` (video) | `dict` with title/description/tags | Anthropic API |
| `uploader.py` | clip path, metadata dict | — | YouTube Data API v3 OAuth2 |
| `scheduler.py` | — | — | APScheduler |
| `config.py` | `.env` file | typed config constants | python-dotenv |

## Data shape (passed between stages)

```python
{
    "video_id":    str,   # YouTube video ID
    "title":       str,   # original video title
    "description": str,   # original description
    "channel":     str,   # channel name
    "url":         str,   # full YouTube URL
}
```
