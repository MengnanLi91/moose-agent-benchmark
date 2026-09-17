# MOOSE Agent Benchmark Collaborative Authoring and Status System

## Implementation Specification for Codex

**Repository:** `https://github.com/MengnanLi91/moose-agent-benchmark`  
**Primary goal:** Add a collaborative, human-friendly benchmark development layer using **Obsidian as the front end** and the existing **Git repository as the authoritative backend**, without changing the core benchmark execution/evaluation architecture.

---

## 1. Objective

The MOOSE Agent Benchmark already has a machine-oriented repository structure for public case contracts, private evaluation criteria, benchmark manifests, scoring, tests, and CI.

The missing capability is a convenient collaborative interface that lets benchmark developers:

1. See the overall benchmark status.
2. See coverage across the four tracks and 16 atomic subcategories.
3. See which cases are:
   - planned,
   - in progress,
   - ready for review,
   - blocked,
   - complete.
4. See who owns each case.
5. Open an individual benchmark case and understand:
   - what problem it represents,
   - what capability it tests,
   - why the case exists,
   - its physics domain,
   - starting information,
   - required output,
   - permitted/prohibited actions,
   - acceptance requirements,
   - source/provenance,
   - implementation status,
   - links to the actual benchmark files.
6. Edit the case information in a normal Markdown editor.
7. Commit changes through Git.
8. Review changes through GitHub pull requests.
9. Automatically validate that the human-facing catalog and the executable benchmark definition remain consistent.

The intended system is:

```text
Obsidian
  |
  | edits ordinary Markdown files
  v
Git repository
  |
  | pull request
  v
GitHub review + CI
  |
  v
main branch
```

The repository remains the source of truth.

Obsidian is only the human-facing authoring and navigation layer.

---

# 2. Design Principles

## 2.1 Git is the authoritative backend

Do not introduce Excel, Airtable, Notion, SQLite, or another external database as an authoritative benchmark catalog.

All persistent benchmark-development information must remain in files tracked by Git.

Benefits:

- full version history,
- branch-based development,
- code review,
- reproducibility,
- easy scripting,
- no synchronization between multiple databases,
- no vendor lock-in.

---

## 2.2 Obsidian is a view/editor, not a new storage system

The repository root should be usable directly as an Obsidian vault.

Example:

```bash
git clone https://github.com/MengnanLi91/moose-agent-benchmark.git
cd moose-agent-benchmark
```

Then open the repository root in Obsidian using:

```text
Open folder as vault
```

Obsidian should operate on ordinary Markdown files committed to Git.

Use **Obsidian Bases** to provide database-like table views over Markdown properties.

Optionally use the **Obsidian Git** community plugin for contributors who prefer Git operations from within Obsidian.

Do not require Obsidian for benchmark execution or CI.

---

## 2.3 Do not replace the existing case contract

The current machine-readable benchmark structure should remain intact.

Existing structure:

```text
benchmark/
  manifest.yaml
  public/
    cases/
      <case-id>/
        case.yaml
        prompt.md
        artifacts/
        evidence/
  private/
    cases/
      <case-id>/
        ...
```

The catalog is an additional human-facing layer.

---

## 2.4 Separate machine state from project-management state

Use the following ownership model.

### `case.yaml`

Authoritative for executable participant-facing benchmark metadata.

Examples:

- case ID,
- track,
- subcategory,
- physics domain,
- difficulty,
- participant-visible artifacts,
- actions,
- budgets,
- submission requirements,
- starting state.

### private evaluator files

Authoritative for hidden benchmark truth and scoring criteria.

Examples:

- gold answer,
- hard gates,
- accepted values,
- hidden mutants,
- hidden thresholds,
- private diagnostics.

### catalog Markdown

Authoritative for benchmark-development/project-management metadata.

Examples:

- development status,
- owner,
- reviewer,
- priority,
- motivation,
- benchmark purpose,
- construction notes,
- source/provenance summary,
- checklist,
- open issues,
- implementation notes.

CI must verify that duplicated identity fields remain synchronized.

---

# 3. Benchmark Taxonomy

The dashboard must support the four benchmark tracks.

```text
FORM
  F1 Physics specification and constitutive closure
  F2 Weak form and boundary terms
  F3 MOOSE object and coupling map
  F4 Input assembly and parameter wiring

DIAG
  D1 Failure-stage classification
  D2 Causal-chain reconstruction
  D3 Root-cause localization
  D4 Discriminating next test

REPAIR
  R1 HIT, schema, and reference repair
  R2 Residual, Jacobian, and coupling repair
  R3 Solver, scaling, and nullspace repair
  R4 Initialization and step-control repair

VERIFY
  V1 Exact-solution and MMS verification
  V2 Discretization-error estimation
  V3 Conservation and invariant checks
  V4 External evidence comparison
```

