# Database Entity Details

Each section below describes one database entity (table).

---

## Entity: `source_elements`

**Summary** One row per element record extracted from a state's primary source
document (AZ XLSX, WI Confluence, MN Mapping Matrix, TX TWEDS, IN IDOE XLSX).
Rows in this table are the source-lens ingest output. They feed the
fact-extraction stage so the scoring pipeline can run against documentation the
state explicitly authored or backfilled from the Ed-Fi swagger.

**Created at stage** Ingest step — `poc3 ingest <state>`.

| Field | Description | Data Type |
|---|---|---|
| `state` | State code, e.g. `AZ`, `WI`, `MN`, `TX`, `IN` | TEXT |
| `edfi_version` | Ed-Fi version string from the artifact header | TEXT |
| `domain` | Logical domain, e.g. `Master Schedule` | TEXT |
| `entity` | Normalized entity name, e.g. `Section` | TEXT |
| `raw_entity` | Original entity string from the source document, e.g. `edfi.Section` or `az.SectionExtension` | TEXT |
| `element_name` | Field or property name | TEXT |
| `data_type` | Canonical or source-verbatim data type | TEXT |
| `definition_text` | State-authored definition text, or text backfilled from the Ed-Fi swagger | TEXT |
| `source` | Element origin: `core`, `extension`, `unknown`, or `filtered` | TEXT |
| `extension_name` | Extension identifier when `source = 'extension'` | TEXT |
| `business_rules_text` | Entity-level shared business rules narrative | TEXT |
| `element_specific_rules` | Per-element rules or special instructions | TEXT |
| `regulatory_citations` | Array of extracted regulatory citations | JSONB |
| `related_entities` | Array of cross-entity references | JSONB |
| `descriptor_table_code` | Descriptor table identifier | TEXT |
| `descriptor_table_values` | Array of descriptor code/value objects | JSONB |
| `collections_text` | Raw collection or submission-scope text | TEXT |
| `edfi_standard_definition` | Ed-Fi standard definition when available from the swagger | TEXT |
| `source_document` | Originating source document name | TEXT |
| `source_page_or_section` | Location within the source document | TEXT |
| `documented` | Whether the state source explicitly documents this element | BOOLEAN |
| `documentation_source` | Provenance label: `source_doc`, `swagger`, or `swagger_leaf` | TEXT |

**Does ingest erase and recreate all rows for a state?** Yes. The current sync
deletes every row where `state = <state>` before inserting the new snapshot.
Each `poc3 ingest <state>` run produces a fresh set of rows for that state. No
historical snapshots are retained.

---

## Entity: `spine_elements`

**Summary** One row per element record produced by walking the Ed-Fi swagger
spine catalog directly, enriched with any documentation the state's source has
for that element. This is the spine-lens counterpart of `source_elements`. Rows
in this table enumerate the full spine catalog for a state and mark elements as
`documented` or `documented=False` depending on whether the state's source doc
covers them. Spine elements also feed fact extraction.

**Created at stage** Ingest step — same as `source_elements`.

| Field | Description | Data Type |
|---|---|---|
| `state` | State code | TEXT |
| `edfi_version` | Ed-Fi version string from the artifact header | TEXT |
| `domain` | Logical domain | TEXT |
| `entity` | Normalized entity name | TEXT |
| `raw_entity` | Original entity string from the spine or source | TEXT |
| `element_name` | Field or property name | TEXT |
| `data_type` | Canonical or source-verbatim data type | TEXT |
| `definition_text` | Definition text from state source when available, otherwise from the swagger | TEXT |
| `source` | Element origin: `core`, `extension`, `unknown`, or `filtered` | TEXT |
| `extension_name` | Extension identifier when `source = 'extension'` | TEXT |
| `business_rules_text` | Entity-level shared business rules narrative | TEXT |
| `element_specific_rules` | Per-element rules or special instructions | TEXT |
| `regulatory_citations` | Array of extracted regulatory citations | JSONB |
| `related_entities` | Array of cross-entity references | JSONB |
| `descriptor_table_code` | Descriptor table identifier | TEXT |
| `descriptor_table_values` | Array of descriptor code/value objects | JSONB |
| `collections_text` | Raw collection or submission-scope text | TEXT |
| `edfi_standard_definition` | Ed-Fi standard definition from the swagger | TEXT |
| `source_document` | Originating source document name | TEXT |
| `source_page_or_section` | Location within the source document | TEXT |
| `documented` | Whether the state source explicitly documents this element | BOOLEAN |
| `documentation_source` | Provenance label: `source_doc`, `swagger`, or `swagger_leaf` | TEXT |

