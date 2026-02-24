---
title: "Build Data Science Claude Code Plugin"
type: feat
date: 2026-02-24
status: pending
---

# Build Data Science Claude Code Plugin

## Enhancement Summary

**Deepened on:** 2026-02-24
**Sections enhanced:** 12
**Research agents used:** create-agent-skills, compound-docs, architecture-patterns, DS experiment tracking researcher, Claude Code plugin format docs, writing-clearly, architecture-strategist, code-simplicity-reviewer, pattern-recognition-specialist, learnings-from-plugin-versioning

### Key Improvements

1. **Plugin naming fix (CRITICAL):** Plugin name must be `"ds"` in plugin.json (not `"data-science"`). The `name` field becomes the namespace prefix — Claude Code injects the colon automatically, so `"ds"` → `/ds:plan`. Command files must NOT contain colons in their `name:` frontmatter.
2. **Command file paths fix (CRITICAL):** Commands must use subdirectory pattern `commands/ds/plan.md` (not `commands/ds-plan.md`). This follows the compound-engineering convention for namespaced commands.
3. **`$ARGUMENTS` syntax fix (CRITICAL):** The official placeholder is `$ARGUMENTS` (not `#$ARGUMENTS`). All command bodies updated.
4. **Agent `<examples>` blocks (CRITICAL):** All agents must include `<examples>` blocks with concrete invocation scenarios — mandatory for Claude Code agent routing.
5. **`disable-model-invocation: true` (CRITICAL):** All 6 commands and 2 skills (`model-card`, `dataset-card`) must include this frontmatter field — they produce file-writing side effects.
6. **Output directory consolidation:** Consolidate 7 scattered output directories (`docs/plans/`, `docs/eda/`, `docs/ds/experiments/`, `docs/reviews/`, `docs/deployments/`, `docs/ds/learnings/`, `model/`) into `docs/ds/` with subdirectories.
7. **Experiment tracking enhancements:** Add environment/library versions, data version/hash, git commit SHA, compute cost fields per MLflow/W&B standards.
8. **Model card enhancements:** Add Environmental Impact, Explainability, How to Get Started sections per HuggingFace and NVIDIA Model Card++ standards.
9. **Google ML Test Score alignment:** Model review checklist reorganized into 4 categories (Data Tests, Model Tests, Infrastructure Tests, Monitoring Tests) per Google's 28-test framework.
10. **Compounding mechanism hardened:** Added `findings` array, `mechanism` enum, `impact` enum, `lifecycle_stage` field, bidirectional cross-references, and deduplication gate.
11. **Writing clarity:** All agent and command descriptions rewritten for active voice, concrete language, and imperative form per Strunk's rules.
12. **Simplicity option documented:** Code-simplicity-reviewer identified a minimal MVP path (4 agents, 6 skills, 4 templates = 14 files vs 38) as an alternative for teams wanting to start smaller.

### New Considerations Discovered

- Plugin `name` field is the namespace mechanism — no colons in component names
- `model: inherit` IS valid per official Claude Code docs (confirmed)
- `preconditions` is NOT an official frontmatter field — remove from any command
- Skills encode methodology (how to think); templates encode form (what to fill in) — distinct purposes, no duplication
- Two-phase orchestration recommended for `/ds:review`: agents return text only, command orchestrator writes the consolidated file
- Per-project configuration via `.ds-config.yaml` enables cross-project learning aggregation
- Experiment series tracking (linking related experiments) prevents orphaned experiment chains

---

## Overview

Create a Claude Code plugin (`data-science`) that brings the compound engineering philosophy to data science and ML workflows. The plugin provides 9 agents, 6 commands, 11 skills, and 8 reusable templates that help DS/ML teams work in a structured, compounding way — where each project leaves behind artifacts (experiment logs, feature notes, evaluation checklists, postmortems) that make future projects faster and better.

**Workflow:** `Frame → Explore → Experiment → Review → Ship → Compound → Repeat`

**Namespace:** `/ds:` — short, memorable, no collision with Claude Code built-ins.

## Problem Statement

Data science teams face compounding problems that software engineering tools don't address:

- **Experiment drift** — Teams repeat failed experiments because nobody documented what was tried
- **Invisible assumptions** — Data splits, feature transformations, and evaluation metrics are chosen ad-hoc without review
- **Lost institutional knowledge** — Learnings about data quirks, model behaviors, and domain constraints live in individual notebooks
- **Reproducibility gaps** — Work that "ran on my machine" can't be recreated by teammates
- **No review culture** — Unlike code PRs, model decisions rarely get structured peer review

## Proposed Solution

A Claude Code plugin with 6 workflow commands that mirror the data science lifecycle, 9 specialized agents for deep-dive tasks, 11 skills encoding DS best practices, and a compounding mechanism (`docs/ds/learnings/`) that surfaces past experiment insights before new work begins.

---

## SpecFlow Analysis — Key Revisions

The following critical gaps were identified during flow analysis and incorporated into the plan:

### Wiring Fixes (all agents and skills now have invocation paths)

| Component | Now Invoked By |
|---|---|
| `feature-engineer` agent | `/ds:eda` (step 5b: after distribution analysis, suggest feature transformations) |
| `model-evaluator` agent | `/ds:experiment` (step 7: when generating result report) |
| `imbalanced-classification` skill | `/ds:eda` (step 5: auto-surfaced when target imbalance >5:1) |
| `time-series-validation` skill | `/ds:experiment` (step 3: auto-invoked when temporal data detected by split-strategy) |
| `feature-importance` skill | `/ds:experiment` (step 7: invoked alongside model-evaluator) |
| `statistical-tests` skill | `/ds:experiment` (step 3: invoked in comparison protocol design) |
| `target-leakage-detection` skill | `/ds:eda` (step 5a: invoked when target column is identified) AND `/ds:experiment` |

### Learnings Search (all 6 commands now surface learnings)

| Command | Searches Learnings For |
|---|---|
| `/ds:plan` | All categories matching the problem description |
| `/ds:eda` | `category: data` learnings |
| `/ds:experiment` | `category: modeling` and `category: features` learnings |
| `/ds:review` | `category: evaluation` learnings |
| `/ds:ship` | `category: deployment` learnings |
| `/ds:compound` | Existing learnings to avoid duplicates |

Search includes relevance ranking: (a) tag overlap count, (b) recency weighting, (c) outcome filtering, (d) capped at 5 results.

### Phase Adjustments

- `/ds:eda` moved to MVP (Phase 1) — it is the most common DS entry point
- `reproducibility-auditor` moved to Phase 2 — required by `/ds:review` which is Phase 2
- `data-profiler` moved to MVP (Phase 1) — required by `/ds:eda`

### Revised MVP: `/ds:plan` + `/ds:eda` + `/ds:experiment` + `/ds:compound` (4 commands, 6 agents)

> `feature-engineer` moved to MVP — it is invoked by `/ds:eda` step 5b and cannot be deferred.

### Edge Case Handling Added

- **Cold start**: All commands run `mkdir -p docs/ds/learnings/` before searching. Zero-results message: "No prior learnings found for this topic. Starting fresh."
- **Large datasets**: `/ds:eda` samples at 100K rows if dataset exceeds 100MB. Reports sample size.
- **Failed experiments**: `/ds:experiment` generates a failure report when execution fails, using a failure analysis section of the result template.
- **Filename collisions**: Learning filenames use `YYYY-MM-DD-HHMMSS-<topic>.md` with timestamp precision.

### Compounding Mechanism Hardening

- YAML frontmatter schema validation added to `/ds:compound` with enum enforcement for `category` (modeling, data, features, evaluation, deployment, infrastructure, process) and `outcome` (success, failure, mixed)
- `status` field added to learnings: `active` (default), `superseded`, `deprecated`
- Search filters to `status: active` by default
- `/ds:compound --update <path>` flag for updating existing learnings

### Convention Compliance

- All commands include `$ARGUMENTS` placeholder for argument passing (official syntax — no `#` prefix)
- All commands include `disable-model-invocation: true` in frontmatter (they produce file-writing side effects)
- All agents include `<examples>` blocks with concrete invocation scenarios (mandatory for Claude Code agent routing)
- `model-card` and `dataset-card` skills include `disable-model-invocation: true` (they generate deployment artifacts)
- `CLAUDE.md` content drafted below with versioning, compliance, and naming conventions

---

## A) Plugin Architecture

```
data-science-plugin/
├── .claude-plugin/
│   └── plugin.json                          # Plugin metadata
├── agents/
│   ├── analysis/                            # Data understanding agents
│   │   ├── problem-framer.md                # Frame business problems as DS problems
│   │   ├── data-profiler.md                 # Profile datasets for quality and structure
│   │   └── feature-engineer.md              # Design and evaluate feature transformations
│   ├── modeling/                            # Model-focused agents
│   │   ├── experiment-designer.md           # Design rigorous experiments
│   │   ├── model-evaluator.md              # Evaluate model performance with rigor
│   │   └── error-analyst.md                # Slice errors to find failure modes
│   └── review/                             # Quality and governance agents
│       ├── ds-reviewer.md                  # Review DS work like a senior data scientist
│       ├── reproducibility-auditor.md      # Audit reproducibility of experiments
│       └── documentation-synthesizer.md    # Synthesize learnings into reusable docs
├── commands/
│   └── ds/                                 # Subdirectory pattern for namespaced commands
│       ├── plan.md                         # /ds:plan — Frame problem and plan approach
│       ├── eda.md                          # /ds:eda — Guided exploratory data analysis
│       ├── experiment.md                   # /ds:experiment — Design and run experiments
│       ├── review.md                       # /ds:review — Multi-agent DS review
│       ├── ship.md                         # /ds:ship — Package model for deployment
│       └── compound.md                     # /ds:compound — Capture learnings
├── skills/
│   ├── eda-checklist/
│   │   └── SKILL.md                        # Structured EDA methodology
│   ├── target-leakage-detection/
│   │   └── SKILL.md                        # Detect target leakage in features
│   ├── split-strategy/
│   │   └── SKILL.md                        # Train/validation/test split patterns
│   ├── imbalanced-classification/
│   │   └── SKILL.md                        # Handle class imbalance
│   ├── time-series-validation/
│   │   └── SKILL.md                        # Time-aware cross-validation
│   ├── feature-importance/
│   │   └── SKILL.md                        # Feature importance analysis methods
│   ├── error-slicing/
│   │   └── SKILL.md                        # Systematic error analysis
│   ├── experiment-tracking/
│   │   └── SKILL.md                        # Experiment logging format
│   ├── model-card/
│   │   └── SKILL.md                        # Model card template (Google standard)
│   ├── dataset-card/
│   │   └── SKILL.md                        # Dataset documentation template
│   └── statistical-tests/
│       └── SKILL.md                        # Statistical test selection guide
├── templates/                              # Reusable artifact templates
│   ├── problem-framing.md                  # Problem definition document
│   ├── dataset-assessment.md               # Dataset quality assessment
│   ├── experiment-plan.md                  # Experiment design document
│   ├── experiment-result.md                # Experiment result report
│   ├── error-analysis.md                   # Error analysis report
│   ├── model-review-checklist.md           # Model review checklist
│   ├── model-card.md                       # Model card for deployment
│   └── postmortem.md                       # Project learnings/postmortem
├── CLAUDE.md                               # Plugin development guidelines
├── README.md                               # Plugin documentation
└── CHANGELOG.md                            # Version history
```

