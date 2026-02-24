---
title: "Scikit-learn skill integration and experiment command improvements"
category: integration-issues
tags: [scikit-learn, skill-integration, unsupervised, broken-references, matplotlib, seaborn, command-wiring, preprocessing, pipeline]
module: commands/experiment, commands/eda, commands/plan, skills/scikit-learn, skills/setup
symptom: "Plugin agents described ML concepts at high level but provided no concrete scikit-learn API patterns; experiment command assumed supervised learning only; two skill references pointed to nonexistent skills; visualization libraries not checked by setup"
root_cause: "API reference gap between conceptual agents and actionable code; incomplete cross-command wiring; forward references to planned-but-unbuilt skills; import-setup drift when copying skills with scripts"
date: 2026-02-24
outcome: success
versions: "1.4.0, 1.5.0"
---

# Scikit-learn Skill Integration and Experiment Command Improvements

## Problem

Five related integration issues in the ds plugin (v1.3.0):

1. **No sklearn API reference** -- Agents like `feature-engineer` and `model-evaluator` described preprocessing, pipelines, and evaluation conceptually but provided no concrete scikit-learn code patterns. Users had to look up `Pipeline`, `GridSearchCV`, `ColumnTransformer` themselves.

2. **Skill wired to one command only** -- After initial integration, scikit-learn was only accessible through `/ds:experiment`. The `/ds:eda` command suggested preprocessing transforms with no implementation guidance, and `/ds:plan` proposed algorithms with no selection reference.

3. **Supervised-only experiment workflow** -- `commands/experiment.md` assumed supervised learning throughout: hypotheses with dependent/independent variables, baselines to beat, train/test splits, leakage checks. Clustering and dimensionality reduction experiments had no path.

4. **Broken skill references** -- `experiment.md` referenced `feature-importance` (line 94) and `time-series-validation` (line 53) skills that were planned in the scaffold but never created. These were phantom dependencies.

5. **Missing visualization library checks** -- Scripts in `statistical-analysis` and `scikit-learn` skills import matplotlib and seaborn, but `/ds:setup` didn't check for them and `requirements.txt` didn't list them.

## Investigation

- Read the scikit-learn source skill (520-line SKILL.md, 6 references, 2 scripts) from `claude-scientific-skills`
- Analyzed overlap with existing skills: `split-strategy` covers train/test splits, `model-evaluator` covers evaluation concepts, `statistical-analysis` covers statistical tests -- none provide sklearn API code
- Identified that `Pipeline`, `ColumnTransformer`, and `GridSearchCV` patterns had zero coverage
- Searched all commands for integration points where scikit-learn would add value
- Mapped every supervised-only assumption in `experiment.md` (steps 2, 3, 4, 7)
- Grepped for `feature-importance` and `time-series-validation` to confirm they don't exist as skill directories
- Grepped all scripts for matplotlib/seaborn imports to confirm the dependency gap

## Solution

### v1.4.0 -- Scikit-learn skill integration

Copied `skills/scikit-learn/` from `claude-scientific-skills` with:
- SKILL.md (adapted frontmatter, kept `license`/`metadata`, added "Role in ds plugin" paragraph, fixed `uv uv` typo, removed K-Dense promo)
- 6 reference files (supervised_learning, unsupervised_learning, model_evaluation, preprocessing, pipelines_and_composition, quick_reference)
- 2 scripts (classification_pipeline.py, clustering_analysis.py)

Wired into `/ds:experiment` at:
- Step 3: pipeline construction, hyperparameter search, algorithm selection
- Step 6: code scaffold generation references pipeline patterns and example scripts
- Step 7: evaluation utilities for metrics and learning curves

### v1.5.0 -- Cross-command wiring and improvements

**Item 1 -- scikit-learn in eda/plan:**
- `commands/eda.md` step 6b: reference `preprocessing.md` after feature-engineer suggestions
- `commands/plan.md` step 3: reference `quick_reference.md` algorithm selection before proposing approaches
- Updated CLAUDE.md invocation map for both commands

**Item 2 -- Unsupervised experiment workflow:**
- Added step 1b: "Experiment Type Detection" routing (supervised vs. unsupervised)
- Step 2: conditional hypothesis (null/alternative vs. research question)
- Step 3: conditional methodology (split/baseline/metrics vs. stability/internal-metrics/comparison-protocol)
- Step 4: labeled "supervised only", skip for unsupervised
- Step 7: split into supervised and unsupervised result sections
- Updated `experiment-designer` agent with unsupervised framing
- Updated `experiment-plan` template with conditional fields

**Item 3 -- Fixed broken references:**
- `time-series-validation` replaced with `split-strategy` temporal mode + scikit-learn TimeSeriesSplit reference
- `feature-importance` replaced with inline scikit-learn guidance (tree-based `feature_importances_`, RFE, `permutation_importance`)

**Item 4 -- matplotlib/seaborn:**
- Added to `skills/setup/SKILL.md` optional dict
- Added to `requirements.txt` as commented optional deps
- Updated README optional install command

## Prevention

### Skill Integration Checklist

When adding a new skill to the ds plugin:

- [ ] **Cross-cut audit**: review ALL commands for integration points, not just the most obvious one
- [ ] **Import audit**: cross-reference all `import` statements in scripts against setup skill checks
- [ ] **No phantom references**: every skill name in commands/agents must resolve to an actual `skills/<name>/SKILL.md`
- [ ] **Paradigm check**: consider supervised, unsupervised, and time-series paths
- [ ] **Three-place sync**: update plugin.json, README.md, CHANGELOG.md
- [ ] **Invocation map**: update CLAUDE.md for every command that references the skill

### Architecture Principles

1. **Agents advise, skills provide code** -- every conceptual agent recommendation should pair with a skill that has runnable code patterns
2. **The Invocation Map is a contract** -- if a skill is not in the map, it's invisible; if it's in the map but doesn't exist, the workflow is broken
3. **Design for all paradigms, ship for one** -- include routing/branching logic even if only one path is implemented initially

## Related

- [Scikit-learn integration plan](../../plans/2026-02-24-feat-integrate-scikit-learn-skill-plan.md)
- [Experiment improvements plan](../../plans/2026-02-24-feat-experiment-command-improvements-plan.md)
- [EDA skill integration plan](../../plans/2026-02-24-feat-integrate-exploratory-data-analysis-skill-plan.md)
- [Statistical-analysis replacement plan](../../plans/2026-02-24-feat-replace-statistical-tests-with-statistical-analysis-plan.md)
