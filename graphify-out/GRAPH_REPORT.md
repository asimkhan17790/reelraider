# Graph Report - /Users/maverickhan17/Projects/reelraider  (2026-05-30)

## Corpus Check
- 12 files · ~30,139 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 162 nodes · 213 edges · 21 communities detected
- Extraction: 76% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 52 edges (avg confidence: 0.82)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]

## God Nodes (most connected - your core abstractions)
1. `config.py` - 13 edges
2. `extract_clip()` - 11 edges
3. `Pipeline (linear flow)` - 11 edges
4. `Composite Video Scoring Requirement` - 11 edges
5. `main()` - 10 edges
6. `score_videos()` - 10 edges
7. `clipper.py` - 10 edges
8. `Highlight Shorts Clipper Design (archived)` - 9 edges
9. `run_pipeline()` - 8 edges
10. `discovery.py` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Scoring model (8 signals)` --semantically_similar_to--> `Spec: Composite multi-signal window scoring`  [INFERRED] [semantically similar]
  docs/superpowers/plans/2026-05-16-video-scorer.md → openspec/specs/highlight-scoring/spec.md
- `Pipeline (linear flow)` --references--> `Pipeline Wiring Task (score_videos in main.py)`  [INFERRED]
  ARCHITECTURE.md → docs/superpowers/plans/2026-05-16-video-scorer.md
- `Scoring model (8 signals)` --semantically_similar_to--> `Spec: Composite video scoring (score_videos)`  [INFERRED] [semantically similar]
  docs/superpowers/plans/2026-05-16-video-scorer.md → openspec/specs/video-scoring/spec.md
- `main()` --calls--> `find_viral_videos_by_keyword()`  [INFERRED]
  test_discovery_scoring.py → pipeline/discovery.py
- `main()` --calls--> `filter_safe_videos()`  [INFERRED]
  test_discovery_scoring.py → pipeline/copyright_check.py

## Hyperedges (group relationships)
- **Highlight Shorts Clipper sub-pipeline: score → select → crop → stitch** — spec_highlight_scoring_composite, spec_segment_greedy_selection, spec_vertical_crop_center, spec_clip_stitching_xfade [INFERRED 0.92]
- **Highlight clipper rewrite: design + tasks + proposal as change package** — archive_highlight_clipper_proposal, archive_highlight_clipper_design, archive_highlight_clipper_tasks [INFERRED 0.90]
- **Video scorer integration: discovery enrichment → scorer → pipeline selection** — architecture_discovery, video_scorer_scorer_py, architecture_pipeline [EXTRACTED 0.95]
- **Security Remediation Three-Agent Parallel Fix Dispatch** — security_remediation_design_d1_multiagent, security_remediation_tasks, security_remediation_design [EXTRACTED 1.00]
- **Keyword Discovery Two-Step API + Transcript + CC Filter Pipeline** — kwd_discovery_spec_keyword_search, kwd_discovery_spec_statistics_enrichment, kwd_discovery_spec_cc_prefilter, kwd_discovery_spec_transcript_attachment [EXTRACTED 1.00]
- **Composite Video Scorer Multi-Signal Scoring** — video_scorer_spec_composite_scoring, video_scorer_spec_velocity_signal, video_scorer_spec_minmax_normalization, video_scorer_spec_seo_subscore [EXTRACTED 1.00]

## Communities

### Community 0 - "Community 0"
Cohesion: 0.11
Nodes (27): clipper.py, Archive Spec: Clip stitching (crossfade + passthrough), D1: Composite scoring rationale (signal sum vs ML), D2: Greedy selection rationale (vs DP), D3: ffmpeg two-pass (segment + stitch) rationale (vs moviepy), D4: Face density via OpenCV Haar (vs mediapipe), D5: Scene change via ffmpeg select (vs PySceneDetect), Highlight Shorts Clipper Design (archived) (+19 more)

### Community 1 - "Community 1"
Cohesion: 0.13
Nodes (22): caption_gen.py, config.py, copyright_check.py, discovery.py, downloader.py, Pipeline (linear flow), scheduler.py, uploader.py (+14 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (18): Chapter Marker Bonus Requirement, Composite Multi-Signal Window Scoring Requirement, Face Density Computation Requirement (Soft Dependency), Scene Change Rate Computation Requirement, Spectral Flux Computation Requirement, Video Scorer Design Document, D1: Min-Max Normalization Per Batch Rationale, D2: Velocity Equal Weight to View Count Rationale (+10 more)

### Community 3 - "Community 3"
Cohesion: 0.19
Nodes (9): filter_safe_videos(), find_viral_videos_by_keyword(), _safe_int(), download_video(), cli(), _configure_logging(), run_pipeline(), _run_pipeline_safe() (+1 more)

### Community 4 - "Community 4"
Cohesion: 0.16
Nodes (14): Spec: Composite video scoring (score_videos), score_videos() — no mutation of input dicts, _days_since() helper, Discovery Metadata Extension Task, _norm() min-max normalization, Pipeline Wiring Task (score_videos in main.py), Video Scorer Implementation Plan, _quality_score() helper (+6 more)

### Community 5 - "Community 5"
Cohesion: 0.18
Nodes (14): D4: DISCOVERY_KEYWORD Constant + Default Parameter Rationale, Hardcoded Default Keyword Constant Requirement, Scheduler Job Error Containment Requirement, Upload Loop Max-Chunk Guard Requirement, video_id Format Validation Requirement, DISCOVERY_KEYWORD Canonical Source Requirement, video_id Format Guard in Discovery Requirement, D1: Multiagent Fix Dispatch Rationale (+6 more)

### Community 6 - "Community 6"
Cohesion: 0.32
Nodes (11): _compute_audio_signals(), _compute_face_density(), _compute_scene_changes(), extract_clip(), _extract_segment(), _normalize(), _parse_chapters(), _score_windows() (+3 more)

### Community 7 - "Community 7"
Cohesion: 0.36
Nodes (10): _days_since(), _norm(), _quality_score(), Score all candidate videos and return the top-n highest-scoring ones., score_videos(), _seo_score(), _speech_density_norm(), _title_hook_score() (+2 more)

### Community 8 - "Community 8"
Cohesion: 0.25
Nodes (8): D1: Two-Step API (search → videos.list) Rationale, Statistics Enrichment via Second API Call Requirement, Safe Int Casting on YouTube API Stat Fields Requirement, Statistics Enrichment Safe Int Casting Requirement, D2: Prompt Injection XML Delimiter Approach Rationale, D3: contentDetails in Existing API Call Rationale, Statistics Enrichment via Second API Call (Video Scorer), Video Scorer Proposal

### Community 9 - "Community 9"
Cohesion: 0.33
Nodes (6): Keyword-Based Video Discovery Design Document, D3: Transcript via youtube-transcript-api Flat String Rationale, Keyword-Based Video Discovery Proposal, Keyword-Based Video Search Requirement, Transcript Metadata Attachment Requirement, Keyword-Based Video Discovery Tasks

### Community 10 - "Community 10"
Cohesion: 1.0
Nodes (2): _get_credentials(), upload_clip()

### Community 11 - "Community 11"
Cohesion: 1.0
Nodes (0): 

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (2): D2: Keep videoLicense Filter + copyright_check Belt-and-Suspenders Rationale, Creative Commons Pre-Filter in Search Requirement

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (0): 

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (0): 

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (1): Graphify knowledge graph rules

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (1): Graph Report Community Structure

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): God Nodes (most connected)

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): Knowledge Gaps

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): Security Code Remediation Design Document

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (1): Existing Discovery Function Preserved Requirement

## Knowledge Gaps
- **56 isolated node(s):** `Quick smoke test: discovery → copyright_check → scorer. No download/clip/upload.`, `Score all candidate videos and return the top-n highest-scoring ones.`, `Video dict data shape`, `Graphify knowledge graph rules`, `_norm() min-max normalization` (+51 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 11`** (2 nodes): `generate_caption()`, `caption_gen.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (2 nodes): `D2: Keep videoLicense Filter + copyright_check Belt-and-Suspenders Rationale`, `Creative Commons Pre-Filter in Search Requirement`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (1 nodes): `config.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (1 nodes): `Graphify knowledge graph rules`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (1 nodes): `Graph Report Community Structure`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (1 nodes): `God Nodes (most connected)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (1 nodes): `Knowledge Gaps`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `Security Code Remediation Design Document`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `Existing Discovery Function Preserved Requirement`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `clipper.py` connect `Community 0` to `Community 1`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `Composite Video Scoring Requirement` connect `Community 2` to `Community 8`, `Community 5`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `Spec: Composite multi-signal window scoring` connect `Community 0` to `Community 4`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `config.py` (e.g. with `Environment Variables` and `Segment config parameters (SHORT_TOTAL_DURATION, SHORT_SEGMENT_DURATION, SHORT_SCORING_STEP)`) actually correct?**
  _`config.py` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `main()` (e.g. with `find_viral_videos_by_keyword()` and `_days_since()`) actually correct?**
  _`main()` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Quick smoke test: discovery → copyright_check → scorer. No download/clip/upload.`, `Score all candidate videos and return the top-n highest-scoring ones.`, `Video dict data shape` to the rest of the system?**
  _56 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.11 - nodes in this community are weakly interconnected._