### Compounding Mechanism

The plugin creates a `docs/ds/` directory tree in the user's project (not inside the plugin). All plugin output is consolidated under this single root to avoid scattered directories.

```
[user-project]/
├── docs/
│   └── ds/                                 # All plugin output consolidated here
│       ├── plans/                          # Created by /ds:plan
│       │   └── 2026-02-24-churn-prediction-plan.md
│       ├── eda/                            # Created by /ds:eda
│       │   └── 2026-02-24-customers-eda.md
│       ├── experiments/                    # Created by /ds:experiment
│       │   ├── 2026-02-24-churn-xgb-plan.md
│       │   └── 2026-02-24-churn-xgb-result.md
│       ├── reviews/                        # Created by /ds:review
│       │   └── 2026-02-24-churn-model-review.md
│       ├── deployments/                    # Created by /ds:ship
│       │   └── 2026-02-24-churn-xgb-ship.md
│       └── learnings/                      # Created by /ds:compound
│           ├── 2026-02-24-churn-feature-engineering.md
│           ├── 2026-02-20-time-series-split-gotcha.md
│           └── 2026-02-15-xgboost-hyperparameter-ranges.md
```

> **Research Insight — Output Directory Consolidation:** The architecture-strategist identified 7 scattered directories as a maintenance burden. Consolidating under `docs/ds/` makes it easy to `.gitignore`, find all plugin artifacts, and prevents namespace collisions with other tools. All command output paths updated to use `docs/ds/<type>/` pattern.

Learnings frontmatter (enhanced with research findings):
```yaml
---
title: "XGBoost hyperparameter ranges for tabular classification"
category: modeling          # modeling | data | features | evaluation | deployment | infrastructure | process
tags: [xgboost, hyperparameters, classification, tabular]
created: 2026-02-15
project: churn-prediction
outcome: success            # success | failure | mixed
status: active              # active | superseded | deprecated
findings:                   # Structured findings array for machine-searchable learnings
  - insight: "learning_rate 0.01-0.1 with more trees outperforms 0.3 default"
    mechanism: hyperparameter_tuning
    impact: high
lifecycle_stage: experiment  # framing | eda | experiment | review | deployment
supersedes: ""              # Path to learning this replaces (if any)
related:                    # Bidirectional cross-references
  - docs/ds/experiments/2026-02-15-churn-xgb-result.md
---
```

> **Research Insight — Compounding Schema:** The compound-docs skill identified that flat learnings degrade search quality as the knowledge base grows. The `findings` array enables structured search (grep by `mechanism:` or `impact:`). The `lifecycle_stage` field enables stage-specific surfacing (e.g., `/ds:eda` only searches `lifecycle_stage: eda` learnings). The `supersedes` chain prevents stale knowledge from accumulating. A deduplication gate in `/ds:compound` greps existing learnings for matching tags before writing, presenting any matches to the user with "Update existing or create new?" prompt.

---

## B) File/Folder Scaffold

### Files to Create

| File | Purpose |
|------|---------|
| `.claude-plugin/plugin.json` | Plugin metadata (9 agents, 6 commands, 11 skills) |
| `agents/analysis/problem-framer.md` | Frame business problems as DS problems |
| `agents/analysis/data-profiler.md` | Profile datasets for quality and structure |
| `agents/analysis/feature-engineer.md` | Design feature transformations |
| `agents/modeling/experiment-designer.md` | Design rigorous experiments |
| `agents/modeling/model-evaluator.md` | Evaluate model performance |
| `agents/modeling/error-analyst.md` | Slice errors to find failure modes |
| `agents/review/ds-reviewer.md` | Senior DS peer review |
| `agents/review/reproducibility-auditor.md` | Audit experiment reproducibility |
| `agents/review/documentation-synthesizer.md` | Synthesize learnings into docs |
| `commands/ds/plan.md` | `/ds:plan` — Problem framing and approach planning |
| `commands/ds/eda.md` | `/ds:eda` — Guided exploratory data analysis |
| `commands/ds/experiment.md` | `/ds:experiment` — Experiment design and execution |
| `commands/ds/review.md` | `/ds:review` — Multi-agent DS review |
| `commands/ds/ship.md` | `/ds:ship` — Package model for deployment |
| `commands/ds/compound.md` | `/ds:compound` — Capture learnings |
| `skills/eda-checklist/SKILL.md` | Structured EDA methodology |
| `skills/target-leakage-detection/SKILL.md` | Detect target leakage |
| `skills/split-strategy/SKILL.md` | Train/val/test split patterns |
| `skills/imbalanced-classification/SKILL.md` | Handle class imbalance |
| `skills/time-series-validation/SKILL.md` | Time-aware validation |
| `skills/feature-importance/SKILL.md` | Feature importance methods |
| `skills/error-slicing/SKILL.md` | Systematic error analysis |
| `skills/experiment-tracking/SKILL.md` | Experiment logging format |
| `skills/model-card/SKILL.md` | Model card template |
| `skills/dataset-card/SKILL.md` | Dataset documentation |
| `skills/statistical-tests/SKILL.md` | Statistical test selection |
| `templates/problem-framing.md` | Problem definition template |
| `templates/dataset-assessment.md` | Dataset quality template |
| `templates/experiment-plan.md` | Experiment design template |
| `templates/experiment-result.md` | Experiment result template |
| `templates/error-analysis.md` | Error analysis template |
| `templates/model-review-checklist.md` | Model review template |
| `templates/model-card.md` | Model card template |
| `templates/postmortem.md` | Project learnings template |
| `CLAUDE.md` | Plugin development guidelines |
| `README.md` | Plugin documentation |
| `CHANGELOG.md` | Version history |

**Total: 38 files** (9 agents + 6 commands + 11 skills + 8 templates + 4 meta files)

> **Research Insight — Simplicity Alternative:** The code-simplicity-reviewer identified a minimal MVP path for teams wanting to start smaller: 4 agents (problem-framer, data-profiler, experiment-designer, documentation-synthesizer), 6 skills (eda-checklist, split-strategy, target-leakage-detection, experiment-tracking, model-card, statistical-tests), 4 templates (problem-framing, experiment-plan, experiment-result, postmortem) = **14 files** total. This cuts scope by 63% while preserving the core Frame → Experiment → Compound loop. The full 38-file scaffold is recommended for teams with established DS practices; the 14-file version suits teams adopting structured DS workflows for the first time.

---

## C) Draft Content for All Components

### plugin.json

```json
{
  "name": "ds",
  "version": "1.0.0",
  "description": "Data science and ML workflow tools. 9 agents, 6 commands, 11 skills for problem framing, EDA, experimentation, model review, and knowledge compounding.",
  "author": {
    "name": "Andika Rachman",
    "url": "https://github.com/andikarachman"
  },
  "license": "MIT",
  "keywords": [
    "data-science",
    "machine-learning",
    "eda",
    "experiment-tracking",
    "model-evaluation",
    "feature-engineering",
    "reproducibility",
    "compound-engineering"
  ],
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp"
    }
  }
}
```

> **Research Insight — Plugin Naming:** The `name` field in plugin.json is the namespace mechanism. Claude Code automatically injects a colon between the plugin name and the command name. So `"name": "ds"` + command file `commands/ds/plan.md` with `name: plan` → user invokes `/ds:plan`. The command's `name:` frontmatter must NOT contain colons — the colon is injected by the system. Confirmed via official Claude Code plugin docs.

---

### Commands

#### `/ds:plan` — Frame Problem and Plan Approach

```yaml
---
name: plan
description: Frame a data science problem and plan the approach, surfacing relevant past learnings
argument-hint: "[problem description or business question]"
disable-model-invocation: true
---
```

**Workflow:**

1. **Search past learnings** — Grep `docs/ds/learnings/*.md` for related tags/categories. Summarize any relevant findings ("Found 3 prior learnings related to churn prediction...").
2. **Problem framing** — Use the `problem-framer` agent to structure the business question as a DS problem:
   - What is being predicted/estimated/classified?
   - What actions will be taken based on the output?
   - What does success look like (metric + threshold)?
   - What data is available?
   - What are the known constraints (latency, fairness, interpretability)?
3. **Approach selection** — Propose 2-3 candidate approaches (e.g., "logistic regression baseline → gradient boosting → neural net") with trade-offs.
4. **Write artifact** — Generate a `docs/ds/plans/YYYY-MM-DD-<name>-plan.md` using the `templates/problem-framing.md` template.
5. **Next steps** — Ask user: "Plan ready. What next?" with options: Start EDA (`/ds:eda`), Refine plan, Start experiment (`/ds:experiment`).

**Inputs:** Business question or problem description.
**Outputs:** Problem framing document in `docs/ds/plans/`.

---

#### `/ds:eda` — Guided Exploratory Data Analysis

```yaml
---
name: eda
description: Profile a dataset for structure, quality, distributions, and anomalies, then output an EDA report
argument-hint: "[path to dataset or description of data source]"
disable-model-invocation: true
---
```

