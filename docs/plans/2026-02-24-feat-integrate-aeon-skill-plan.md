---
title: "feat: Integrate aeon skill for time series machine learning"
type: feat
date: 2026-02-24
---

# Integrate aeon Skill for Time Series Machine Learning

## Overview

Integrate the `aeon` skill from `claude-scientific-skills` into the ds plugin (v1.8.0). The plugin's time-series support currently covers classical statistical forecasting via the `statsmodels` skill (ARIMA, SARIMAX, ETS) but has no reference for time-series-specific ML algorithms -- classification, regression, clustering, anomaly detection, segmentation, or specialized distance metrics. This integration gives agents and commands a dedicated reference for time series ML workflows that complement the existing statistical approach.

## Problem Statement

The ds plugin (v1.7.0) routes `/ds:experiment` between three paradigms: supervised, unsupervised, and time-series. The time-series path only covers forecasting via statsmodels. When a user wants to:

1. **Classify time series** (e.g., "classify heartbeat ECGs as normal vs abnormal") -- there is no reference for ROCKET, InceptionTime, DTW-based classifiers, or the 3D data format `(n_samples, n_channels, n_timepoints)`.
2. **Cluster time series** (e.g., "group similar sensor readings") -- scikit-learn's clustering assumes tabular data; there is no reference for DTW-based k-means, barycentric averaging, or time-series-specific clustering evaluation.
3. **Detect anomalies in time series** (e.g., "find unusual patterns in server metrics") -- there is no experiment paradigm for anomaly detection at all.
4. **Extract time-series features** (e.g., "create ROCKET or Catch22 features for a traditional ML model") -- the feature-engineer agent has no reference for temporal feature extraction beyond lag features and rolling statistics.
5. **Use specialized distance metrics** (e.g., DTW for time series similarity) -- no reference exists.

Agents currently produce time-series ML code from general knowledge, leading to inconsistent patterns and missing the scikit-learn-compatible API that aeon provides.

## Proposed Solution

### 1. Copy and Adapt `skills/aeon/`

Source: `../claude-scientific-skills/scientific-skills/aeon/`

**Files to copy:**

- [x] `SKILL.md` (370 lines -- adapt frontmatter, add "Role in ds plugin", remove K-Dense promo, fix `plt.show()` in example)
- [x] `references/classification.md` (copy as-is)
- [x] `references/regression.md` (copy as-is)
- [x] `references/clustering.md` (copy as-is)
- [x] `references/forecasting.md` (copy as-is)
- [x] `references/anomaly_detection.md` (copy as-is)
- [x] `references/segmentation.md` (copy as-is)
- [x] `references/similarity_search.md` (copy as-is)
- [x] `references/transformations.md` (copy as-is)
- [x] `references/distances.md` (copy as-is)
- [x] `references/networks.md` (copy as-is)
- [x] `references/datasets_benchmarking.md` (copy as-is)

No scripts to copy (aeon has no scripts/ directory).

**SKILL.md adaptations:**

- [x] Rewrite frontmatter `description` to include ds plugin context and boundary guidance
- [x] Keep `license` and `metadata` fields from source
- [x] Add "Role in ds plugin" section after the Overview
- [x] Remove "Suggest Using K-Dense Web For Complex Worflows" section at the end
- [x] Replace `plt.show()` in the "Anomaly Detection with Visualization" example with `plt.savefig()` + `plt.close(fig)` per DS plugin matplotlib conventions

**"Role in ds plugin" content:**

The aeon skill provides the time series machine learning reference for the ds plugin. It is the reference for time-series-specific classification, regression, clustering, anomaly detection, segmentation, similarity search, feature extraction, and distance metrics.

**Boundary with other skills:**

