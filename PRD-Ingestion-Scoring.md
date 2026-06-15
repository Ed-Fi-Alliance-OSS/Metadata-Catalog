# Metadata Catalog — Ingestion & Scoring PRD

> **Status:** Draft · **Last updated:** 2026-06-15 · **Owner:** Ed-Fi Alliance Staff

---

## 1. Product Overview

### 1.1 Background

The Data Standard Metadata Collection and Usage initiative collects, stores, and analyzes metadata about Ed-Fi Data Standard implementations — specifically the API specifications and supplemental data collection rules that state education agencies (SEAs) publish for vendors. Two high-value workflows sit at the center of the initiative: a **scoring engine** that measures the complexity of each SEA's data collection requirements, and a **cluster analysis** that surfaces cross-state patterns.

This PRD covers the phase 2 of automated ingestion and NACHOS scoring

This document covers the two pipelines that make those workflows possible:

* the **Ingestion Pipeline**, which converts raw SEA artifacts (Swagger/OAS files and supplemental business documentation) into structured, element-level records.
* and the **Scoring Engine**, which assigns NACHOS complexity scores to those records.

Access the following PRD for an overview of the overall Metadata Project.  **Link To be added**

### 1.2 Problem Statement

Vendor integration costs are a widely-cited barrier to expanding K-12 data access. Those costs stem from complex, aggregated, and inconsistent requirements across states. Without a systematic way to extract and score SEA specification metadata, Ed-Fi staff have no scalable method to:

* Measure the complexity of a state's data collection requirements.
* Compare complexity across states.
* Identify which specific elements drive implementation burden.
* Prioritize standardization conversations with the highest-leverage states.

Manual scoring is slow, inconsistent across reviewers, and does not scale to the number of states and elements in scope. An LLM-assisted pipeline that produces auditable, human-overridable scores addresses all four gaps.

### 1.3 Target Users for this PRD

| User | Role |
|---|---|
| **Ed-Fi Alliance Staff** | Primary operators of both pipelines; consumers of score reports and standardization analytics |

Excluded from this PRD are: Vendors and SEA Staff.  They will be interested in read only capacity to some of the data. Vendors and SEA Staff may be given read access to some of the data in the future. SEA Staff may be given access to write a commitment form, and submit corrections to the scoring and business requirements.

### 1.4 Design Principles

**Auditability over automation.** Every score is traceable to an evidence record. A score without a traceable rationale is not acceptable.

**Human override is a feature, not an exception.** Staff can override any machine-assigned score. Overrides and their rationale are persisted alongside the original evidence record.

**Disagreement is signal.** Where the engine and a human reviewer assign different tiers, those rows are routed for review — they may surface a methodology question, not just an engine error. They are not silently tuned away to match one reviewer.

**Distributions over rankings.** Cross-state comparisons SHALL report Score Context distributions (Implementation Shape, Documentation Style, Documentation Gap), not a single-scalar ranking that can misread documentation culture as quality.

**No student data, no PII.** The system is scoped exclusively to specification metadata. No student data or personally identifiable information flows through any component at any time.

---

## 2. Functional Requirements

### 2.1 JTBD 1 — Ingestion Pipeline - IDENTIFIED AS "JTBD 1: Scoring" in Initial PRD

**Story:** As Ed-Fi Alliance Staff, I want to load a state's Swagger/OAS specification and supplemental business documentation into a structured catalog, so that I have clean, element-level records ready for scoring and analysis.

#### 2.1.1 Source Input Collection

The system SHALL present an input form that accepts one or both of the following source types for the state's API specification:

| Input Type | Description |
|---|---|
| **File upload** | One or more Swagger/OAS files (`.json` or `.yaml`) uploaded directly |
| **URL** | A publicly accessible URL pointing to a Swagger/OAS document |

Possible formats:

* URL to a webpage
* PDF files
* Excel files or worksheets, with multiple tabs
* URL to a webpage that is in Confluence format.
* Excel files with inside links to other webpages.