**Workflow:**

1. **Load data** — Read the dataset (CSV, Parquet, or database query). If path not provided, ask.
2. **Structural profiling** — Use the `data-profiler` agent:
   - Row/column counts, dtypes, memory usage
   - Missing value rates per column
   - Cardinality of categorical columns
   - Numeric summary statistics (mean, median, std, min, max, percentiles)
3. **Distribution analysis** — For each feature:
   - Numeric: distribution shape, outliers (IQR method), skewness
   - Categorical: value counts, rare categories
   - Temporal: time range, gaps, seasonality signals
4. **Relationship analysis** — Correlation matrix for numeric features, association tests for categoricals, target correlation ranking.
5. **Data quality flags** — Apply the `eda-checklist` skill. Flag: duplicates, constant columns, high-cardinality categoricals, suspicious distributions, potential leakage columns.
6. **Write artifact** — Generate a `docs/ds/eda/YYYY-MM-DD-<dataset-name>-eda.md` report with findings, visualizations described, and recommended next steps.
7. **Next steps** — Ask: "EDA complete. What next?" with options: Feature engineering, Run experiment (`/ds:experiment`), Investigate specific finding.

**Inputs:** Dataset path or data source description.
**Outputs:** EDA report in `docs/ds/eda/`.

---

#### `/ds:experiment` — Design and Run Experiments

```yaml
---
name: experiment
description: Design an ML experiment with hypothesis, split strategy, leakage check, and evaluation plan
argument-hint: "[experiment description or hypothesis]"
disable-model-invocation: true
---
```

**Workflow:**

