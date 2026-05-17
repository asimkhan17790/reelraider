## Why

13 security and code quality issues were found across the pipeline by automated audit agents, including a copyright check logic bug that causes CC-licensed-only intent to be violated, a prompt injection vector via untrusted YouTube metadata, and world-readable OAuth tokens. These issues create legal exposure, reliability failures, and security risk in an automated pipeline running on a schedule.

## What Changes

- Fix `copyright_check.py` CC license logic — remove the broken `licensedContent is False` branch
- Add prompt injection mitigations in `caption_gen.py` — wrap YouTube metadata in XML delimiters before Claude prompt
- Harden `token.json` file permissions to `0o600` on write
- Validate `UPLOAD_PRIVACY` at startup against allowed values
- Pin `TOKEN_FILE` to absolute path in `config.py`
- Add per-item `try/except` around `int()` casts on YouTube API stat fields
- Add `try/except` around `run_pipeline()` in scheduler to prevent job death on error
- Add max-chunk loop guard on YouTube upload to prevent infinite hang
- Consolidate `DISCOVERY_KEYWORD` constant into `config.py`
- Add `video_id` format validation before use in file paths
- Fix `scorer.py` — stop mutating input dict in-place with `_score` key

## Capabilities

### New Capabilities
- `pipeline-hardening`: Input validation, error containment, and safe defaults across all pipeline stages — covers video_id validation, API response int-casting guards, scheduler error handling, and upload loop guard
- `secure-credentials`: OAuth token written with restricted permissions and resolved to absolute path; `UPLOAD_PRIVACY` validated at startup

### Modified Capabilities
- `keyword-video-discovery`: Add `video_id` format validation; wrap `int()` stat casts in per-item error handling so one bad API response does not abort the run
- `video-scoring`: Remove in-place mutation of input dict (`_score` key)

## Impact

- `pipeline/copyright_check.py` — logic change (behavioral)
- `pipeline/caption_gen.py` — prompt structure change (Claude API call)
- `pipeline/uploader.py` — token write, upload loop, privacy validation
- `pipeline/discovery.py` — per-item error handling, video_id guard
- `pipeline/scorer.py` — remove dict mutation side effect
- `config.py` — absolute TOKEN_FILE path, UPLOAD_PRIVACY assertion, DISCOVERY_KEYWORD moved here
- `scheduler.py` — wrap run_pipeline() call
- No new dependencies required
