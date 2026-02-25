"""
End-to-end preprocessing pipeline orchestrator.

Executes a sequence of preprocessing steps with per-step tracking,
data hashing for reproducibility, and structured reporting.

Usage:
    python scripts/pipeline.py

This script demonstrates a complete preprocessing workflow:
1. Load raw data
2. Execute pipeline steps with tracking
3. Validate output
4. Generate summary report
"""

import hashlib
import os
import time

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def compute_hash(df):
    """Compute SHA-256 hash of a DataFrame for reproducibility tracking."""
    return hashlib.sha256(
        pd.util.hash_pandas_object(df).values.tobytes()
    ).hexdigest()


# ---------------------------------------------------------------------------
# Pipeline step functions
# ---------------------------------------------------------------------------
# Each step function takes (df, **kwargs) and returns (df, info_dict).

def step_deduplicate(df, subset=None, keep="first"):
    """Remove duplicate rows."""
    n_before = len(df)
    df_clean = df.drop_duplicates(subset=subset, keep=keep)
    n_removed = n_before - len(df_clean)
    return df_clean, {"duplicates_removed": n_removed}


def step_drop_high_missing_cols(df, threshold=0.9):
    """Drop columns where missing rate exceeds threshold."""
    missing_rates = df.isnull().mean()
    cols_to_drop = missing_rates[missing_rates > threshold].index.tolist()
    rates = {col: round(float(missing_rates[col]), 4) for col in cols_to_drop}
    return df.drop(columns=cols_to_drop), {
        "columns_dropped": cols_to_drop,
        "missing_rates": rates,
    }


def step_drop_high_missing_rows(df, threshold=0.5):
    """Drop rows where missing rate exceeds threshold."""
    row_missing = df.isnull().mean(axis=1)
    mask = row_missing <= threshold
    n_dropped = (~mask).sum()
    return df[mask].copy(), {"rows_dropped": int(n_dropped)}


def step_drop_constant_columns(df):
    """Drop columns with a single unique value."""
    nunique = df.nunique()
    constant = nunique[nunique <= 1].index.tolist()
    return df.drop(columns=constant), {"columns_dropped": constant}


def step_coerce_types(df, type_map=None):
    """Coerce column types safely.

    type_map: dict of {column: target_type}.
    target_type: 'numeric', 'datetime', 'category', 'string'.
    """
    if type_map is None:
        type_map = {}
    df_clean = df.copy()
    failed = {}
    for col, target in type_map.items():
        if col not in df_clean.columns:
            failed[col] = "column not found"
            continue
        try:
            if target == "numeric":
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
            elif target == "datetime":
                df_clean[col] = pd.to_datetime(df_clean[col], errors="coerce")
            elif target == "category":
                df_clean[col] = df_clean[col].astype("category")
            elif target == "string":
                df_clean[col] = df_clean[col].astype(str)
        except Exception as e:
            failed[col] = str(e)
    return df_clean, {"coerced": list(type_map.keys()), "failed": failed}


def step_normalize_strings(df, columns=None, case="lower"):
    """Strip whitespace and normalize case for string columns."""
    if columns is None:
        columns = df.select_dtypes(include="object").columns.tolist()
    df_clean = df.copy()
    for col in columns:
        df_clean[col] = df_clean[col].str.strip()
        if case == "lower":
            df_clean[col] = df_clean[col].str.lower()
        elif case == "upper":
            df_clean[col] = df_clean[col].str.upper()
    return df_clean, {"normalized_columns": columns}


def step_replace_placeholders(df, placeholders=None):
    """Replace common placeholder values with NaN."""
    if placeholders is None:
        placeholders = [
            "", "N/A", "n/a", "NA", "na", "null", "NULL",
            "None", "none", "-", "--", ".", "?",
            "unknown", "UNKNOWN", "missing", "MISSING",
        ]
    df_clean = df.replace(placeholders, np.nan)
    replacements = {}
    for col in df.columns:
        diff = int(df[col].isin(placeholders).sum())
        if diff > 0:
            replacements[col] = diff
    return df_clean, {"replacements": replacements}


def step_remove_outliers_iqr(df, columns=None, factor=1.5):
    """Remove rows with outliers using IQR method."""
    if columns is None:
        columns = df.select_dtypes(include="number").columns.tolist()
    mask = pd.Series(True, index=df.index)
    counts = {}
    for col in columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        col_outliers = ~df[col].between(lower, upper)
        counts[col] = int(col_outliers.sum())
        mask &= ~col_outliers
    n_removed = int((~mask).sum())
    return df[mask].copy(), {"rows_removed": n_removed, "outlier_counts": counts}


