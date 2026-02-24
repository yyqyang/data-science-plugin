---
title: "feat: Experiment command improvements and cleanup"
type: feat
date: 2026-02-24
---

# Experiment Command Improvements and Cleanup

## Overview

Address four deferred items from the scikit-learn integration plan. These range from quick wins (matplotlib/seaborn in setup, fixing broken skill references) to moderate enhancements (wiring scikit-learn into more commands, unsupervised experiment support). Shipped as version 1.5.0.

## Items

### 1. Wire scikit-learn into `/ds:eda` and `/ds:plan`

**Problem:** The scikit-learn skill is only wired into `/ds:experiment`. The EDA command suggests preprocessing transforms but provides no implementation guidance. The plan command proposes candidate algorithms but has no algorithm selection reference.

**Changes:**

**`commands/eda.md` -- step 6b (Feature Engineering Suggestions, ~line 67):**

Add after the `feature-engineer` agent invocation:

```markdown
After suggestions are generated, reference the `scikit-learn` skill's `references/preprocessing.md` for concrete implementation patterns (scaling, encoding, imputation) matching the identified data characteristics.
```

**`commands/plan.md` -- step 3 (Approach Selection, ~line 39):**

Add before the existing "Propose 2-3 candidate approaches" text:

```markdown
Invoke the `scikit-learn` skill's `references/quick_reference.md` (Algorithm Selection cheat sheet) to map the problem type, dataset size, and constraints to candidate algorithms.
```

**`CLAUDE.md` invocation map:**
- Add `scikit-learn` to `/ds:eda` row
- Add `scikit-learn` to `/ds:plan` row

### 2. Unsupervised experiment workflow in `/ds:experiment`

**Problem:** The experiment command assumes supervised learning throughout -- hypotheses with dependent/independent variables, baselines to beat, train/test splits, leakage checks. Users running clustering or dimensionality reduction experiments hit a paradigm mismatch.

**Approach:** Add a routing step (like `eda.md` does for tabular vs. scientific formats) that detects supervised vs. unsupervised and adjusts the workflow conditionally.

**Changes to `commands/experiment.md`:**

Add a routing step after step 1 (Search Past Experiments):

```markdown
### 1b. Experiment Type Detection

Determine whether this is a **supervised** or **unsupervised** experiment:
- **Supervised** (classification, regression): has a target variable -- proceed to step 2
- **Unsupervised** (clustering, dimensionality reduction): no target variable -- use unsupervised variants of steps 2-7

If unclear, ask the user.
```

**Step 2 -- conditional hypothesis:**
- Supervised: keep current text (null/alternative hypothesis, independent/dependent variable)
- Unsupervised: replace with research question framing ("Are there natural customer segments?", "Can we reduce to N dimensions with <X% information loss?")

**Step 3 -- conditional methodology:**
- Supervised: keep current text
- Unsupervised: replace "Data split strategy" with "Stability assessment (resampling)", replace "Baseline to beat" with "Algorithm comparison protocol", replace "Evaluation metrics" with internal metrics (silhouette, Davies-Bouldin, explained variance). Reference `scikit-learn` skill's `references/unsupervised_learning.md` and `scripts/clustering_analysis.py`.

**Step 4 -- conditional leakage check:**
- Supervised: keep current text
- Unsupervised: skip ("Leakage check not applicable for unsupervised experiments -- no target variable.")

**Step 7 -- conditional results:**
- Supervised: keep current text
- Unsupervised: use clustering/DR-specific metrics, skip assumption checks on residuals, skip feature importance

**Changes to `agents/modeling/experiment-designer.md`:**

Add an unsupervised framing alternative in the agent's methodology section, so it can produce both supervised and unsupervised experiment designs.

**Changes to `templates/experiment-plan.md`:**

Add conditional sections for unsupervised experiments (research question instead of hypothesis, internal metrics instead of baseline comparison).

### 3. Fix broken skill references in experiment.md

**Problem:** Two lines in experiment.md reference skills that don't exist: `feature-importance` (line 94) and `time-series-validation` (line 53). These were planned for later phases but never created.

**Approach:** Replace the dangling references with inline guidance using existing skills.

