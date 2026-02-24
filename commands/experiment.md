---
name: ds:experiment
description: Design an ML experiment with hypothesis, split strategy, leakage check, and evaluation plan
argument-hint: "[experiment description or hypothesis]"
---

# Design and Run Experiments

## Input

<experiment_description> $ARGUMENTS </experiment_description>

**If the experiment description above is empty, ask the user:** "What experiment do you want to run? Describe the hypothesis, model, or approach you want to test."

## Workflow

### 1. Search Past Experiments

Search `docs/ds/learnings/*.md` for `category: modeling` and `category: features` learnings. Also search `docs/ds/experiments/` for related prior work.

If `docs/ds/learnings/` does not exist, run `mkdir -p docs/ds/learnings/` and report: "No prior learnings found for this topic. Starting fresh."

Surface what was tried before and what worked/failed.

### 2. Hypothesis Formulation

Use the `experiment-designer` agent:
- Null hypothesis and alternative hypothesis
- Independent variable (what's being changed)
- Dependent variable (what's being measured)
- Controls (what's held constant)

### 3. Methodology Design

Define:
- **Data split strategy** -- invoke `split-strategy` skill
- **Feature set** -- reference any feature engineering from prior EDA
- **Model(s) to evaluate**
- **Hyperparameter search strategy** (grid, random, Bayesian)
- **Evaluation metrics** (primary + secondary)
- **Baseline to beat**

Invoke the `statistical-analysis` skill for:
- **Test selection**: Use `references/test_selection_guide.md` to choose the right statistical test for the comparison protocol
- **Power analysis**: Determine minimum sample size needed to detect the expected effect size
- **Assumption planning**: Note which assumptions will need checking after results are in

Invoke the `scikit-learn` skill for:
- **Pipeline construction**: Use `references/pipelines_and_composition.md` to design preprocessing + model pipelines with `Pipeline` and `ColumnTransformer`
- **Hyperparameter search implementation**: Use `references/model_evaluation.md` for concrete `GridSearchCV` / `RandomizedSearchCV` patterns
- **Algorithm selection**: Use `references/quick_reference.md` for algorithm selection cheat sheets based on data characteristics

If temporal data is detected, auto-invoke `time-series-validation` skill.

### 4. Leakage Check

Invoke `target-leakage-detection` skill on the proposed feature set.

### 5. Write Experiment Plan

Generate `docs/ds/experiments/YYYY-MM-DD-<experiment-name>-plan.md` from `templates/experiment-plan.md`.

Create the directory if needed: `mkdir -p docs/ds/experiments/`

### 6. Execute or Defer

Ask the user: "Experiment plan ready. What next?" with options:
- Write experiment code scaffold
- Just save the plan (implement later)
- Review plan with `/ds:review`

When generating the code scaffold, use the `scikit-learn` skill's pipeline patterns (`references/pipelines_and_composition.md`) and the example scripts (`scripts/classification_pipeline.py` or `scripts/clustering_analysis.py`) as structural references.

### 7. Generate Results (if executing)

After completion, generate `docs/ds/experiments/YYYY-MM-DD-<experiment-name>-result.md` from `templates/experiment-result.md` with:
- Actual metrics vs. baseline
- Environment details (Python version, library versions, git commit SHA)
- Data hash (SHA-256 of the dataset file)
- Compute cost (wall time, GPU hours if applicable)
- Key observations

Use the `model-evaluator` agent for comprehensive performance assessment.

Use the `scikit-learn` skill's evaluation utilities:
- Generate classification/regression metrics using `references/model_evaluation.md` patterns
- Create learning curves and validation curves for overfitting diagnosis

Run the `statistical-analysis` skill's assumption checks on the results:
- Use `scripts/assumption_checks.py` to verify normality and variance homogeneity of residuals/predictions
- Report results in APA format using `references/reporting_standards.md`
- Calculate and report effect sizes with confidence intervals

Invoke `feature-importance` skill alongside model-evaluator for feature attribution analysis.

### 8. Experiment Tracking

Log the experiment using the `experiment-tracking` skill format, including:
- Hypothesis, configuration, results, decision
- Series linkage (parent/child experiments)
- Environment and reproducibility details
