---
title: "Preprocessing Report: [Dataset Name]"
date: YYYY-MM-DD
dataset_name: "[Dataset Name]"
input_path: "[path/to/raw/data]"
output_path: "[path/to/preprocessed/data]"
input_hash: "[SHA-256 hash of input data]"
output_hash: "[SHA-256 hash of output data]"
input_rows: 0
input_columns: 0
output_rows: 0
output_columns: 0
pipeline_steps: 0
total_execution_time: "0.0s"
---

# Preprocessing Report: [Dataset Name]

## Learnings Applied

[List any past learnings from `docs/ds/learnings/` that informed this preprocessing run. If none, state "No prior learnings applied."]

## Input Data Summary

| Property | Value |
|----------|-------|
| File | [input_path] |
| Format | [CSV / Parquet / Excel / TSV] |
| Rows | [input_rows] |
| Columns | [input_columns] |
| File size | [size in MB] |
| Data hash | [input_hash] |

### Column Types

| Type | Count | Columns |
|------|-------|---------|
| Numeric | [N] | [column list] |
| Categorical | [N] | [column list] |
| Temporal | [N] | [column list] |
| Text | [N] | [column list] |

## Pipeline Configuration

| Step | Function | Key Parameters |
|------|----------|---------------|
| 1. [Step name] | [function_name] | [param=value, ...] |
| 2. [Step name] | [function_name] | [param=value, ...] |
| ... | ... | ... |

## Execution Log

| Step | Status | Rows In | Rows Out | Cols In | Cols Out | Time (s) | Details |
|------|--------|---------|----------|---------|----------|----------|---------|
| [Step 1] | [success/failed] | [N] | [N] | [N] | [N] | [N.NNN] | [brief note] |
| [Step 2] | [success/failed] | [N] | [N] | [N] | [N] | [N.NNN] | [brief note] |
| ... | ... | ... | ... | ... | ... | ... | ... |

**Total execution time:** [N.NNN]s

## Before / After Comparison

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Rows | [N] | [N] | [+/- N] |
| Columns | [N] | [N] | [+/- N] |
| Total missing values | [N] | [N] | [+/- N] |
| Duplicate rows | [N] | [N] | [+/- N] |
| Memory usage | [N MB] | [N MB] | [+/- N MB] |

### Column-Level Changes

| Column | Change | Details |
|--------|--------|---------|
| [column_name] | Dropped | [reason, e.g., 95% missing] |
| [column_name] | Type coerced | [string -> numeric, N values became NaN] |
| [column_name] | Normalized | [whitespace stripped, lowercased] |
| [column_name] | Outliers removed | [N rows removed via IQR] |

## Validation Results

[Include output from schema validation. If all checks pass: "All validation checks passed."]

### Schema Checks

| Column | Rule | Status | Details |
|--------|------|--------|---------|
| [col] | [dtype/nullable/range/...] | [PASS/FAIL] | [details if failed] |

### Custom Rules

| Rule | Status | Details |
|------|--------|---------|
| [rule_name] | [PASS/FAIL] | [details] |

## Output Data Summary

| Property | Value |
|----------|-------|
| File | [output_path] |
| Format | [CSV / Parquet] |
| Rows | [output_rows] |
| Columns | [output_columns] |
| File size | [size in MB] |
| Data hash | [output_hash] |

## Warnings and Issues

[List any warnings generated during pipeline execution. If none: "No warnings."]

- [Warning 1]
- [Warning 2]