**TBD: Does the ingestion UML need to know the format type for these sources.  Have we seen word documents?**

The system SHALL accept up to **10** total paths or files per ingestion run across both source types combined.

The system SHALL validate that each provided file or URL resolves to a parseable Swagger/OAS document before proceeding. If a source fails validation the system SHALL report the failure and allow the user to correct or remove the invalid entry without re-submitting valid sources.

> [!NOTE: DOES THIS LIMIT HELP CODING?]
> The 10-source limit applies to a single ingestion run. A state with more than 10 specification artifacts should be broken into multiple runs or the artifacts consolidated before upload.

Columns resulting the end of this process:

| Column | Description |
|---|---|
| `entity_name` | Entity name as it appears in the state's Swagger |
| `standard_entity` | Best-match entity name from the Ed-Fi Data Standard |
| `domain` | Ed-Fi domain (e.g., Student, Enrollment, Assessment) |
| `match_confidence` | High / Medium / Low / Unmatched |
| `match_notes` | Flags for extension entities, renamed entities, or descriptor overloads |
| `element_name` | element name from the state definition |
| `element_type` | entity name from the Ed-Fi Data Standard |
| `element_cardinality` | identify keys, optional, required, optional conditional |

> [DO WE INCLUDE THESE?]
| `Ed-FI_element_name` | Best-match entity name from the state definition |
| `Ed-FI_element_type` | Best-match entity name from the Ed-Fi Data Standard |
| `standard_entity` | Best-match entity name from the Ed-Fi Data Standard |

#### 2.1.2 Entity Matching to Standard Domain

After parsing the Swagger/OAS document(s), the system SHALL match each API entity (resource, descriptor, association) to its corresponding **Ed-Fi Data Standard domain definition** using a standard domain registry.

The system SHALL produce a match report with the following columns at minimum:

| Column | Description |
|---|---|
| `entity_name` | Entity name as it appears in the state's Swagger |
| `standard_entity` | Best-match entity name from the Ed-Fi Data Standard |
| `domain` | Ed-Fi domain (e.g., Student, Enrollment, Assessment) |
| `match_confidence` | High / Medium / Low / Unmatched |
| `match_notes` | Flags for extension entities, renamed entities, or descriptor overloads |

Unmatched entities SHALL be flagged for staff review rather than silently dropped. Staff MAY resolve an unmatched entity by manually mapping it or marking it as a state-specific extension.

**Question: do we produce a report to pull elements that do not match other state definitions**

#### 2.1.3 Business Logic Extraction IDENTIFIED AS "JBTD 3: Standardization of Data Collection Metadata " in Initial PRD

**Story:** As Ed-Fi Alliance Staff, I want to extract data collection requirements from any SEA and store them in a standardized manner, so that I can analyze and help improve the SEA's requirements.

**Acceptance Criteria:**

* Standardized metadata storage with a schema that can represent normalized metadata plus provenance and curation status
* The standardized repository SHALL preserve provenance and curation status for each material metadata element, including whether it came from exact artifact import, inexact supplemental extraction, or manual editing.
* Phase 1 minimum acceptance: Ed-Fi Alliance Staff MUST be able to load, store, and manually curate standardized metadata in that repository even before any scoring or other downstream analytical consumer is delivered.
* Ed-Fi Alliance Staff MUST be able to manually curate standardized metadata regardless of whether it originated from exact import or inexact extraction.
* Phase 2 downstream-consumer readiness: the standardized repository SHALL expose standardized metadata programmatically to the scoring engine and other downstream use cases once those consumers are introduced.
* The schema SHALL be at the **(resource, property) grain** and SHALL map state documentation onto the **canonical Ed-Fi Data Standard surface**, so a source lens and an API-model (coverage) lens are possible.
* The repository SHALL retain the **source narrative text** (or stable, normalized references) sufficient to validate and display _cited spans_; a cited span cannot be shown against source text that was not retained. (The Phase-1 schema should anticipate this.)