- **statsmodels** remains the primary reference for classical statistical forecasting (ARIMA, SARIMAX, ETS with full diagnostics, p-values, AIC/BIC, residual analysis). Use aeon when ML-based forecasters are needed (TCN, DeepAR, regression-based) or when statsmodels methods are insufficient for the pattern complexity.
- **scikit-learn** remains the primary reference for general ML pipelines, preprocessing, and evaluation on cross-sectional (tabular) data. Use aeon for time-series-specific estimators (classifiers, regressors, clusterers, transformations) that plug into scikit-learn pipelines via aeon's scikit-learn-compatible API.
- **matplotlib** remains the primary reference for visualization. aeon provides no built-in visualization; generated visualization code for aeon results should follow the matplotlib skill's DS plugin conventions.
- **statistical-analysis** remains the primary reference for guided test selection and APA reporting. Use aeon's `benchmarking` module for time-series-specific evaluation metrics and statistical comparison (Nemenyi, Wilcoxon).

**DS plugin conventions for aeon:**

- Always set `random_state` (or numpy/tf seeds for deep learning) for reproducibility
- Use aeon's scikit-learn-compatible API (`fit`, `predict`, `transform`) for consistency with plugin pipeline patterns
- Normalize time series before most algorithms using `aeon.transformations.collection.Normalizer`
- Expect 3D data format: `(n_samples, n_channels, n_timepoints)` -- document this shape convention in generated code comments
- Start with ROCKET/MiniROCKET for fast prototyping before trying deep learning
- For visualization of aeon results, follow the `matplotlib` skill's DS plugin conventions (OO interface, savefig + close, no plt.show)

### 2. Extend `/ds:experiment` Routing

**Step 1b -- extend experiment type detection:**

Currently routes between supervised, unsupervised, and time-series. Extend to detect sub-types:

- [x] **Temporal supervised** (time-series classification, time-series regression) -- input features are time series (3D: samples x channels x timepoints), target is a class label or continuous value. Use aeon classifiers/regressors instead of standard scikit-learn.
- [x] **Temporal unsupervised** (time-series clustering) -- input is a collection of unlabeled time series. Use aeon clusterers with temporal distance metrics instead of standard scikit-learn clustering.
- [x] **Anomaly detection** (NEW paradigm) -- input is one or more time series, goal is to identify unusual points, subsequences, or series. Use aeon anomaly detectors.
- [x] **Time-series forecasting** (existing) -- remains unchanged, statsmodels primary, aeon supplements with ML-based forecasters.

Detection heuristics for the new sub-types:
- Temporal supervised: user mentions "classify time series", "time series classification/regression", data has shape (samples, channels, timepoints)
- Temporal unsupervised: user mentions "cluster time series", "group similar series", "time series clustering"
- Anomaly detection: user mentions "anomaly", "outlier", "unusual pattern", "discord", "change point"

### 3. Wire into `/ds:experiment` Command

**Step 2 -- Hypothesis Formulation:**

- [x] **Temporal supervised:** "Classification hypothesis (e.g., 'ROCKET will classify ECG signals with >90% accuracy, outperforming 1-NN Euclidean baseline'). What temporal patterns distinguish the classes?"
- [x] **Temporal unsupervised:** "Clustering hypothesis (e.g., 'DTW-based k-means with k=5 will reveal distinct operational regimes in sensor data'). What temporal structure is expected?"
- [x] **Anomaly detection:** "Detection hypothesis (e.g., 'STOMP with window_size=50 will identify >80% of known anomalies with <5% false positive rate'). What constitutes an anomaly in this domain?"

**Step 3 -- Methodology Design:**

- [x] **Temporal supervised** -- define:
  - **Data format**: Verify 3D shape `(n_samples, n_channels, n_timepoints)`. Reference aeon SKILL.md "Data Preparation" section.
  - **Algorithm selection**: Reference `aeon` skill's `references/classification.md` (or `regression.md`). Use algorithm selection guide: MiniROCKET for speed, HIVECOTEV2 for accuracy, ShapeletTransform for interpretability.
  - **Feature extraction alternative**: If converting to tabular, reference `aeon` skill's `references/transformations.md` (ROCKET, Catch22, TSFresh) then use scikit-learn classifiers.
  - **Distance metric selection**: For distance-based methods, reference `references/distances.md` for DTW, LCSS, etc.
  - **Split strategy**: Invoke `split-strategy` skill. For temporal classification, standard stratified splits are acceptable (unlike forecasting which requires temporal splits).
  - **Evaluation**: Standard classification/regression metrics from scikit-learn. Additionally, reference aeon's `references/datasets_benchmarking.md` for comparison with published results on standard datasets.

