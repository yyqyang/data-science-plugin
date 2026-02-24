---
title: "feat: Integrate scikit-learn skill"
type: feat
date: 2026-02-24
---

# Integrate scikit-learn Skill

## Overview

Add the scikit-learn skill from `claude-scientific-skills` to provide concrete API code patterns for preprocessing, pipelines, model selection, hyperparameter tuning, and evaluation. This is an **addition** (skill count 7 -> 8, version 1.3.0 -> 1.4.0).

## Problem Statement

The ds plugin's agents describe ML concepts at a high level -- `feature-engineer` suggests preprocessing transformations, `experiment-designer` mentions "grid, random, Bayesian" search, `model-evaluator` describes metrics. But none provide concrete scikit-learn API patterns. Users must look up the code themselves. The scikit-learn skill fills this gap as the **API reference layer**.

## Proposed Solution

Copy `skills/scikit-learn/` from `claude-scientific-skills`, adapt the frontmatter, wire it into `/ds:experiment` at three steps, and update metadata.

### What the Source Skill Contains

```
SKILL.md                                  # 520 lines -- comprehensive ML reference
references/
  supervised_learning.md                  # Classification, regression algorithms
  unsupervised_learning.md                # Clustering, dimensionality reduction
  model_evaluation.md                     # Cross-validation, metrics, hyperparameter search
  preprocessing.md                        # Scalers, encoders, imputers, feature selection
  pipelines_and_composition.md            # Pipeline, ColumnTransformer, FeatureUnion
  quick_reference.md                      # Cheat sheets, common patterns, gotchas
scripts/
  classification_pipeline.py              # Complete classification workflow demo
  clustering_analysis.py                  # Clustering comparison demo
```

### Overlap Analysis

| Scikit-learn Topic | Existing Coverage | Resolution |
|---|---|---|
| Train/test splits | `split-strategy` skill covers decision tree + code | Cross-reference `split-strategy`, do not duplicate |
| Evaluation concepts | `model-evaluator` agent covers methodology | Cross-reference agent, scikit-learn provides API patterns |
| Statistical tests | `statistical-analysis` skill covers this | No overlap -- different domains |
| Preprocessing concepts | `feature-engineer` agent suggests transforms | Complementary -- agent picks WHAT, scikit-learn shows HOW |
| Pipelines | **No coverage anywhere** | New -- highest-value addition |
| Hyperparameter search code | Only mentioned by name in experiment.md | New -- concrete GridSearchCV/RandomizedSearchCV patterns |
| Cross-validation functions | `split-strategy` has split objects only | New -- `cross_val_score`, `cross_validate`, `learning_curve` |

## Implementation

### 1. Copy Skill Directory

Copy from `../claude-scientific-skills/scientific-skills/scikit-learn/` to `skills/scikit-learn/`:
- `references/` -- 6 files, as-is
- `scripts/` -- 2 files, as-is (reference demos, not importable utilities)

### 2. Adapt `skills/scikit-learn/SKILL.md`

**Frontmatter changes:**
- Keep `license` and `metadata` fields from the source
- Rewrite `description` in "what + when to use" format

```yaml
---
name: scikit-learn
description: "Scikit-learn API patterns for preprocessing, pipelines, model selection, and evaluation. Use when /ds:experiment needs to build sklearn pipelines, tune hyperparameters, or evaluate models."
license: BSD-3-Clause license
metadata:
    skill-author: K-Dense Inc.
---
```

**Content changes:**
- Add "Role in the ds plugin" paragraph after the Overview section:
  > **Role in the ds plugin:** This skill is invoked by `/ds:experiment` at step 3 (Methodology Design) for pipeline construction and hyperparameter search setup, at step 6 (Execute) for code scaffold generation, and at step 7 (Generate Results) for evaluation utilities. It provides concrete scikit-learn API patterns complementing the `split-strategy` skill (which split to use), the `feature-engineer` agent (which transforms to apply), and the `model-evaluator` agent (evaluation methodology).