The system SHALL accept a second input form — separate from the Swagger input — requesting the path(s) to the state's supplemental **business documentation** (e.g., data dictionaries, collection guides, data submission manuals, annotated spreadsheets).

This form SHALL accept up to **10** total file paths or URLs. Supported formats include PDF, Word (.docx), Excel (.xlsx), plain text, and HTML.

The system SHALL run an LLM extraction process that operates at the **element level**, associating documented business rules to the specific API field or descriptor they govern. The extraction SHALL capture:

* The element name (field path within the entity)
* The extracted business logic text (verbatim quoted span from the source document)
* The source document and page/section reference (cited span)
* A confidence score for the extraction

> [!NOTE]
> The extraction LLM operates on documentation content only. It does not access student data or any data source beyond the files and URLs provided in this form.

#### 2.1.4 Scope Classification

The system SHALL run a scope classification process that determines, for each element in the Swagger, whether it is **in-scope** or **out-of-scope** for the state's data collection.

An element is classified as in-scope if the state's Swagger or business documentation explicitly requires, uses, or references it. Elements present in the Ed-Fi Data Standard but absent from — or explicitly excluded by — the state's artifacts are classified as out-of-scope.

The classification process SHALL emit a confidence level (High / Medium / Low) and a brief rationale for each out-of-scope classification. Staff MAY override any classification.

#### 2.1.5 Ingestion Summary Report

Upon completion of an ingestion run the system SHALL display an ingestion summary report. The report SHALL include, at minimum:

| Metric | Description |
|---|---|
| Total elements retrieved | Count of all element-level records parsed from the Swagger source(s) |
| Elements with business logic | Count of elements for which at least one business rule was extracted |
| Elements in scope | Count of elements classified as in-scope |
| Elements out of scope | Count of elements classified as out-of-scope |
| Unmatched entities | Count of entities that could not be matched to the Ed-Fi Data Standard |
| Extraction confidence distribution | Breakdown of High / Medium / Low confidence extractions |

The report SHALL be exportable as CSV and as a rendered HTML table.

#### 2.1.6 Persistence

After staff review and approval of an ingestion run, the system SHALL write the following data to the storage database for each element:

| Field | Description |
|---|---|
| `run_id` | Unique identifier for the ingestion run |
| `state_id` | State identifier |
| `entity_name` | Entity name from the state's Swagger |
| `element_path` | Full field path within the entity |
| `standard_entity` | Matched Ed-Fi Data Standard entity |
| `domain` | Ed-Fi domain |
| `business_logic` | Extracted business rule text (null if none) |
| `cited_span` | Source document reference for the business logic |
| `in_scope` | Boolean scope flag |
| `scope_confidence` | High / Medium / Low |
| `created_at` | Timestamp of record creation |
| `run_approved_by` | Staff member who approved the run |

The write operation SHALL be transactional. A partially written run SHALL be rolled back in full, not partially committed.

---

### 2.2 JTBD 2 — Scoring Engine - ALSO IDENTIFIED AS "JTBD1: Scoring Engine" in Initial PRD

**Story:** As Ed-Fi Alliance Staff — on behalf of Vendors — I want to run a scoring engine that assigns a complexity score to each SEA data collection requirement, so that I can help the SEA align their data collection with the Ed-Fi Data Standard.

#### 2.2.1 Scoring LLM Execution

**Story:** As Ed-Fi Alliance Staff — on behalf of Vendors — I want to run a scoring engine that assigns a complexity score to each SEA data collection requirement, so that I can help the SEA align their data collection with the Ed-Fi Data Standard.

**Acceptance Criteria:**