- [x] **Temporal unsupervised** -- define:
  - **Algorithm selection**: Reference `aeon` skill's `references/clustering.md`. Use algorithm selection guide: TimeSeriesKMeans with DTW for alignment-based, Catch22Clusterer for interpretability, deep learning clusterers for complex patterns.
  - **Distance metric**: Reference `references/distances.md`. Critical choice for clustering quality.
  - **Averaging method**: Barycentric averaging for DTW-based clustering.
  - **Internal metrics**: Silhouette score, Davies-Bouldin, clustering accuracy (if ground truth available) from `references/datasets_benchmarking.md`.

- [x] **Anomaly detection** -- define:
  - **Point vs subsequence vs collection**: Determine anomaly type. Reference `aeon` skill's `references/anomaly_detection.md` "Point vs Subsequence Anomalies" section.
  - **Algorithm selection**: Reference `references/anomaly_detection.md` algorithm selection guide: STOMP for discord discovery, IsolationForest for no-training-data, ROCKAD for semi-supervised, LeftSTAMPi for streaming.
  - **Window size**: Critical parameter for matrix profile methods. Reference best practices.
  - **Threshold strategy**: Percentile-based, domain-specific, or statistical.
  - **Evaluation metrics**: Range-based precision/recall/F1 from `references/datasets_benchmarking.md`, ROC AUC for scored output.

- [x] **Time-series forecasting** (existing path) -- add:
  - When classical models (ARIMA, SARIMAX) are insufficient, reference `aeon` skill's `references/forecasting.md` for ML-based alternatives: TCNForecaster for long sequences, DeepARNetwork for probabilistic forecasts, RegressionForecaster for using any regressor as a forecaster.

**Step 4 -- Leakage Check:**

- [x] **Temporal supervised**: Invoke `target-leakage-detection` with focus on ensuring no future information in features. For time-series classification, check that normalization parameters are fit on training data only (aeon best practice).
- [x] **Anomaly detection**: Skip traditional leakage check (no target in unsupervised anomaly detection), but verify evaluation labels are not used during training for semi-supervised methods.

**Step 6 -- Code scaffold generation:**

- [x] When generating code scaffolds for temporal supervised experiments, use aeon import patterns and scikit-learn pipeline composition:
  ```python
  from aeon.classification.convolution_based import RocketClassifier
  from aeon.transformations.collection import Normalizer
  ```
  Reference the aeon SKILL.md "Common Workflows" section for pipeline structure.

- [x] When generating code scaffolds for anomaly detection experiments:
  ```python
  from aeon.anomaly_detection import STOMP
  ```
  Reference the aeon SKILL.md "Anomaly Detection" section.

- [x] Include matplotlib visualization boilerplate per existing matplotlib convention.

**Step 7 -- Generate Results:**

- [x] **Temporal supervised results:**
  - Standard classification/regression metrics (accuracy, F1, RMSE) from scikit-learn
  - Comparison with published benchmarks if using standard datasets (reference `references/datasets_benchmarking.md`)
  - Algorithm comparison with statistical testing (Wilcoxon, Nemenyi) from `references/datasets_benchmarking.md`
  - Visualization: confusion matrix (scikit-learn displays), per-class accuracy, feature importance from interpretable models (Catch22 features, shapelet visualization)
  - Use matplotlib skill for result figures

- [x] **Temporal unsupervised results:**
  - Internal metrics (silhouette, Davies-Bouldin, clustering accuracy)
  - Cluster center visualization (plot average time series per cluster)
  - Cluster profiling: describe each cluster by its temporal characteristics
  - Use matplotlib skill for cluster visualization plots