**Does ingest erase and recreate all rows for a state?** Yes — same full-replace
behavior as `source_elements`. Deletes all rows for the state and inserts the
new spine-lens snapshot.

---

## Entity: `ingestion_status`

**Summary** One row per `(state, lens)` pair tracking the most recent successful
ingest sync. This is the metadata control record that tells you what was last
loaded, when it was loaded, and how many elements it contained. Query this table
to check whether a state's ingest data is current before starting fact
extraction.

**Created at stage** Written or upserted as part of Ingest step.

| Field | Description | Data Type |
|---|---|---|
| `state` | State code (PK component) | TEXT |
| `lens` | `source` or `spine` (PK component) | TEXT |
| `edfi_version` | Ed-Fi version from the artifact | TEXT |
| `extracted_at` | Timestamp when the ingest adapter produced the artifact | TIMESTAMPTZ |
| `element_count` | Number of element rows in the artifact | INTEGER |
| `source_inputs` | Common input list for the snapshot. Source lens stores unique source document filenames; spine lens stores the swagger URLs used to build the spine manifest. | JSONB |
| `status` | Sync status; current code always writes `completed` | TEXT |
| `synced_at` | Timestamp when the PostgreSQL sync ran | TIMESTAMPTZ |

**Does ingest erase and recreate all rows for a state?** No. This table is
upserted — the existing row for `(state, lens)` is updated in place on every
sync. It always reflects the latest sync run.

---

## Entity: `gap_logs`

**Summary** One row per state summarizing the gap analysis between the state's
source document and the Ed-Fi spine catalog. The gap log captures how well the
source document covers the spine, which spine elements are unmatched, and what
the un flatten recovery produced. This is a diagnostic artifact; it is computed
and stored after the ingest step.

**Created at stage** Ingest step — `poc3 ingest <state>` (or `poc3 ingest gap
<state>` for a gap-only refresh). The `gap_logs` table stores one summary row
per state.

| Field | Description | Data Type |
|---|---|---|
| `state` | State code (PK) | TEXT |
| `spine_source` | Relative path to the spine JSON file used for the gap computation | TEXT |
| `spine_unique_element_keys` | Total unique element keys in the spine catalog in scope | INTEGER |
| `spine_extension_element_count` | Count of extension elements in the spine | INTEGER |
| `source_element_count` | Number of source-lens rows considered during the gap analysis | INTEGER |
| `source_coverage` | JSON object with `matched`, `total`, `pct`, `note` | JSONB |
| `spine_coverage` | JSON object with `matched_unique_keys`, `total_spine_keys`, `pct`, `note` | JSONB |
| `unmatched_source_count` | Number of source rows that could not be matched to a spine key | INTEGER |
| `unflatten_recovered_count` | Number of keys recovered by the unflatten heuristic | INTEGER |
| `unflatten_recovered` | Array of objects describing each recovered mapping (from_entity, to_entity, sub_collection, element_name) | JSONB |
| `unmatched_by_entity` | Object keyed by entity name, with the count of unmatched elements for each | JSONB |
| `missing_from_docs_count` | Total spine keys not covered by the state's source doc | INTEGER |
| `missing_from_docs_samples` | Sample array of missing spine keys | JSONB |
| `extra` | Free-form state-specific additions from `build_gap_log(..., extra=...)` | JSONB |
| `synced_at` | Timestamp when this row was written to PostgreSQL | TIMESTAMPTZ |

**Does ingest erase and recreate all rows for a state?** Yes. One row per state.
Re-running gap analysis for a state replaces the existing row.

---

## Entity: `fact_runs`

**Summary** One row per phase-A fact extraction job. Tracks which state, lens,
fact name, model, and prompt version produced a batch of observations. This is
the parent record for all `fact_observations` rows produced in that job. It also
stores run-level header metrics from the phase-A artifact header
(`record_count`, `scored_count`, `entities_processed`, cost/caching counters,
and deterministic `true_count`/`false_count`).

**Created at stage** Phase-A fact extraction — created or resolved when a fact
extraction job starts. The job streams observation rows into `fact_observations`
and updates run metadata from the artifact header as extraction
progresses/completes.