* Ed-Fi Alliance's existing manual scoring SHALL seed the evaluation set, treated as **human-scored observations** (used to measure agreement), not infallible ground truth. Before formal acceptance, Ed-Fi SHALL define the evaluation set and SHOULD grow it — ideally with more than one reviewer — so acceptance testing is credible.
* >= 80% score-tier alignment on rows scored by both the engine and a reviewer.
* >= 0.7 F1 overall and >= 0.9 F1 for "simple" (score-zero) rows, measured against the evaluation set as a calibration signal (not proof of correctness).
* >= 0.6 Cohen's Kappa (inter-rater agreement).
* Where the engine and a reviewer disagree on tier, treat those rows as the calibration target — they may point to a methodology question, not just an engine error, so route them to review rather than tuning them away to match one reviewer.
* Ed-Fi Alliance Staff MUST be able to override the assigned score based on human judgment, with the override and rationale recorded against the row's evidence record.
* **NACHOS Score Context (peer signal).** Every scored row SHALL carry, beside the scalar: _Implementation Shape_ (structural complexity, deterministic from the Swagger/API model), _Documentation Style_ (Prescriptive | Conceptual | Cross-reference | Regulatory | Unspecified), and _Documentation Gap_ (complex structure the documentation under-explains).
* **Semantic-fidelity adjustment.** When a state narrows, broadens, or changes the canonical Ed-Fi meaning of an element, apply an adjustment (exact magnitudes subject to Alliance methodology review).
* **Evidence record (per row).** Every score SHALL emit a cached evidence record (extracted facts, confidence, cited spans, firing rule path, review routing) — extending the provenance model (NFR-DATA-2/3) to the scoring layer, so a score is inspectable without re-running the model.
* Cross-state outputs SHALL report Score Context **distributions**, not a single-scalar ranking that can misread documentation culture as quality.

The system SHALL run a Scoring LLM against each in-scope element record produced by the Ingestion Pipeline. For each element the LLM SHALL extract and emit an **evidence record** containing, at minimum:

| Field | Description |
|---|---|
| `element_path` | Full field path within the entity |
| `conditional_logic` | Boolean — does the row describe conditional or branching logic? |
| `cross_entity_logic` | Boolean — does the row involve lookups or constraints across entity boundaries? |
| `aggregation` | Boolean — does the row require computed aggregates or derived values? |
| `concatenation` | Boolean — does the row require string construction from multiple fields? |
| `semantic_divergence` | Boolean — does the state narrow, broaden, or redefine the canonical Ed-Fi meaning? |
| `documentation_style` | `Prescriptive` \| `Conceptual` \| `Cross-reference` \| `Regulatory` \| `Unspecified` |
| `extension_necessity` | Boolean — does the element require a non-standard extension or descriptor override? |
| `cited_spans` | List of verbatim excerpts from source documentation that support the above flags |
| `nachos_score` | Base NACHOS scalar (integer) |
| `adjusted_nachos` | NACHOS score after semantic-fidelity adjustment (integer) |
| `adjustment_rationale` | Plain-text explanation of any adjustment applied |
| `candidate_recommendations` | List of suggested simplification or standardization actions |
| `firing_rule_path` | The ordered list of rules from the rule cascade that produced this score |
| `confidence` | Overall confidence in the score assignment (High / Medium / Low) |
| `review_routing` | `Auto-accept` \| `Route-for-review` (see §2.2.2) |

> [!NOTE]
> **NACHOS Score Context (peer signal).** Every scored row SHALL carry, alongside the scalar score:
>
> * **Implementation Shape** — structural complexity, deterministic from the Swagger/API model
> * **Documentation Style** — one of: Prescriptive, Conceptual, Cross-reference, Regulatory, Unspecified
> * **Documentation Gap** — flag for complex structures the documentation under-explains

> [!NOTE]
> **Semantic-fidelity adjustment.** When a state narrows, broadens, or changes the canonical Ed-Fi meaning of an element, an adjustment SHALL be applied to the base NACHOS score. Exact adjustment magnitudes are subject to Alliance methodology review and SHALL be configurable without a code deployment.

#### 2.2.2 Rule Cascade

