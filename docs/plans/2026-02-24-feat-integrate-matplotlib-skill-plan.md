---
title: "feat: Integrate matplotlib skill for visualization patterns"
type: feat
date: 2026-02-24
---

# Integrate matplotlib Skill for Visualization Patterns

## Overview

Integrate the `matplotlib` skill from `claude-scientific-skills` into the ds plugin (v1.7.0). The plugin already references matplotlib in 25+ places for distribution plots, correlation heatmaps, and result visualizations, but provides no dedicated skill with concrete API patterns. This integration gives agents and commands a consistent reference for plot creation, styling, and export.

## Problem Statement

The ds plugin generates visualization code in `/ds:eda` (distribution analysis, correlation heatmaps) and `/ds:experiment` (result plots across all three paradigms). Currently, agents produce matplotlib code from general knowledge rather than from a dedicated skill with consistent patterns. This leads to inconsistent plot styling, missing `plt.close()` calls (memory leaks during multi-feature EDA), and `plt.show()` calls that crash on headless servers.

The scikit-learn and statsmodels skills already contain some matplotlib-using code (e.g., `ConfusionMatrixDisplay`, `plot_diagnostics()`), but these are domain-specific utilities, not general-purpose matplotlib API patterns. There is no reference for subplot layouts, colormap selection, export settings, or custom visualization composition.

## Proposed Solution

### 1. Copy and Adapt `skills/matplotlib/`

Source: `../claude-scientific-skills/scientific-skills/matplotlib/`

**Files to copy:**

- [x] `SKILL.md` (360 lines -- adapt frontmatter, add "Role in ds plugin", remove K-Dense promo)
- [x] `references/plot_types.md` (copy as-is)
- [x] `references/styling_guide.md` (copy as-is)
- [x] `references/api_reference.md` (copy as-is)
- [x] `references/common_issues.md` (copy as-is)
- [x] `scripts/plot_template.py` (copy as-is)
- [x] `scripts/style_configurator.py` (copy as-is)

**SKILL.md adaptations:**

- [x] Rewrite frontmatter `description` to include ds plugin context and boundary guidance
- [x] Keep `license` and `metadata` fields from source
- [x] Add "Role in ds plugin" paragraph after the Overview section
- [x] Remove "Suggest Using K-Dense Web" section at the end

**"Role in ds plugin" paragraph content:**

The matplotlib skill provides the foundational visualization API for the ds plugin. It is the reference for creating custom figures, multi-panel layouts, styling, and export.

Boundary with other skills:
- **scikit-learn** display utilities (`ConfusionMatrixDisplay`, `RocCurveDisplay`, `learning_curve`) remain the primary reference for standard ML diagnostic plots. Use matplotlib when customizing these plots or composing multi-panel figures.
- **statsmodels** built-in plotting (`plot_diagnostics()`, `plot_acf/plot_pacf`) remain the primary reference for time-series and regression diagnostic plots. Use matplotlib for custom forecast visualizations or publication-quality figure assembly.
- **seaborn** (built on matplotlib) is preferred for standard statistical plots (violin plots, pair plots, correlation heatmaps) due to its more concise API. Use matplotlib directly for plot types seaborn does not cover, for fine-grained control, or for multi-panel figure composition.

DS plugin conventions:
- Always use the OO interface (`fig, ax = plt.subplots()`) in generated code
- Default to `plt.savefig()` + `plt.close(fig)` -- never `plt.show()` (headless compatibility)
- Save plot files alongside the report in the same output directory (e.g., `docs/ds/eda/`)
- Use `constrained_layout=True` for automatic spacing
- Use colorblind-friendly colormaps (viridis, cividis) by default

### 2. Wire into `/ds:eda` Command

**Step 5 (Distribution Analysis) -- add visualization sub-step:**

- [x] After computing distributions, reference `matplotlib` skill's `references/plot_types.md` for histogram, boxplot, and violin plot patterns
- [x] Note: for multi-feature distribution comparison, prefer seaborn where available, fall back to matplotlib subplots

**Step 7 (Relationship Analysis) -- add visualization reference:**

- [x] Reference `matplotlib` skill's `references/plot_types.md` (Heatmaps section) for correlation heatmap patterns
- [x] Note: prefer `seaborn.heatmap()` for standard correlation matrices; use matplotlib for custom heatmaps or when seaborn is unavailable

### 3. Wire into `/ds:experiment` Command

**Step 6 (Code scaffold generation) -- add matplotlib import guidance:**

- [x] When generating code scaffolds, include matplotlib import boilerplate and figure-saving pattern from the `matplotlib` skill's "Role in ds plugin" conventions

**Step 7 (Generate Results) -- add visualization references per paradigm:**

Supervised results:
- [x] Reference `matplotlib` skill for custom multi-panel result figures (combining confusion matrix, feature importance, and learning curves in a single figure layout)
- [x] Existing scikit-learn display utilities remain primary for individual diagnostic plots

Unsupervised results:
- [x] Reference `matplotlib` skill's `references/plot_types.md` (Scatter Plots section) for cluster visualization with color-coded groups
- [x] Reference `matplotlib` skill for elbow curve and silhouette plot styling
- [x] Existing scikit-learn `references/unsupervised_learning.md` remains primary for the analytical patterns

