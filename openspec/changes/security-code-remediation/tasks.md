## 1. Agent A — Security Fixes (copyright_check, caption_gen, uploader token, downloader, clipper)

- [x] 1.1 `pipeline/copyright_check.py` — remove `content.get("licensedContent") is False` from the `or` condition; keep only `status.get("license") == "creativeCommon"`
- [x] 1.2 `pipeline/caption_gen.py` — wrap YouTube metadata in `<user_content>` XML delimiters inside the Claude prompt; title, description, and channel must be inside the tags, not inline with instruction text
- [x] 1.3 `pipeline/uploader.py` — replace `open(config.TOKEN_FILE, "w")` with `os.open(..., os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)` + `os.fdopen` for the credential save
- [x] 1.4 `pipeline/downloader.py` — add `re.fullmatch(r"[A-Za-z0-9_-]{11}", video["video_id"])` guard before constructing file path; raise `ValueError` on mismatch
- [x] 1.5 `pipeline/clipper.py` — add same `video_id` format guard before constructing file path

## 2. Agent B — Config & Reliability (config.py, scheduler.py)

- [x] 2.1 `config.py` — change `TOKEN_FILE = "token.json"` to `TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")`
- [x] 2.2 `config.py` — add `DISCOVERY_KEYWORD = os.getenv("DISCOVERY_KEYWORD", "Technology and Artificial Intelligence")`
- [x] 2.3 `config.py` — add startup assertion: `if UPLOAD_PRIVACY not in {"private", "unlisted", "public"}: raise ValueError(f"Invalid UPLOAD_PRIVACY: {UPLOAD_PRIVACY!r}")`
- [x] 2.4 `pipeline/discovery.py` — replace module-level `DISCOVERY_KEYWORD = "..."` with `from config import DISCOVERY_KEYWORD`; remove duplicate definition in `main.py`
- [x] 2.5 `scheduler.py` — wrap `run_pipeline()` call in `try/except Exception as e: logger.exception("Pipeline run failed: %s", e)`

## 3. Agent C — Hardening (discovery int casts, upload loop, scorer mutation)

- [x] 3.1 `pipeline/discovery.py` — add `_safe_int(val, default=0)` helper that returns `default` on `ValueError`; replace bare `int(stats.get(...))` calls with `_safe_int(stats.get(...))`
- [x] 3.2 `pipeline/discovery.py` — add `video_id` format validation (`re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id)`) in the enrichment loop; skip and `logger.warning` on mismatch
- [x] 3.3 `pipeline/uploader.py` — add `chunk_count = 0` before upload loop; increment per iteration; raise `RuntimeError("Upload stalled after 100 chunks")` when `chunk_count > 100`
- [x] 3.4 `pipeline/scorer.py` — replace `video["_score"] = ...` with a local `scores` dict keyed by index; use scores dict for comparison; do not write `_score` back to input dicts

## 4. Supervisor Integration & Verification

- [x] 4.1 Verify `uploader.py` edits from Agent A (token write) and Agent C (upload loop) do not overlap — confirm they touch different line ranges
- [x] 4.2 Run `python -c "import config"` to confirm startup assertions fire correctly with a bad `UPLOAD_PRIVACY` value
- [x] 4.3 Run `python -c "from pipeline.discovery import DISCOVERY_KEYWORD; print(DISCOVERY_KEYWORD)"` to confirm re-export works
- [x] 4.4 Run `python -c "import pipeline.copyright_check"` and inspect `is_cc` logic to confirm the broken branch is gone
- [ ] 4.5 Manual inspect `token.json` permissions after a credential save: `ls -la token.json` must show `-rw-------`
- [x] 4.6 Run `python main.py --once` and confirm no import errors or startup assertion failures
