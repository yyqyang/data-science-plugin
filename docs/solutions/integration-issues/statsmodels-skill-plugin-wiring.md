---
title: "Statsmodels skill integration with time-series experiment routing"
category: integration-issues
tags: [statsmodels, skill-integration, time-series, three-way-routing, skill-boundary, glm, arima, diagnostics, command-wiring]
module: commands/experiment, commands/eda, commands/plan, skills/statsmodels, skills/statistical-analysis
symptom: "Plugin agents described statistical modeling concepts at high level but provided no concrete statsmodels API patterns; experiment command had no time-series path; boundary between statistical-analysis and statsmodels was undefined"
root_cause: "API reference gap between conceptual agents and actionable code; supervised/unsupervised binary couldn't accommodate time-series methodology; multi-skill boundary management not formalized"
date: 2026-02-24
outcome: success
versions: "1.6.0"
---

# Statsmodels Skill Integration with Time-Series Experiment Routing

## Problem

Three related integration issues in the ds plugin (v1.5.0):

1. **No statsmodels API reference** -- Agents like `experiment-designer` and `model-evaluator` described regression, GLM, and time-series concepts but provided no concrete statsmodels code patterns. Users had to look up `sm.OLS`, `ARIMA`, `het_breuschpagan`, and formula API themselves.

2. **No time-series experiment path** -- `commands/experiment.md` step 1b routed between supervised and unsupervised only. Time-series forecasting experiments (ARIMA, SARIMAX, exponential smoothing) are technically supervised but have fundamentally different methodology: stationarity testing, ARIMA order selection via ACF/PACF, temporal splits, forecast evaluation with RMSE/MAE/MAPE. Forcing them into the supervised path produced mismatched guidance (cross-validation folds instead of temporal splits, no stationarity checks, no forecast-specific metrics).

3. **Undefined boundary between overlapping skills** -- The existing `statistical-analysis` skill already uses statsmodels as a supporting library (VIF, Breusch-Pagan, power analysis), but its focus is test selection workflows and APA reporting. The new `statsmodels` skill provides the API reference layer. Without an explicit boundary, both skills would provide overlapping diagnostic guidance at `/ds:experiment` step 7.

## Investigation

- Read the source statsmodels skill (612-line SKILL.md, 5 reference files, no scripts) from `claude-scientific-skills`
- Analyzed overlap with existing skills: `statistical-analysis` covers test selection, assumption checking, APA reporting using statsmodels as a tool; `scikit-learn` covers ML pipelines and evaluation; neither teaches the statsmodels API
- Identified that OLS, GLM, ARIMA/SARIMAX, discrete choice, formula API, and diagnostic test patterns had zero dedicated coverage
- Ran spec-flow analysis that identified 20 gaps including: three-way routing need, undefined boundary, missing conditional routing criteria, underspecified EDA wiring, template gaps for time-series
- Mapped all commands for integration points: experiment (steps 3, 6, 7), eda (step 7), plan (step 3)
- Confirmed no new dependencies needed (statsmodels already required, matplotlib already optional)

## Solution

### v1.6.0 -- Statsmodels skill integration

**Skill copy and adaptation:**

Copied `skills/statsmodels/` from `claude-scientific-skills` with:
- SKILL.md (adapted frontmatter, kept `license`/`metadata`, added "Role in ds plugin" paragraph, removed K-Dense promo, preserved Getting Help section)
- 5 reference files (linear_models, glm, discrete_choice, time_series, stats_diagnostics)
- No scripts (reference files provide sufficient code patterns)

**Three-way experiment routing:**

Extended `/ds:experiment` step 1b from two paths to three:
- **Supervised** (classification, regression) -- has a target variable, cross-sectional data
- **Unsupervised** (clustering, dimensionality reduction) -- no target variable
- **Time-series** (forecasting, temporal modeling) -- target is future values of a time-ordered variable

Added time-series conditional text in:
- Step 2: forecasting hypothesis, expected temporal patterns, forecast horizon
- Step 3: stationarity assessment (ADF/KPSS), temporal split strategy, model identification (ACF/PACF), forecast evaluation metrics, naive baseline
- Step 4: temporal leakage check (verify split boundary respected)
- Step 7: forecast accuracy metrics (RMSE/MAE/MAPE), residual diagnostics (Ljung-Box), model comparison (AIC/BIC), prediction interval visualization, stationarity verification on residuals

