---
name: statistical-tests
description: "Select appropriate statistical tests based on data type, distribution, and hypothesis. Use when comparing groups, testing relationships, or validating assumptions."
---

# Statistical Test Selection Guide

Select the right statistical test based on your data and question.

## Test Selection Table

| Question | Data Types | Normal? | Test |
|---|---|---|---|
| Two group means differ? | Continuous vs. Binary | Yes | Independent t-test |
| Two group means differ? | Continuous vs. Binary | No | Mann-Whitney U |
| Paired measurements differ? | Continuous (paired) | Yes | Paired t-test |
| Paired measurements differ? | Continuous (paired) | No | Wilcoxon signed-rank |
| >2 group means differ? | Continuous vs. Categorical | Yes | One-way ANOVA |
| >2 group means differ? | Continuous vs. Categorical | No | Kruskal-Wallis |
| Two variables related? | Continuous vs. Continuous | Yes | Pearson correlation |
| Two variables related? | Continuous vs. Continuous | No | Spearman correlation |
| Two categories related? | Categorical vs. Categorical | N/A | Chi-squared test |
| Distribution fits expected? | Categorical | N/A | Chi-squared goodness of fit |
| Data is normal? | Continuous | N/A | Shapiro-Wilk (<5000) or K-S test |
| Two models differ? | Model predictions | N/A | McNemar's test (classification) or paired t-test on CV folds |

## Decision Process

1. **Define the hypothesis** -- What are you testing? State H0 and H1.
2. **Identify data types** -- Continuous, ordinal, or categorical?
3. **Check normality** -- Use Shapiro-Wilk for n < 5000, visual inspection (Q-Q plot) for larger samples.
4. **Check assumptions** -- Independence, equal variance (Levene's test), sample size.
5. **Select test** -- Use the table above.
6. **Report results** -- p-value, effect size, confidence interval.

## Multiple Testing Correction

When running more than one test, adjust for multiple comparisons:

- **Bonferroni correction** -- Divide alpha by the number of tests. Conservative but simple.
- **Benjamini-Hochberg FDR** -- Controls false discovery rate. Less conservative, preferred when running many tests.
- **Holm-Bonferroni** -- Step-down procedure. More powerful than Bonferroni, still controls family-wise error.

```python
from scipy import stats
from statsmodels.stats.multitest import multipletests

# Run multiple tests
p_values = [test1_p, test2_p, test3_p]

# Bonferroni correction
reject_bonf, pvals_bonf, _, _ = multipletests(p_values, method='bonferroni')

# Benjamini-Hochberg FDR
reject_fdr, pvals_fdr, _, _ = multipletests(p_values, method='fdr_bh')
```

## Effect Size

Always report effect size alongside p-values. A statistically significant result with tiny effect size may not be practically meaningful.

| Test | Effect Size Measure | Small | Medium | Large |
|---|---|---|---|---|
| t-test | Cohen's d | 0.2 | 0.5 | 0.8 |
| ANOVA | Eta-squared | 0.01 | 0.06 | 0.14 |
| Chi-squared | Cramer's V | 0.1 | 0.3 | 0.5 |
| Correlation | r (or R-squared) | 0.1 | 0.3 | 0.5 |

## Sample Size Guidance

- With <30 observations per group, prefer non-parametric tests regardless of normality
- Power analysis: use `statsmodels.stats.power` to determine minimum sample size before running experiments
- For model comparison: minimum 5-fold CV, preferably 10-fold for small datasets

```python
from statsmodels.stats.power import TTestIndPower

# Minimum sample size for detecting medium effect (d=0.5) with 80% power
analysis = TTestIndPower()
n = analysis.solve_power(effect_size=0.5, power=0.8, alpha=0.05)
# n ~ 64 per group
```
