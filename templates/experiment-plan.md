---
title: "Experiment Plan: [Experiment Name]"
date: YYYY-MM-DD
author: [Name]
status: planned
---

# Experiment Plan: [Experiment Name]

## Hypothesis / Research Question
[Supervised: What we expect to happen and why. Unsupervised: What structure or patterns are we looking for?]

## Background
[Why this experiment? What prior work informs it?]

## Methodology

### Data
- **Dataset:** [Name and version]
- **Date range:** [Training and evaluation periods]
- **Split strategy:** [How data will be divided]

### Features
- **Feature set:** [Description or reference to feature list]
- **New features:** [Any new features being tested]
- **Leakage check:** [Supervised: confirmed clean / pending review. Unsupervised: N/A]

### Model
- **Algorithm:** [What model(s) to train or compare]
- **Hyperparameters:** [Starting values and search strategy]
- **Baseline:** [Supervised: what we're comparing against. Unsupervised: algorithm comparison protocol]

### Evaluation
- **Primary metric:** [Supervised: metric name and why. Unsupervised: internal metric (silhouette, Davies-Bouldin, explained variance)]
- **Secondary metrics:** [List]
- **Slices to evaluate:** [Supervised: important subgroups. Unsupervised: cluster profiles]
- **Stability assessment:** [Unsupervised: resampling strategy for consistency check]

## Reproducibility
- **Random seed:** [Value]
- **Environment:** [Python version, key library versions]
- **Data snapshot:** [How to get the exact data version]

## Expected Timeline
- [ ] Data preparation: [estimate]
- [ ] Training: [estimate]
- [ ] Evaluation: [estimate]
- [ ] Documentation: [estimate]

## Success Criteria
[What result would make us ship this model?]
