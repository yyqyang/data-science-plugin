"""
Data validation functions for preprocessing pipelines.

Validates DataFrames against schemas with column presence, type,
nullability, range, uniqueness, pattern, and allowed value checks.

Usage:
    python scripts/validate_data.py
"""

import re

import numpy as np
import pandas as pd


def validate_schema(df, schema, mode="strict"):
    """Validate DataFrame against a column schema.

    Args:
        df: Input DataFrame.
        schema: Dict of {column_name: {rules}}.
            Supported rules:
            - dtype: Expected type prefix ('int', 'float', 'object', 'datetime')
            - nullable: Whether NaN values are allowed (default True)
            - unique: Whether values must be unique (default False)
            - min: Minimum value (numeric or date string)
            - max: Maximum value (numeric or date string)
            - allowed_values: List of allowed values
            - pattern: Regex pattern for string columns
        mode: 'strict' raises on errors, 'permissive' returns issues as warnings.

    Returns:
        List of issue dicts with keys: column, rule, message, severity.
    """
    issues = []

    # Check for missing columns
    for col in schema:
        if col not in df.columns:
            issues.append({
                "column": col,
                "rule": "presence",
                "message": f"Required column '{col}' not found",
                "severity": "error",
            })

    # Check for unexpected columns
    expected = set(schema.keys())
    unexpected = set(df.columns) - expected
    if unexpected:
        issues.append({
            "column": ", ".join(sorted(unexpected)),
            "rule": "unexpected",
            "message": f"Unexpected columns: {sorted(unexpected)}",
            "severity": "warning",
        })

    # Validate each column
    for col, rules in schema.items():
        if col not in df.columns:
            continue

        # Type check
        if "dtype" in rules:
            expected_dtype = rules["dtype"]
            actual_dtype = df[col].dtype.name
            if expected_dtype == "datetime":
                if not pd.api.types.is_datetime64_any_dtype(df[col]):
                    issues.append({
                        "column": col,
                        "rule": "dtype",
                        "message": f"Expected datetime, got {actual_dtype}",
                        "severity": "error",
                    })
            elif not actual_dtype.startswith(expected_dtype):
                issues.append({
                    "column": col,
                    "rule": "dtype",
                    "message": f"Expected {expected_dtype}, got {actual_dtype}",
                    "severity": "error",
                })

        # Nullability check
        if not rules.get("nullable", True):
            n_null = int(df[col].isnull().sum())
            if n_null > 0:
                issues.append({
                    "column": col,
                    "rule": "nullable",
                    "message": f"{n_null} null values in non-nullable column",
                    "severity": "error",
                })

        # Uniqueness check
        if rules.get("unique", False):
            n_dupes = int(df[col].duplicated().sum())
            if n_dupes > 0:
                issues.append({
                    "column": col,
                    "rule": "unique",
                    "message": f"{n_dupes} duplicate values in unique column",
                    "severity": "error",
                })

        # Range checks
        if "min" in rules and pd.api.types.is_numeric_dtype(df[col]):
            below = int((df[col].dropna() < rules["min"]).sum())
            if below > 0:
                issues.append({
                    "column": col,
                    "rule": "min",
                    "message": f"{below} values below minimum {rules['min']}",
                    "severity": "error",
                })

        if "max" in rules and pd.api.types.is_numeric_dtype(df[col]):
            above = int((df[col].dropna() > rules["max"]).sum())
            if above > 0:
                issues.append({
                    "column": col,
                    "rule": "max",
                    "message": f"{above} values above maximum {rules['max']}",
                    "severity": "error",
                })

        # Allowed values check
        if "allowed_values" in rules:
            non_null = df[col].dropna()
            invalid = non_null[~non_null.isin(rules["allowed_values"])]
            if len(invalid) > 0:
                examples = invalid.unique()[:5].tolist()
                issues.append({
                    "column": col,
                    "rule": "allowed_values",
                    "message": f"{len(invalid)} invalid values. Examples: {examples}",
                    "severity": "error",
                })

        # Pattern check
        if "pattern" in rules and df[col].dtype == "object":
            pattern = re.compile(rules["pattern"])
            non_null = df[col].dropna()
            non_matching = non_null[~non_null.str.match(pattern)]
            if len(non_matching) > 0:
                examples = non_matching.head(3).tolist()
                issues.append({
                    "column": col,
                    "rule": "pattern",
                    "message": f"{len(non_matching)} values don't match pattern. Examples: {examples}",
                    "severity": "error",
                })

    if mode == "strict":
        errors = [i for i in issues if i["severity"] == "error"]
        if errors:
            error_msgs = [f"  - {e['column']}: {e['message']}" for e in errors]
            raise ValueError(
                f"Schema validation failed with {len(errors)} error(s):\n"
                + "\n".join(error_msgs)
            )

    return issues


def check_referential_integrity(df, fk_col, ref_df, ref_col):
    """Check that foreign key values exist in a reference DataFrame.

    Returns:
        List of orphaned values not found in the reference.
    """
    fk_values = set(df[fk_col].dropna().unique())
    ref_values = set(ref_df[ref_col].dropna().unique())
    return sorted(fk_values - ref_values)


def generate_validation_report(issues):
    """Format validation issues as a markdown report section.

    Returns:
        Markdown string.
    """
    lines = ["## Validation Results\n"]

    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]

    if not errors and not warnings:
        lines.append("All validation checks passed.\n")
        return "\n".join(lines)

    lines.append(f"**Errors:** {len(errors)} | **Warnings:** {len(warnings)}\n")

    if errors:
        lines.append("### Errors\n")
        lines.append("| Column | Rule | Message |")
        lines.append("|--------|------|---------|")
        for e in errors:
            lines.append(f"| {e['column']} | {e['rule']} | {e['message']} |")
        lines.append("")

    if warnings:
        lines.append("### Warnings\n")
        lines.append("| Column | Rule | Message |")
        lines.append("|--------|------|---------|")
        for w in warnings:
            lines.append(f"| {w['column']} | {w['rule']} | {w['message']} |")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Create sample data
    df = pd.DataFrame({
        "customer_id": [1, 2, 3, 4, 5, 5],
        "name": ["Alice", "Bob", "Charlie", None, "Eve", "Eve"],
        "age": [25, 30, -5, 45, 200, 35],
        "email": ["a@b.com", "bad-email", "c@d.com", "d@e.com", "e@f.com", "e@f.com"],
        "status": ["active", "inactive", "unknown_status", "active", "active", "inactive"],
    })

    schema = {
        "customer_id": {"dtype": "int", "nullable": False, "unique": True},
        "name": {"dtype": "object", "nullable": False},
        "age": {"dtype": "int", "nullable": False, "min": 0, "max": 150},
        "email": {"dtype": "object", "nullable": False, "pattern": r"^[^@]+@[^@]+\.[^@]+$"},
        "status": {"dtype": "object", "nullable": False, "allowed_values": ["active", "inactive"]},
    }

    print("Validating sample data (permissive mode)...\n")
    issues = validate_schema(df, schema, mode="permissive")
    report = generate_validation_report(issues)
    print(report)