**`commands/experiment.md` line 53** -- replace:

```
If temporal data is detected, auto-invoke `time-series-validation` skill.
```

With:

```
If temporal data is detected, use the `split-strategy` skill with temporal mode and reference the `scikit-learn` skill's `references/model_evaluation.md` (TimeSeriesSplit section) for time-aware cross-validation.
```

**`commands/experiment.md` line 94** -- replace:

```
Invoke `feature-importance` skill alongside model-evaluator for feature attribution analysis.
```

With:

```
For feature attribution analysis, use the `scikit-learn` skill's feature importance patterns: tree-based `feature_importances_` from `references/supervised_learning.md`, feature selection via `references/preprocessing.md` (RFE, SelectFromModel), and `sklearn.inspection.permutation_importance` for model-agnostic importance.
```

### 4. Add matplotlib/seaborn to setup skill and requirements.txt

**Problem:** Multiple scripts import matplotlib and seaborn (`statistical-analysis/scripts/assumption_checks.py`, `scikit-learn/scripts/clustering_analysis.py`, and many reference code examples) but these libraries aren't checked by `/ds:setup` or listed in `requirements.txt`.

**Changes:**

**`skills/setup/SKILL.md`** -- add to optional libraries dict:

```python
optional = {
    'matplotlib': 'matplotlib',
    'seaborn': 'seaborn',
    'xgboost': 'xgboost',
    'lightgbm': 'lightgbm',
    'shap': 'shap',
}
```

Update the optional install command in the skill to include matplotlib and seaborn.

**`requirements.txt`** -- add commented optional lines:

```
# Visualization -- used by scikit-learn and statistical-analysis skills
# matplotlib>=3.7
# seaborn>=0.12
```

**`README.md`** -- update optional install command:

```bash
uv pip install matplotlib seaborn xgboost lightgbm shap
```

## Metadata Updates

- **Version:** `1.4.0` -> `1.5.0` (MINOR -- new functionality in commands)
- **Skill count:** stays at 8 (no new skills added)
- **CLAUDE.md invocation map:** add `scikit-learn` to `/ds:eda` and `/ds:plan` rows
- **CHANGELOG.md:** add `[1.5.0]` entry

## Acceptance Criteria

### Item 1 -- scikit-learn in eda/plan
- [x] `commands/eda.md` references `scikit-learn` skill at step 6b
- [x] `commands/plan.md` references `scikit-learn` skill at step 3
- [x] CLAUDE.md invocation map updated for both commands

### Item 2 -- unsupervised workflow
- [x] `commands/experiment.md` has step 1b routing (supervised vs. unsupervised)
- [x] Steps 2, 3, 4, 7 have conditional text for unsupervised experiments
- [x] `agents/modeling/experiment-designer.md` supports unsupervised framing
- [x] `templates/experiment-plan.md` has unsupervised sections

### Item 3 -- broken references fixed
- [x] No references to `feature-importance` skill in experiment.md
- [x] No references to `time-series-validation` skill in experiment.md
- [x] Replacement text uses existing skills (scikit-learn, split-strategy)

### Item 4 -- matplotlib/seaborn
- [x] `skills/setup/SKILL.md` checks matplotlib and seaborn in optional dict
- [x] `requirements.txt` lists matplotlib and seaborn as commented optional deps
- [x] `README.md` optional install command includes matplotlib and seaborn

### Metadata
- [x] plugin.json version is `1.5.0`
- [x] CHANGELOG.md has `[1.5.0]` entry
- [x] CLAUDE.md invocation map updated

## References

- Deferred from: [2026-02-24-feat-integrate-scikit-learn-skill-plan.md](./2026-02-24-feat-integrate-scikit-learn-skill-plan.md)
- Scaffold plan (feature-importance/time-series-validation specs): [2026-02-24-feat-data-science-plugin-scaffold-plan.md](./2026-02-24-feat-data-science-plugin-scaffold-plan.md)
- Experiment command: [commands/experiment.md](../../commands/experiment.md)
- Experiment designer agent: [agents/modeling/experiment-designer.md](../../agents/modeling/experiment-designer.md)
- Experiment plan template: [templates/experiment-plan.md](../../templates/experiment-plan.md)