- [x] **Anomaly detection results:**
  - Range-based precision, recall, F-score from aeon's evaluation metrics
  - ROC AUC for scored anomaly detection
  - Visualization: time series with anomaly scores overlay, threshold line, detected anomaly regions
  - Use matplotlib skill for anomaly visualization (savefig + close, no plt.show)

- [x] **Time-series forecasting results** (existing path) -- add:
  - When using aeon ML-based forecasters, include aeon-specific evaluation metrics from `references/forecasting.md`

### 4. Wire into `/ds:eda` Command

**Step 5 (Distribution Analysis) -- add temporal feature detection:**

- [x] When temporal columns are detected, suggest time-series feature extraction using aeon transformations. Reference `aeon` skill's `references/transformations.md` for Catch22 (interpretable 22-feature summary) and ROCKET (fast scalable features).

**Step 7b (Stationarity Testing) -- enhance temporal analysis:**

- [x] After stationarity testing (statsmodels remains primary), suggest time-series similarity analysis if multiple time series are present. Reference `aeon` skill's `references/distances.md` for DTW pairwise distance computation.
- [x] If change points are suspected, reference `aeon` skill's `references/segmentation.md` for ClaSP or FLUSS segmenters.

### 5. Wire into `/ds:plan` Command

**Step 3 (Approach Selection) -- extend for time series ML:**

- [x] When the problem involves **time-series classification or regression** (labeled temporal data), invoke the `aeon` skill's SKILL.md "Algorithm Selection Guide" to map the problem to candidate algorithms based on dataset size, accuracy requirements, and interpretability needs.
- [x] When the problem involves **anomaly detection in time series**, invoke the `aeon` skill's `references/anomaly_detection.md` for algorithm selection.
- [x] When the problem involves **time-series clustering**, invoke the `aeon` skill's `references/clustering.md` for algorithm selection.

### 6. Update Agents

**`experiment-designer` agent:**

- [x] Add temporal supervised section: hypothesis formulation for time-series classification/regression experiments, algorithm candidate selection from aeon, split strategy for temporal data
- [x] Add anomaly detection section: detection hypothesis, algorithm selection, threshold strategy, evaluation plan
- [x] Add example for time-series classification experiment design
- [x] Add example for anomaly detection experiment design

**`model-evaluator` agent:**

- [x] Add reference to aeon skill for time-series-specific evaluation metrics (range-based precision/recall for anomaly detection, clustering accuracy, published benchmark comparison)
- [x] Add reference to aeon's benchmarking module for statistical comparison (Nemenyi, Wilcoxon) across multiple datasets

**`data-profiler` agent:**

- [x] Add reference to aeon skill for temporal feature extraction suggestions (Catch22, ROCKET features) when profiling time-series data

**`feature-engineer` agent:**

- [x] Add reference to aeon skill's `references/transformations.md` for time-series feature extraction (ROCKET, Catch22, TSFresh, shapelet transforms, SAX/PAA symbolic representations)
- [x] Add time-series-specific feature candidates: aeon transformations as an alternative to manual lag/rolling features

**No changes to:** `problem-framer` (boundary: framing uses aeon indirectly through plan command), `documentation-synthesizer` (produces learnings, not code)

### 7. Update Templates

**Experiment plan template (`templates/experiment-plan.md`):**

- [x] Add temporal supervised fields under Methodology:
  - **Data format**: `(n_samples, n_channels, n_timepoints)` shape confirmation
  - **Distance metric**: DTW, Euclidean, or other (for distance-based methods)
  - **Algorithm category**: Convolution-based, distance-based, shapelet, deep learning, hybrid, etc.
- [x] Add anomaly detection fields under Methodology:
  - **Anomaly type**: Point, subsequence, or collection-level
  - **Window size**: For matrix profile methods
  - **Threshold strategy**: Percentile, domain-specific, or statistical
  - **Detection approach**: Semi-supervised (labeled normal data) or unsupervised
- [x] Add temporal unsupervised fields under Methodology:
  - **Distance metric**: For time-series clustering
  - **Averaging method**: Barycentric, shift-invariant, etc.

**Experiment result template (`templates/experiment-result.md`):**