Time-series results:
- [x] Reference `matplotlib` skill for forecast vs actual line plots with prediction interval shading (`ax.fill_between()`)
- [x] Existing statsmodels `plot_diagnostics()` and `plot_acf/plot_pacf` remain primary for diagnostic plots

### 4. Update Agents

**`data-profiler` agent:**

- [x] Add matplotlib skill reference for generating distribution and quality visualizations during EDA profiling

**`model-evaluator` agent:**

- [x] Add matplotlib skill reference for composing result visualizations (multi-panel figures, publication-quality plots)

**No changes to:** `experiment-designer` (methodology focus, not code generation), `feature-engineer` (analytical focus), `problem-framer`, `documentation-synthesizer`

### 5. Update Templates

**EDA report template (`skills/exploratory-data-analysis/assets/report_template.md`):**

- [x] Add guidance comments to visualization placeholder sections referencing the matplotlib skill

**Experiment result template (`templates/experiment-result.md`):**

- [x] Add per-paradigm visualization guidance in the "Key Plots" section referencing the matplotlib skill

### 6. Metadata Sync

- [x] `.claude-plugin/plugin.json` -- bump version to `1.7.0`, update description: "10 skills"
- [x] `README.md` -- update Components table (Skills: 10), add `matplotlib` row to Skills table, update intro line
- [x] `CHANGELOG.md` -- add `[1.7.0]` entry
- [x] `CLAUDE.md` -- add `matplotlib` to Invocation Map for `/ds:eda` and `/ds:experiment` rows

### 7. No Changes Needed

- [x] `requirements.txt` -- matplotlib already listed as optional (update comment to mention matplotlib skill)
- [x] `skills/setup/SKILL.md` -- already checks matplotlib as optional
- [x] `/ds:plan` command -- planning stage does not produce visualizations
- [x] `/ds:compound` command -- no visualization generation

## Technical Considerations

### Headless Environment Compatibility

All generated matplotlib code must default to `plt.savefig()` + `plt.close(fig)`, not `plt.show()`. The adapted SKILL.md's "Role in ds plugin" paragraph codifies this convention. This prevents crashes on headless servers, CI pipelines, and remote environments.

### Plot Output Convention

Plot files are saved alongside the corresponding report in the same output directory:
- EDA plots: `docs/ds/eda/YYYY-MM-DD-<dataset>-<plot-type>.png`
- Experiment plots: `docs/ds/experiments/YYYY-MM-DD-<experiment>-<plot-type>.png`

This keeps visualizations co-located with their analysis context.

### Missing matplotlib Handling

matplotlib remains optional. The plugin does not auto-install libraries (convention from setup skill design). When visualization code references matplotlib but it is not installed:
- The setup skill already reports missing optional libraries
- Generated code sections that use matplotlib are clearly labeled as visualization blocks
- The `common_issues.md` reference provides installation guidance

### Boundary with Existing Skills

The key boundary rule: **domain-specific skills own their standard plots; matplotlib owns custom composition and styling.**

| Plot Type | Primary Reference | matplotlib Role |
|-----------|-------------------|-----------------|
| Confusion matrix | scikit-learn `ConfusionMatrixDisplay` | Custom styling, multi-panel layout |
| Learning curve | scikit-learn `learning_curve` | Fine-grained control, publication quality |
| ACF/PACF | statsmodels `plot_acf/plot_pacf` | Custom styling only |
| Residual diagnostics | statsmodels `plot_diagnostics()` | Custom styling only |
| Distribution histograms | matplotlib `references/plot_types.md` | Primary reference |
| Correlation heatmap | matplotlib (or seaborn) | Primary reference |
| Forecast vs actual | matplotlib `references/plot_types.md` | Primary reference |
| Cluster scatter | matplotlib `references/plot_types.md` | Primary reference |
| Multi-panel summary | matplotlib `references/api_reference.md` | Primary reference |

## Acceptance Criteria

- [x] `skills/matplotlib/SKILL.md` exists with adapted frontmatter and "Role in ds plugin" paragraph
- [x] 4 reference files and 2 scripts copied to `skills/matplotlib/`
- [x] `/ds:eda` steps 5 and 7 reference the matplotlib skill with specific reference file paths
- [x] `/ds:experiment` steps 6 and 7 reference the matplotlib skill for all three paradigms
- [x] `data-profiler` and `model-evaluator` agents reference the matplotlib skill
- [x] EDA report template and experiment result template updated with visualization guidance
- [x] `plugin.json` version `1.7.0`, description says "10 skills"
- [x] `README.md` Components table shows 10 skills, Skills table includes matplotlib row
- [x] `CHANGELOG.md` has `[1.7.0]` entry
- [x] `CLAUDE.md` Invocation Map includes matplotlib in eda and experiment rows
- [x] `requirements.txt` comment updated to mention matplotlib skill
- [x] No `plt.show()` calls in any adapted skill content -- all use `plt.savefig()` + `plt.close(fig)`
- [x] K-Dense promotional section removed from adapted SKILL.md

## References

- Source skill: `../claude-scientific-skills/scientific-skills/matplotlib/`
- [Scikit-learn integration solution](../solutions/integration-issues/scikit-learn-skill-plugin-wiring.md)
- [Statsmodels integration solution](../solutions/integration-issues/statsmodels-skill-plugin-wiring.md)
- [Skill Integration Checklist](../solutions/integration-issues/statsmodels-skill-plugin-wiring.md#prevention)
