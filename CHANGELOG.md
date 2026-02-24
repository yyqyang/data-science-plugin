# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [1.3.0] - 2026-02-24

### Changed
- Replaced `statistical-tests` skill with comprehensive `statistical-analysis` skill -- adds assumption checking script, Bayesian methods, APA reporting templates, power analysis, and 5 reference files
- `/ds:experiment` now uses `statistical-analysis` for test selection, power analysis, assumption verification, and APA-formatted reporting

## [1.2.0] - 2026-02-24

### Added
- `exploratory-data-analysis` skill -- file type detection and format-specific EDA for 200+ scientific formats, with analyzer script, report template, and 6 format reference files
- File type detection step in `/ds:eda` command workflow
- Structured report template reference in `/ds:eda` artifact output

## [1.1.0] - 2026-02-24

### Added
- `requirements.txt` with required and optional Python dependencies
- `setup` skill (`/ds:setup`) -- check Python environment for required libraries and report versions
- Prerequisites section in README with `uv pip install` commands

## [1.0.0] - 2026-02-24

### Added
- Plugin scaffold with `"name": "ds"` namespace
- 6 agents: problem-framer, data-profiler, feature-engineer, experiment-designer, model-evaluator, documentation-synthesizer
- 4 commands: `/ds:plan`, `/ds:eda`, `/ds:experiment`, `/ds:compound`
- 5 skills: eda-checklist, split-strategy, target-leakage-detection, experiment-tracking, statistical-tests
- 5 templates: problem-framing, dataset-assessment, experiment-plan, experiment-result, postmortem
- Compounding mechanism with `docs/ds/learnings/` and enhanced YAML frontmatter
- Learnings search with relevance ranking (tag overlap, recency, outcome filtering)
- Deduplication gate in `/ds:compound`
- Cold start handling (auto-creates `docs/ds/` directories)
- Large dataset sampling (100K rows when >100MB)
- MCP server: context7 for framework documentation lookup