- [x] Add temporal supervised result section with paradigm-specific visualization guidance:
  - Per-class accuracy, comparison with published benchmarks
  - Algorithm comparison statistical tests
- [x] Add anomaly detection result section:
  - Range-based metrics table (precision, recall, F-score)
  - Threshold analysis
  - Visualization guidance (time series with anomaly overlay)
- [x] Add temporal unsupervised result section:
  - Cluster center visualization guidance
  - Temporal clustering metrics

**EDA report template (`skills/exploratory-data-analysis/assets/report_template.md`):**

- [x] Add HTML comment in temporal analysis section referencing aeon skill for time-series feature extraction and segmentation

### 8. Update Overlapping Skill Boundaries

**`statsmodels` SKILL.md -- update "Role in ds plugin":**

- [x] Add boundary clarification: "For ML-based time-series forecasting (TCN, DeepAR) and time-series classification/regression, use the `aeon` skill. Statsmodels remains the primary reference for classical statistical methods with inference (p-values, diagnostics, AIC/BIC)."

**`scikit-learn` SKILL.md -- update "Role in ds plugin":**

- [x] Add boundary clarification: "For time-series-specific classification, regression, and clustering, use the `aeon` skill. Aeon estimators follow the scikit-learn API and work within sklearn pipelines. Scikit-learn remains the primary reference for cross-sectional (tabular) ML."

### 9. Dependency and Environment Updates

**`requirements.txt`:**

- [x] Add aeon to the optional section (after matplotlib/seaborn, before xgboost):
  ```
  # Optional -- time series ML (used by aeon skill)
  # aeon>=0.11
  ```

**`skills/setup/SKILL.md`:**

- [x] Add `aeon` to the optional library check list

**`README.md` Prerequisites:**

- [x] Add aeon to optional install command:
  ```bash
  uv pip install matplotlib seaborn aeon xgboost lightgbm shap
  ```

### 10. Metadata Sync

- [x] `.claude-plugin/plugin.json` -- bump version to `1.8.0`, update description: "11 skills"
- [x] `README.md` -- update Components table (Skills: 11), add `aeon` row to Skills table, update intro line
- [x] `CHANGELOG.md` -- add `[1.8.0]` entry
- [x] `CLAUDE.md` -- add `aeon` to Invocation Map for `/ds:plan`, `/ds:eda`, and `/ds:experiment` rows

## Technical Considerations

### Aeon Data Format Convention

Aeon expects time series in 3D numpy arrays: `(n_samples, n_channels, n_timepoints)`. This differs from the standard tabular format `(n_samples, n_features)` that scikit-learn expects. The adapted SKILL.md's "Role in ds plugin" section codifies this convention. When users have tabular time-series data (columns are time steps), generated code must reshape it:

```python
# Reshape tabular to aeon format: (n_samples, 1, n_timepoints)
X_aeon = X_tabular.values.reshape(X_tabular.shape[0], 1, -1)
```

### Aeon as a Non-Foundational Library Skill

Unlike matplotlib (which is used internally by other skills), aeon is NOT a foundational skill. No existing skill imports or uses aeon. This makes the integration simpler -- there is no "convention gravity" concern. Aeon is a domain-specific skill like scikit-learn and statsmodels: it provides algorithms for a specific problem domain (time series ML).

The boundary with statsmodels is domain-based, not foundational:
- statsmodels = statistical inference on time series (diagnostics, p-values, model comparison)
- aeon = ML algorithms for time series (classification, regression, clustering, feature extraction)

### Scope of New Experiment Paradigms

This integration adds three new experiment sub-types:

| New Sub-type | Added by | Routing Detection |
|---|---|---|
| Temporal supervised (TS classification/regression) | aeon | "classify time series", 3D data shape |
| Temporal unsupervised (TS clustering) | aeon | "cluster time series", "group similar series" |
| Anomaly detection | aeon | "anomaly", "outlier", "unusual pattern" |

Segmentation and similarity search are NOT added as experiment paradigms -- they are utility capabilities referenced in EDA and as helper tasks within other experiments.

### Deep Learning Dependencies