Integrated end-to-end workflow cases must remain separate from atomic capability reporting.

---

# 4. Proposed Repository Layout

Add the following structure.

```text
moose-agent-benchmark/
│
├── .obsidian/
│   └── ... minimal shared Obsidian configuration
│
├── catalog/
│   ├── README.md
│   ├── Benchmark Dashboard.md
│   ├── benchmark.base
│   │
│   ├── tracks/
│   │   ├── FORM.md
│   │   ├── DIAG.md
│   │   ├── REPAIR.md
│   │   └── VERIFY.md
│   │
│   ├── subcategories/
│   │   ├── F1.md
│   │   ├── F2.md
│   │   ├── F3.md
│   │   ├── F4.md
│   │   ├── D1.md
│   │   ├── D2.md
│   │   ├── D3.md
│   │   ├── D4.md
│   │   ├── R1.md
│   │   ├── R2.md
│   │   ├── R3.md
│   │   ├── R4.md
│   │   ├── V1.md
│   │   ├── V2.md
│   │   ├── V3.md
│   │   └── V4.md
│   │
│   ├── cases/
│   │   ├── DIAG-THERMAL-SCHEMA-001.md
│   │   └── ...
│   │
│   └── templates/
│       ├── atomic-case-record.md
│       ├── integrated-case-record.md
│       └── case-proposal.md
│
├── benchmark/
│   ├── manifest.yaml
│   ├── public/
│   └── private/
│
├── src/
├── tests/
├── ci/
└── ...
```

The initial implementation does not need to modify the executable benchmark directory organization.

---

# 5. Case Record Schema

Every implemented or planned benchmark case should have one Markdown catalog record.

Path:

```text
catalog/cases/<case-id>.md
```

Use YAML frontmatter for fields that must be queryable by Obsidian Bases and by the Python validator.

Recommended schema:

```yaml
---
catalog_schema_version: "1.0"

case_id: DIAG-THERMAL-SCHEMA-001
title: Classify an unregistered MOOSE object failure

case_kind: atomic
track: DIAG
subcategory: D1

physics_domains:
  - thermal_energy_transport

difficulty: L1

status: in_progress
priority: normal

owner: MengnanLi91
reviewers: []

source_type: synthetic
source_name: ""
source_url: ""

base_problem_id: THERMAL-CONDUCTION-BASE-001

public_contract_ready: true
private_evaluator_ready: true
gold_submission_ready: true
mutants_ready: false
moose_validated: false
ci_passing: false
review_complete: false

github_issue: ""
github_pr: ""

tags:
  - benchmark-case
  - diag
  - d1
  - thermal
---
```

---

# 6. Controlled Vocabulary

Use a controlled vocabulary so Bases filters and CI remain reliable.

## 6.1 `status`

Allowed values:

```text
planned
in_progress
review
blocked
complete
```

Meaning:

### `planned`

Accepted benchmark idea, but implementation has not started.

### `in_progress`

A contributor is actively implementing the case.

### `review`

Implementation is considered ready for benchmark/domain review.

### `blocked`

Progress cannot continue because of a known dependency, access issue, technical problem, benchmark ambiguity, or missing data.

### `complete`

The benchmark case has passed all required validation and review conditions.

---

## 6.2 `priority`

Allowed values:

```text
low
normal
high
release_blocker
```

---

## 6.3 `case_kind`

Allowed values:

```text
atomic
integrated
```

---

## 6.4 `track`

Allowed values:

```text
FORM
DIAG
REPAIR
VERIFY
```

---

## 6.5 `subcategory`

Allowed atomic capability values:

```text
F1
F2
F3
F4
D1
D2
D3
D4
R1
R2
R3
R4
V1
V2
V3
V4
```

Integrated cases may use:

```yaml
subcategory: null
```

or omit the field if the existing schema and validator handle this consistently.

---

## 6.6 Difficulty

Use the benchmark difficulty convention:

```text
L1
L2
L3
L4
```

---

# 7. Case Record Template

Create:

```text
catalog/templates/atomic-case-record.md
```

with content similar to:

```markdown
---
catalog_schema_version: "1.0"

case_id: REPLACE_ME
title: REPLACE_ME

case_kind: atomic
track: REPLACE_ME
subcategory: REPLACE_ME

physics_domains: []

difficulty: L1

status: planned
priority: normal

owner: ""
reviewers: []

source_type: synthetic
source_name: ""
source_url: ""

base_problem_id: ""

public_contract_ready: false
private_evaluator_ready: false
gold_submission_ready: false
mutants_ready: false
moose_validated: false
ci_passing: false
review_complete: false

github_issue: ""
github_pr: ""

tags:
  - benchmark-case
---

# {{title}}

## Benchmark purpose

Explain why this case exists.

State the primary capability being isolated and what successful behavior demonstrates.

## Problem description

Describe the physical or numerical problem represented by this benchmark.

Keep this section understandable to a domain expert without requiring them to inspect the YAML contract first.

## What this case tests

Primary capability:

```text
<subcategory> — <capability name>
```

Describe exactly what should be measured.

Also explain nearby capabilities that are intentionally not being measured.

## Starting information

Describe what is supplied to the participant.

Examples:

- physical problem description,
- strong form,
- weak form,
- object plan,
- failing input,
- execution log,
- accepted executable model,
- external reference data.

## Required output

Describe what the participant must return.

This section should match the public case contract.

## Permitted actions

Summarize permitted actions.

## Prohibited actions

Summarize prohibited actions.

## Isolation rationale

Explain how this case isolates the designated capability.

For an atomic case, answer:

- What upstream truth is supplied?
- What downstream work is excluded?
- If a defect exists, is there exactly one independent primary defect?
- Could the case accidentally measure another subcategory?
- What information prevents upstream capability differences from dominating the result?

## Case construction

Explain how the benchmark case was created.

Examples:

- adapted from a verification manual,
- derived from a MOOSE example,
- generated from an MMS problem,
- created from a clean base case plus an injected mutation.

For mutation-based diagnosis/repair cases, describe the mutation family at a level appropriate for the visibility of this repository.

Do not place hidden gold answers here if the catalog is public.

## Evidence available to the participant

List participant-visible evidence.

Examples:

- input file,
- MOOSE validation log,
- PETSc output,
- residual history,
- solution field,
- experimental data,
- mesh sequence.

## Acceptance summary

Describe the high-level acceptance conditions.

Do not duplicate hidden evaluator details or private numeric thresholds into a public catalog file.

## Source and provenance

Record:

- original benchmark or source,
- citation,
- URL,
- source version,
- MOOSE application,
- MOOSE revision if applicable,
- redistribution/license notes.

## Implementation checklist

- [ ] Public contract written
- [ ] Prompt written
- [ ] Required artifacts added
- [ ] Participant-visible evidence added
- [ ] Private evaluator written
- [ ] Gold submission created
- [ ] Incorrect mutant(s) created
- [ ] Manifest entry added
- [ ] Local validation passes
- [ ] MOOSE validation/execution completed if required
- [ ] CI passes
- [ ] Domain review complete
- [ ] Benchmark-design review complete

## Files

Public case:

```text
benchmark/public/cases/<case-id>/
```

Private evaluator:

```text
benchmark/private/cases/<case-id>/
```

Manifest:

```text
benchmark/manifest.yaml
```

## Open questions

Document unresolved design questions here.

## Development notes

Record implementation notes useful for future maintainers.
```

---

# 8. Integrated Case Template

Create:

```text
catalog/templates/integrated-case-record.md
```

Integrated cases should not pretend to isolate one atomic capability.

The template should include:

```markdown
## End-to-end objective

## Physical problem

## Required workflow

## Applicable benchmark stages

- formulation
- execution
- diagnosis
- repair
- verification

## Expected deliverables

## Hard gates

## Stage-reached reporting

## Failure attribution

## Reference solution / accepted model

## Credibility evidence

## Implementation checklist
```

Integrated cases should use:

```yaml
case_kind: integrated
track: INTEGRATED
```

if supported by the existing benchmark schema.

If the executable benchmark currently uses another convention, preserve that convention and adapt only the catalog field.

---

# 9. Public/Private Information Boundary

This is important because the GitHub repository is currently public.

The catalog must not accidentally expose hidden evaluator information.

Public catalog records may include:

- benchmark purpose,
- physics problem,
- target capability,
- starting state,
- participant-visible evidence,
- required output,
- permitted/prohibited actions,
- source/provenance,
- high-level acceptance statement,
- implementation status.

Do **not** include hidden information such as:

- exact private gold answer,
- hidden mutants,
- hidden tolerance values,
- hidden diagnostic signatures,
- evaluator-only reasoning,
- unreleased reference outputs,
- private acceptance thresholds.

If future production evaluation requires genuinely secret benchmark content, move:

```text
benchmark/private/
```

to a protected evaluator repository or service.

The public repository should then contain only participant-visible material and non-secret catalog information.

---

# 10. Identity Fields That Must Stay Synchronized

