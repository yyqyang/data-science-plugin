---
title: "feat: Replace statistical-tests with statistical-analysis skill"
type: feat
date: 2026-02-24
---

# Replace statistical-tests with statistical-analysis

## Overview

Replace the existing `statistical-tests` skill (83-line test selection table) with the comprehensive `statistical-analysis` skill from `claude-scientific-skills`. This is a **replacement**, not an addition -- `statistical-analysis` is a strict superset that covers everything in `statistical-tests` plus assumption checking, Bayesian methods, APA reporting, power analysis, and 5 reference files with a Python script. The skill count stays at 7.

## Problem Statement

The current `statistical-tests` skill is a minimal lookup table for test selection. It lacks:
- Systematic assumption checking before running tests
- Code examples for running tests end-to-end (only has multiple testing correction code)
- Bayesian alternatives
- APA-style reporting templates (critical for publishing results)
- Power analysis for study planning
- Reference materials for edge cases and diagnostics

The `/ds:experiment` command references `statistical-tests` in step 3 for "designing the comparison protocol", but the skill only provides a test selection table -- it doesn't guide through the full statistical workflow.

## Proposed Solution

Replace `skills/statistical-tests/` with `skills/statistical-analysis/`, wire it into `/ds:experiment`, and update all references.

## Technical Approach

### Phase 1: Replace Skill

#### 1.1 Delete existing skill

Remove `skills/statistical-tests/SKILL.md` and the `statistical-tests/` directory.

#### 1.2 Create new skill directory

```
skills/statistical-analysis/
  SKILL.md                                    # Adapted from source
  scripts/assumption_checks.py                # Automated assumption verification
  references/
    test_selection_guide.md                   # Decision tree for test selection
    assumptions_and_diagnostics.md            # Handling violations
    effect_sizes_and_power.md                 # Effect sizes + power analysis
    bayesian_statistics.md                    # Bayesian methods guide
    reporting_standards.md                    # APA-style reporting
```

#### 1.3 Adapt SKILL.md

- Remove `license`, `metadata` fields
- Rewrite description: "Guided statistical analysis with test selection, assumption checking, power analysis, and APA reporting. Use when /ds:experiment needs to design comparison protocols or validate results."
- Add "Role in the ds plugin" paragraph explaining it's invoked by `/ds:experiment` at step 3
- Remove K-Dense promotional section
- Update report save paths to use `docs/ds/experiments/` convention

### Phase 2: Update /ds:experiment Command

#### 2.1 Update `commands/experiment.md`

Replace the single reference at step 3 (`Invoke statistical-tests skill when designing the comparison protocol`) with a more specific integration:

```markdown
### 3. Methodology Design

...

Invoke the `statistical-analysis` skill for:
- **Test selection**: Use the skill's test selection guide to choose the right statistical test for the comparison protocol
- **Power analysis**: Determine minimum sample size needed using the skill's power analysis workflow
- **Assumption planning**: Note which assumptions will need checking after results are in
```

#### 2.2 Add assumption checking to results step

In step 7 (Generate Results), add:

```markdown
Run the `statistical-analysis` skill's assumption checks on the results:
- Use `scripts/assumption_checks.py` to verify normality and variance homogeneity
- Report results in APA format using `references/reporting_standards.md`
```

### Phase 3: Update Metadata

#### 3.1 All reference updates

Replace `statistical-tests` with `statistical-analysis` in:
- `CLAUDE.md` -- Invocation Map table (line 55)
- `README.md` -- Skills table
- `CHANGELOG.md` -- Add `[1.3.0]` entry noting the replacement

#### 3.2 Version and counts

- `.claude-plugin/plugin.json`: bump `1.2.0` -> `1.3.0`
- Skill count stays at **7** (replacement, not addition)

## Acceptance Criteria

- [ ] `skills/statistical-tests/` directory is deleted
- [ ] `skills/statistical-analysis/SKILL.md` exists with ds plugin frontmatter
- [ ] `skills/statistical-analysis/scripts/assumption_checks.py` is present
- [ ] All 5 reference files present in `skills/statistical-analysis/references/`
- [ ] `/ds:experiment` command references `statistical-analysis` (not `statistical-tests`)
- [ ] No remaining references to `statistical-tests` anywhere in the codebase (except CHANGELOG history)
- [ ] `ls -d skills/*/ | wc -l` still returns 7
- [ ] Version is `1.3.0` in `plugin.json`
- [ ] CLAUDE.md Invocation Map updated
- [ ] K-Dense promotional content removed from SKILL.md

## What's Gained

| Capability | statistical-tests (old) | statistical-analysis (new) |
|---|---|---|
| Test selection table | Yes (simple table) | Yes (comprehensive decision tree + reference file) |
| Multiple testing correction | Yes (code) | Yes (code) |
| Effect sizes | Yes (table only) | Yes (table + code + CI examples) |
| Sample size / power | Basic (2 code snippets) | Full (a priori + sensitivity + reference file) |
| Assumption checking | No | Yes (script + reference file) |
| Bayesian methods | No | Yes (PyMC examples + reference file) |
| APA reporting templates | No | Yes (t-test, ANOVA, regression, Bayesian templates) |
| Best practices / pitfalls | No | Yes (10 best practices, 10 pitfalls) |

## Dependencies & Risks

- **New optional dependency**: `pingouin` (used in code examples). Already optional -- the skill handles it gracefully if not installed.
- **Breaking reference**: Any external reference to `statistical-tests` will break. Low risk since the plugin is at v1.2.0 with no known external consumers.
- **Skill count unchanged**: 7 skills (replace, not add). No count updates needed in README or plugin.json description.

## References

- Source skill: `../claude-scientific-skills/scientific-skills/statistical-analysis/`
- Existing skill being replaced: [skills/statistical-tests/SKILL.md](../../skills/statistical-tests/SKILL.md)
- Experiment command: [commands/experiment.md](../../commands/experiment.md)
- CLAUDE.md invocation map: [CLAUDE.md](../../CLAUDE.md)
