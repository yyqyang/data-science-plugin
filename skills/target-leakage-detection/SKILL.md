---
name: target-leakage-detection
description: "Detect target leakage in feature sets by checking temporal validity, feature-target correlation, and information flow. Use before training any model."
---

# Target Leakage Detection

Detect data leakage that would inflate model performance during development but fail in production.

## Detection Methodology

### 1. Temporal Leakage

For each feature, verify it would be available at prediction time:

- Features derived from future events (e.g., `outcome_date` when predicting outcome)
- Aggregations that include the prediction period
- Features updated after the target was determined

**Check:** For each feature, ask: "At the moment we need to make a prediction, would this value already be known?" If no, it's leakage.

### 2. Direct Leakage

Check for features that are transformations of the target:

- Features that are downstream effects of the target (e.g., `cancellation_reason` when predicting churn)
- One-to-one mappings with the target
- Encoded versions of the target (e.g., `revenue_bucket` when predicting revenue)

**Check:** If removing this feature drops model performance by >50%, it may be a proxy for the target.

### 3. Statistical Signals

Flag when any of these occur:

| Signal | Classification Threshold | Regression Threshold |
|---|---|---|
| Single feature AUC | > 0.95 | N/A |
| Single feature R-squared | N/A | > 0.95 |
| Feature importance dominated by 1 feature | >50% of total importance | >50% of total importance |
| Train and test performance nearly identical | Gap < 0.5% | Gap < 0.5% |

**Check:** Run single-feature models. Any feature with AUC > 0.95 or R-squared > 0.95 warrants investigation.

### 4. Group Leakage

Check for information leaking across the train/test boundary:

- Same entity (customer, patient) appearing in both train and test
- Preprocessing (scaling, encoding) fit on combined train+test data
- Target encoding computed on the full dataset instead of just training folds

**Check:** Verify that `train_ids.intersection(test_ids)` is empty for all entity identifiers.

## Remediation

For each detected leakage:

1. **Describe the mechanism** -- How is future/target information flowing into the feature?
2. **Assess impact** -- What happens to model performance if the feature is removed?
3. **Suggest fix:**
   - Remove the feature entirely
   - Adjust the time window (e.g., use only data before prediction point)
   - Fix the split strategy (group-aware splits)
   - Fix preprocessing (fit only on training data)

## Quick Check Script

```python
import pandas as pd
from sklearn.metrics import roc_auc_score

def check_leakage(df, target_col, feature_cols):
    """Flag features with suspiciously high single-feature AUC."""
    results = []
    for col in feature_cols:
        if df[col].dtype in ['float64', 'int64']:
            try:
                auc = roc_auc_score(df[target_col], df[col])
                auc = max(auc, 1 - auc)  # Handle inverse correlation
                if auc > 0.95:
                    results.append({'feature': col, 'auc': auc, 'risk': 'HIGH'})
                elif auc > 0.85:
                    results.append({'feature': col, 'auc': auc, 'risk': 'MEDIUM'})
            except Exception:
                pass
    return pd.DataFrame(results).sort_values('auc', ascending=False)
```