- Fix `uv uv pip install` typo to `uv pip install` (lines 19, 22, 25 of source)
- Remove K-Dense promotional section at the end (lines 520-521)
- Keep "Additional Resources" section (official scikit-learn URLs are useful)

### 3. Wire into `/ds:experiment` Command

**Step 3 (Methodology Design)** -- add after the existing hyperparameter search bullet (line 39):

```markdown
Invoke the `scikit-learn` skill for:
- **Pipeline construction**: Use `references/pipelines_and_composition.md` to design preprocessing + model pipelines with `Pipeline` and `ColumnTransformer`
- **Hyperparameter search implementation**: Use `references/model_evaluation.md` for concrete `GridSearchCV` / `RandomizedSearchCV` patterns
- **Algorithm selection**: Use `references/quick_reference.md` for algorithm selection cheat sheets based on data characteristics
```

**Step 6 (Execute or Defer)** -- when user selects "Write experiment code scaffold", add:

```markdown
When generating the code scaffold, use the `scikit-learn` skill's pipeline patterns (`references/pipelines_and_composition.md`) and the example scripts (`scripts/classification_pipeline.py` or `scripts/clustering_analysis.py`) as structural references.
```

**Step 7 (Generate Results)** -- add after model-evaluator agent invocation (line 76), before statistical-analysis:

```markdown
Use the `scikit-learn` skill's evaluation utilities:
- Generate classification/regression metrics using `references/model_evaluation.md` patterns
- Create learning curves and validation curves for overfitting diagnosis
```

### 4. Update Metadata

**`.claude-plugin/plugin.json`:**
- Version: `1.3.0` -> `1.4.0`
- Description: `7 skills` -> `8 skills`

**`README.md`:**
- Line 3: `7 skills` -> `8 skills`
- Components table: Skills `7` -> `8`
- Skills table: add `| scikit-learn | Scikit-learn API patterns for preprocessing, pipelines, model selection, and evaluation |`

**`CHANGELOG.md`:**
- Add `[1.4.0]` entry

**`CLAUDE.md`:**
- Invocation map: add `scikit-learn` to `/ds:experiment` row

## Acceptance Criteria

- [x] `skills/scikit-learn/` directory exists with SKILL.md, 6 reference files, 2 scripts
- [x] SKILL.md frontmatter adapted (license/metadata kept, description in "what + when" format)
- [x] K-Dense promo section removed, `uv uv` typo fixed
- [x] "Role in the ds plugin" paragraph added with cross-references
- [x] `/ds:experiment` references `scikit-learn` at steps 3, 6, and 7
- [x] `ls -d skills/*/ | wc -l` returns `8`
- [x] plugin.json version is `1.4.0`, description says `8 skills`
- [x] README.md says `8 skills` in intro and Components table, scikit-learn in Skills table
- [x] CHANGELOG.md has `[1.4.0]` entry
- [x] CLAUDE.md invocation map includes `scikit-learn` in `/ds:experiment` row

## Out of Scope

- Wiring scikit-learn into `/ds:eda` or `/ds:plan` (future enhancement)
- Unsupervised experiment workflow in `/ds:experiment` (requires paradigm changes)
- Fixing pre-existing broken references to `feature-importance` and `time-series-validation` skills in experiment.md
- Adding matplotlib/seaborn to setup skill's optional library checks

## References

- Source skill: [../claude-scientific-skills/scientific-skills/scikit-learn/](../../../claude-scientific-skills/scientific-skills/scikit-learn/)
- Prior EDA integration plan: [2026-02-24-feat-integrate-exploratory-data-analysis-skill-plan.md](./2026-02-24-feat-integrate-exploratory-data-analysis-skill-plan.md)
- Prior statistical-analysis plan: [2026-02-24-feat-replace-statistical-tests-with-statistical-analysis-plan.md](./2026-02-24-feat-replace-statistical-tests-with-statistical-analysis-plan.md)