The scoring logic SHALL implement the rule cascade defined in the **POC Recommendation document (page 11)**. The rule cascade determines which combination of extracted flags maps to which NACHOS tier and drives the `firing_rule_path` field in the evidence record.

> [!IMPORTANT]
> Reference: _POC Recommendation document, page 11 — Rule Cascade table_. The rule cascade is the authoritative source for score assignment logic. Any discrepancy between this PRD and that document should be resolved in favor of the POC Recommendation document pending a formal methodology review.

Staff SHALL be able to inspect the full `firing_rule_path` for any scored element to understand exactly which rules fired.

#### 2.2.3 Score Reports

Upon completion of a scoring run the system SHALL produce a tabular score report. The report SHALL include, at minimum, one row per scored element with the following columns:

| Column | Description |
|---|---|
| `entity_name` | Entity name |
| `element_path` | Full field path |
| `domain` | Ed-Fi domain |
| `nachos_score` | Base NACHOS scalar |
| `adjusted_nachos` | Adjusted NACHOS scalar |
| `documentation_style` | Documentation style classification |
| `implementation_shape` | Structural complexity flag |
| `documentation_gap` | Boolean |
| `review_routing` | Auto-accept or Route-for-review |
| `has_override` | Boolean — has this row been manually overridden by staff? |

The report SHALL be sortable and filterable by score, adjusted score, domain, documentation style, and review routing. It SHALL be exportable as CSV.

Cross-state score reports SHALL report **Score Context distributions** (counts and percentages by Documentation Style, Implementation Shape tier, and Documentation Gap rate) rather than a single aggregate ranking.

#### 2.2.4 Score Persistence

After a scoring run is approved by staff, the system SHALL write scores to the storage database, extending each element record with the following fields:

| Field | Description |
|---|---|
| `scoring_run_id` | Unique identifier for the scoring run |
| `nachos_score` | Base NACHOS scalar |
| `adjusted_nachos` | Adjusted NACHOS scalar |
| `implementation_shape` | Structural complexity classification |
| `documentation_style` | Documentation style classification |
| `documentation_gap` | Boolean |
| `evidence_record` | Full JSON evidence record (all LLM-extracted fields) |
| `firing_rule_path` | Ordered rule list that produced the score |
| `review_routing` | Auto-accept or Route-for-review |
| `override_score` | Staff-assigned score (null if not overridden) |
| `override_rationale` | Staff-provided rationale for override (null if not overridden) |
| `override_by` | Staff member who applied the override (null if not overridden) |
| `scored_at` | Timestamp of score assignment |

The evidence record SHALL be stored in full so that any score is inspectable without re-running the model.

#### 2.2.5 Scored Element Forms

The system SHALL produce two filtered views (exportable as printable/shareable forms) from a completed scoring run:

**Form A — Elements Requiring Review** (`adjusted_nachos > 0`)

All elements where the Adjusted NACHOS score is greater than zero, sorted by adjusted score descending. This form surfaces elements that carry implementation complexity and are candidates for standardization conversations with the SEA.

**Form B — Simple Elements** (`adjusted_nachos = 0`)

All elements where the Adjusted NACHOS score equals zero. These elements are assessed as straightforward implementations with no deviation from the canonical Ed-Fi definition. A high F1 score on this form (target >= 0.9) is a key quality signal.

Both forms SHALL display, at minimum: entity name, element path, domain, base NACHOS score, adjusted NACHOS score, documentation style, and any candidate recommendations.

---

### 2.3 JTBD 3 — Score Evaluation Analytics _(TBD)_

Analysis of aggregate score data across states and across time is scoped for a future phase. Requirements will be defined separately.

---

## 3. Non-Functional Requirements

### 3.1 Implemented Requirements