| Field | Description | Data Type |
|---|---|---|
| `fact_run_id` | Surrogate primary key | BIGSERIAL |
| `state` | State code | TEXT |
| `lens` | `source` or `spine` | TEXT |
| `fact_name` | Fact label, e.g. `business_rules_present` or `has_conditional_logic` | TEXT |
| `artifact_name` | Short label for the run, e.g. `AZ_source_business_rules_present` | TEXT |
| `artifact_path` | Path to the emitted artifact file (optional but useful for replay/debug) | TEXT |
| `prompt_version` | Prompt or extraction version used for this run | TEXT |
| `model_id` | Model identifier for LLM-based runs; `deterministic` for det-fact runs (`header.model`) | TEXT |
| `mode` | Extraction mode from header, e.g. `deterministic` or `llm` | TEXT |
| `status` | Header status for the run, e.g. `complete` | TEXT |
| `cost_cap_hit` | Whether the run hit its configured cost cap | BOOLEAN |
| `schema_error` | Header-level schema validation error text, when present | TEXT |
| `scored_at` | Header timestamp for artifact completion | TIMESTAMPTZ |
| `source_hash` | Optional checksum for deduplicating repeated submissions of the same job | TEXT |
| `record_count` | Number of observation rows in the run | INTEGER |
| `scored_count` | Number of rows scored in the run | INTEGER |
| `skipped_count` | Number of rows skipped in the run | INTEGER |
| `entities_processed` | Distinct entities processed in the run | INTEGER |
| `total_tokens_in` | Input tokens consumed by the run (`0` for deterministic) | INTEGER |
| `total_tokens_out` | Output tokens produced by the run (`0` for deterministic) | INTEGER |
| `total_usd` | Total run cost in USD (`0.0` for deterministic) | DOUBLE PRECISION |
| `cache_hit_count` | Number of cache hits during extraction | INTEGER |
| `downgrade_count` | Number of downgraded outputs in the run | INTEGER |
| `true_count` | Number of rows where the fact fired (or nonzero count for int facts) | INTEGER |
| `false_count` | Number of rows where the fact did not fire | INTEGER |
| `started_at` | Timestamp when the extraction job started | TIMESTAMPTZ |
| `finished_at` | Timestamp when the extraction job finished | TIMESTAMPTZ |
| `header` | Full raw header JSON for forward-compatible replay and audit | JSONB |
| `imported_at` | Timestamp when this run record was first created in PostgreSQL | TIMESTAMPTZ |
| `notes` | Free-form operator notes | TEXT |

**Does a new run erase prior fact observations?** For the normal operational
flow, yes — it should replace the prior fact snapshot for the same state+lens
after ingest refreshes the underlying `source_elements` or `spine_elements`
rows. Facts are derived from the latest element snapshot, so rerunning fact
extraction after ingest should recalculate facts against the newer element rows.

---

## Entity: `fact_observations`

**Summary** One row per extracted fact observation — the primary storage for
every binary or enum fact the pipeline produces about a single element. Each row
belongs to a `fact_runs` parent and carries the extracted value, confidence,
justification, source spans, and the raw payload for forward compatibility.

**Created at stage** Phase-A fact extraction — written directly as facts are
produced. Each observation is inserted the moment it is available within its
parent job.

| Field | Description | Data Type |
|---|---|---|
| `fact_observation_id` | Surrogate primary key | BIGSERIAL |
| `fact_run_id` | Foreign key to the parent `fact_runs` row | BIGINT |
| `record_index` | Zero-based position of this observation within the job, combined with `fact_run_id` as a unique key | INTEGER |
| `state` | State code; duplicated for partition-friendly filtering | TEXT |
| `lens` | `source` or `spine`; duplicated for the same reason | TEXT |
| `entity` | Normalized entity name the fact was extracted for | TEXT |
| `element_name` | Element or property the fact is about | TEXT |
| `fact_name` | Extracted fact label, e.g. `has_conditional_logic` | TEXT |
| `fact_value` | Extracted value stored as text to preserve mixed enums and booleans | TEXT |
| `confidence` | Confidence label or score from the extractor | TEXT |
| `justification` | Human-readable rationale from the extractor | TEXT |
| `source_spans` | Array of evidence spans or citations when available | JSONB |
| `raw_payload` | Full original observation payload preserved for forward-compatible replay | JSONB |
| `created_at` | Timestamp when this row was inserted | TIMESTAMPTZ |

**Does a new extraction erase prior observations?** For the normal operational
flow, yes — the prior fact snapshot for the same state+lens should be replaced
when extraction is rerun against refreshed element rows. If you intentionally
keep history, that should be an explicit design choice, for example by retaining
older `fact_run_id` versions separately. The default current-state model should
be: latest ingest snapshot in `source_elements` / `spine_elements`, latest
derived fact snapshot in `fact_observations`.

## Entity: `score_records`