Aeon's deep learning classifiers/regressors/clusterers require TensorFlow. This is a heavy optional dependency. The SKILL.md should note:
- Deep learning estimators are optional and require TensorFlow
- Start with non-deep-learning methods (ROCKET, DTW-based) which need only numpy/scipy
- The setup skill does not need to check for TensorFlow (it's a transitive dependency of specific aeon features)

### Boundary with Existing Skills

| Capability | Primary Reference | aeon Role |
|---|---|---|
| Classical forecasting (ARIMA, SARIMAX) | statsmodels | ML-based alternatives (TCN, DeepAR) |
| Stationarity testing | statsmodels | Not aeon's job |
| Time-series diagnostics (Ljung-Box, ACF/PACF) | statsmodels | Not aeon's job |
| Tabular classification/regression | scikit-learn | Not aeon's job |
| Tabular clustering (k-means, DBSCAN) | scikit-learn | Not aeon's job |
| Time-series classification/regression | aeon | Primary reference |
| Time-series clustering | aeon | Primary reference |
| Anomaly detection in time series | aeon | Primary reference |
| Time-series feature extraction (ROCKET, Catch22) | aeon | Primary reference |
| Temporal distance metrics (DTW, LCSS) | aeon | Primary reference |
| Segmentation / change point detection | aeon | Primary reference |
| Visualization of results | matplotlib | aeon code uses matplotlib conventions |
| Statistical test selection | statistical-analysis | Not aeon's job |
| Pipeline composition | scikit-learn | aeon estimators work in sklearn pipelines |

## Acceptance Criteria

- [ ] `skills/aeon/SKILL.md` exists with adapted frontmatter and "Role in ds plugin" section
- [ ] 11 reference files copied to `skills/aeon/references/`
- [ ] `/ds:experiment` step 1b extended with temporal supervised, temporal unsupervised, and anomaly detection routing
- [ ] `/ds:experiment` steps 2, 3, 4, 6, 7 have aeon references for the new sub-types
- [ ] `/ds:eda` steps 5 and 7b reference the aeon skill for temporal feature extraction and segmentation
- [ ] `/ds:plan` step 3 references the aeon skill for time-series ML algorithm selection
- [ ] `experiment-designer` agent has temporal supervised and anomaly detection sections with examples
- [ ] `model-evaluator` agent references aeon evaluation metrics
- [ ] `data-profiler` agent references aeon for temporal feature extraction
- [ ] `feature-engineer` agent references aeon transformations
- [ ] `statsmodels` and `scikit-learn` SKILL.md "Role in ds plugin" paragraphs updated with aeon boundary
- [ ] Experiment plan template has temporal supervised, temporal unsupervised, and anomaly detection fields
- [ ] Experiment result template has paradigm-specific sections for the new sub-types
- [ ] EDA report template updated with temporal analysis guidance
- [ ] `aeon` added to `requirements.txt` optional section
- [ ] `aeon` added to `skills/setup/SKILL.md` optional checks
- [ ] `plugin.json` version `1.8.0`, description says "11 skills"
- [ ] `README.md` Components table shows 11 skills, Skills table includes aeon row, Prerequisites updated
- [ ] `CHANGELOG.md` has `[1.8.0]` entry
- [ ] `CLAUDE.md` Invocation Map includes aeon in plan, eda, and experiment rows
- [ ] No `plt.show()` calls in adapted skill content -- all use `plt.savefig()` + `plt.close(fig)`
- [ ] K-Dense promotional section removed from adapted SKILL.md

## References

- Source skill: `../claude-scientific-skills/scientific-skills/aeon/`
- [Matplotlib integration solution](../solutions/integration-issues/matplotlib-skill-plugin-wiring.md)
- [Statsmodels integration solution](../solutions/integration-issues/statsmodels-skill-plugin-wiring.md)
- [Scikit-learn integration solution](../solutions/integration-issues/scikit-learn-skill-plugin-wiring.md)
- [Skill Integration Checklist](../solutions/integration-issues/matplotlib-skill-plugin-wiring.md#prevention)