Some metadata will appear in both:

```text
catalog/cases/<case-id>.md
```

and:

```text
benchmark/public/cases/<case-id>/case.yaml
```

The validator must enforce equality for shared identity fields.

At minimum validate:

```text
case_id
title
case_kind
track
subcategory
difficulty
base_problem_id
physics_domains
```

Do not automatically copy project-management fields into `case.yaml`.

Do not automatically copy participant contract fields into the catalog.

Each file has a distinct responsibility.

---

# 11. Catalog Validation CLI

Extend the existing CLI with:

```bash
uv run moose-benchmark catalog validate
```

Optionally support:

```bash
uv run moose-benchmark catalog validate --strict
```

and:

```bash
uv run moose-benchmark catalog report
```

---

## 11.1 Validation responsibilities

The validator should check:

### File/schema checks

- all case records parse as Markdown with YAML frontmatter,
- required fields exist,
- controlled vocabulary values are valid,
- `case_id` matches the filename,
- no duplicate `case_id`,
- track/subcategory combinations are valid.

### Repository consistency

- every implemented public benchmark case has a catalog record,
- every catalog record claiming an implemented case points to an existing public case,
- every `complete` case exists in the manifest,
- manifest case IDs are unique,
- catalog and `case.yaml` shared metadata match.

### File-link checks

Verify that expected files exist when readiness fields are true.

Example:

```text
public_contract_ready: true
```

requires:

```text
benchmark/public/cases/<case-id>/case.yaml
```

Likewise:

```text
private_evaluator_ready: true
```

requires the expected private evaluator file.

Do not rely only on manually checked boxes.

### Completion checks

A case must not use:

```yaml
status: complete
```

unless required readiness and validation conditions pass.

For atomic cases, the exact rule should be configurable, but a reasonable initial policy is:

```text
public_contract_ready
AND private_evaluator_ready
AND gold_submission_ready
AND mutants_ready
AND ci_passing
AND review_complete
```

For cases requiring actual MOOSE execution also require:

```text
moose_validated
```

The validator should fail if a contributor marks a case complete while required evidence is missing.

---

# 12. Derived Status vs Manually Entered Status

Keep `status` human-controlled for workflow management.

However, also compute a machine-derived readiness state in reports.

Example:

```text
workflow_status = in_progress
derived_readiness = missing_mutants
```

Do not automatically overwrite the Markdown file during validation.

The report should explain why a case cannot yet be complete.

Example:

```text
DIAG-THERMAL-SCHEMA-001
  status: review
  derived readiness: incomplete
  missing:
    - incorrect mutant submission
    - benchmark-design review
```

---

# 13. Catalog Report Command

Implement:

```bash
uv run moose-benchmark catalog report
```

The command should produce a human-readable summary.

Example:

```text
MOOSE Agent Benchmark Development Status

Total catalog cases: 42

Status
  planned       14
  in_progress   12
  review         6
  blocked        2
  complete       8

Tracks
  FORM          11 / target 30
  DIAG          12 / target 30
  REPAIR        13 / target 45
  VERIFY         6 / target 15

Atomic subcategories
  F1   3
  F2   2
  F3   2
  F4   4

  D1   4
  D2   3
  D3   3
  D4   2

  ...

Missing owners: 5
Ready for review: 6
Blocked: 2
```

Also support machine-readable output:

```bash
uv run moose-benchmark catalog report --format json
```

This allows future dashboards or GitHub Pages to consume the same data.

---

# 14. Coverage Configuration

The benchmark design currently targets an initial 120-case release:

```text
FORM      30
DIAG      30
REPAIR    45
VERIFY    15
TOTAL    120
```

Do not hard-code these numbers deep in Python.

Add a configuration file such as:

```text
catalog/coverage.yaml
```

Example:

```yaml
release: initial-120

track_targets:
  FORM: 30
  DIAG: 30
  REPAIR: 45
  VERIFY: 15

difficulty_targets:
  L1: 24
  L2: 36
  L3: 42
  L4: 18
```

Optionally add future subcategory/domain targets later.

The report should compare actual implemented/planned cases with target coverage.

---

# 15. Obsidian Dashboard

Create:

```text
catalog/Benchmark Dashboard.md
```

The page should be the first page contributors open.

Suggested content:

