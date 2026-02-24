---
name: split-strategy
description: "Select and implement appropriate train/validation/test split strategies based on data characteristics. Use when designing the evaluation framework for a model."
---

# Split Strategy

Select the right train/validation/test split based on your data characteristics. Follow the decision tree below.

## Decision Tree

### 1. Is there a time dimension?

**Yes** -> **Temporal split**: Train on past, validate on recent, test on most recent. Never shuffle across time.
- Use `TimeSeriesSplit` for cross-validation
- Set embargo gap = largest feature look-back window

**No** -> Continue to next question.

### 2. Are observations grouped?

Examples: multiple rows per customer, multiple images per patient, repeated measurements.

**Yes** -> **Group-aware split**: Keep all observations of a group in the same fold.
- Use `GroupKFold` or `GroupShuffleSplit`
- Never let the same group appear in both train and test

**No** -> Continue.

### 3. Is the target imbalanced?

Minority class <10% of total.

**Yes** -> **Stratified split**: Preserve class ratios across folds.
- Use `StratifiedKFold` or `StratifiedShuffleSplit`
- Combine with group awareness if needed: `StratifiedGroupKFold`

**No** -> **Simple random split**: Standard `train_test_split` with fixed seed.

### 4. Is the dataset small?

Less than 5,000 rows.

**Yes** -> **Cross-validation**: Use 5-fold or 10-fold CV instead of a single holdout. Report mean and std of metrics.

**No** -> Single holdout is fine (70/15/15 or 80/10/10).

## Split Ratios

| Dataset Size | Recommended Split | Notes |
|---|---|---|
| <1,000 | Leave-one-out or 10-fold CV | Every data point matters |
| 1,000-10,000 | 5-fold CV or 80/10/10 | CV preferred for reliable estimates |
| 10,000-100,000 | 80/10/10 | Single holdout usually sufficient |
| >100,000 | 90/5/5 or 95/2.5/2.5 | Large test sets are unnecessary |

## Common Mistakes

1. **Shuffling time-series data** -- Destroys temporal structure, causes leakage
2. **Fitting preprocessors before splitting** -- Scalers, encoders must be fit only on training data
3. **Using test set for tuning** -- Test set should be touched only once, at the very end
4. **Ignoring groups** -- Correlated observations in different folds inflate performance estimates
5. **Not setting random seed** -- Results are not reproducible without `random_state`

## Implementation

```python
from sklearn.model_selection import train_test_split, StratifiedKFold, GroupKFold, TimeSeriesSplit

# Simple stratified split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Temporal split
tscv = TimeSeriesSplit(n_splits=5)
for train_idx, val_idx in tscv.split(X):
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]

# Group-aware split
gkf = GroupKFold(n_splits=5)
for train_idx, val_idx in gkf.split(X, y, groups=groups):
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
```