# ---------------------------------------------------------------------------
# Pipeline runner
# ---------------------------------------------------------------------------

def run_pipeline(df, steps):
    """Execute a preprocessing pipeline with per-step tracking.

    Args:
        df: Input DataFrame.
        steps: List of (step_name, function, kwargs) tuples.

    Returns:
        (processed_df, execution_log)
    """
    log = []
    current = df.copy()

    for step_name, func, kwargs in steps:
        n_before = len(current)
        cols_before = len(current.columns)
        t_start = time.time()

        try:
            current, info = func(current, **kwargs)
            elapsed = time.time() - t_start
            log.append({
                "step": step_name,
                "status": "success",
                "rows_in": n_before,
                "rows_out": len(current),
                "cols_in": cols_before,
                "cols_out": len(current.columns),
                "elapsed_seconds": round(elapsed, 3),
                "info": info,
            })
        except Exception as e:
            elapsed = time.time() - t_start
            log.append({
                "step": step_name,
                "status": "failed",
                "rows_in": n_before,
                "rows_out": n_before,
                "cols_in": cols_before,
                "cols_out": cols_before,
                "elapsed_seconds": round(elapsed, 3),
                "error": str(e),
                "error_type": type(e).__name__,
            })
            break  # Stop on failure

    return current, log


def generate_summary(df_input, df_output, log, input_hash, output_hash):
    """Generate a markdown summary of the pipeline execution.

    Returns:
        Markdown string.
    """
    lines = [
        "## Pipeline Execution Summary\n",
        f"**Input:** {len(df_input)} rows x {len(df_input.columns)} columns (hash: `{input_hash[:12]}...`)",
        f"**Output:** {len(df_output)} rows x {len(df_output.columns)} columns (hash: `{output_hash[:12]}...`)",
        f"**Rows removed:** {len(df_input) - len(df_output)}",
        f"**Columns removed:** {len(df_input.columns) - len(df_output.columns)}",
        "",
        "### Step Log\n",
        "| Step | Status | Rows In | Rows Out | Cols In | Cols Out | Time (s) |",
        "|------|--------|---------|----------|---------|----------|----------|",
    ]

    total_time = 0
    for entry in log:
        status = entry["status"]
        rows_out = entry.get("rows_out", "N/A")
        cols_out = entry.get("cols_out", "N/A")
        elapsed = entry.get("elapsed_seconds", 0)
        total_time += elapsed
        lines.append(
            f"| {entry['step']} | {status} | {entry['rows_in']} | "
            f"{rows_out} | {entry['cols_in']} | {cols_out} | {elapsed} |"
        )

    lines.append(f"\n**Total execution time:** {round(total_time, 3)}s")

    # Check for failures
    failures = [e for e in log if e["status"] == "failed"]
    if failures:
        lines.append("\n### Failures\n")
        for f in failures:
            lines.append(f"- **{f['step']}**: {f.get('error_type', 'Error')}: {f.get('error', 'Unknown')}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Create sample data for demonstration
    np.random.seed(42)
    n = 1000
    df = pd.DataFrame({
        "id": range(n),
        "name": [f"  User {i % 100}  " for i in range(n)],
        "age": np.random.normal(35, 15, n),
        "income": np.random.lognormal(10, 1, n),
        "status": np.random.choice(["active", "ACTIVE", "inactive", "N/A"], n),
        "signup_date": pd.date_range("2020-01-01", periods=n, freq="h").astype(str),
        "empty_col": np.nan,
    })
    # Add some duplicates
    df = pd.concat([df, df.head(50)], ignore_index=True)

    print(f"Input shape: {df.shape}")
    input_hash = compute_hash(df)

    # Define pipeline
    steps = [
        ("deduplicate", step_deduplicate, {"subset": ["id"], "keep": "first"}),
        ("replace_placeholders", step_replace_placeholders, {}),
        ("drop_constant_cols", step_drop_constant_columns, {}),
        ("drop_high_missing_cols", step_drop_high_missing_cols, {"threshold": 0.9}),
        ("normalize_strings", step_normalize_strings, {"columns": ["name", "status"]}),
        ("coerce_types", step_coerce_types, {"type_map": {"signup_date": "datetime"}}),
        ("remove_outliers", step_remove_outliers_iqr, {"columns": ["age", "income"], "factor": 3.0}),
    ]

    # Execute
    df_clean, log = run_pipeline(df, steps)
    output_hash = compute_hash(df_clean)

    # Report
    summary = generate_summary(df, df_clean, log, input_hash, output_hash)
    print(summary)

    print(f"\nOutput shape: {df_clean.shape}")
    print(f"Input hash:  {input_hash[:16]}...")
    print(f"Output hash: {output_hash[:16]}...")