1. **Search past experiments** — Grep `docs/ds/learnings/*.md` and `docs/ds/experiments/` for related work. Surface what was tried before and what worked/failed.
2. **Hypothesis formulation** — Use the `experiment-designer` agent:
   - Null hypothesis and alternative hypothesis
   - Independent variable (what's being changed)
   - Dependent variable (what's being measured)
   - Controls (what's held constant)
3. **Methodology design** — Define:
   - Data split strategy (invoke `split-strategy` skill)
   - Feature set (reference any feature engineering from prior EDA)
   - Model(s) to evaluate
   - Hyperparameter search strategy (grid, random, Bayesian)
   - Evaluation metrics (primary + secondary)
   - Baseline to beat
4. **Leakage check** — Invoke `target-leakage-detection` skill on the proposed feature set.
5. **Write experiment plan** — Generate `docs/ds/experiments/YYYY-MM-DD-<experiment-name>-plan.md` from `templates/experiment-plan.md`.
6. **Execute or defer** — Ask: "Experiment plan ready. What next?" with options:
   - Write experiment code scaffold
   - Just save the plan (implement later)
   - Review plan with `/ds:review`
7. **If executing** — After completion, generate `docs/ds/experiments/YYYY-MM-DD-<experiment-name>-result.md` from `templates/experiment-result.md` with actual metrics, comparisons to baseline, and key observations.

**Inputs:** Hypothesis or experiment description.
**Outputs:** Experiment plan and (optionally) result report in `docs/ds/experiments/`.

---

#### `/ds:review` — Multi-Agent DS Review

```yaml
---
name: review
description: Run parallel review agents on DS work and consolidate findings into a single report
argument-hint: "[path to notebook, script, or experiment report to review]"
disable-model-invocation: true
---
```

**Workflow (two-phase orchestration):**

> **Research Insight — Two-Phase Orchestration:** The architecture-strategist recommends that review agents return text only (no file writes). The `/ds:review` command orchestrator collects all agent outputs, deduplicates findings, and writes the single consolidated review file. This prevents race conditions and ensures consistent formatting.

1. **Read the artifact** — Load the notebook, script, or experiment report.
2. **Search learnings** — Grep `docs/ds/learnings/*.md` for `category: evaluation` learnings. Surface relevant prior review findings.
3. **Parallel agent reviews (text-only)** — Launch 3 agents in parallel. Each returns structured text, no file writes:
   - `ds-reviewer` — Overall methodology, statistical rigor, conclusion validity
   - `reproducibility-auditor` — Random seeds, data versioning, environment specs, hardcoded paths
   - `error-analyst` — Error patterns, failure modes, edge cases not covered
4. **Consolidate findings** — Orchestrator merges agent outputs, deduplicates overlapping findings, and categorizes:
   - **CRITICAL** — Must fix before trusting results
   - **RECOMMENDATION** — Should fix to improve quality
   - **OBSERVATION** — Minor improvement or style point
   - **STRENGTH** — Highlight what was done well
5. **Apply checklists** — Run `model-review-checklist` template against the work.
6. **Write review** — Orchestrator writes the consolidated review to `docs/ds/reviews/YYYY-MM-DD-<name>-review.md`.
7. **Next steps** — Ask: "Review complete. What next?" with options: Address findings, Ship (`/ds:ship`), Capture learnings (`/ds:compound`).

**Inputs:** Path to notebook, script, or report.
**Outputs:** Structured review report in `docs/ds/reviews/`.

---

#### `/ds:ship` — Package Model for Deployment

```yaml
---
name: ship
description: Package a trained model with model card, dataset card, and deployment artifacts
argument-hint: "[path to model or training script]"
disable-model-invocation: true
---
```

**Workflow:**

1. **Pre-ship checklist** — Verify:
   - [ ] Model artifact exists and is loadable
   - [ ] Evaluation metrics documented
   - [ ] Train/test performance gap acceptable
   - [ ] No data leakage flags from review
   - [ ] Feature list finalized
   - [ ] Input schema documented
   - [ ] Inference latency measured (if applicable)
2. **Generate model card** — Use `model-card` skill and `templates/model-card.md`:
   - Model type, version, training date
   - Intended use and limitations
   - Training data description
   - Evaluation results (overall + per-slice)
   - Ethical considerations
   - Caveats and recommendations
3. **Generate dataset card** — Use `dataset-card` skill and `templates/dataset-assessment.md` for training data documentation.
4. **Package artifacts** — Create or verify:
   - `model/` directory with serialized model
   - `model/requirements.txt` or `model/environment.yml`
   - `model/predict.py` (inference entrypoint)
   - `model/MODEL_CARD.md`
5. **Write ship log** — Append to `docs/ds/deployments/YYYY-MM-DD-<model-name>-ship.md`.
6. **Next steps** — Ask: "Ship artifacts ready. What next?" with options: Deploy, Capture learnings (`/ds:compound`), Run monitoring setup.

**Inputs:** Path to model or training script.
**Outputs:** Model card, dataset card, packaging artifacts, ship log.

---

#### `/ds:compound` — Capture Learnings

```yaml
---
name: compound
description: Extract and categorize learnings from completed experiments into docs/learnings/ for future retrieval
argument-hint: "[description of what was learned, or path to experiment report]"
disable-model-invocation: true
---
```

**Workflow:**

1. **Gather context** — Read recent experiment reports, reviews, and any referenced artifacts.
2. **Extract learnings** — Use the `documentation-synthesizer` agent to identify:
   - What worked and why
   - What failed and why
   - Surprising findings
   - Reusable patterns (feature transformations, evaluation recipes, hyperparameter ranges)
   - Gotchas and domain-specific caveats
3. **Categorize** — Classify each learning:
   - `modeling` — Model selection, hyperparameters, architecture
   - `data` — Data quality, preprocessing, collection
   - `features` — Feature engineering, selection, transformation
   - `evaluation` — Metrics, validation, error analysis
   - `deployment` — Serving, monitoring, latency
4. **Write learning** — Create `docs/ds/learnings/YYYY-MM-DD-<topic>.md` with YAML frontmatter:
   ```yaml
   ---
   title: "Descriptive title of the learning"
   category: modeling
   tags: [relevant, tags, here]
   created: 2026-02-24
   project: project-name
   outcome: success
   ---
   ```
5. **Cross-reference** — Link to the experiment report, review, or notebook that produced this learning.
6. **Verify retrieval** — Search `docs/ds/learnings/` to confirm the new learning would surface for related future queries.
7. **Summary** — Display what was captured and where it was saved.

**Inputs:** Description of learnings or path to experiment report.
**Outputs:** Learning document in `docs/ds/learnings/`.

---

### Agents

> **Research Insight — Agent `<examples>` Blocks (MANDATORY):** Every agent MUST include an `<examples>` block at the end of its markdown body. This is how Claude Code routes tasks to the correct agent. Without examples, the agent may never be invoked. Each example should follow this format:
>
> ```xml
> <examples>
>   <example>
>     <context>User is starting a new churn prediction project</context>
>     <user>Frame the churn prediction problem for our SaaS product</user>
>     <assistant>I'll structure this as a binary classification problem...</assistant>
>     <commentary>Activated because user needs to translate a business question into a DS formulation</commentary>
>   </example>
> </examples>
> ```
>
> Include 2-3 examples per agent covering its primary use cases. The `<context>` tag provides situational context, `<user>` shows the trigger message, `<assistant>` shows a brief response, and `<commentary>` explains why this agent was chosen.

#### 1. problem-framer (analysis/)

```yaml
---
name: problem-framer
description: "Translate business questions into DS problems with target variables, metrics, and constraints. Use when starting a project or when the objective needs sharpening."
model: inherit
---
```

You are Problem Framer, a senior data scientist who specializes in translating business questions into well-defined data science problems.

**Your approach:**

1. **Clarify the business objective** — What decision will this model/analysis inform? Who is the stakeholder? What action will they take?
2. **Define the DS formulation** — Is this classification, regression, ranking, clustering, causal inference, or descriptive analytics? What is the target variable?
3. **Specify success criteria** — What metric matters most? What threshold makes this useful? Is there a baseline to beat (e.g., current heuristic, human performance)?
4. **Identify constraints** — Latency requirements, fairness constraints, interpretability needs, data availability, labeling cost, regulatory requirements.
5. **Map data to problem** — What features are available? What's the observation unit (row)? What's the time horizon for prediction? Is there temporal ordering?
6. **Flag risks** — Label noise, distribution shift, selection bias, survivorship bias, concept drift.

**Output format:**

```markdown
## Problem Framing

### Business Objective
[What business question are we answering?]

### DS Formulation
- **Type:** [classification | regression | ranking | clustering | causal | descriptive]
- **Target:** [What we're predicting/estimating]
- **Observation unit:** [What each row represents]
- **Prediction horizon:** [How far ahead, if applicable]

### Success Criteria
- **Primary metric:** [metric] >= [threshold]
- **Secondary metrics:** [list]
- **Baseline:** [current performance or heuristic]

### Constraints
[Latency, fairness, interpretability, data, regulatory]

### Data Landscape
[Available data sources, join keys, temporal range, known quality issues]

### Risks
[Key risks and proposed mitigations]
```

---

#### 2. data-profiler (analysis/)

```yaml
---
name: data-profiler
description: "Profile datasets: missing rates, distributions, outliers, type issues. Use after loading data to characterize it before modeling."
model: inherit
---
```

You are Data Profiler, a data quality specialist who systematically characterizes datasets.

**Your approach:**

1. **Structural overview** — Shape, dtypes, memory usage, index structure.
2. **Missing data analysis** — Missing rates per column, missing patterns (MCAR/MAR/MNAR assessment), columns with >50% missing.
3. **Numeric profiling** — For each numeric column: mean, median, std, min, max, p5/p25/p75/p95, skewness, kurtosis, zero rate, negative rate.
4. **Categorical profiling** — For each categorical column: cardinality, top-N values with counts, rare category count (<1% frequency).
5. **Temporal profiling** — For datetime columns: range, gaps, frequency regularity, timezone.
6. **Anomaly flags** — Constant columns, columns that look like IDs, suspicious value ranges, duplicate rows, mixed-type columns.
7. **Target analysis** (if identified) — Distribution, class balance, relationship with top features.

Generate code using pandas for profiling. Report findings in a structured markdown table format. Flag anything that needs investigation with a warning marker.

---

#### 3. feature-engineer (analysis/)

```yaml
---
name: feature-engineer
description: "Generate candidate features, check for leakage, and produce a feature registry. Use when building or evaluating feature sets."
model: inherit
---
```

You are Feature Engineer, a specialist in creating predictive features from raw data.

**Your approach:**

1. **Understand the target** — What are we predicting? What features are available? What's the observation grain?
2. **Generate candidates** — For each raw feature, propose transformations:
   - Numeric: binning, log/sqrt transforms, polynomial interactions, rolling statistics, lag features
   - Categorical: target encoding, frequency encoding, one-hot (for low cardinality), embeddings (for high cardinality)
   - Temporal: day-of-week, hour, recency, time-since-event, cyclical encoding
   - Text: TF-IDF, word counts, sentiment, entity extraction
   - Cross-features: ratios, differences, interactions between semantically related columns
3. **Check for leakage** — For each proposed feature, verify it would be available at prediction time. Flag any feature that uses future information.
4. **Evaluate importance** — Suggest a feature importance analysis plan (permutation importance, SHAP, or correlation-based).
5. **Document** — Produce a feature registry table:

```markdown
| Feature Name | Source Columns | Transformation | Leakage Risk | Rationale |
|---|---|---|---|---|
```

---

#### 4. experiment-designer (modeling/)

```yaml
---
name: experiment-designer
description: "Define hypothesis, variables, split strategy, baselines, and comparison protocol. Use before running an experiment to lock down methodology."
model: inherit
---
```

You are Experiment Designer, a methodologist who ensures ML experiments are rigorous and reproducible.

**Your approach:**

1. **Hypothesis** — State what you expect to happen and why. Null vs. alternative hypothesis.
2. **Variables** — Independent (what changes), dependent (what's measured), controlled (what's held constant).
3. **Data split** — Define train/validation/test strategy. If time-series, use temporal splits. If grouped data, use group-aware splits. Specify random seed.
4. **Baselines** — Define at least one baseline: random, majority class, simple heuristic, or previous best model.
5. **Metrics** — Primary metric (the one that decides the winner) and secondary metrics (for monitoring). Justify the choice.
6. **Comparison protocol** — How to determine if a result is "better": statistical significance test, confidence intervals, or practical significance threshold.
7. **Resource budget** — Expected training time, compute cost, number of hyperparameter trials.
8. **Reproducibility checklist** — Random seed, library versions, data snapshot, environment specification.

---

#### 5. model-evaluator (modeling/)

```yaml
---
name: model-evaluator
description: "Compute metrics, slice by subgroups, check calibration, and flag fairness gaps. Use after training to decide ship/iterate/abandon."
model: inherit
---
```

You are Model Evaluator, a specialist in rigorous model assessment.

**Your approach:**

1. **Overall metrics** — Compute primary and secondary metrics on the held-out test set. Report with confidence intervals (bootstrap).
2. **Comparison to baseline** — Show improvement over baseline in absolute and relative terms.
3. **Slice analysis** — Evaluate performance across meaningful subgroups (demographics, segments, time periods, edge cases). Flag slices where performance degrades >10% vs. overall.
4. **Calibration** — For probabilistic models: reliability diagram, expected calibration error (ECE), Brier score.
5. **Error analysis** — Confusion matrix (classification) or residual analysis (regression). Identify systematic failure patterns.
6. **Fairness** — If relevant, check for disparate impact across protected groups. Report ratio metrics.
7. **Robustness** — Sensitivity to feature perturbation, performance across time periods, train/test gap analysis.
8. **Recommendation** — Ship, iterate, or abandon, with clear reasoning.

---

#### 6. error-analyst (modeling/)

```yaml
---
name: error-analyst
description: "Slice errors by feature, confidence, and subgroup to find failure patterns and root causes. Use after evaluation to prioritize fixes."
model: inherit
---
```

You are Error Analyst, a specialist in understanding why models fail.

**Your approach:**

1. **Categorize errors** — Separate errors by type (false positives, false negatives, large residuals, confident-but-wrong).
2. **Slice by features** — For each categorical feature, compute error rate per group. For numeric features, bin and compute error rate per bin. Identify over-represented slices in the error set.
3. **Find patterns** — Look for systematic failure modes:
   - Does the model fail on rare categories?
   - Does performance degrade at distribution tails?
   - Are there temporal patterns in errors?
   - Do certain feature combinations predict failure?
4. **Sample analysis** — Pick 10-20 representative errors and analyze them individually. What would a human need to get these right?
5. **Root cause hypotheses** — For each failure pattern, propose causes:
   - Missing features
   - Label noise
   - Distribution shift
   - Insufficient training data for that subgroup
   - Model capacity limitations
6. **Improvement recommendations** — Rank potential fixes by expected impact and feasibility.

---

#### 7. ds-reviewer (review/)

```yaml
---
name: ds-reviewer
description: "Check methodology, statistical validity, and conclusion soundness as a senior DS peer reviewer. Use before sharing results or deploying."
model: inherit
---
```

You are DS Reviewer, a senior data scientist conducting a thorough peer review.

**Your review covers:**

1. **Problem formulation** — Is the problem well-defined? Does the metric align with the business objective? Are success criteria realistic?
2. **Data handling** — Is the data split valid? Any leakage risk? Are missing values handled appropriately? Is the data representative?
3. **Methodology** — Is the approach appropriate for the data and problem? Were simpler baselines tried? Are hyperparameters tuned systematically?
4. **Evaluation** — Are metrics appropriate? Is the test set truly held out? Are confidence intervals reported? Is the comparison to baseline fair?
5. **Statistical rigor** — Are statistical tests appropriate? Is multiple testing accounted for? Are effect sizes reported alongside p-values?
6. **Conclusions** — Do conclusions follow from the evidence? Are limitations acknowledged? Are next steps clear?
7. **Reproducibility** — Can this be recreated? Are seeds set? Is the environment specified? Is the data versioned?

**Output as:**
- **CRITICAL** — Must fix before trusting results
- **RECOMMENDATION** — Should fix to improve quality
- **OBSERVATION** — Minor improvement or style point
- **STRENGTH** — Highlight what was done well

---

#### 8. reproducibility-auditor (review/)

```yaml
---
name: reproducibility-auditor
description: "Audit seeds, data versions, environment specs, hardcoded paths, and pipeline determinism. Use before shipping to catch reproducibility gaps."
model: inherit
---
```

You are Reproducibility Auditor, a specialist in making ML work reproducible.

**Your checklist:**

1. **Random seeds** — Are all random seeds set? (numpy, random, torch, sklearn, data shuffling)
2. **Data versioning** — Is the exact dataset version specified? Hash, timestamp, or version tag?
3. **Environment** — Are library versions pinned? Is there a `requirements.txt`, `environment.yml`, or `pyproject.toml`?
4. **Hardcoded paths** — Any absolute paths that won't work on another machine?
5. **Data pipeline** — Are all preprocessing steps captured in code (not manual)?
6. **Configuration** — Are hyperparameters, thresholds, and settings in config files (not buried in code)?
7. **Ordering** — Are results sensitive to data ordering? Is shuffling with seed applied?
8. **Non-determinism** — GPU non-determinism acknowledged? Multi-threading order dependencies?
9. **Documentation** — Are instructions for reproducing the full pipeline documented?

Flag each issue as: `PASS`, `FAIL`, or `WARN` with explanation.

---

#### 9. documentation-synthesizer (review/)

```yaml
---
name: documentation-synthesizer
description: "Extract reusable insights from experiment results and write them as searchable learning documents. Use at project end to capture what worked, failed, and surprised."
model: inherit
---
```

You are Documentation Synthesizer, an expert at extracting and organizing institutional knowledge from data science work.

**Your approach:**

1. **Read artifacts** — Gather experiment plans, results, reviews, notebooks, and any notes.
2. **Extract learnings** — Identify:
   - What worked (reusable patterns, effective approaches)
   - What failed (dead ends, bad assumptions)
   - Surprises (unexpected findings, data quirks)
   - Domain knowledge (business rules, data semantics learned during the project)
3. **Categorize** — Tag each learning by: `modeling`, `data`, `features`, `evaluation`, `deployment`.
4. **Generalize** — Transform project-specific findings into reusable guidance. "XGBoost worked well for churn" → "For tabular classification with mixed types and moderate feature count (<100), gradient boosting consistently outperforms logistic regression by 3-5% AUC."
5. **Format** — Write as a `docs/ds/learnings/` file with YAML frontmatter.
6. **Cross-reference** — Link to the source artifacts and related prior learnings.

---

### Skills

> **Research Insight — Skill vs Template Boundary:** Skills encode **methodology** (how to think about a problem — decision trees, checklists, technique guides). Templates encode **form** (what fields to fill in — blank documents with placeholders). They serve distinct purposes and are not duplicates. For example, the `model-card` skill teaches what goes in each section and why; the `templates/model-card.md` is the blank form to fill in. Skills are invoked by commands during execution; templates are instantiated by commands to create output files.

#### 1. eda-checklist

```yaml
---
name: eda-checklist
description: "Systematic exploratory data analysis checklist covering structure, quality, distributions, relationships, and target analysis. Use when starting EDA on any dataset."
---
```

**Checklist:**

- [ ] **Shape and types** — Row count, column count, dtypes, memory usage
- [ ] **Missing data** — Missing rates per column, patterns (heatmap), columns >50% missing
- [ ] **Duplicates** — Exact duplicate rows, near-duplicate detection on key columns
- [ ] **Target distribution** — Class balance (classification) or distribution shape (regression)
- [ ] **Numeric distributions** — Histograms, skewness, outlier detection (IQR and z-score)
- [ ] **Categorical distributions** — Value counts, rare categories (<1%), high cardinality (>50 unique)
- [ ] **Temporal patterns** — Time range, gaps, seasonality, trend
- [ ] **Correlations** — Numeric correlation matrix, top correlated pairs, multicollinearity check (VIF)
- [ ] **Target correlations** — Feature-target correlation ranking, point-biserial for categorical-target
- [ ] **Constant/near-constant** — Columns with single value or >99% same value
- [ ] **ID-like columns** — Columns with all unique values that may be identifiers
- [ ] **Leakage suspects** — Features with suspiciously high target correlation (>0.95)
- [ ] **Cross-feature patterns** — Scatter matrix for top features, interaction effects

---

#### 2. target-leakage-detection

```yaml
---
name: target-leakage-detection
description: "Detect target leakage in feature sets by checking temporal validity, feature-target correlation, and information flow. Use before training any model."
---
```

**Detection methodology:**

1. **Temporal leakage** — For each feature, verify it would be available at prediction time. Check:
   - Features derived from future events (e.g., "outcome_date" when predicting outcome)
   - Aggregations that include the prediction period
   - Features updated after the target was determined

2. **Direct leakage** — Check for:
   - Features that are transformations of the target (e.g., "revenue_bucket" when predicting revenue)
   - Features that are downstream effects of the target
   - One-to-one mappings with the target

3. **Statistical signals** — Flag when:
   - Single feature AUC > 0.95 (classification) or R-squared > 0.95 (regression)
   - Feature importance is dominated by a single feature
   - Train and test performance are nearly identical (too good to be true)

4. **Group leakage** — Check for:
   - Train/test split that separates related observations (same customer in both sets)
   - Preprocessing (e.g., scaling) fit on combined train+test

**Remediation:** For each detected leakage, describe the mechanism and suggest a fix (remove feature, adjust time window, fix split strategy).

---

#### 3. split-strategy

```yaml
---
name: split-strategy
description: "Select and implement appropriate train/validation/test split strategies based on data characteristics. Use when designing the evaluation framework for a model."
---
```

**Decision tree:**

1. **Is there a time dimension?**
   - Yes → **Temporal split**: Train on past, validate on recent, test on most recent. Never shuffle across time.
   - No → Continue to next question.

2. **Are observations grouped?** (e.g., multiple rows per customer)
   - Yes → **Group-aware split**: Keep all observations of a group in the same fold. Use `GroupKFold` or `GroupShuffleSplit`.
   - No → Continue.

3. **Is the target imbalanced?** (<10% minority class)
   - Yes → **Stratified split**: Use `StratifiedKFold` or `StratifiedShuffleSplit` to preserve class ratios.
   - No → **Simple random split**: Standard `train_test_split` with fixed seed.

4. **Is the dataset small?** (<5,000 rows)
   - Yes → **Cross-validation**: Use 5-fold or 10-fold CV instead of a single holdout. Report mean and std.
   - No → Single holdout is fine (70/15/15 or 80/10/10).

**Common mistakes:**
- Shuffling time-series data
- Fitting preprocessors (scalers, encoders) on the full dataset before splitting
- Using the test set for hyperparameter tuning (it should be touched only once)
- Not accounting for groups when observations are correlated

---

#### 4. imbalanced-classification

```yaml
---
name: imbalanced-classification
description: "Handle class imbalance in classification problems with appropriate techniques for sampling, loss functions, and evaluation. Use when minority class is <20% of data."
---
```

**Approach by severity:**

| Imbalance Ratio | Recommended Approach |
|---|---|
| 5:1 to 10:1 (mild) | Class weights in the loss function, stratified sampling |
| 10:1 to 100:1 (moderate) | SMOTE or random undersampling + class weights + threshold tuning |
| >100:1 (severe) | Anomaly detection framing, focal loss, cost-sensitive learning |

**Technique guide:**

- **Class weights** — Most frameworks support `class_weight='balanced'`. Always try this first — it's simple and often sufficient.
- **Oversampling (SMOTE)** — Apply only to training set, never to validation/test. Use `imblearn.over_sampling.SMOTE`.
- **Undersampling** — Random undersampling of the majority class. Consider ensemble-based approaches (`BalancedRandomForest`).
- **Threshold tuning** — Train normally, then optimize the decision threshold on validation set using precision-recall curve.
- **Focal loss** — Reduce loss for well-classified examples. Useful for neural networks.

**Evaluation — never use accuracy.** Use:
- **PR-AUC** (precision-recall AUC) — Best single metric for imbalanced problems
- **F1 at optimal threshold** — Practical operating point
- **Recall at fixed precision** — When false positives have known cost

---

#### 5. time-series-validation

```yaml
---
name: time-series-validation
description: "Implement time-aware validation strategies for time-series and temporal data. Use when data has a time dimension that affects the prediction setup."
---
```

**Core principle:** Never use future information to predict the past. The validation setup must mirror how the model will be used in production.

**Strategies:**

1. **Expanding window** — Train on all data up to time T, validate on T to T+h. Move T forward and repeat. Most realistic but computationally expensive.

2. **Sliding window** — Train on fixed-size window [T-w, T], validate on [T, T+h]. Useful when older data is less relevant.

3. **Time-series cross-validation** — Use `sklearn.model_selection.TimeSeriesSplit`. Set `n_splits` based on available time range.

4. **Embargo gap** — Leave a gap between train and validation to prevent leakage from features with look-ahead (e.g., rolling averages). Gap size = largest look-back window.

**Validation checklist:**
- [ ] No shuffling of temporal data
- [ ] Train set always precedes validation/test set chronologically
- [ ] Embargo gap matches the feature look-back period
- [ ] Feature engineering (rolling stats, lags) computed only on the training portion within each fold
- [ ] Evaluation accounts for temporal patterns (performance by month/quarter)

---

#### 6. feature-importance

```yaml
---
name: feature-importance
description: "Analyze feature importance using multiple methods to understand model behavior and select features. Use after training to interpret which features drive predictions."
---
```

**Methods (use at least two for cross-validation):**

1. **Permutation importance** — Shuffle each feature and measure performance drop. Model-agnostic, works on any metric. Use `sklearn.inspection.permutation_importance`.

2. **SHAP values** — Shapley additive explanations. Best for understanding per-prediction feature contributions. Use `shap.TreeExplainer` (tree models) or `shap.KernelExplainer` (any model).

3. **Built-in importance** — `feature_importances_` for tree models (split-based). Fast but biased toward high-cardinality features.

4. **Correlation-based** — Feature-target correlations. Simple but misses interactions and non-linear relationships.

5. **Drop-column importance** — Retrain without each feature and measure performance change. Most accurate but computationally expensive.

**Interpretation pitfalls:**
- Correlated features split importance (both look unimportant individually)
- Built-in importance is not the same as permutation importance
- Importance on training set can differ from test set (overfitting features)
- SHAP interaction values needed to understand feature combinations

---

#### 7. error-slicing

```yaml
---
name: error-slicing
description: "Systematically slice model errors by features, segments, and conditions to find failure modes. Use after model evaluation to diagnose where the model underperforms."
---
```

**Slicing methodology:**

1. **By categorical features** — For each categorical column, compute error rate per group. Sort by error rate descending. Flag groups with error rate >2x the overall rate.

2. **By numeric feature bins** — Bin numeric features into quantiles (5-10 bins). Compute error rate per bin. Look for monotonic trends (model degrades at extremes).

3. **By prediction confidence** — Bin predictions by confidence/probability. Errors concentrated in high-confidence predictions indicate calibration issues.

4. **By data characteristics** — Slice by: missing value count, feature value rarity, distance from training distribution.

5. **Intersection slicing** — Combine 2-3 features to find interaction-based failure modes (e.g., "model fails on young customers in rural areas").

**Output format:**

```markdown
| Slice | Count | Error Rate | Overall Rate | Ratio | Priority |
|---|---|---|---|---|---|
| category_X = "rare_value" | 45 | 0.42 | 0.12 | 3.5x | HIGH |
```

---

#### 8. experiment-tracking

```yaml
---
name: experiment-tracking
description: "Standard format for logging ML experiments including hypothesis, config, results, and learnings. Use when running experiments to maintain a consistent record."
---
```

**Experiment log format:**

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
[Ship | Iterate | Abandon] — [Reasoning]

### Next Steps
- [What to try next based on findings]

### Series
- **Parent experiment:** [link to prior experiment this builds on, if any]
- **Child experiments:** [links to follow-up experiments, if any]
```

> **Research Insight — Experiment Tracking Fields:** Analysis of MLflow, Weights & Biases, Neptune, and DVC tracking schemas revealed minimum viable fields that the plan was missing: data hash/version, environment/library versions, git commit SHA, compute cost, and experiment series linkage. The `Series` section prevents orphaned experiment chains — every experiment should reference what it builds on and what followed. The `Environment` section is required for reproducibility (identified as the #1 cause of "works on my machine" failures in ML teams per Google's ML Test Score framework).

---

#### 9. model-card

```yaml
---
name: model-card
description: "Generate model cards following Google's Model Cards standard for documenting model purpose, performance, and limitations. Use before deploying any model."
---
```

**Model card structure (per Google Model Cards for Model Reporting):**

```markdown
# Model Card: [Model Name]

## Model Details
- **Developer:** [Team/person]
- **Model date:** [Training date]
- **Model version:** [Version]
- **Model type:** [Algorithm/architecture]
- **Framework:** [sklearn/xgboost/pytorch/etc.]
- **License:** [If applicable]

## Intended Use
- **Primary use cases:** [What it's designed for]
- **Out-of-scope uses:** [What it should NOT be used for]
- **Users:** [Who will use the model outputs]

## Training Data
- **Source:** [Where the data comes from]
- **Date range:** [Time period covered]
- **Size:** [Row/column count]
- **Preprocessing:** [Key steps]

## Evaluation Data
- **Source:** [Same or different from training]
- **Size:** [Row/column count]
- **Relationship to training data:** [How it was split]

## Performance
[Metrics table with slices]

## How to Get Started
` ` `python
# Example inference code
from model import predict
result = predict(input_data)
` ` `

## Explainability
- **Method:** [SHAP / LIME / permutation importance / built-in]
- **Top features:** [Top 5 features driving predictions]
- **Explanation availability:** [Per-prediction explanations available? Y/N]

## Limitations
- [Known failure modes]
- [Data limitations]
- [Fairness concerns]

## Ethical Considerations
- [Potential harms]
- [Mitigations applied]

## Environmental Impact
- **Hardware:** [GPU type, count]
- **Training time:** [hours]
- **Carbon footprint:** [estimated CO2 if known]
```

> **Research Insight — Model Card Enhancements:** HuggingFace's model card template adds "How to Get Started" (critical for adoption — a model nobody can load is a model nobody uses) and "Environmental Impact" sections. NVIDIA Model Card++ adds "Explainability" with feature attribution methods. These three sections were missing from the original Google-only template.

---

#### 10. dataset-card

```yaml
---
name: dataset-card
description: "Document dataset characteristics, provenance, quality issues, and usage guidelines following dataset documentation standards. Use when preparing data for a project or sharing datasets."
---
```

**Dataset card structure:**

```markdown
# Dataset Card: [Dataset Name]

## Overview
- **Description:** [What this dataset represents]
- **Source:** [Origin/collection method]
- **Date range:** [Time period covered]
- **Size:** [Rows x columns, file size]
- **Format:** [CSV/Parquet/SQL/etc.]
- **Update frequency:** [One-time/daily/weekly/etc.]

## Schema
| Column | Type | Description | Missing % | Example |
|---|---|---|---|---|

## Collection Process
- **How collected:** [API, survey, logs, scraping, etc.]
- **Sampling strategy:** [Random, stratified, convenience, etc.]
- **Known biases:** [Selection bias, survivorship bias, etc.]

## Quality Assessment
- **Duplicate rate:** [%]
- **Missing data pattern:** [Random/systematic]
- **Known issues:** [List]
- **Freshness:** [Last updated]

## Usage Guidelines
- **Appropriate uses:** [What analyses this data supports]
- **Inappropriate uses:** [What this data should NOT be used for]
- **Privacy considerations:** [PII, anonymization, consent]
- **Join keys:** [How to link to other datasets]

## Changelog
| Date | Change | Author |
|---|---|---|
```

---

#### 11. statistical-tests

```yaml
---
name: statistical-tests
description: "Select appropriate statistical tests based on data type, distribution, and hypothesis. Use when comparing groups, testing relationships, or validating assumptions."
---
```

**Test selection guide:**

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

**Multiple testing:** When running >1 test, apply Bonferroni correction (divide alpha by number of tests) or Benjamini-Hochberg FDR correction.

**Effect size:** Always report effect size alongside p-values. Cohen's d for means, Cramr's V for chi-squared, R-squared for correlations.

**Sample size guidance:** With <30 observations per group, prefer non-parametric tests regardless of normality.

---

### Templates

#### templates/problem-framing.md

```markdown
---
title: "Problem Framing: [Project Name]"
date: YYYY-MM-DD
author: [Name]
status: draft
---

# Problem Framing: [Project Name]

## Business Context
[What is the business problem? Who is the stakeholder? What decision will this inform?]

## Data Science Formulation
- **Type:** [classification | regression | ranking | clustering | causal | descriptive]
- **Target variable:** [What we're predicting]
- **Observation unit:** [What each row represents]
- **Prediction horizon:** [How far ahead, if applicable]

## Success Criteria
- **Primary metric:** [metric] >= [threshold]
- **Baseline:** [Current approach and its performance]
- **Business impact:** [Expected impact if successful]

## Available Data
| Dataset | Description | Rows | Columns | Date Range | Join Key |
|---|---|---|---|---|---|

## Constraints
- **Latency:** [Real-time / batch / near-real-time]
- **Interpretability:** [Black-box OK / needs explanations / fully interpretable]
- **Fairness:** [Protected attributes to monitor]
- **Regulatory:** [Compliance requirements]

## Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|

## Proposed Approach
1. [Approach 1 with trade-offs]
2. [Approach 2 with trade-offs]

## Open Questions
- [ ] [Question 1]
- [ ] [Question 2]
```

---

#### templates/dataset-assessment.md

```markdown
---
title: "Dataset Assessment: [Dataset Name]"
date: YYYY-MM-DD
author: [Name]
---

# Dataset Assessment: [Dataset Name]

## Overview
- **Source:** [Where the data comes from]
- **Size:** [Rows x columns]
- **Date range:** [Time period]
- **Collection method:** [How it was collected]

## Schema Summary
| Column | Type | Missing % | Unique Values | Notes |
|---|---|---|---|---|

## Quality Issues
- [ ] [Issue 1 — severity, impact, proposed fix]
- [ ] [Issue 2]

## Distribution Notes
[Key observations about feature distributions, outliers, class balance]

## Relationships
[Key correlations, associations, potential predictive features]

## Leakage Risks
[Features that might leak target information]

## Recommendation
[Suitable for modeling / needs cleaning / insufficient for the task]
```

---

#### templates/experiment-plan.md

```markdown
---
title: "Experiment Plan: [Experiment Name]"
date: YYYY-MM-DD
author: [Name]
status: planned
---

# Experiment Plan: [Experiment Name]

## Hypothesis
[What we expect to happen and why]

## Background
[Why this experiment? What prior work informs it?]

## Methodology

### Data
- **Dataset:** [Name and version]
- **Date range:** [Training and evaluation periods]
- **Split strategy:** [How data will be divided]

### Features
- **Feature set:** [Description or reference to feature list]
- **New features:** [Any new features being tested]
- **Leakage check:** [Confirmed clean / pending review]

### Model
- **Algorithm:** [What model(s) to train]
- **Hyperparameters:** [Starting values and search strategy]
- **Baseline:** [What we're comparing against]

### Evaluation
- **Primary metric:** [Metric name and why]
- **Secondary metrics:** [List]
- **Slices to evaluate:** [Important subgroups]

## Reproducibility
- **Random seed:** [Value]
- **Environment:** [Python version, key library versions]
- **Data snapshot:** [How to get the exact data version]

## Expected Timeline
- [ ] Data preparation: [estimate]
- [ ] Training: [estimate]
- [ ] Evaluation: [estimate]
- [ ] Documentation: [estimate]

## Success Criteria
[What result would make us ship this model?]
```

---

#### templates/experiment-result.md

```markdown
---
title: "Experiment Result: [Experiment Name]"
date: YYYY-MM-DD
author: [Name]
status: complete
experiment_plan: "[path to experiment plan]"
outcome: [success | failure | mixed]
---

# Experiment Result: [Experiment Name]

## Summary
[1-2 sentence summary of what happened]

## Results

### Overall Performance
| Metric | Train | Validation | Test | Baseline | Delta |
|---|---|---|---|---|---|

### Slice Performance
| Slice | Metric | Value | Overall | Ratio |
|---|---|---|---|---|

### Key Plots
[Description of important visualizations — confusion matrix, PR curve, calibration plot, SHAP summary]

## Analysis
[What worked, what didn't, why]

## Comparison to Hypothesis
[Did the hypothesis hold? Why or why not?]

## Artifacts
- **Model:** [Path to saved model]
- **Predictions:** [Path to prediction files]
- **Notebook:** [Path to analysis notebook]

## Decision
**[Ship | Iterate | Abandon]** — [Reasoning]

## Next Steps
- [ ] [Action 1]
- [ ] [Action 2]

## Learnings
[What should be captured in docs/learnings/ for future reference?]
```

---

#### templates/error-analysis.md

```markdown
---
title: "Error Analysis: [Model/Experiment Name]"
date: YYYY-MM-DD
author: [Name]
---

# Error Analysis: [Model/Experiment Name]

## Error Overview
- **Total predictions:** [N]
- **Total errors:** [N] ([%])
- **Error type breakdown:** [FP/FN counts for classification, or residual distribution for regression]

## Slice Analysis
| Slice | Count | Error Rate | Overall Rate | Ratio | Priority |
|---|---|---|---|---|---|

## Failure Patterns
### Pattern 1: [Description]
- **Affected slice:** [What data is affected]
- **Error rate:** [Rate vs. overall]
- **Root cause hypothesis:** [Why this happens]
- **Example cases:** [2-3 representative examples]
- **Potential fix:** [What could improve this]

### Pattern 2: [Description]
[Same structure]

## Confidence Analysis
[Errors by prediction confidence — are high-confidence errors common?]

## Recommendations
| Fix | Expected Impact | Effort | Priority |
|---|---|---|---|
```

---

#### templates/model-review-checklist.md

```markdown
---
title: "Model Review: [Model Name]"
date: YYYY-MM-DD
reviewer: [Name]
---

# Model Review: [Model Name]

> Organized per Google's ML Test Score framework (28 tests in 4 categories). Score each item 0 (not done) or 1 (done) — total score indicates ML maturity.

## Data Tests (7 items)
- [ ] Data sources are documented with provenance
- [ ] Data quality issues are identified and handled
- [ ] No target leakage detected
- [ ] Train/test split is appropriate (temporal, grouped, stratified as needed)
- [ ] Feature engineering is reproducible and documented
- [ ] Data schema is validated (expected types, ranges, cardinality)
- [ ] Data freshness is verified (no stale data in production pipeline)

## Model Tests (10 items)
- [ ] Business objective is clear and measurable
- [ ] DS formulation matches the business need
- [ ] Success criteria are defined with specific thresholds
- [ ] Baseline is appropriate and documented
- [ ] Model choice is justified; simpler alternatives were considered
- [ ] Hyperparameter tuning is systematic (not manual guessing)
- [ ] Metrics align with business objective
- [ ] Performance reported on held-out test set with confidence intervals
- [ ] Slice analysis performed on meaningful subgroups
- [ ] Error analysis identifies failure modes and calibration checked

## Infrastructure Tests (6 items)
- [ ] Random seeds set for all stochastic components
- [ ] Environment specified (requirements.txt / environment.yml)
- [ ] Data version documented (hash, snapshot, or version tag)
- [ ] Pipeline runs end-to-end without manual steps
- [ ] Inference latency measured and within budget
- [ ] Input schema documented with example payloads

## Monitoring Tests (5 items)
- [ ] Model card completed
- [ ] Monitoring plan defined (metrics to track, alert thresholds)
- [ ] Drift detection strategy documented (PSI, KL divergence, or custom)
- [ ] Fallback strategy documented (what happens when model fails)
- [ ] Retraining trigger criteria defined

## Overall Assessment
**ML Test Score:** [X / 28]
**Verdict:** [Approved | Needs revision | Rejected]
**Key concerns:** [List]
**Strengths:** [List]
```

> **Research Insight — Google ML Test Score:** The original checklist was organized by workflow phase (Problem Framing, Data, Methodology, Evaluation, Reproducibility, Deployment). Google's ML Test Score paper proposes a more actionable 4-category framework: Data Tests, Model Tests, Infrastructure Tests, and Monitoring Tests. Each item scores 0 or 1, giving a concrete ML maturity score out of 28. Teams scoring <15 have significant risk; 15-22 is acceptable; >22 is production-ready. This scoring system makes review outcomes objective rather than subjective.

---

#### templates/model-card.md

```markdown
---
title: "Model Card: [Model Name]"
date: YYYY-MM-DD
version: [Model version]
author: [Name]
---

# Model Card: [Model Name]

## Model Details
- **Version:** [v1.0.0]
- **Type:** [Algorithm/architecture]
- **Framework:** [sklearn/xgboost/pytorch/etc.]
- **Training date:** [YYYY-MM-DD]
- **Training duration:** [Time]
- **Model size:** [Parameters / file size]

## Intended Use
- **Primary use:** [What decisions this model informs]
- **Users:** [Who consumes the predictions]
- **Out of scope:** [What this model should NOT be used for]

## Training Data
- **Source:** [Dataset name and version]
- **Date range:** [Period covered]
- **Size:** [Rows after preprocessing]
- **Key preprocessing:** [Major transformations applied]

## Evaluation
### Overall Metrics
| Metric | Value | 95% CI |
|---|---|---|

### Slice Performance
| Slice | N | Primary Metric | Delta vs. Overall |
|---|---|---|---|

## Limitations
- [Known failure modes]
- [Data limitations]
- [Generalization concerns]

## Ethical Considerations
- [Bias risks]
- [Fairness metrics checked]
- [Privacy protections applied]

## Monitoring
- [Metrics to track in production]
- [Drift detection strategy]
- [Alerting thresholds]
```

---

#### templates/postmortem.md

```markdown
---
title: "Postmortem: [Project/Experiment Name]"
date: YYYY-MM-DD
author: [Name]
project: [project-name]
outcome: [success | failure | mixed]
---

# Postmortem: [Project/Experiment Name]

## Summary
[1-2 sentences: what was the project, what happened]

## Timeline
| Date | Event |
|---|---|

## What Worked
- [Effective approach or decision and why it worked]

## What Didn't Work
- [Failed approach and why it failed]

## Surprises
- [Unexpected finding and its implications]

## Key Learnings
### Data
- [Data-related learnings]

### Modeling
- [Modeling-related learnings]

### Process
- [Process-related learnings]

## Reusable Artifacts
- [Feature transformations, evaluation recipes, or code worth keeping]

## Recommendations for Next Time
- [ ] [Specific, actionable recommendation]
- [ ] [Specific, actionable recommendation]
```

---

## D) README

```markdown
# Data Science Plugin

Data science and ML workflow tools that compound institutional knowledge. 9 agents, 6 commands, 11 skills for problem framing, EDA, experimentation, model review, and knowledge management.

## Install

` ` `bash
/install-plugin ds
` ` `

## Workflow

` ` `
Frame → Explore → Experiment → Review → Ship → Compound → Repeat
` ` `

| Command | Purpose |
|---------|---------|
| `/ds:plan` | Frame business questions as DS problems and plan approach |
| `/ds:eda` | Run structured exploratory data analysis |
| `/ds:experiment` | Design and run rigorous ML experiments |
| `/ds:review` | Multi-agent peer review of DS work |
| `/ds:ship` | Package models with documentation for deployment |
| `/ds:compound` | Capture learnings to make future projects faster |

Each cycle compounds: experiment learnings surface in future plans, error patterns inform feature engineering, and review feedback becomes institutional knowledge.

## Components

| Component | Count |
|-----------|-------|
| Agents | 9 |
| Commands | 6 |
| Skills | 11 |
| MCP Servers | 1 |

## Agents

### Analysis (3)

| Agent | Description |
|-------|-------------|
| `problem-framer` | Frame business questions as structured DS problems |
| `data-profiler` | Profile datasets for quality, structure, and anomalies |
| `feature-engineer` | Design and evaluate feature transformations |

### Modeling (3)

| Agent | Description |
|-------|-------------|
| `experiment-designer` | Design rigorous experiments with hypotheses and evaluation plans |
| `model-evaluator` | Evaluate performance with slicing, calibration, and fairness checks |
| `error-analyst` | Slice errors to find failure modes and improvement opportunities |

### Review (3)

| Agent | Description |
|-------|-------------|
| `ds-reviewer` | Senior DS peer review for methodology and statistical rigor |
| `reproducibility-auditor` | Audit experiments for reproducibility issues |
| `documentation-synthesizer` | Synthesize findings into reusable learning documents |

## Commands

| Command | Description |
|---------|-------------|
| `/ds:plan` | Search past learnings, frame the problem, plan the approach, output a plan doc |
| `/ds:eda` | Profile data, analyze distributions, check quality, output an EDA report |
| `/ds:experiment` | Formulate hypothesis, design methodology, check for leakage, output experiment plan and results |
| `/ds:review` | Run 3 parallel review agents (methodology, reproducibility, error analysis), output consolidated review |
| `/ds:ship` | Pre-ship checklist, generate model card and dataset card, package artifacts |
| `/ds:compound` | Extract learnings from completed work, categorize, and save to docs/learnings/ |

## Skills

| Skill | Description |
|-------|-------------|
| `eda-checklist` | Systematic EDA methodology covering structure, quality, distributions, relationships |
| `target-leakage-detection` | Detect temporal, direct, and group leakage in feature sets |
| `split-strategy` | Train/validation/test split decision tree based on data characteristics |
| `imbalanced-classification` | Handle class imbalance with sampling, loss functions, and evaluation |
| `time-series-validation` | Time-aware cross-validation and embargo gap strategies |
| `feature-importance` | Multi-method feature importance analysis (SHAP, permutation, built-in) |
| `error-slicing` | Systematic error slicing by features, confidence, and intersections |
| `experiment-tracking` | Standard experiment logging format |
| `model-card` | Model documentation following Google Model Cards standard |
| `dataset-card` | Dataset documentation covering provenance, schema, quality, and usage |
| `statistical-tests` | Statistical test selection guide based on data type and hypothesis |

## MCP Servers

| Server | Description |
|--------|-------------|
| `context7` | Framework documentation lookup for DS/ML libraries |

## Example Usage

### Starting a new project

` ` `
/ds:plan We need to predict customer churn for our SaaS product.
         We have 2 years of usage logs, billing data, and support tickets.
         The business wants to identify at-risk customers 30 days before they cancel.
` ` `

### Exploring a dataset

` ` `
/ds:eda ./data/customers.parquet
` ` `

### Running an experiment

` ` `
/ds:experiment Hypothesis: Adding rolling 7-day usage features will improve
               churn prediction AUC by >2% over the baseline feature set.
` ` `

### Reviewing work

` ` `
/ds:review ./notebooks/churn_model_v2.ipynb
` ` `

### Shipping a model

` ` `
/ds:ship ./models/churn_xgb_v2.pkl
` ` `

### Capturing learnings

` ` `
/ds:compound The churn experiment showed that recency features (days since
             last login, days since last support ticket) were more predictive
             than aggregate features (total logins, total tickets).
` ` `

## Compounding Mechanism

The plugin creates `docs/ds/learnings/` in your project with YAML-frontmattered files.
`/ds:plan` and `/ds:experiment` search these before starting new work.

` ` `
docs/ds/learnings/
├── 2026-02-24-churn-recency-features.md
├── 2026-02-20-temporal-split-gotcha.md
└── 2026-02-15-xgboost-tabular-ranges.md
` ` `

Over time, your learnings directory becomes an institutional knowledge base
that makes every new project faster.

## Philosophy

**Each experiment should make the next one easier.**

Traditional data science accumulates technical debt: notebooks that can't be reproduced,
experiments that repeat past failures, and learnings trapped in individual heads.

This plugin inverts that. 80% is in framing and review, 20% is in execution:
- Frame problems thoroughly before modeling
- Review to catch methodological issues early
- Compound learnings so they're reusable
- Ship with documentation so models are maintainable

## License

MIT
```

---

## E) Phased Implementation Plan

### Phase 1: MVP (v1.0.0)

**Goal:** Core workflow loop with the most common entry points.

**Scope:**
- [ ] Plugin scaffold (`.claude-plugin/plugin.json` with `"name": "ds"`, `CLAUDE.md`, `README.md`, `CHANGELOG.md`)
- [ ] 4 commands: `/ds:plan`, `/ds:eda`, `/ds:experiment`, `/ds:compound` (all with `disable-model-invocation: true`)
- [ ] 6 agents: `problem-framer`, `data-profiler`, `feature-engineer`, `experiment-designer`, `model-evaluator`, `documentation-synthesizer` (all with `<examples>` blocks)
- [ ] 5 skills: `eda-checklist`, `split-strategy`, `target-leakage-detection`, `experiment-tracking`, `statistical-tests`
- [ ] 5 templates: `problem-framing.md`, `dataset-assessment.md`, `experiment-plan.md`, `experiment-result.md`, `postmortem.md`
- [ ] Compounding mechanism: `docs/ds/learnings/` with enhanced YAML frontmatter (findings array, lifecycle_stage, deduplication gate), and relevance-ranked search
- [ ] Command files use subdirectory pattern: `commands/ds/plan.md`, `commands/ds/eda.md`, etc.
- [ ] All output consolidated under `docs/ds/` (plans, eda, experiments, learnings subdirectories)

**Why this subset:** Covers Plan → EDA → Experiment → Compound — the most natural DS workflow. EDA is the most common entry point for data scientists, so including it in MVP ensures the plugin is useful on day one. `feature-engineer` moved to MVP because `/ds:eda` invokes it (step 5b) — shipping `/ds:eda` without `feature-engineer` would leave a dead reference.

**Acceptance Criteria:**
- [ ] `/ds:plan` with no learnings produces a valid problem framing doc
- [ ] `/ds:plan` with existing learnings surfaces relevant ones in output
- [ ] `/ds:eda` profiles a CSV/Parquet file and produces an EDA report
- [ ] `/ds:eda` flags leakage suspects when target column is identified
- [ ] `/ds:eda` invokes `feature-engineer` after distribution analysis
- [ ] `/ds:experiment` generates an experiment plan with split strategy and leakage check
- [ ] `/ds:experiment` invokes `model-evaluator` when generating result reports
- [ ] `/ds:experiment` logs environment, data hash, and git commit in experiment records
- [ ] `/ds:compound` runs deduplication gate (searches existing learnings before writing)
- [ ] `/ds:compound` validates YAML frontmatter against enhanced schema before writing
- [ ] `/ds:compound` writes properly frontmattered files to `docs/ds/learnings/`
- [ ] Cold start works (no `docs/ds/` directory yet — auto-created via `mkdir -p`)
- [ ] Large dataset handling: `/ds:eda` samples when >100MB
- [ ] All 6 agents have `<examples>` blocks (verified by grep)
- [ ] All 4 commands have `disable-model-invocation: true` and use `$ARGUMENTS`
- [ ] Plugin `name` is `"ds"` in plugin.json
- [ ] Plugin installs cleanly via `/plugin install`
- [ ] README documents all MVP components

### Phase 2: Full Workflow (v2.0.0)

**Goal:** Complete the workflow with review and ship commands.

**Scope:**
- [ ] 2 additional commands: `/ds:review`, `/ds:ship` (both with `disable-model-invocation: true`)
- [ ] 3 additional agents: `error-analyst`, `ds-reviewer`, `reproducibility-auditor` (all with `<examples>` blocks)
- [ ] 4 additional skills: `imbalanced-classification`, `feature-importance`, `error-slicing`, `model-card`
- [ ] 2 additional templates: `error-analysis.md`, `model-review-checklist.md` (with Google ML Test Score format)
- [ ] `/ds:review` uses two-phase orchestration: agents return text only, orchestrator writes consolidated review
- [ ] `/ds:compound --update <path>` flag for editing existing learnings
- [ ] Learnings `status` field (active/superseded/deprecated) with search filtering
- [ ] Model card template includes How to Get Started, Explainability, and Environmental Impact sections
- [ ] Output to `docs/ds/reviews/` and `docs/ds/deployments/` subdirectories

**Acceptance Criteria:**
- [ ] Full workflow loop works end-to-end: Plan → EDA → Experiment → Review → Ship → Compound
- [ ] `/ds:review` runs 3 agents concurrently and consolidates findings via orchestrator
- [ ] `/ds:ship` generates model card (enhanced) and dataset card
- [ ] `/ds:ship` runs pre-ship checklist and blocks on critical failures
- [ ] Model review checklist produces ML Test Score (X / 28)
- [ ] Learning update and deprecation workflow works
- [ ] All commands surface relevant learnings before starting work
- [ ] README and CHANGELOG updated with all components
- [ ] Version bumped in plugin.json, CHANGELOG.md updated, README counts verified

### Phase 3: Team Features (v3.0.0)

**Goal:** Features that make the plugin better for team collaboration and iteration.

**Scope:**
- [ ] 2 additional skills: `time-series-validation`, `dataset-card`
- [ ] 1 additional template: `model-card.md` (full deployment version)
- [ ] Experiment comparison: `/ds:compare` — compare two experiment results side by side
- [ ] Experiment index: `docs/ds/experiments/index.md` auto-updated by `/ds:experiment`
- [ ] Experiment series tracking: link related experiments via `parent_experiment` / `child_experiments` fields
- [ ] Cross-project learning aggregation via `.ds-config.yaml`
- [ ] Data versioning skill (file hash, DVC integration, query pinning)
- [ ] Per-project configuration: `.ds-config.yaml` with output directory, default category, cross-project paths

**Acceptance Criteria:**
- [ ] 9 agents, 7+ commands, 11 skills fully operational
- [ ] `/ds:compare` shows side-by-side experiment results
- [ ] Experiment index tracks all experiments per project
- [ ] Experiment series links parent/child experiments for traceability
- [ ] Cross-project search works with configurable project paths
- [ ] README and CHANGELOG fully current

---

## F) Future Extensions

### v4+ Roadmap Ideas

1. **LLM evaluation** — `/ds:eval-llm` command for evaluating LLM outputs (accuracy, hallucination rate, latency, cost). Skills for prompt evaluation, retrieval quality metrics.

2. **RAG evaluation** — `rag-evaluator` agent that assesses retrieval quality (recall@k, MRR), answer faithfulness, and context relevance. Template for RAG experiment tracking.

3. **Model monitoring** — `/ds:monitor` command that generates monitoring dashboards and alerting rules. Skills for drift detection (PSI, KL divergence), performance decay detection, and data quality monitoring.

4. **Data drift detection** — `drift-detector` agent that compares production data distributions against training data. Skills for covariate shift detection and concept drift identification.

5. **A/B test analysis** — `/ds:ab-test` command for analyzing online experiments. Skills for sample size calculation, sequential testing, and multi-armed bandit evaluation.

6. **Feature store integration** — Skills for documenting feature definitions in feature store format (Feast, Tecton, custom). Agent that audits feature freshness and consistency.

7. **Pipeline templates** — Skills for common pipeline patterns: batch prediction, real-time serving, retraining schedules. Templates for pipeline documentation.

8. **Fairness toolkit** — `fairness-auditor` agent that runs comprehensive bias analysis. Skills for disparate impact analysis, equalized odds checking, and fairness-constrained optimization.

9. **Cost estimation** — Skills for estimating compute costs of training runs, inference costs at scale, and cost-accuracy trade-off analysis.

10. **Notebook-to-pipeline** — Agent that reviews notebooks and suggests refactoring into production-grade pipeline code.

---

## References

### Internal
- Compound Engineering Plugin patterns: `/Users/andikarachman/personal_projects/compound-engineering-plugin/plugins/compound-engineering/`
- Plugin format conventions: `/Users/andikarachman/personal_projects/compound-engineering-plugin/plugins/compound-engineering/CLAUDE.md`
- Agent format examples: `/Users/andikarachman/personal_projects/compound-engineering-plugin/plugins/compound-engineering/agents/review/kieran-rails-reviewer.md`
- Command format examples: `/Users/andikarachman/personal_projects/compound-engineering-plugin/plugins/compound-engineering/commands/workflows/plan.md`
- Skill format examples: `/Users/andikarachman/personal_projects/compound-engineering-plugin/plugins/compound-engineering/skills/compound-docs/SKILL.md`

### External
- [Google Model Cards](https://modelcards.withgoogle.com/about)
- [Google ML Test Score](https://research.google.com/pubs/pub46555.html) — 28 tests in 4 categories for ML system maturity
- [HuggingFace Model Card Guide](https://huggingface.co/docs/hub/model-cards) — Extended model card with How to Get Started, Environmental Impact
- [NVIDIA Model Card++](https://developer.nvidia.com/blog/nvidia-model-card/) — Adds Explainability and Safety sections
- [Datasheets for Datasets](https://arxiv.org/abs/1803.09010) — Gebru et al. dataset documentation standard
- [Claude Code Plugin Documentation](https://docs.claude.com/en/docs/claude-code/plugins)
- [Plugin Reference](https://docs.claude.com/en/docs/claude-code/plugins-reference)
- [MLflow Experiment Tracking](https://mlflow.org/docs/latest/tracking.html) — Minimum viable experiment log fields
- [Statsig Compounding Knowledge Patterns](https://www.statsig.com/) — Institutional knowledge management
- [ydata-profiling](https://github.com/ydataai/ydata-profiling) — EDA best practices for automated profiling

---

## G) CLAUDE.md Requirements for the Plugin

> **Research Insight — Versioning & Component Count Sync:** The learnings-from-plugin-versioning agent identified that the compound-engineering plugin maintains strict version/count sync across 3 files. The data-science plugin CLAUDE.md must include the same requirements.

The plugin's `CLAUDE.md` file must include:

1. **Versioning requirements** — Every change must update `plugin.json` version, `CHANGELOG.md`, and `README.md` component counts
2. **Component count verification** — Before committing, verify agent/command/skill/template counts in `plugin.json` description match actual file counts
3. **Invocation map** — Document which commands invoke which agents and skills (prevents orphaned components)
4. **Naming conventions** — Commands use `commands/ds/` subdirectory, agents use category subdirectories, skills use kebab-case directories
5. **Format requirements** — All agents need `<examples>`, all commands need `disable-model-invocation: true` and `$ARGUMENTS`, model-card/dataset-card skills need `disable-model-invocation: true`
