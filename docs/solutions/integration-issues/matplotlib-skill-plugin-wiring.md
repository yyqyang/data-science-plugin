---
title: "Matplotlib skill integration with visualization wiring across EDA and experiment commands"
category: integration-issues
tags: [matplotlib, visualization, skill-integration, eda, experiment, headless-rendering, memory-leak, multi-panel, seaborn, boundary-management, foundational-skill]
module: commands/eda, commands/experiment, skills/matplotlib, agents/data-profiler, agents/model-evaluator
symptom: "Agents generated matplotlib code from general knowledge with inconsistent patterns; plt.show() crashed headless environments; missing plt.close() caused memory leaks during multi-feature EDA; no reference for subplot layouts or colormap selection; undefined boundary between matplotlib and visualization code already in scikit-learn and statsmodels skills"
root_cause: "Plugin referenced matplotlib conceptually in 25+ places but had no dedicated skill with concrete API patterns, DS plugin conventions, or boundary definitions against overlapping visualization code in scikit-learn and statsmodels skills"
date: 2026-02-24
outcome: success
versions: "1.7.0"
---

# Matplotlib Skill Integration with Visualization Wiring

## Problem

The ds plugin (v1.6.0) generated visualization code across `/ds:eda` and `/ds:experiment` without a dedicated matplotlib skill. This caused five concrete issues:

1. **Inconsistent plot styling** -- agents (data-profiler, model-evaluator) produced matplotlib code from general knowledge, mixing pyplot state-machine calls with OO interface calls and using no standard style configuration.
2. **`plt.show()` crashes on headless environments** -- generated code included `plt.show()` which blocks or errors in CI, Docker, and remote SSH sessions.
3. **Memory leaks from missing `plt.close()`** -- figures accumulated in memory across long EDA runs (profiling dozens of columns) because generated code never closed figures after saving.
4. **No guidance on subplot composition** -- multi-panel summary figures (residuals + feature importance + learning curves) had no reference for GridSpec or subplot layout, producing ad-hoc layout code.
5. **Undefined boundary with existing visualization code** -- scikit-learn provides `ConfusionMatrixDisplay`, `RocCurveDisplay`; statsmodels provides `plot_diagnostics()`, `plot_acf()`; seaborn provides `heatmap()`, `pairplot()`. Without boundary rules, generated code duplicated these built-in utilities with raw matplotlib or ignored matplotlib when custom visualization was needed.

## Investigation

- Read the source matplotlib skill (360-line SKILL.md, 4 reference files, 2 scripts) from `claude-scientific-skills`
- Inventoried all existing matplotlib usage across the plugin: 25+ conceptual references, zero dedicated API patterns
- Analyzed overlap: scikit-learn skill already references display utilities; statsmodels skill already references `plot_diagnostics()` and `plot_acf/plot_pacf`; seaborn already optional in setup/requirements
- Ran spec-flow analysis identifying 10 gaps including: missing visualization sub-steps in EDA, no code scaffold boilerplate, undefined boundary with scikit-learn/statsmodels/seaborn, headless environment handling, plot output directory convention
- Mapped all commands for integration points: eda (steps 5, 7), experiment (steps 6, 7 all paradigms)
- Confirmed no new dependencies needed (matplotlib already optional in requirements.txt and setup skill)

## Solution

### v1.7.0 -- Matplotlib skill integration

**Skill copy and adaptation:**

Copied `skills/matplotlib/` from `claude-scientific-skills` with:
- SKILL.md (adapted frontmatter, kept `license`/`metadata`, added "Role in ds plugin" paragraph with boundary rules and DS plugin conventions, removed K-Dense promo)
- 4 reference files (plot_types.md, styling_guide.md, api_reference.md, common_issues.md)
- 2 scripts (plot_template.py, style_configurator.py)

**"Role in ds plugin" defines three boundary rules:**

1. **scikit-learn display utilities** (`ConfusionMatrixDisplay`, `RocCurveDisplay`, `learning_curve`) remain primary for standard ML diagnostic plots. Use matplotlib when customizing these or composing multi-panel figures.
2. **statsmodels built-in plotting** (`plot_diagnostics()`, `plot_acf/plot_pacf`) remain primary for time-series and regression diagnostics. Use matplotlib for custom forecast visualizations or publication-quality figure assembly.
3. **seaborn** is preferred for standard statistical plots (violin plots, pair plots, heatmaps) due to its concise API. Use matplotlib directly for plot types seaborn does not cover, for fine-grained control, or for multi-panel composition.

**DS plugin conventions codified in SKILL.md:**

- Always use the OO interface (`fig, ax = plt.subplots()`)
- Default to `plt.savefig()` + `plt.close(fig)` -- never `plt.show()` (headless compatibility)
- Save plot files alongside the report in the same output directory
- Use `constrained_layout=True` for automatic spacing
- Use colorblind-friendly colormaps (viridis, cividis) by default

**Cross-command wiring:**