```markdown
# MOOSE Agent Benchmark Dashboard

## Benchmark objective

Short description of the benchmark.

## Development status

Open the Benchmark Cases database view:

![[benchmark.base]]

## Tracks

- [[tracks/FORM|FORM — Physics-to-MOOSE formulation]]
- [[tracks/DIAG|DIAG — MOOSE-native error analysis]]
- [[tracks/REPAIR|REPAIR — Repair and execution]]
- [[tracks/VERIFY|VERIFY — Verification and credibility]]

## Contributor workflow

1. Choose or propose a case.
2. Assign yourself as owner.
3. Set status to `in_progress`.
4. Implement the catalog record and benchmark files.
5. Run local validation.
6. Submit a GitHub pull request.
7. Address domain and benchmark-design review.
8. Merge after CI passes.

## Useful commands

```bash
uv sync --extra dev
uv run moose-benchmark catalog validate
uv run moose-benchmark catalog report
uv run moose-benchmark validate benchmark/manifest.yaml
uv run pytest -q
```
```

---

# 16. Obsidian Bases Views

Create one Bases configuration:

```text
catalog/benchmark.base
```

The main database should operate on:

```text
catalog/cases/*.md
```

Required views:

## 16.1 All cases

Columns:

```text
case_id
title
track
subcategory
physics_domains
difficulty
status
owner
priority
review_complete
```

---

## 16.2 Needs owner

Filter:

```text
owner is empty
AND status != complete
```

---

## 16.3 In progress

Filter:

```text
status = in_progress
```

---

## 16.4 Ready for review

Filter:

```text
status = review
```

---

## 16.5 Blocked

Filter:

```text
status = blocked
```

---

## 16.6 Complete

Filter:

```text
status = complete
```

---

## 16.7 Track views

Separate filtered views for:

```text
FORM
DIAG
REPAIR
VERIFY
```

---

## 16.8 Subcategory views

Provide easy filtering/grouping by:

```text
F1-F4
D1-D4
R1-R4
V1-V4
```

It is acceptable to implement these initially as filters or separate track/subcategory Markdown pages that embed the main Base.

Do not duplicate case data to build the views.

---

# 17. Track Pages

Create:

```text
catalog/tracks/FORM.md
catalog/tracks/DIAG.md
catalog/tracks/REPAIR.md
catalog/tracks/VERIFY.md
```

Each page should contain:

1. Track purpose.
2. Four subcategories.
3. What should and should not be measured.
4. Link/embed to filtered case view.
5. Target case count.
6. Links to benchmark-design documentation.

Example:

```markdown
# DIAG — MOOSE-native error analysis

The diagnosis track evaluates reasoning over an immutable failing artifact.

The agent may inspect supplied evidence and run only permitted diagnostics.

Repair is not scored in atomic diagnosis cases.

## Subcategories

- [[../subcategories/D1|D1 — Failure-stage classification]]
- [[../subcategories/D2|D2 — Causal-chain reconstruction]]
- [[../subcategories/D3|D3 — Root-cause localization]]
- [[../subcategories/D4|D4 — Discriminating next test]]

## Cases

<filtered Bases view>
```

---

# 18. Subcategory Pages

Create one Markdown page per atomic capability.

Example:

```text
catalog/subcategories/D3.md
```

Each page should describe:

```markdown
# D3 — Root-cause localization

## Capability

Name the cause family and locate the faulty block, object, parameter,
variable, or equation term.

## Primary grading target

Cause class, precise location, and artifact-bound evidence.

## Supplied upstream truth

Describe what must be supplied so D3 does not also score F1/F2/F3/etc.

## Excluded downstream work

Repair is not scored.

## Common case patterns

- missing constraint,
- incorrect object configuration,
- invalid coupling,
- incorrect parameter,
- equation-term defect,
- etc.

## Case-design review questions

- Is D1 already supplied or otherwise prevented from dominating?
- Is the failure chain unambiguous enough to support a gold root cause?
- Is there exactly one primary root cause?
- Is the target location objectively gradable?
- Is repair unnecessary for receiving full credit?

## Cases

<filtered Bases view>
```

These pages should encode the benchmark-design intent and help contributors create non-overlapping cases.

---

# 19. Case Proposal Workflow

Do not require every idea to immediately create benchmark directories.

Use GitHub Issues for lightweight proposals.

Add:

```text
.github/ISSUE_TEMPLATE/benchmark-case-proposal.yml
```

Fields should include:

```text
Proposed title
Candidate track
Candidate subcategory
Physics domain
Candidate difficulty
Problem/source
Why this tests the target capability
Available reference evidence
Potential overlap with other subcategories
Licensing/provenance concerns
Suggested owner
```

Lifecycle:

```text
GitHub issue
    |
    | proposal accepted
    v
catalog case record
    |
    | implementation
    v
pull request
    |
    | review + CI
    v
main
```

The issue is for discussion.

The catalog record is for accepted benchmark-development work.

---

# 20. Contributor Workflow

