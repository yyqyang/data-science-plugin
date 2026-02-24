---
title: "Experiment Result: [Experiment Name]"
date: YYYY-MM-DD
author: [Name]
status: complete
experiment_plan: "[path to experiment plan]"
outcome: [success | failure | mixed]
---

# Experiment Result: [Experiment Name]

## Summary
[1-2 sentence summary of what happened]

## Results

### Overall Performance
| Metric | Train | Validation | Test | Baseline | Delta |
|---|---|---|---|---|---|

### Slice Performance
| Slice | Metric | Value | Overall | Ratio |
|---|---|---|---|---|

### Key Plots
<!-- Supervised: confusion matrix (scikit-learn ConfusionMatrixDisplay), learning curves, feature importance bar charts, residual plots. Use matplotlib skill for multi-panel composition. -->
<!-- Unsupervised: cluster scatter plots with color-coded groups, elbow curves, silhouette plots. Use matplotlib skill's references/plot_types.md. -->
<!-- Time-series: forecast vs actual line plots with prediction interval shading (matplotlib fill_between), diagnostic plots (statsmodels plot_diagnostics). -->
[Description of important visualizations -- confusion matrix, PR curve, calibration plot, SHAP summary]

### Time-Series Forecast Performance (if applicable)
| Model | Order | AIC | RMSE | MAE | MAPE | vs Baseline |
|---|---|---|---|---|---|---|

### Residual Diagnostics (if applicable)
| Test | Statistic | p-value | Result |
|---|---|---|---|
| Ljung-Box | | | |
| ADF (residuals) | | | |
| Breusch-Pagan | | | |

## Analysis
[What worked, what didn't, why]

## Comparison to Hypothesis
[Did the hypothesis hold? Why or why not?]

## Artifacts
- **Model:** [Path to saved model]
- **Predictions:** [Path to prediction files]
- **Notebook:** [Path to analysis notebook]

## Decision
**[Ship | Iterate | Abandon]** -- [Reasoning]

## Next Steps
- [ ] [Action 1]
- [ ] [Action 2]

## Learnings
[What should be captured in docs/ds/learnings/ for future reference?]