**Summary** One row per scored element, written by `poc3 score aggregate`. This
is the central result table of the pipeline. It holds the per-element NACHOS
score, quality diagnostics, confidence, review flags, and the full dimension
breakdown for both the source lens and the spine lens. Rows in this table are
the input for analyst workbooks and reviewer comparisons.

**Created at stage** Phase-C scoring step — `poc3 score aggregate --state
<state> --lens <source|spine>`. The aggregate pipeline writes to populate this
table.

| Field | Description | Data Type |
|---|---|---|
| `state` | State code (PK component) | TEXT |
| `lens` | `source` or `spine` (PK component) | TEXT |
| `record_key` | Unique element key in the form `STATE\|Entity\|element_name` (PK component) | TEXT |
| `entity` | Normalized entity name | TEXT |
| `element_name` | Field or property name | TEXT |
| `quality_mean_diagnostic` | Internal arithmetic mean of the quality dimension scores (not surfaced on workbooks) | DOUBLE PRECISION |
| `complexity_score` | Business logic complexity tier: 0–3 | INTEGER |
| `confidence_composite` | Minimum confidence across all dimensions: `high`, `medium`, or `low` | TEXT |
| `adjusted_nachos_score` | Final NACHOS score after extension and multi-entity adjustments, capped at 4.5 | DOUBLE PRECISION |
| `in_scope` | Whether this element is in scope for NACHOS methodology scoring | BOOLEAN |
| `nachos_justification` | Human-readable rule label and adjustment breakdown string | TEXT |
| `discovery_lens` | Provenance: `source` for source-doc rows, `spine_anchored` for gap-recovered rows | TEXT |
| `documentation_source` | Provenance label: `source_doc`, `swagger`, or `swagger_leaf` | TEXT |
| `dimensions` | Per-dimension score objects (value, rule_matched, inputs_used, confidence) | JSONB |
| `fact_provenance` | Per-fact audit trail (value, confidence, downgraded, downgrade_reason, spans) | JSONB |
| `review` | Review block (needs_review, reasons, route) | JSONB |

**Does scoring erase and recreate all rows for a state?** Yes. Each aggregate
run deletes all rows where `state = <state> AND lens = <lens>` before inserting
the new snapshot. Re-running `poc3 score aggregate` for a state+lens fully
replaces that lens's scored rows. Source-lens and spine-lens rows are
independent — aggregating one lens does not affect the other lens's rows.

---

## Entity: `score_status`

**Summary** One row per `(state, lens)` pair tracking the latest score aggregate
run. Stores header-level statistics such as mean quality score, NACHOS
histogram, needs-review count, and scoring plan version. Use this table to
verify that a state's scores are current and to surface run-level KPIs without
querying the full `score_records` table.

**Created at stage** Phase-C scoring step — upserted by
`maybe_sync_scores_payload(...)` as part of every successful aggregate run.

| Field | Description | Data Type |
|---|---|---|
| `state` | State code (PK component) | TEXT |
| `lens` | `source` or `spine` (PK component) | TEXT |
| `edfi_version` | Ed-Fi version recorded in the score sidecar | TEXT |
| `scored_at` | Timestamp when the scoring pipeline produced the artifact | TIMESTAMPTZ |
| `record_count` | Total number of records in the sidecar | INTEGER |
| `scored_count` | Number of records that were scored | INTEGER |
| `skipped_count` | Number of records skipped during scoring | INTEGER |
| `mean_quality_score` | Arithmetic mean of per-record quality scores for documented-authored rows | DOUBLE PRECISION |
| `needs_review_count` | Number of rows flagged for reviewer attention | INTEGER |
| `scoring_plan_version` | Scoring plan version string, e.g. `26` | TEXT |
| `model` | Model identifier used for LLM fact extraction, e.g. `claude-sonnet-4-6` | TEXT |
| `prompt_version` | Prompt version string, e.g. `phase-a.v1` | TEXT |
| `in_scope_count` | Number of in-scope rows used for NACHOS histogram and mean | INTEGER |
| `documentation_gap_count` | Count of rows where the documentation gap dimension fired | INTEGER |
| `header` | Full sidecar header JSON excluding the `scores` array. This includes `dimension_stats`, `nachos_score_histogram`, `adjusted_nachos_score_histogram`, `mean_nachos_score`, and `mean_adjusted_nachos_score`. | JSONB |
| `synced_at` | Timestamp when PostgreSQL sync ran | TIMESTAMPTZ |

**Does scoring erase and recreate all rows for a state?** No. This table is
upserted. The existing `(state, lens)` row is updated in place on every
aggregate run. It always reflects the latest run's statistics.

---