Document the following recommended process.

## Step 1 — Pull latest changes

```bash
git switch main
git pull
```

## Step 2 — Create a branch

```bash
git switch -c add-d3-thermal-case
```

## Step 3 — Create the catalog record

Copy:

```text
catalog/templates/atomic-case-record.md
```

to:

```text
catalog/cases/<case-id>.md
```

## Step 4 — Assign owner and status

Example:

```yaml
owner: jdoe
status: in_progress
```

## Step 5 — Implement benchmark files

Create or update:

```text
benchmark/public/cases/<case-id>/
benchmark/private/cases/<case-id>/
benchmark/manifest.yaml
```

## Step 6 — Validate locally

```bash
uv run moose-benchmark catalog validate
uv run moose-benchmark validate benchmark/manifest.yaml
uv run pytest -q
```

Run required MOOSE validation/execution if applicable.

## Step 7 — Set status to review

```yaml
status: review
```

## Step 8 — Commit

Example:

```bash
git add .
git commit -m "Add D3 thermal root-cause diagnosis case"
git push -u origin add-d3-thermal-case
```

## Step 9 — Open pull request

The PR must receive appropriate review and pass CI.

## Step 10 — Complete

Before merge or immediately after final review, set:

```yaml
status: complete
```

only if the validator confirms all completion requirements.

---

# 21. Pull Request Template

Add or update:

```text
.github/pull_request_template.md
```

Suggested benchmark-case section:

```markdown
## Benchmark case changes

Case IDs:

- ...

Primary capabilities:

- ...

Physics domains:

- ...

## Isolation review

- [ ] Each atomic case has exactly one primary capability.
- [ ] Required upstream truth is supplied.
- [ ] Downstream work cannot hide the tested capability.
- [ ] Diagnosis/repair mutation cases contain one independent primary defect unless explicitly designed as integrated/compound cases.
- [ ] Extra downstream work does not affect atomic scoring.

## Case completeness

- [ ] Catalog record added/updated.
- [ ] Public case contract added/updated.
- [ ] Private evaluator added/updated.
- [ ] Gold submission added.
- [ ] Incorrect mutant(s) added.
- [ ] Manifest updated.
- [ ] Local catalog validation passes.
- [ ] Benchmark validation passes.
- [ ] Tests pass.
- [ ] MOOSE execution/verification performed when required.

## Review

- [ ] Domain review completed.
- [ ] Benchmark-design review completed.
```

---

# 22. Review Roles

For substantial benchmark cases, distinguish two kinds of review.

## Domain review

Checks:

- governing physics,
- equations,
- BCs/ICs,
- constitutive relations,
- numerical setup,
- reference solution,
- scientific credibility.

## Benchmark-design review

Checks:

- atomic capability isolation,
- correct track/subcategory,
- appropriate evidence,
- no unintended cross-credit,
- objective grading,
- correct public/private boundary,
- sufficient negative/mutant tests.

A reviewer may fill both roles, but the review concerns should remain conceptually distinct.

---

# 23. CI Integration

Add catalog validation to existing CI.

Suggested sequence:

```bash
uv sync --extra dev

uv run moose-benchmark catalog validate --strict

uv run moose-benchmark validate benchmark/manifest.yaml

uv run pytest -q
```

If a real MOOSE executable is available on a dedicated runner:

```bash
ci/moose_smoke.sh
```

or future case-specific validation jobs.

CI should fail on catalog inconsistency.

---

# 24. CI Checks for Changed Cases

A later optimization may inspect the Git diff and run only expensive validation for changed benchmark cases.

Example future command:

```bash
uv run moose-benchmark changed-cases origin/main HEAD
```

Output:

```text
DIAG-THERMAL-SCHEMA-001
R2-SOLID-JACOBIAN-003
```

Then expensive MOOSE jobs can target those cases.

This is not required for the initial implementation.

---

# 25. Tests to Add

Add unit tests for the catalog subsystem.

Suggested files:

```text
tests/catalog/
  test_catalog_loader.py
  test_catalog_schema.py
  test_catalog_consistency.py
  test_catalog_completion.py
  test_catalog_report.py
```

Required test cases:

### Parsing

- valid Markdown frontmatter parses,
- missing frontmatter fails,
- malformed YAML fails.

### Controlled vocabulary

- invalid status fails,
- invalid track fails,
- invalid subcategory fails,
- invalid difficulty fails.

### Identity

- filename must match `case_id`,
- duplicate `case_id` fails.

### Contract consistency

- catalog track mismatch with `case.yaml` fails,
- title mismatch fails,
- physics-domain mismatch fails,
- missing public case fails for implemented records.

