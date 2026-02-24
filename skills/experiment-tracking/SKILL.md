---
name: experiment-tracking
description: "Standard format for logging ML experiments including hypothesis, config, results, and learnings. Use when running experiments to maintain a consistent record."
---

# Experiment Tracking

Standard format for logging ML experiments. Every experiment gets a plan and a result document.

## Experiment Log Format

```markdown
## Experiment: [Short descriptive name]

**Date:** YYYY-MM-DD
**Author:** [Name]
**Status:** [planned | running | complete | abandoned]

### Hypothesis
[What you expect to happen and why]

### Configuration
- **Model:** [algorithm and key settings]
- **Features:** [feature set identifier or description]
- **Data:** [dataset version, date range, row count]
- **Data hash:** [SHA-256 of the dataset file or query fingerprint]
- **Split:** [strategy, ratios, seed]
- **Hyperparameters:** [key hyperparameters]

### Environment
- **Python:** [version]
- **Key libraries:** [e.g., sklearn 1.4.0, xgboost 2.1.0, pandas 2.2.0]
- **Hardware:** [CPU/GPU, memory]
- **Git commit:** [SHA of the code at experiment time]
- **Compute cost:** [wall time, GPU hours if applicable]

### Results
| Metric | Train | Validation | Test | Baseline |
|---|---|---|---|---|
| [primary] | | | | |
| [secondary] | | | | |

### Key Observations
- [What worked, what didn't, surprises]

### Decision
[Ship | Iterate | Abandon] -- [Reasoning]

### Next Steps
- [What to try next based on findings]

### Series
- **Parent experiment:** [link to prior experiment this builds on, if any]
- **Child experiments:** [links to follow-up experiments, if any]
```

## Required Fields

Every experiment log must include:

| Field | Why |
|---|---|
| Hypothesis | Forces clear thinking about what you expect |
| Data hash | Reproducibility -- exact data version |
| Split + seed | Reproducibility -- exact train/test split |
| Environment | Reproducibility -- library versions matter |
| Git commit | Reproducibility -- exact code version |
| Baseline comparison | Context -- improvement means nothing without a reference |
| Decision | Accountability -- forces a clear outcome |
| Series linkage | Continuity -- prevents orphaned experiment chains |

## Naming Convention

Experiment files follow this pattern:
```
docs/ds/experiments/YYYY-MM-DD-<experiment-name>-plan.md
docs/ds/experiments/YYYY-MM-DD-<experiment-name>-result.md
```

Use lowercase, hyphens, and descriptive names: `2026-02-24-churn-xgb-recency-features-plan.md`

## Environment Capture

```python
import sys
import pkg_resources
import subprocess

def capture_environment():
    """Capture current environment for experiment logging."""
    env = {
        "python": sys.version.split()[0],
        "libraries": {},
        "git_commit": subprocess.getoutput("git rev-parse HEAD").strip(),
    }
    for pkg in ['pandas', 'numpy', 'sklearn', 'xgboost', 'lightgbm', 'torch']:
        try:
            env["libraries"][pkg] = pkg_resources.get_distribution(pkg).version
        except pkg_resources.DistributionNotFound:
            pass
    return env
```

## Data Hash Capture

```python
import hashlib

def hash_file(path, algorithm='sha256'):
    """Compute hash of a data file for version tracking."""
    h = hashlib.new(algorithm)
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()
```