| ID | Category | Requirement | Implementation |
|---|---|---|---|
| NFR-PERF-1 | Performance | Ingestion of a single-state Swagger file (up to 500 endpoints) SHALL complete within 5 minutes | Async job queue; progress indicator displayed to user |
| NFR-PERF-2 | Performance | Scoring run for up to 2,000 elements SHALL complete within 15 minutes | Batched LLM calls; parallel processing where element order permits |
| NFR-DATA-1 | Data Integrity | All ingestion and scoring runs SHALL be transactional — no partial writes | Database transaction wrapping each run |
| NFR-DATA-2 | Provenance | Every ingestion record SHALL carry a `run_id`, `state_id`, and `created_at` timestamp | Applied at write time |
| NFR-DATA-3 | Provenance | Every score SHALL carry a full evidence record persisted alongside the scalar | `evidence_record` JSON column on score table |
| NFR-SEC-1 | Security | No student data or PII SHALL flow through any pipeline component | Input validation at ingestion form; static analysis gate in CI |
| NFR-ACC-1 | Accessibility | All reports and forms SHALL meet WCAG 2.1 AA | Verified with automated accessibility checker in CI |

### 3.2 Quality Gates (Scoring Engine)

| ID | Metric | Target | Notes |
|---|---|---|---|
| QG-1 | Score-tier alignment | >= 80% | Measured against the evaluation set seeded by Ed-Fi's existing manual scores, treated as human-scored observations, not ground truth |
| QG-2 | F1 (overall) | >= 0.7 | Calibration signal against evaluation set |
| QG-3 | F1 (simple / score-zero rows) | >= 0.9 | High precision on simple rows is critical — false positives here create unnecessary review burden |
| QG-4 | Cohen's Kappa | >= 0.6 | Inter-rater agreement between engine and human reviewer |
| QG-5 | Disagreement routing | 100% of tier disagreements routed for review | Disagreements are treated as calibration signal, not auto-resolved |

> [!NOTE]
> Before formal acceptance testing, Ed-Fi Alliance SHALL define the composition of the evaluation set and SHOULD grow it — ideally with more than one reviewer — so that acceptance metrics are credible. The evaluation set is a living artifact, not a one-time snapshot.

---

## 4. Architecture

### 4.1 Technology Stack

> [!NOTE: TO BE VALIDATED]
| Component | Technology | Notes |
|---|---|---|
| Ingestion LLM | Claude (Anthropic) | Configurable model; defaults to claude-sonnet-4-6 |
| Scoring LLM | Claude (Anthropic) | Same model pool; scoring prompt is distinct from ingestion prompt |
| Storage | PostgreSQL | Element catalog, evidence records, score tables |
| Job Queue | To be determined | Async execution of ingestion and scoring runs |
| API layer | To be determined | REST endpoints for form submissions, run status, report export |
| Frontend | To be determined | Input forms, progress views, report tables, scored element forms |

### 4.2 Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  INGESTION PIPELINE                                                  │
│                                                                      │
│  [User: Swagger file/URL]                                            │
│         │                                                            │
│         ▼                                                            │
│  Parse & Validate OAS  ──► Entity Match to Ed-Fi Domain Registry    │
│         │                                                            │
│  [User: Business doc paths/URLs]                                     │
│         │                                                            │
│         ▼                                                            │
│  Business Logic Extraction LLM  (element-level, with cited spans)   │
│         │                                                            │
│         ▼                                                            │
│  Scope Classification  ──► Ingestion Summary Report                 │
│         │                                                            │
│         ▼                                                            │
│  [Staff review & approve]                                            │
│         │                                                            │
│         ▼                                                            │
│  Write to Storage DB  (elements + business logic + scope flags)     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  SCORING ENGINE                                                      │
│                                                                      │
│  Read in-scope elements from Storage DB                             │
│         │                                                            │
│         ▼                                                            │
│  Scoring LLM  ──► Evidence Record (flags, cited spans, confidence)  │
│         │                                                            │
│         ▼                                                            │
│  Rule Cascade  ──► NACHOS Score + Adjusted NACHOS                   │
│         │                                                            │
│         ▼                                                            │
│  Score Report (tabular) + Form A (adj > 0) + Form B (adj = 0)       │
│         │                                                            │
│         ▼                                                            │
│  [Staff review; override where needed]                              │
│         │                                                            │
│         ▼                                                            │
│  Write scores + evidence records to Storage DB                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.3 Data Model (Key Tables)

