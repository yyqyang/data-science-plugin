"""
Data transformation functions for preprocessing pipelines.

Provides reusable transformations for deduplication, type coercion,
string normalization, outlier handling, and column operations.

Usage:
    python scripts/transform_data.py
"""

import re

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def deduplicate_exact(df, subset=None, keep="first"):
    """Remove exact duplicate rows.

    Args:
        subset: Columns to check. None = all columns.
        keep: 'first', 'last', or False (drop all duplicates).

    Returns:
        (cleaned_df, info_dict)
    """
    n_before = len(df)
    df_clean = df.drop_duplicates(subset=subset, keep=keep)
    return df_clean, {"duplicates_removed": n_before - len(df_clean)}


def deduplicate_by_key(df, key_cols, sort_col=None, sort_ascending=False):
    """Keep one row per business key, preferring most recent.

    Args:
        key_cols: Columns that define a unique entity.
        sort_col: Column to sort by before dedup (e.g., 'updated_at').
        sort_ascending: Sort direction for the tiebreaker.

    Returns:
        (cleaned_df, info_dict)
    """
    n_before = len(df)
    if sort_col:
        df = df.sort_values(sort_col, ascending=sort_ascending)
    df_clean = df.drop_duplicates(subset=key_cols, keep="first")
    return df_clean, {"duplicates_removed": n_before - len(df_clean)}


# ---------------------------------------------------------------------------
# Type coercion
# ---------------------------------------------------------------------------

def coerce_to_numeric(df, columns):
    """Convert string columns to numeric, setting unparseable values to NaN.

    Returns:
        (cleaned_df, info_dict)
    """
    df_clean = df.copy()
    new_nulls = {}
    for col in columns:
        if col not in df_clean.columns:
            continue
        original_nulls = int(df_clean[col].isnull().sum())
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
        created = int(df_clean[col].isnull().sum()) - original_nulls
        if created > 0:
            new_nulls[col] = created
    return df_clean, {"coerced": columns, "new_nulls_from_coercion": new_nulls}


def parse_dates(df, columns, date_format=None, utc=False):
    """Parse string columns to datetime.

    Args:
        columns: Columns to parse.
        date_format: Expected format (e.g., '%Y-%m-%d'). None = auto-detect.
        utc: Convert to UTC.

    Returns:
        (cleaned_df, info_dict)
    """
    df_clean = df.copy()
    failed = {}
    for col in columns:
        if col not in df_clean.columns:
            continue
        original_nulls = int(df_clean[col].isnull().sum())
        df_clean[col] = pd.to_datetime(
            df_clean[col], format=date_format, errors="coerce", utc=utc
        )
        created = int(df_clean[col].isnull().sum()) - original_nulls
        if created > 0:
            failed[col] = created
    return df_clean, {"parsed": columns, "failed_parses": failed}


# ---------------------------------------------------------------------------
# String cleaning
# ---------------------------------------------------------------------------

def normalize_strings(df, columns=None, case="lower"):
    """Strip whitespace and normalize case.

    Args:
        columns: String columns. None = auto-detect object columns.
        case: 'lower', 'upper', 'title', or None.

    Returns:
        (cleaned_df, info_dict)
    """
    if columns is None:
        columns = df.select_dtypes(include="object").columns.tolist()
    df_clean = df.copy()
    for col in columns:
        if col not in df_clean.columns:
            continue
        df_clean[col] = df_clean[col].str.strip()
        if case == "lower":
            df_clean[col] = df_clean[col].str.lower()
        elif case == "upper":
            df_clean[col] = df_clean[col].str.upper()
        elif case == "title":
            df_clean[col] = df_clean[col].str.title()
    return df_clean, {"normalized": columns}


def replace_placeholders(df, placeholders=None):
    """Replace common placeholder values with NaN.

    Returns:
        (cleaned_df, info_dict)
    """
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


# ---------------------------------------------------------------------------
# Outlier handling
# ---------------------------------------------------------------------------

def remove_outliers_iqr(df, columns, factor=1.5):
    """Remove rows with outliers using IQR method.

    For outlier-robust scaling (not removal), use RobustScaler
    from the scikit-learn skill.

    Returns:
        (cleaned_df, info_dict)
    """
    mask = pd.Series(True, index=df.index)
    counts = {}
    for col in columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        col_mask = df[col].between(lower, upper)
        counts[col] = int((~col_mask).sum())
        mask &= col_mask
    return df[mask].copy(), {"rows_removed": int((~mask).sum()), "per_column": counts}


