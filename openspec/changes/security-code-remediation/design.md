## Context

The reelraider pipeline is a fully automated, scheduled Python process that discovers YouTube videos, scores them, downloads, clips, generates captions via Claude, and re-uploads. Because it runs unattended and handles OAuth tokens, YouTube API keys, and Anthropic API keys, security defects have outsized impact — a logic bug can cause copyright infringement at scale, and a reliability defect can silently kill the daily scheduler job with no alert.

Two audit agents (security + code review) surfaced 13 issues across 10 source files. Fixes are applied by a multiagent system: one agent per independent fix domain, dispatched in parallel, integrated by a supervisor.

## Goals / Non-Goals

**Goals:**
- Fix the CC license logic so only genuinely CC-licensed videos are processed
- Neutralise the Claude prompt injection surface via YouTube metadata
- Harden OAuth token file permissions and path resolution
- Add startup validation for critical config values
- Add error containment at every pipeline boundary so one failure cannot kill the scheduler or the whole run
- Consolidate duplicated constants into `config.py`
- Remove the `scorer.py` input-dict mutation side effect

**Non-Goals:**
- Rewriting or refactoring the pipeline architecture
- Adding a test suite (separate effort)
- Changing the logging format set by the code-review agent (already applied)
- Addressing `run_local_server()` headless OAuth — tracked separately

## Decisions

### D1 — Multiagent fix dispatch

Fixes are grouped into three independent domains dispatched as parallel agents:

| Agent | Domain | Files |
|---|---|---|
| Agent A — Security fixes | CC logic, prompt injection, token perms, video_id guard | `copyright_check.py`, `caption_gen.py`, `uploader.py`, `downloader.py`, `clipper.py` |
| Agent B — Config/reliability | Startup assertions, absolute paths, DISCOVERY_KEYWORD consolidation, scheduler guard | `config.py`, `scheduler.py` |
| Agent C — Hardening | int() casts, upload loop guard, scorer dict mutation | `discovery.py`, `uploader.py`, `scorer.py` |

**Why parallel?** The domains share no files except `uploader.py` (Agents A and C both touch it). Agent A handles the token write; Agent C handles the upload loop. These are non-overlapping lines, so no conflict risk.

**Why not one agent?** Single agents on multi-file security remediations tend to miss fixes under token pressure. Focused agents with narrow scope produce higher-quality targeted changes.

### D2 — Prompt injection mitigation approach

Option A: Strip or sanitize YouTube metadata before embedding.
Option B: Wrap metadata in XML delimiters so Claude's context boundary is explicit.

**Chose B.** Option A requires maintaining a blocklist of instruction-like patterns, which is brittle. XML delimiters are the Anthropic-recommended approach for separating untrusted content from instructions in prompts.

### D3 — `DISCOVERY_KEYWORD` consolidation

Currently defined in both `pipeline/discovery.py` (module-level) and `main.py`. Moving to `config.py` with an env var override (`DISCOVERY_KEYWORD`, default `"Technology and Artificial Intelligence"`) allows runtime configuration without code changes and eliminates the drift risk.

The existing spec for `keyword-video-discovery` requires the constant to be importable from `pipeline.discovery`. A re-export shim (`from config import DISCOVERY_KEYWORD`) satisfies backward compatibility.

### D4 — CC license check

Remove `content.get("licensedContent") is False` from the `or` condition entirely. The YouTube search already passes `videoLicense="creativeCommon"` as a pre-filter. The `copyright_check` stage's role is to confirm `status.license == "creativeCommon"` — nothing else.

### D5 — token.json permissions

Use `os.open` with `O_CREAT | O_WRONLY | O_TRUNC` and mode `0o600` instead of `open(..., "w")`. This avoids the umask race window entirely.

## Risks / Trade-offs

**[Risk] Agent C edits `uploader.py` and Agent A also edits it**
→ Mitigation: scope each agent to non-overlapping line ranges. Agent A: credential section (lines ~10-30). Agent C: upload loop (lines ~45-60). Supervisor verifies no overlap before merging.

**[Risk] XML delimiters in caption prompt change Claude's output format**
→ Mitigation: delimiters only wrap the `<user_content>` block; the instruction and output format sections remain unchanged. Tested prompt structure included in spec.

**[Risk] Moving `DISCOVERY_KEYWORD` to `config.py` breaks the existing spec**
→ Mitigation: re-export from `pipeline/discovery.py` satisfies the importability requirement. Spec delta included.

## Open Questions

- Should `token.json` path be configurable via env var or always resolved relative to `config.py`'s directory? (Defaulting to `os.path.dirname(__file__)` for now.)
- Max upload chunk retry count — using 10 as a reasonable default; no upstream guidance found.