### Completion policy

- `status: complete` with missing private evaluator fails,
- `status: complete` with missing mutant fails,
- `status: complete` with failed CI readiness fails,
- valid complete case passes.

### Reporting

- correct count per status,
- correct count per track,
- correct count per subcategory,
- target coverage computed correctly.

---

# 26. Suggested Python Package Structure

Extend the existing package rather than create a standalone application.

Suggested additions:

```text
src/moose_benchmark/
  catalog/
    __init__.py
    models.py
    loader.py
    validator.py
    report.py
    coverage.py
```

Responsibilities:

## `models.py`

Typed catalog schema.

Prefer the same validation/data-model approach already used by the repository.

## `loader.py`

Load:

```text
catalog/cases/*.md
```

Parse YAML frontmatter.

## `validator.py`

Validate:

- schema,
- controlled values,
- cross-file consistency,
- completion rules,
- file existence.

## `coverage.py`

Load target coverage configuration and compute actual coverage.

## `report.py`

Generate:

- text report,
- JSON report.

---

# 27. Markdown Frontmatter Parsing

Use a well-supported parser instead of ad hoc regular expressions if possible.

Requirements:

- preserve normal Markdown body,
- parse YAML frontmatter deterministically,
- produce useful line/file errors,
- avoid arbitrary code execution.

If the current project already has a YAML dependency, reuse it where appropriate.

---

# 28. Obsidian Configuration

Commit only minimal shared configuration.

Recommended to share:

- enabled core plugin needed for Bases,
- possibly workspace-independent settings useful to the project.

Avoid committing user-specific state such as:

- window layout,
- recently opened files,
- local hotkeys unless intentionally standardized,
- machine-specific plugin state.

Review `.gitignore` for Obsidian-generated local state.

The project should remain completely usable without Obsidian.

---

# 29. Obsidian Git

Obsidian Git may be recommended but should not be required.

Recommended contributor behavior:

```text
manual pull
manual commit
manual push
```

Do not configure automated periodic commits for benchmark development.

Meaningful commits are important for review.

Good commit:

```text
Add V1 phase-field MMS verification case
```

Avoid generated commits such as:

```text
vault backup 2026-09-16 15:42
```

---

# 30. Do Not Duplicate Status in GitHub Projects

Do not make GitHub Projects another authoritative project-status database.

The source of truth for case-development status should be:

```text
catalog/cases/*.md
```

GitHub Issues are useful for discussion.

GitHub Pull Requests are useful for review.

GitHub Projects may be added later as a generated/read-only view if desired, but manual two-way synchronization should be avoided.

---

# 31. Optional Future Web View

The Markdown catalog should be designed so the repository can later generate a public web portal.

Possible future stack:

```text
catalog Markdown
      |
      v
static site generator
      |
      v
GitHub Pages
```

Potential tools:

- MkDocs,
- Material for MkDocs,
- custom static report.

Do not build this in the first implementation unless trivial.

The first milestone is the Obsidian + Git + CI workflow.

---

# 32. Suggested First Implementation Milestone

Implement the collaboration layer without restructuring the benchmark engine.

Required changes:

```text
1. Add catalog directory.
2. Add catalog schema.
3. Add atomic case template.
4. Add integrated case template.
5. Add benchmark dashboard.
6. Add track pages.
7. Add 16 subcategory pages.
8. Add benchmark.base.
9. Add coverage configuration.
10. Add catalog loader.
11. Add catalog validator.
12. Add catalog report.
13. Add CLI commands.
14. Add tests.
15. Add CI validation.
16. Add GitHub issue template.
17. Add/update PR template.
18. Add a catalog record for the existing
    DIAG-THERMAL-SCHEMA-001 example.
19. Update README contributor instructions.
```

Do not redesign the scorer, evaluator, public/private case contract, or submission format as part of this milestone unless required by a catalog integration bug.

---

# 33. Implementation Phases

## Phase 1 — Minimal catalog

Deliver:

- `catalog/`,
- templates,
- one example case,
- Markdown schema,
- dashboard,
- track/subcategory documentation.

Acceptance:

```text
A contributor can open the repository as an Obsidian vault,
find the existing benchmark case, read its human-facing description,
and edit its development metadata.
```

---

## Phase 2 — Validation

Deliver:

```bash
moose-benchmark catalog validate
```

Acceptance:

```text
CI detects invalid metadata, missing case records,
case-ID mismatch, and disagreement between catalog metadata
and case.yaml.
```

---

## Phase 3 — Coverage/reporting

Deliver:

```bash
moose-benchmark catalog report
```

and:

```text
catalog/coverage.yaml
```