def clip_outliers(df, columns, lower_pct=0.01, upper_pct=0.99):
    """Clip values to percentile bounds instead of removing rows.

    Returns:
        (cleaned_df, info_dict)
    """
    df_clean = df.copy()
    bounds = {}
    for col in columns:
        lower = float(df[col].quantile(lower_pct))
        upper = float(df[col].quantile(upper_pct))
        df_clean[col] = df_clean[col].clip(lower, upper)
        bounds[col] = {"lower": lower, "upper": upper}
    return df_clean, {"clipped": columns, "bounds": bounds}


# ---------------------------------------------------------------------------
# Column operations
# ---------------------------------------------------------------------------

def select_columns(df, keep=None, drop=None):
    """Select or drop columns.

    Returns:
        (filtered_df, info_dict)
    """
    if keep:
        return df[keep].copy(), {"kept": keep}
    elif drop:
        return df.drop(columns=drop), {"dropped": drop}
    return df.copy(), {}


def rename_columns(df, rename_map=None, convention="snake_case"):
    """Rename columns using a map or naming convention.

    Returns:
        (renamed_df, info_dict)
    """
    if rename_map:
        return df.rename(columns=rename_map), {"renamed": rename_map}

    if convention == "snake_case":
        new_names = {}
        for col in df.columns:
            new = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", str(col))
            new = re.sub(r"[^a-zA-Z0-9_]", "_", new)
            new = re.sub(r"_+", "_", new).strip("_").lower()
            if new != col:
                new_names[col] = new
        if new_names:
            return df.rename(columns=new_names), {"renamed": new_names}

    return df.copy(), {"renamed": {}}


# ---------------------------------------------------------------------------
# Structural missing data
# ---------------------------------------------------------------------------

def drop_high_missing_cols(df, threshold=0.9):
    """Drop columns with missing rate above threshold.

    Returns:
        (cleaned_df, info_dict)
    """
    rates = df.isnull().mean()
    to_drop = rates[rates > threshold].index.tolist()
    return df.drop(columns=to_drop), {
        "dropped": to_drop,
        "rates": {c: round(float(rates[c]), 4) for c in to_drop},
    }


def drop_high_missing_rows(df, threshold=0.5):
    """Drop rows with missing rate above threshold.

    Returns:
        (cleaned_df, info_dict)
    """
    row_missing = df.isnull().mean(axis=1)
    mask = row_missing <= threshold
    return df[mask].copy(), {"rows_dropped": int((~mask).sum())}


def drop_constant_columns(df):
    """Drop columns with a single unique value.

    Returns:
        (cleaned_df, info_dict)
    """
    nunique = df.nunique()
    constant = nunique[nunique <= 1].index.tolist()
    return df.drop(columns=constant), {"dropped": constant}


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Create sample data
    np.random.seed(42)
    df = pd.DataFrame({
        "CustomerID": range(100),
        "  Full Name  ": [f"  User {i}  " for i in range(100)],
        "Age": list(range(20, 80)) + [999, -5] + list(range(20, 58)),
        "Income": np.random.lognormal(10, 1, 100),
        "Status": ["active", "INACTIVE", "N/A", "active"] * 25,
        "SignupDate": ["2024-01-15"] * 50 + ["invalid_date"] * 50,
        "Empty": [np.nan] * 100,
    })

    print("Original shape:", df.shape)
    print("Columns:", list(df.columns))

    # Rename to snake_case
    df, info = rename_columns(df, convention="snake_case")
    print(f"\nRenamed: {info['renamed']}")

    # Replace placeholders
    df, info = replace_placeholders(df)
    print(f"Placeholders replaced: {info['replacements']}")

    # Normalize strings
    df, info = normalize_strings(df, case="lower")
    print(f"Normalized: {info['normalized']}")

    # Drop constant columns
    df, info = drop_constant_columns(df)
    print(f"Constant columns dropped: {info['dropped']}")

    # Remove outliers
    df, info = remove_outliers_iqr(df, columns=["age"], factor=3.0)
    print(f"Outlier rows removed: {info['rows_removed']}")

    print(f"\nFinal shape: {df.shape}")
