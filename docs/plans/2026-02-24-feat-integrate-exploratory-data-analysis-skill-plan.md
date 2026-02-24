---
title: "feat: Integrate exploratory-data-analysis skill from claude-scientific-skills"
type: feat
date: 2026-02-24
---

# Integrate exploratory-data-analysis Skill

## Overview

Copy the `exploratory-data-analysis` skill from `claude-scientific-skills` into the ds plugin. This adds file-type detection for 200+ scientific formats, a structured report template, a Python analyzer script, and 6 format reference files. The existing `eda-checklist` skill remains as-is -- it serves a different purpose (checklist for manual review vs. automated format-aware analysis).

## Problem Statement

The current `/ds:eda` workflow handles CSV and Parquet well but lacks:
- Automatic file type detection for non-tabular scientific formats (HDF5, FASTA, NetCDF, FITS, etc.)
- A structured report template (current output is free-form markdown)
- A standalone Python script for quick profiling outside the agent loop
- Format-specific EDA guidance (what to check for a VCF file vs. a PDB file vs. a CSV)

## Proposed Solution

Copy the entire `exploratory-data-analysis` skill (SKILL.md + scripts/ + references/ + assets/) into `skills/exploratory-data-analysis/`, adapt the frontmatter to match ds plugin conventions, and wire it into the `/ds:eda` command.

## Technical Approach

### Phase 1: Copy and Adapt Skill

#### 1.1 Create skill directory

```
skills/exploratory-data-analysis/
  SKILL.md
  scripts/eda_analyzer.py
  assets/report_template.md
  references/
    general_scientific_formats.md
    bioinformatics_genomics_formats.md
    chemistry_molecular_formats.md
    microscopy_imaging_formats.md
    spectroscopy_analytical_formats.md
    proteomics_metabolomics_formats.md
```

#### 1.2 Adapt SKILL.md frontmatter

Change from claude-scientific-skills format:

```yaml
---
name: exploratory-data-analysis
description: "..."
license: MIT license
metadata:
    skill-author: K-Dense Inc.
---
```

To ds plugin format:

```yaml
---
name: exploratory-data-analysis
description: "Detect file types and perform format-specific EDA across 200+ scientific formats. Use when analyzing non-tabular or unfamiliar data files."
---
```

- Remove `license` and `metadata` fields (not used by ds plugin skills)
- Rewrite description to match ds convention: "what + when to use"
- Remove the K-Dense Web promotional section at the bottom of SKILL.md

#### 1.3 Keep scripts, references, and assets as-is

The `eda_analyzer.py` script, report template, and 6 reference files are self-contained and work correctly. No modifications needed.

### Phase 2: Wire into /ds:eda Command

#### 2.1 Update `commands/eda.md`

Add a new step between "Load Data" and "Structural Profiling" that invokes the `exploratory-data-analysis` skill for file type detection:

```markdown
### 2b. File Type Detection

Use the `exploratory-data-analysis` skill to detect the file type and load format-specific analysis guidance. For standard tabular data (CSV, Parquet, Excel), proceed to step 3. For scientific formats (HDF5, FASTA, PDB, NetCDF, etc.), follow the format-specific EDA approach from the skill's references.
```

#### 2.2 Update report output

Reference the `assets/report_template.md` in step 7 (Write Artifact) so the EDA report follows the structured template format when applicable.

### Phase 3: Update Metadata

#### 3.1 `CLAUDE.md`

Add `exploratory-data-analysis` to the `/ds:eda` skills list in the Invocation Map table.

#### 3.2 `.claude-plugin/plugin.json`

- Bump version: `1.1.0` -> `1.2.0`
- Update description: "6 skills" -> "7 skills"

#### 3.3 `README.md`

- Update intro: "6 skills" -> "7 skills"
- Update Components table: Skills count to 7
- Add `exploratory-data-analysis` row to Skills table

#### 3.4 `CHANGELOG.md`

Add `[1.2.0]` entry.

## Acceptance Criteria

- [ ] `skills/exploratory-data-analysis/SKILL.md` exists with ds plugin frontmatter
- [ ] `skills/exploratory-data-analysis/scripts/eda_analyzer.py` is executable
- [ ] All 6 reference files are present in `skills/exploratory-data-analysis/references/`
- [ ] Report template at `skills/exploratory-data-analysis/assets/report_template.md`
- [ ] `/ds:eda` command references the new skill for file type detection
- [ ] `ls -d skills/*/ | wc -l` returns 7
- [ ] Version is `1.2.0` in `plugin.json`
- [ ] Skill counts updated in `plugin.json`, `README.md`, `CHANGELOG.md`
- [ ] Invocation Map updated in `CLAUDE.md`
- [ ] K-Dense promotional content removed from SKILL.md

## Dependencies & Risks

- **No new Python dependencies** -- the `eda_analyzer.py` script uses only pandas, numpy, h5py, BioPython, and Pillow, all of which are optional (it handles ImportErrors gracefully)
- **Risk: skill size** -- the 6 reference files are large (10K+ words each). This is fine for a skill directory but means the skill consumes more tokens when loaded. The SKILL.md itself instructs agents to search references by extension rather than loading entire files.
- **Existing eda-checklist is preserved** -- no breaking changes to the existing workflow

## References

- Source skill: `../claude-scientific-skills/scientific-skills/exploratory-data-analysis/`
- Existing EDA command: [commands/eda.md](../../commands/eda.md)
- Existing checklist skill: [skills/eda-checklist/SKILL.md](../../skills/eda-checklist/SKILL.md)
- Data profiler agent: [agents/analysis/data-profiler.md](../../agents/analysis/data-profiler.md)
