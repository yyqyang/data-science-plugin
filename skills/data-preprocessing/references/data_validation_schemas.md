# Data Validation Schemas

Patterns for validating data against schemas and rules using pandas and Python standard library. No external validation frameworks required.

## Schema Definition

A schema is a Python dict describing expected column properties:

```python
schema = {
    "customer_id": {
        "dtype": "int",
        "nullable": False,
        "unique": True,
    },
    "age": {
        "dtype": "float",
        "nullable": True,
        "min": 0,
        "max": 150,
    },
    "email": {
        "dtype": "object",
        "nullable": False,
        "pattern": r"^[^@]+@[^@]+\.[^@]+$",
    },
    "status": {
        "dtype": "object",
        "nullable": False,
        "allowed_values": ["active", "inactive", "suspended"],
    },
    "created_at": {
        "dtype": "datetime",
        "nullable": False,
        "min": "2020-01-01",
        "max": "2026-12-31",
    },
}
```

## Schema Validation

### Full Schema Validator

```python
import re
import pandas as pd

def validate_schema(df, schema, mode="strict"):
    """Validate DataFrame against a schema.

    Args:
        df: Input DataFrame.
        schema: Dict of column rules.
        mode: 'strict' (all rules enforced) or 'permissive' (warnings only).

    Returns:
        List of dicts with keys: column, rule, message, severity.
    """
    issues = []

    # Check for missing required columns
    for col in schema:
        if col not in df.columns:
            issues.append({
                "column": col,
                "rule": "presence",
                "message": f"Required column '{col}' not found",
                "severity": "error",
            })

    # Check for unexpected columns (info only)
    expected = set(schema.keys())
    unexpected = set(df.columns) - expected
    if unexpected:
        issues.append({
            "column": ", ".join(sorted(unexpected)),
            "rule": "unexpected",
            "message": f"Unexpected columns found: {sorted(unexpected)}",
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
            n_null = df[col].isnull().sum()
            if n_null > 0:
                issues.append({
                    "column": col,
                    "rule": "nullable",
                    "message": f"{n_null} null values in non-nullable column",
                    "severity": "error",
                })

        # Uniqueness check
        if rules.get("unique", False):
            n_dupes = df[col].duplicated().sum()
            if n_dupes > 0:
                issues.append({
                    "column": col,
                    "rule": "unique",
                    "message": f"{n_dupes} duplicate values in unique column",
                    "severity": "error",
                })

        # Range check (numeric)
        if "min" in rules and pd.api.types.is_numeric_dtype(df[col]):
            below = (df[col] < rules["min"]).sum()
            if below > 0:
                issues.append({
                    "column": col,
                    "rule": "min",
                    "message": f"{below} values below minimum {rules['min']}",
                    "severity": "error",
                })

        if "max" in rules and pd.api.types.is_numeric_dtype(df[col]):
            above = (df[col] > rules["max"]).sum()
            if above > 0:
                issues.append({
                    "column": col,
                    "rule": "max",
                    "message": f"{above} values above maximum {rules['max']}",
                    "severity": "error",
                })

        # Allowed values check
        if "allowed_values" in rules:
            invalid = df[col].dropna()[~df[col].dropna().isin(rules["allowed_values"])]
            if len(invalid) > 0:
                examples = invalid.unique()[:5].tolist()
                issues.append({
                    "column": col,
                    "rule": "allowed_values",
                    "message": f"{len(invalid)} values not in allowed set. Examples: {examples}",
                    "severity": "error",
                })

        # Pattern check (regex)
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

    return issues
```

## Referential Integrity

Check that foreign key values exist in a reference column:

```python
def check_referential_integrity(df, fk_col, ref_df, ref_col):
    """Check that all values in fk_col exist in ref_df[ref_col].

    Returns:
        List of orphaned values not found in the reference.
    """
    fk_values = set(df[fk_col].dropna().unique())
    ref_values = set(ref_df[ref_col].dropna().unique())
    orphans = fk_values - ref_values
    return sorted(orphans)
```

## Custom Rules

Define arbitrary validation rules as functions:

```python
def validate_custom_rules(df, rules):
    """Apply custom validation rules.

    Args:
        rules: List of (rule_name, function) tuples.
            Each function takes df and returns (passed: bool, message: str).

    Returns:
        List of dicts with keys: rule, passed, message.
    """
    results = []
    for rule_name, rule_func in rules:
        passed, message = rule_func(df)
        results.append({"rule": rule_name, "passed": passed, "message": message})
    return results

# Example custom rules
custom_rules = [
    ("no_future_dates", lambda df: (
        df["created_at"].max() <= pd.Timestamp.now(),
        f"Latest date: {df['created_at'].max()}"
    )),
    ("positive_amounts", lambda df: (
        (df["amount"] >= 0).all(),
        f"Negative amounts: {(df['amount'] < 0).sum()}"
    )),
    ("email_domain_check", lambda df: (
        df["email"].str.contains("@").all(),
        f"Invalid emails: {(~df['email'].str.contains('@')).sum()}"
    )),
]
```

## Validation Report Format

Generate a structured validation report:

```python
def generate_validation_report(issues, custom_results=None):
    """Format validation results as a markdown report section.

    Returns:
        Markdown string for inclusion in preprocessing report.
    """
    lines = ["## Validation Results\n"]

    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]

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
        lines.append("")

    if custom_results:
        lines.append("### Custom Rules\n")
        lines.append("| Rule | Status | Message |")
        lines.append("|------|--------|---------|")
        for r in custom_results:
            status = "PASS" if r["passed"] else "FAIL"
            lines.append(f"| {r['rule']} | {status} | {r['message']} |")

    return "\n".join(lines)
```
