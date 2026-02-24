# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This workspace references the **Compound Engineering Plugin** repository (`compound-engineering-plugin/`), a Bun/TypeScript CLI that converts Claude Code plugins into formats for 7 other AI coding platforms (OpenCode, Codex, Droid, Pi, Copilot, Gemini, Kiro). It also hosts a plugin marketplace featuring the `compound-engineering` plugin — a collection of 29 agents, 22 commands, 19 skills, and 1 MCP server.

## Build & Test Commands

```bash
bun install                    # Install dependencies
bun test                       # Run all tests (Bun's native test runner)
bun run dev                    # Run CLI in dev mode
bun run src/index.ts install ./plugins/compound-engineering --to opencode  # Local install
```

There is no separate lint command. CI runs `bun test` on push/PR via GitHub Actions.

## Architecture

The CLI follows a **Parse → Convert → Write** pipeline:

1. **Parsers** (`src/parsers/`) read Claude plugin structure from the filesystem (markdown files with YAML frontmatter)
2. **Converters** (`src/converters/claude-to-*.ts`) transform Claude format into target-specific types, handling tool/permission/model name mappings
3. **Writers** (`src/targets/*.ts`) output files to each platform's expected directory structure

The target registry in `src/targets/index.ts` maps each platform name to its `convert` + `write` functions via a `TargetHandler` interface. Adding a new provider means: define types in `src/types/`, implement a converter, implement a writer, register in the targets index, and add tests.

### Key Directories

- `src/commands/` — CLI subcommands (`convert`, `install`, `list`, `sync`) using the `citty` framework
- `src/types/` — TypeScript type definitions for Claude and each target platform
- `src/utils/` — Shared utilities (frontmatter parsing, file ops, symlinks)
- `plugins/compound-engineering/` — The actual plugin content (agents, commands, skills as markdown files)
- `tests/` — Test suite with per-target converter and writer tests; fixtures in `tests/fixtures/sample-plugin/`

### Plugin Content Structure

Agents, commands, and skills are markdown files with YAML frontmatter. Agents are organized by category subdirectories (`review/`, `research/`, `design/`, `workflow/`, `docs/`). Commands use a `workflows:` prefix for workflow commands to avoid collisions with Claude Code built-ins.

## Versioning & Component Count Sync

When adding/removing agents, commands, or skills, counts must be updated in **three places**:
1. `plugins/compound-engineering/.claude-plugin/plugin.json` — `description` field + version bump
2. `.claude-plugin/marketplace.json` — plugin `description` field + version
3. `plugins/compound-engineering/README.md` — intro paragraph

Verification:
```bash
ls plugins/compound-engineering/agents/**/*.md | wc -l
ls plugins/compound-engineering/commands/*.md | wc -l
ls -d plugins/compound-engineering/skills/*/ 2>/dev/null | wc -l
```

After changes, run `/release-docs` to regenerate the documentation site.

## Target Output Locations

| Target | Output Path | Notes |
|--------|------------|-------|
| OpenCode | `~/.config/opencode/` | `opencode.json` is deep-merged, never overwritten wholesale |
| Codex | `~/.codex/` | Skill descriptions truncated to 1024 chars |
| Droid | `~/.factory/` | Claude tools mapped to Factory equivalents (`Bash`→`Execute`, `Write`→`Create`) |
| Pi | `~/.pi/agent/` | Includes MCPorter config for interoperability |
| Copilot | `.github/` | MCP env vars prefixed `COPILOT_MCP_` |
| Gemini | `.gemini/` | Namespaced commands create directory structure |
| Kiro | `.kiro/` | Only stdio MCP servers supported (HTTP skipped) |

## Conventions

- **ASCII-first**: Use ASCII unless the file already contains Unicode
- **Marketplace spec**: Only include fields from the official Claude Code plugin spec — no custom fields
- **Skill references**: Link files with markdown links `[file.md](./references/file.md)`, never bare backticks
- **Branching**: Create feature branches for non-trivial changes
- **Testing**: Run `bun test` after changes to parsing, conversion, or output logic
- **Dependencies**: Minimal — only `citty` (CLI framework) and `js-yaml` (frontmatter parsing)