Acceptance:

```text
The team can see progress toward the 120-case release
by status, track, subcategory, difficulty, and physics domain.
```

---

## Phase 4 — Contributor workflow

Deliver:

- issue template,
- PR template,
- contributor documentation,
- review checklist.

Acceptance:

```text
A new contributor can propose, implement, validate,
submit, and review a benchmark case using the documented workflow.
```

---

## Phase 5 — Optional generated public site

Only after the Markdown catalog is stable.

---

# 34. Definition of Done for the Collaboration System

The implementation is complete when all of the following are true.

## Repository usability

- [ ] Repository root opens cleanly as an Obsidian vault.
- [ ] Existing Python/CLI workflows remain unchanged.
- [ ] Obsidian is optional.

## Dashboard

- [ ] All benchmark cases are visible.
- [ ] Cases can be filtered by track.
- [ ] Cases can be filtered by subcategory.
- [ ] Cases can be filtered by status.
- [ ] Cases can be filtered by owner.
- [ ] Cases can be filtered by physics domain.
- [ ] Cases can be filtered by difficulty.

## Case detail

- [ ] Every implemented case has a human-facing Markdown record.
- [ ] Case purpose is documented.
- [ ] Target capability is documented.
- [ ] Starting information is documented.
- [ ] Required output is documented.
- [ ] Isolation rationale is documented.
- [ ] Source/provenance is documented.
- [ ] Links to executable benchmark files work.

## Validation

- [ ] Shared identity metadata is automatically cross-checked.
- [ ] Duplicate case IDs fail validation.
- [ ] Missing catalog records fail strict validation.
- [ ] Invalid status values fail.
- [ ] Invalid taxonomy values fail.
- [ ] Invalid complete status fails.

## CI

- [ ] Catalog validation runs on pull requests.
- [ ] Existing benchmark validation still runs.
- [ ] Existing unit tests still run.

## Collaboration

- [ ] Benchmark case proposal issue template exists.
- [ ] Pull request checklist exists.
- [ ] Contributor documentation describes the full workflow.
- [ ] Git history remains the authoritative record of changes.

---

# 35. Non-Goals for the First Implementation

Do not implement the following yet:

- custom web application,
- external database,
- real-time multiplayer editing,
- automatic GitHub Project synchronization,
- automatic status edits performed by CI,
- redesign of benchmark scoring,
- redesign of public/private evaluator contracts,
- redesign of answer bundles,
- full public leaderboard,
- distributed execution service,
- permissions system inside Obsidian.

Keep the first implementation focused.

---

# 36. Recommended Codex Execution Order

Codex should implement this incrementally.

## Step 1

Inspect the existing repository:

```text
README.md
benchmark/manifest.yaml
benchmark/public/
benchmark/private/
templates/
src/moose_benchmark/
tests/
.github/
```

Reuse existing schema/model conventions.

Do not invent incompatible patterns.

## Step 2

Create catalog data model and Markdown parser.

## Step 3

Create catalog files/templates and migrate the existing example case.

## Step 4

Implement `catalog validate`.

## Step 5

Add tests.

## Step 6

Implement `catalog report`.

## Step 7

Create Obsidian Bases/dashboard views.

## Step 8

Add CI integration.

## Step 9

Add issue/PR templates and contributor documentation.

## Step 10

Run the full repository validation and test suite.

---

# 37. Expected Final Repository Experience

A benchmark developer should be able to:

```text
git pull
```

open the repository in Obsidian, navigate to:

```text
catalog/Benchmark Dashboard.md
```

see something conceptually similar to:

```text
MOOSE Agent Benchmark

Initial target: 120 cases

FORM       12 / 30
DIAG        8 / 30
REPAIR      5 / 45
VERIFY      3 / 15

Complete         8
Review           6
In progress     12
Planned         14
Blocked          2
```

select:

```text
DIAG -> D3 -> <case>
```

and immediately see:

```text
Benchmark purpose
Problem description
What the case tests
Starting information
Required output
Permitted/prohibited actions
Isolation rationale
Case construction
Evidence
Acceptance summary
Source/provenance
Implementation checklist
Owner/reviewers
Open questions
Links to benchmark files
```

The contributor edits the Markdown and benchmark files, runs:

```bash
uv run moose-benchmark catalog validate
uv run moose-benchmark validate benchmark/manifest.yaml
uv run pytest -q
```

then commits the branch and opens a GitHub pull request.

The pull request becomes the collaboration and review mechanism.

This gives the project a human-friendly benchmark-development interface while preserving Git, CI, executable validation, and benchmark contracts as the authoritative engineering workflow.