**Cross-command wiring:**

- `commands/experiment.md` step 3: statsmodels for regression with inference (OLS/WLS/GLS), GLM (family/link selection), discrete choice, time-series model identification
- `commands/experiment.md` step 6: statsmodels Quick Start Guide and formula API for code scaffolding
- `commands/experiment.md` step 7: residual analysis, influence diagnostics, AIC/BIC comparison, robust SEs (supervised); Ljung-Box, diagnostic plots, stationarity verification (time-series)
- `commands/eda.md` step 7a: VIF multicollinearity check via `variance_inflation_factor`
- `commands/eda.md` step 7b: stationarity testing (ADF/KPSS) when temporal columns detected
- `commands/plan.md` step 3: statsmodels for inference/GLM/time-series approach selection
- Updated CLAUDE.md invocation map for all three commands

**Boundary clarification:**

Updated `statistical-analysis` SKILL.md "Role in ds plugin" paragraph:
- Statistical-analysis owns the *workflow* (which test to run, assumption sequence, APA reporting)
- Statsmodels owns the *API reference* (how to call functions, interpret result objects, troubleshoot convergence)
- Both skills' "Role in ds plugin" paragraphs now reference each other with the boundary rule

**Agent and template updates:**

- `experiment-designer` agent: added time-series framing section (9 steps: forecasting hypothesis, stationarity assessment, model candidates, order selection, temporal split, forecast evaluation, residual diagnostics, resource budget, reproducibility) and time-series example
- `experiment-plan.md` template: added time-series conditional fields (temporal characteristics, model order, forecast horizon, time-series-specific metrics and baselines)
- `experiment-result.md` template: added time-series forecast performance table and residual diagnostics table (Ljung-Box, ADF, Breusch-Pagan)

## Prevention

### Updated Skill Integration Checklist

When adding a new skill to the ds plugin, follow the base checklist plus the new items marked with (+):

- [ ] **Cross-cut audit**: review ALL commands for integration points, not just the most obvious one
- [ ] **Cross-command wiring matrix** (+): create a matrix (commands x steps) marking where the new skill adds value before implementing
- [ ] **Import audit**: cross-reference all `import` statements in scripts against setup skill checks
- [ ] **No phantom references**: every skill name in commands/agents must resolve to an actual `skills/<name>/SKILL.md`
- [ ] **Paradigm check**: consider supervised, unsupervised, and time-series paths
- [ ] **Paradigm extension** (+): if the skill enables a new experiment type that doesn't fit existing routing, extend routing at the entry point (step 1b) rather than patching existing steps
- [ ] **Multi-skill boundary** (+): if the new skill overlaps with existing skills, define the boundary explicitly in BOTH skills' "Role in ds plugin" paragraphs
- [ ] **Template evolution** (+): update experiment templates with conditional fields for each paradigm using consistent `[Paradigm: ...]` labels
- [ ] **Three-place sync**: update plugin.json, README.md, CHANGELOG.md
- [ ] **Invocation map**: update CLAUDE.md for every command that references the skill
- [ ] **Spec-flow analysis** (+): run before implementation to identify gaps that inform the integration design

### Architecture Principles

1. **Agents advise, skills provide code** -- every conceptual agent recommendation should pair with a skill that has runnable code patterns
2. **The Invocation Map is a contract** -- if a skill is not in the map, it's invisible; if it's in the map but doesn't exist, the workflow is broken
3. **Design for all paradigms, ship for one** -- include routing/branching logic even if only one path is implemented initially
4. **Boundary rules are bilateral** (+) -- when two skills overlap, both must document the boundary in their "Role in ds plugin" paragraph, not just the newer skill
5. **Extend routing, don't patch** (+) -- when a new paradigm doesn't fit existing routing, create a new path at the entry point rather than adding conditionals to every step of an existing path

## Related

- [Statsmodels integration plan](../../plans/2026-02-24-feat-integrate-statsmodels-skill-plan.md)
- [Scikit-learn integration solution](./scikit-learn-skill-plugin-wiring.md)
- [Scikit-learn integration plan](../../plans/2026-02-24-feat-integrate-scikit-learn-skill-plan.md)
- [Experiment improvements plan](../../plans/2026-02-24-feat-experiment-command-improvements-plan.md)