- `commands/eda.md` step 5: matplotlib for distribution visualization -- histograms, boxplots, violin plots from `references/plot_types.md` Sections 4-5; prefer seaborn for multi-feature comparison
- `commands/eda.md` step 7: matplotlib for correlation heatmaps and scatter plots from `references/plot_types.md` Sections 2, 6; prefer `seaborn.heatmap()` for standard cases
- `commands/experiment.md` step 6: matplotlib import boilerplate in code scaffolds, reference `scripts/plot_template.py` for function structure
- `commands/experiment.md` step 7 supervised: multi-panel summary (GridSpec), custom residual/feature importance plots; scikit-learn display utilities remain primary for standard diagnostics
- `commands/experiment.md` step 7 time-series: forecast vs actual line plots, prediction interval shading (`fill_between`); statsmodels diagnostic plots remain primary
- `commands/experiment.md` step 7 unsupervised: cluster scatter with color-coding, elbow/silhouette plots; scikit-learn remains primary for DR code
- Updated CLAUDE.md invocation map for eda and experiment commands

**Agent updates:**

- `data-profiler` agent: added matplotlib skill reference for OO interface, savefig+close, plot_types.md patterns
- `model-evaluator` agent: added matplotlib skill reference for multi-panel GridSpec figures and custom result plots

**Template updates:**

- EDA report template: HTML comments in visualization placeholder sections referencing matplotlib skill sections
- Experiment result template: per-paradigm visualization guidance comments in Key Plots section

## Prevention

### Foundational Skill Integration Principles

The matplotlib integration introduced a new skill type: a "foundational" skill whose target library is already used internally by other skills. This differs from prior integrations (scikit-learn, statsmodels) where the skill was the sole reference for its library.

**Principles for foundational skills:**

1. **Library-user vs. library-reference asymmetry** -- skills that happen to use the library (scikit-learn uses matplotlib for displays) are "library users." The foundational skill is the "library reference." Never duplicate foundational library teaching in a library-user skill -- cross-reference instead.

2. **Invocation layering, not replacement** -- adding a foundational skill layers onto existing invocations. `/ds:eda` invokes both scikit-learn (for its built-in displays) and matplotlib (for custom visualizations). These are complementary, not competing.

3. **Convention gravity** -- the foundational skill's DS plugin conventions section is the single source of truth for how the library is used across the entire plugin. Other skills generating code with that library must follow these conventions.

4. **Bounded scope despite broad reach** -- bound by workflow stage (EDA distributions, experiment evaluation) and output type (static figures to disk, not interactive dashboards). Before adding content, ask "Will a ds plugin agent actually generate this code?"

### Updated Skill Integration Checklist

When integrating a visualization or utility skill, follow the base checklist plus these items marked with (+):

- [ ] **Cross-cut audit**: review ALL commands for integration points
- [ ] **Cross-command wiring matrix**: create a matrix (commands x steps) marking where the skill adds value
- [ ] **Import audit**: cross-reference all `import` statements in scripts against setup skill checks
- [ ] **No phantom references**: every skill name in commands/agents must resolve to an actual `skills/<name>/SKILL.md`
- [ ] **Paradigm check**: consider supervised, unsupervised, and time-series paths
- [ ] **Existing usage inventory** (+): scan all existing skills and agents for calls to the target library; classify each as "library user" or "library teacher"
- [ ] **Boundary definition** (+): write explicit "Role in ds plugin" addressing the trilateral boundary -- this skill, existing skills that use the library, and wrapper libraries (seaborn for matplotlib, etc.)
- [ ] **Environment safety** (+): codify headless backend directive, savefig+close convention, and output path convention in the SKILL.md itself
- [ ] **Template guidance** (+): add HTML comment hints in every template section where visualization code is expected
- [ ] **Convention gravity check** (+): verify that the foundational skill's conventions do not contradict any existing code patterns in other skills
- [ ] **Three-place sync**: update plugin.json, README.md, CHANGELOG.md
- [ ] **Invocation map**: update CLAUDE.md for every command that references the skill

### Common Visualization Pitfalls

| Pitfall | Prevention |
|---------|------------|
| `plt.show()` in generated code | SKILL.md directive: always `savefig` + `close`, never `show` |
| Unclosed figures in loops | Mandate `fig, ax = plt.subplots()` pattern; every block ends with `plt.close(fig)` |
| Seaborn ambiguity | Decision rule: seaborn for one-liner statistical plots; matplotlib for custom composition |
| Boundary collision with built-in displays | "NOT this skill's job" list in SKILL.md; decision tree in agent prompts |
| Inconsistent style across outputs | Minimal style baseline in DS plugin conventions (colormap, figsize, grid) |
| Path hardcoding | Use `pathlib.Path` relative to plugin output directory |

## Related

- [Matplotlib integration plan](../../plans/2026-02-24-feat-integrate-matplotlib-skill-plan.md)
- [Statsmodels integration solution](./statsmodels-skill-plugin-wiring.md)
- [Scikit-learn integration solution](./scikit-learn-skill-plugin-wiring.md)
- [Experiment improvements plan](../../plans/2026-02-24-feat-experiment-command-improvements-plan.md)