| Table | Primary Key | Key Columns |
|---|---|---|
| `ingestion_runs` | `run_id` | `state_id`, `created_at`, `approved_by`, `status` |
| `elements` | `element_id` | `run_id`, `state_id`, `entity_name`, `element_path`, `standard_entity`, `domain`, `in_scope`, `business_logic`, `cited_span` |
| `scoring_runs` | `scoring_run_id` | `run_id` (FK → ingestion_runs), `created_at`, `approved_by`, `status` |
| `scores` | `score_id` | `element_id` (FK → elements), `scoring_run_id`, `nachos_score`, `adjusted_nachos`, `evidence_record` (JSON), `override_score`, `override_by` |

---

## 5. Out of Scope

The following are explicitly out of scope for this PRD:

* JTBD 3 (Score Evaluation Analytics) — requirements TBD in a subsequent document
* Student data of any kind
* Real-time or webhook-based specification monitoring (batch ingestion only)
* Direct SEA portal access or automated fetching from SEA systems
* Vendor-facing score exposure (internal Ed-Fi staff use only in this phase)
* Natural language query interface (separate capability in the broader initiative)
* Cluster analysis across states (separate capability)

---

## 6. Backlog

Active issues are tracked in the project issue tracker. The following items are known open questions as of this draft:

| ID | Area | Question | Status |
|---|---|---|---|
| TBD | Scoring | Exact NACHOS adjustment magnitudes for semantic divergence cases | Pending Alliance methodology review |
| TBD | Ingestion | Handling of multi-version Swagger files for the same state | Open |
| TBD | Scoring | Evaluation set composition and reviewer assignment | Ed-Fi SHALL define before acceptance testing |
| TBD | Architecture | Job queue technology selection | Open |
| TBD | Reporting | Format and delivery mechanism for cross-state distribution reports | Open |

---

## 7. Environment Variable Reference

### 7.1 Ingestion Pipeline

| Variable | Description | Default |
|---|---|---|
| `INGESTION_LLM_MODEL` | Claude model ID for business logic extraction | `claude-sonnet-4-6` |
| `INGESTION_LLM_MAX_TOKENS` | Max tokens per extraction call | `4096` |
| `INGESTION_MAX_SOURCES` | Maximum files/URLs per ingestion run | `10` |
| `INGESTION_SUPPORTED_DOC_FORMATS` | Comma-separated list of accepted doc extensions | `pdf,docx,xlsx,txt,html` |
| `DB_CONNECTION_STRING` | PostgreSQL connection string | _(required)_ |

### 7.2 Scoring Engine

| Variable | Description | Default |
|---|---|---|
| `SCORING_LLM_MODEL` | Claude model ID for scoring | `claude-sonnet-4-6` |
| `SCORING_LLM_MAX_TOKENS` | Max tokens per scoring call | `4096` |
| `SCORING_BATCH_SIZE` | Elements per LLM batch call | `25` |
| `NACHOS_ADJUSTMENT_CONFIG` | Path to YAML file defining semantic-fidelity adjustment magnitudes | `config/nachos-adjustments.yaml` |
| `RULE_CASCADE_CONFIG` | Path to YAML file defining the rule cascade | `config/rule-cascade.yaml` |
| `QG_TIER_ALIGNMENT_THRESHOLD` | Score-tier alignment quality gate threshold | `0.80` |
| `QG_F1_OVERALL_THRESHOLD` | Overall F1 quality gate threshold | `0.70` |
| `QG_F1_SIMPLE_THRESHOLD` | F1 quality gate threshold for score-zero rows | `0.90` |
| `QG_KAPPA_THRESHOLD` | Cohen's Kappa quality gate threshold | `0.60` |
