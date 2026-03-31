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

---

## Financial Data: Purging, Embargo & Walk-Forward

Financial time-series require additional safeguards beyond basic `TimeSeriesSplit`.
These techniques are from López de Prado's *Advances in Financial Machine Learning*.

### Purging

**Problem:** When labels use a forward-looking window (e.g., T+5 return), training
samples near the test boundary have labels that overlap with the test period.

**Solution:** Remove (purge) training samples whose label window overlaps with any
test sample.

```
Label window = 5 days
Test starts at day 100

Without purging:
  Train: [day 1 ............. day 99]  ← day 95-99 labels leak into test!
  Test:  [day 100 ............. day 120]

With purging:
  Train: [day 1 ........ day 94]  ← days 95-99 removed
  Test:  [day 100 ............. day 120]

Purge size = label_window - 1 = 4 days
```

### Embargo

**Problem:** In expanding-window CV, training folds after the test fold can also
leak information backward (autocorrelation in financial series).

**Solution:** Add a gap (embargo) after the test period before resuming training.

```
Walk-forward fold with purge + embargo:

  Train: [day 1 ... day 94]  [PURGE 5d]  Test: [day 100-120]  [EMBARGO 5d]  Train: [day 126 ...]
```

**Embargo size heuristic:** Use the same size as the label window, or the
autocorrelation decay length of your series (whichever is larger).

### Walk-Forward Validation

The standard approach for backtesting trading strategies. Simulates how the
model would be trained and used in production over time.

```
Fold 1: Train [2020-01 to 2021-12] → Test [2022-01 to 2022-03]
Fold 2: Train [2020-01 to 2022-03] → Test [2022-04 to 2022-06]  (expanding)
Fold 3: Train [2020-01 to 2022-06] → Test [2022-07 to 2022-09]
...

Or with fixed window (sliding):
Fold 1: Train [2020-01 to 2021-12] → Test [2022-01 to 2022-03]
Fold 2: Train [2020-04 to 2022-03] → Test [2022-04 to 2022-06]  (sliding)
```

**Expanding vs sliding window:**
- **Expanding:** More training data each fold. Use when regime is stable.
- **Sliding:** Fixed window size. Use when recent data is more relevant (regime changes).

### Sector/Ticker Group Awareness

In cross-sectional financial models (e.g., factor models across stocks), group
leakage occurs when the same ticker or sector appears in both train and test.

```python
# Group by ticker — never train and test on the same stock
groups = df["ticker"]
gkf = GroupKFold(n_splits=5)

# Group by sector — never train and test on the same sector
groups = df["sector"]

# Combined: temporal + group awareness
# (custom implementation needed — sklearn doesn't have this built in)
```

### Survivorship Bias

Only including stocks that exist today ignores delisted/bankrupt companies,
inflating backtested returns.

**Checklist:**
- [ ] Does your dataset include delisted stocks?
- [ ] Does your data start from the earliest date the stock was available?
- [ ] Are corporate actions (splits, mergers) handled correctly?
- [ ] Is the benchmark survivorship-bias-free?

### Implementation: Purged Walk-Forward CV

```python
import numpy as np
from sklearn.model_selection import BaseCrossValidator

class PurgedWalkForwardCV(BaseCrossValidator):
    """Walk-forward CV with purging and embargo for financial data.

    Args:
        n_splits: Number of walk-forward folds.
        purge_window: Number of samples to purge before test set.
        embargo_window: Number of samples to embargo after test set.
        expanding: If True, training window expands. If False, slides.
        min_train_size: Minimum training samples required.
    """
    def __init__(self, n_splits=5, purge_window=5, embargo_window=5,
                 expanding=True, min_train_size=252):
        self.n_splits = n_splits
        self.purge_window = purge_window
        self.embargo_window = embargo_window
        self.expanding = expanding
        self.min_train_size = min_train_size

    def split(self, X, y=None, groups=None):
        n = len(X)
        test_size = (n - self.min_train_size) // self.n_splits
        if test_size < 1:
            raise ValueError("Not enough data for requested splits")

        for i in range(self.n_splits):
            test_start = self.min_train_size + i * test_size
            test_end = min(test_start + test_size, n)

            # Training indices: everything before test, minus purge window
            if self.expanding:
                train_end = test_start - self.purge_window
            else:
                train_start = max(0, test_start - self.min_train_size - self.purge_window)
                train_end = test_start - self.purge_window

            train_start = 0 if self.expanding else train_start
            if train_end <= train_start:
                continue

            train_idx = np.arange(train_start, train_end)
            test_idx = np.arange(test_start, test_end)

            yield train_idx, test_idx

    def get_n_splits(self, X=None, y=None, groups=None):
        return self.n_splits

# Usage:
cv = PurgedWalkForwardCV(
    n_splits=5,
    purge_window=5,    # match your label window (e.g., T+5 returns)
    embargo_window=5,
    expanding=True,
    min_train_size=252  # ~1 year of trading days
)
for train_idx, test_idx in cv.split(X):
    model.fit(X[train_idx], y[train_idx])
    score = model.score(X[test_idx], y[test_idx])
```

---

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
