# Data Standard Metadata Collection and Usage — PRD

- Status: Draft
- Owner: Stephen Fuqua
- Last Updated: 2026-06-01
- Related Jira: TBD

## 1. Product Overview

The **Data Standard Metadata Collection and Usage** initiative creates a suite of tools that collect, store, and analyze metadata about Ed-Fi Data Standard implementations — specifically the API specifications and supplemental data collection rules that state education agencies (SEAs) publish for vendors to implement.

The core problem: vendor integration costs are a widely-cited barrier to expanding K-12 data access. Those costs stem from complex, aggregated, and inconsistent requirements across states. By systematically extracting SEA specification metadata into a structured repository, the initiative enables two high-value workflows: (1) a **scoring engine** that measures the complexity of each SEA's requirements, giving Ed-Fi staff actionable leverage to help states simplify and standardize; and (2) a **cluster analysis** that surfaces cross-state commonalities, identifying where the Ed-Fi Data Standard itself can be extended or clarified to reduce fragmentation.

Beyond those primary goals, the repository supports additional use cases including a browseable specification viewer, a use case mapping library for vendors entering new markets, a natural language query interface, and an opportunity tracking system for Ed-Fi staff to log and monitor standardization conversations with SEAs.

The system is intended for internal Ed-Fi Alliance use first, with selected capabilities exposed to SEA staff and vendors over time. It is explicitly scoped to metadata — no student data or PII flows through any component.

### 1.1 Strategic Alignment

This PRD describes systems and processes designed to drive down the cost of vendor integrations with state data collections, the costs of which are reported as a significant barrier to expanded access to K-12 data.

Per reports from these vendors, high implementation costs are driven primarily by:

- Complex requirements ("if A then report X, else report Y, …")
- Aggregations ("report average daily attendance") instead of granular data (daily attendance)
- Inconsistent use of the Data Standard (State A and State B place the same information into different areas of the Ed-Fi Data Standard)

Some requirements described below are not directly applicable to this strategic goal. Consequently, these other requirements — while useful to the Ed-Fi Community — have a lower priority.

#### Lessons Learned from MappingEDU

MappingEDU was an Ed-Fi Alliance project that had some overlap with the requirements in this PRD — particularly: storing specification details, discovering specifications, and storing mappings between systems or use cases. This project was shut down around 2022 for the following reasons:

1. For most of the intended audience, Excel continued to be a better / simpler choice for documenting data mappings.
2. There were fewer than ten consistent users.
3. The custom application stack had accreted significant tech debt, which (at the time) would have cost hundreds of thousands of dollars to remediate, with no clear path to a return on investment.

These observations should be borne in mind when developing solutions for the requirements below.

### 1.2 Target Users and Personas

1. **Ed-Fi Staff** — primarily members of the Ed-Fi Alliance's product and solutions teams, these individuals have mandates to:
   - Expand the data standard to cover new use cases
   - Absorb common extension solutions into the core model where sensible
   - Help state agencies bring their data collection requirements into close alignment with the core data model, both in terms of using existing elements in the data standard and adhering to core modeling principles (e.g. favoring granular data over aggregations)

2. **SEA Staff** — these individuals design and support a state's data collection efforts. These efforts are primarily focused on policy-driven reporting requirements, and secondarily on data required for research efforts and for services provisioned back to the schools.

3. **Vendors** — whether a business analyst or a programmer, vendor staff need to build integrations with the Ed-Fi Data Standard. They are looking to minimize their cost to build an integration through true standardization across states. In addition, they may be looking for existing use case mappings when trying to break into a new market.

### 1.3 Jobs to Be Done / User Journeys

See [Section 3](#3-jobs-to-be-done) for detailed JTBD stories and acceptance criteria. Summary:

| #       | Job                                         | Primary Persona | Priority                                |
| ------- | ------------------------------------------- | --------------- | --------------------------------------- |
| JTBD 1  | Scoring Engine                              | Ed-Fi Staff     | Must have                               |
| JTBD 2  | Cluster Analysis                            | Ed-Fi Staff     | Must have                               |
| JTBD 3  | Standardization of Data Collection Metadata | Ed-Fi Staff     | Must have                               |
| JTBD 4  | Storage of API Specifications               | Ed-Fi Staff     | Must have                               |
| JTBD 5  | Viewing API Specifications                  | All             | Must have (Staff) / Could have (others) |
| JTBD 6  | Enrichment of API Specifications            | Ed-Fi Staff     | Must / Should have                      |
| JTBD 7  | Storage Engine                              | Ed-Fi Staff     | Must have                               |
| JTBD 8  | Use Case Exploration                        | All             | Could have                              |
| JTBD 9  | Use Case Mapping                            | All             | Could have                              |
| JTBD 11 | Natural Language Query                      | All             | Should have                             |
| JTBD 12 | Opportunity Tracking                        | Ed-Fi Staff     | Must have                               |
| JTBD 13 | SEA Specification Dashboard                 | Ed-Fi Staff     | Must have                               |
| JTBD 14 | SEA Static Report                           | Ed-Fi Staff     | Must have                               |

## 2. Enterprise and System Context

All jobs-to-be-done described in this PRD relate to **metadata**, not to the actual data collected by education organizations. No student data or other PII would flow through the systems built in support of these JTBDs.

The architecture envisions a single metadata repository at the center of the JTBDs; however, further design work could conceivably lead to metadata being replicated in more than one repository format to achieve the stated goals.

_[Architecture diagram placeholder — a 10,000-foot view diagram should be embedded here.]_

**Architectural notes (open for resolution):**

- Could [OpenMetadata](https://open-metadata.org/) support any of this? What about multiple user types? At what cost?
- Assumption: core requirements may require a bespoke system.
- The ideal central repository would use a hybrid model supporting:
  - Relational or document storage for use case mapping and opportunity tracking
  - Vector storage for semantic similarity searches

## 3. Jobs to Be Done

### JTBD 1: Scoring Engine

**Story:** As Ed-Fi Staff — on behalf of Vendors — I want to run a classification algorithm ("scoring engine") that analyzes and assigns a complexity score to SEA data collection requirements, so that I can help the SEA align their data collection with the Ed-Fi Data Standard.

**Acceptance Criteria:**

- 80% or better accuracy
- 0.7+ F1 score overall, with 0.9+ F1 score for attributes deemed "simple"
- 0.6+ Cohen's Kappa value
- Must be able to override the assigned score based on human judgment

**Depends on:** JTBD 3 (Standardization of Data Collection Metadata)

**Priority:** Must have

### JTBD 2: Cluster Analysis

**Story:** As Ed-Fi Staff — on behalf of Vendors — I want to run a periodic cluster analysis that looks for commonalities among different state data collection specifications, so that I can find market-driven (3+ states affected) opportunities to modify the Ed-Fi Data Standard and thereby reduce fragmentation across SEA specifications.

**Acceptance Criteria:**

- Minimal case: infer similarity from keyword matching
- Preferred case: infer similarity from semantic matching

**Depends on:** JTBD 3 (Standardized metadata storage for SEA specifications)

**Priority:** Must have

### JTBD 3: Standardization of Data Collection Metadata

**Story:** As Ed-Fi Staff, I want to extract data collection requirements from any SEA and store them in a standardized manner, so that I can analyze and help improve the SEA's requirements.

**Acceptance Criteria:**

- Standardized data storage
- Accessible to the scoring engine and other use cases

**Depends on:**

- JTBD 4 (Extraction of metadata from API specifications)
- JTBD 6 (Extraction of additional metadata rules from other sources: spreadsheet, PDF, web, etc.)

**Priority:** Must have

### JTBD 4: Storage of API Specifications

**Story:** As Ed-Fi Staff, I want to extract metadata from API specifications derived from the Ed-Fi Data Standard and/or extensions, so that I can use that metadata for various purposes and share the metadata with external users.

**Acceptance Criteria:**

- Automated conversion of either OpenAPI spec files and/or MetaEd files
- Storage of extracted information in a standardized format

**Depends on:** JTBD 7 (Storage Engine)

**Priority:** Must have

### JTBD 5: Viewing API Specifications

**Story:** As any type of user, I want to view API specification details, so that I will be able to read and understand the state's data collection requirements.

**Acceptance Criteria:**

- User interface for filtering / drilling into Domains > Entities > Attributes

**Depends on:** JTBD 7 (Storage Engine), JTBD 4

**Priority:**

- Must have for Ed-Fi Staff
- Could have for other personas

### JTBD 6: Enrichment of API Specifications

**Story:** As Ed-Fi Staff, I want to extract additional data collection requirements from documentation supplementary to the API specifications, so that I can enrich the collected API specifications with the full range of information required for building integrations with the SEA's data collection API.

**Acceptance Criteria:**

- Automated conversion of documents such as spreadsheets, web pages, PDF files, etc.
- Storage of extracted information in a standardized format
- Given the variable nature of the source documents, it is not realistic to expect 100% accuracy from an automated conversion. 80% accuracy is acceptable, though 90% or better is desired.
- Must be able to override the automated conversion based on human judgment
- While staff usage is the first priority, there may be a future requirement to assign ownership of the specification data to external users, allowing them to update / own the metadata. This does not need to be solved in the initial rollout.

**Depends on:** JTBD 7 (Storage Engine)

**Priority:**

- Must have: the storage requirements
- Should have: the automation requirements (MVP: while manual data entry is not desired, it should not be a complete blocker to progress toward JTBD 1 and 2)

### JTBD 7: Storage Engine

**Story:** As Ed-Fi Staff, I want to implement a storage engine for recording metadata that describes the API specification and other rules required for building a client-server integration with an SEA data collection API.

**Acceptance Criteria:**

- The storage engine SHALL run in a managed service environment, preferentially in Azure
- The storage engine SHALL support infrastructure-as-code deployment of schema
- The storage engine SHALL support a query language
- Metadata to be stored SHALL include at least the following fields (and other fields as implied to fulfil other jobs-to-be-done):

**Resource-level fields:**

| Column               | Example                                          |
| -------------------- | ------------------------------------------------ |
| Model Name           | `"ed-fi"` or the extension name                  |
| Version              | `5.2.0`                                          |
| Resource Name        | `applicantProfiles`                              |
| Resource Description | The profile of the person making an application. |
| Domains              | `RecruitingAndStaffing`                          |

**Property-level fields:**

| Column               | Example                                          |
| -------------------- | ------------------------------------------------ |
| Model Name           | `"ed-fi"` or the extension name                  |
| Version              | `5.2.0`                                          |
| Resource Name        | `applicantProfiles`                              |
| Property Name        | `lastSurname`                                    |
| Property Description | The name borne in common by members of a family. |
| Data Type            | `string`                                         |
| Min Length           | `0`                                              |
| Max Length           | `75`                                             |
| Validation RegEx     | `[A-Za-z\'\-\.]+`                                |
| Is Identity Key      | `false`                                          |
| Is Nullable          | `false`                                          |
| Is Required          | `true`                                           |

**Depends on:** No further dependencies

**Priority:** Must have

### JTBD 8: Use Case Exploration

**Story:** As any type of user, I want to explore the Ed-Fi Data Standard and state specifications by use case, so that I can learn how to build either a source or reporting system integration for that use case.

**Acceptance Criteria:**

- Accessible user interface for browsing and discovering use cases
- Data dictionary mapping between the use case's data elements and the data element names in the specifications

**Depends on:** JTBD 7 (Storage Engine), JTBD 3, JTBD 9 (Use Case Mapping)

**Priority:** Could have

### JTBD 9: Use Case Mapping

**Story:** As any type of user, I want to load mappings between a use case and the Ed-Fi Data Standard or state specifications into the storage engine for end users to discover.

**Acceptance Criteria:**

- Must have: import / update from spreadsheet / CSV
- Should have: ability to deprecate a mapping (and reverse)
- Should have: ability to archive a mapping, hiding it from public view (and reverse)
- Could have: other formats (to be determined)
- Could have: GUI for manual CRUD operations
- Could have: tracking of vendors or agencies who support or require a given use case
- Should have — edit rights:
  - Original creator can edit the use case
  - Ed-Fi Staff can edit the use case
  - Original creator can share editing rights (delegate) with another user
- Must have: anyone can read
- Must have: user can set a status indicator showing if the mapping is:
  - Work in progress
  - Proposed
  - Published / used in production

**Priority:**

- Could have
- MVP: editing by Ed-Fi staff only

### JTBD 10: Natural Language Query

**Story:** As any type of user, I want to use a natural language query to explore the Ed-Fi Data Standard and state specifications, so that I can find and synthesize information without manually building database queries.

**Acceptance Criteria:**

- Accessible through a chat interface (e.g. in a web application, Slack, or connected to a conversational AI system)
- Must obey the authorization patterns established for the metadata; for example, only allowing Ed-Fi Staff to access opportunity tracking data
- Should store user queries for diagnostic purposes
- Should allow users to provide feedback on the responses, for diagnostic purposes

**Sample Queries:**

- "Help me find where to store Intervention data"
- "Which states are using positive daily attendance?"
- "Rank the states by overall extension complexity"
- "Which states are using Data Standard 6?"

**Depends on:** JTBD 7 (Storage Engine), JTBD 3, JTBD 9 (Use Case Mapping)

**Priority:** Should have

### JTBD 11: Opportunity Tracking

**Story:** As Ed-Fi staff, I want to store notes about proposed changes and SEA responses so that I can track and report on the outcomes from the work to further standardize SEA data collections.

**Acceptance Criteria:**

- Storage of free text notes and potentially pre-defined fields
- Must have: user interface accessible only to Ed-Fi staff
- Could have (details to be determined): user interface accessible to other personas

**Depends on:** JTBD 7 (Storage Engine), JTBD 3

**Priority:** Must have

### JTBD 12: SEA Specification Dashboard

**Story:** As Ed-Fi staff, I want to view a dashboard summarizing information about any given state specification, so that I can get a sense of the size, scope, and complexity of that specification.

**Acceptance Criteria:**

- Must include at least these measures of attributes:
  - Number of attributes
  - Average complexity of attributes
- Should have filtering / roll-up of attributes by:
  - Domain
  - Entity
- Must have direct links to access and/or edit specification details
- Could have direct links to use case mappings that reference the state specification
- Future option: make this available to external users, though the complexity analysis may need to remain private

**Depends on:** JTBD 7 (Storage Engine), JTBD 3

**Priority:**

- Must have for Ed-Fi staff
- Could have for external users

### JTBD 13: SEA Static Report

**Story:** As Ed-Fi staff, I want to generate a static report, similar to the dashboard, so that I can distribute it to SEA staff for review.

**Acceptance Criteria:**

- Must be generated as a PDF
- Should be created from an action on the user interface dashboard

**Depends on:** JTBD 7 (Storage Engine), JTBD 3, JTBD 12 (Dashboard)

**Priority:** Must have

## 4. Non-Functional Requirements

### NFR-TECH: Technology Stack

- **NFR-TECH-1:** Backend transactional services MUST use either C# or JavaScript/TypeScript.
- **NFR-TECH-2:** Backend data processing services (scoring engine, ETL) SHOULD use Python (preferred), JavaScript, or C#.
- **NFR-TECH-3:** Frontend services SHOULD use either React or Alpine.js.
- **NFR-TECH-4:** Data storage SHOULD utilize either managed PostgreSQL or CosmosDB unless there is a strongly compelling reason and comparative cost analysis for an alternative.

### NFR-CICD: CI/CD and Operations

- **NFR-CICD-1:** CI/CD processes MUST be set up using GitHub Actions, conformant with the Ed-Fi Alliance's guidelines for use of GitHub Actions.
- **NFR-CICD-2:** Any custom services SHALL be deployable in at least the following isolated environments:
  - Localhost for development and testing, utilizing Docker Compose orchestration for dependent services
  - Staging / UAT
  - Production
- **NFR-CICD-3:** The system will be maintained by Ed-Fi Alliance staff.

### NFR-TEST: Testing

- **NFR-TEST-1:** Custom code MUST have at least 80% unit test coverage (the remaining 20% typically comes from I/O-connected code, such as HTTP bindings or ORM mappings).
- **NFR-TEST-2:** Integration test coverage MUST demonstrate full system connectivity in core happy path scenarios.

### NFR-BACKEND: Backend Patterns

- **NFR-BACKEND-1:** Backend code MUST use async, retry with exponential backoff, and circuit breaker patterns.

### NFR-SCALE: Scale and Availability

- **NFR-SCALE-1:** Actual application use will be low volume. User interface applications need to be generally available during normal working hours, but do not require scale-out or high availability.

### NFR-LICENSE: Licensing

- **NFR-LICENSE-1:** Any custom software developed MUST be made freely available under the Apache-2.0 license.

### NFR-AUTH: Authentication and Authorization

- **NFR-AUTH-1:** MUST use an OpenID Connect provider for user management. Options to investigate include:
  - Microsoft Entra ID, adding users to Ed-Fi's Azure subscription (could be time-consuming to manage and may not scale well)
  - SSO with the existing Salesforce platform (the approach used with the cancelled MappingEDU product; the Alliance is trying to move away from Salesforce)
  - Keycloak (experience from Ed-Fi Admin App; not currently deployed for production; can store its own users and proxy out to other SSO providers — may be a good solution)

### NFR-INFRA: Infrastructure

- **NFR-INFRA-1:** Any custom services SHOULD run within Azure as managed services (preferred) or container services.
- **NFR-INFRA-2:** Total operational cost is expected to be less than $100/month as a rule of thumb; higher cost might be acceptable but must be reviewed with executive management.

### NFR-DATA: Data Management

- **NFR-DATA-1:** Production database systems require standard weekly full backup, nightly differential backup, and documented rollback/restore processes.

## 5. System Architecture

| Component                        | Description                                                                                    | Technology Candidates                                                     | Deployment Target                       |
| -------------------------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | --------------------------------------- |
| Metadata Storage Engine          | Central repository for API specification metadata, use case mappings, and opportunity tracking | PostgreSQL (relational) + pgvector or CosmosDB (hybrid relational/vector) | Azure managed service                   |
| API Specification Extractor      | Converts OpenAPI / MetaEd files to standardized metadata                                       | Python or C# ETL service                                                  | Azure container or function             |
| Document Enrichment Service      | Extracts supplemental rules from spreadsheets, PDFs, web pages                                 | Python (preferred) with LLM assistance                                    | Azure container or function             |
| Scoring Engine                   | Classifies and scores attribute complexity                                                     | Python ML service                                                         | Azure container or function             |
| Cluster Analysis                 | Identifies commonalities across SEA specifications                                             | Python ML / NLP service                                                   | Azure container or function (scheduled) |
| Web Application                  | UI for browsing specs, dashboard, opportunity tracking, use case exploration                   | React or Alpine.js frontend + C#/TS backend                               | Azure App Service or Static Web App     |
| Natural Language Query Interface | Chat-based query layer over the metadata store                                                 | LLM + RAG over vector store                                               | Azure container or managed AI service   |
| Identity Provider                | Authentication and authorization for all services                                              | Keycloak / Microsoft Entra ID / Salesforce SSO                            | Azure container or managed service      |

## 6. Out of Scope and Known Limitations

- **No student data or PII** — the systems described here operate on metadata only.
- **External user ownership of specification data** (JTBD 6) — not required in the initial rollout; deferred to a future release.
- **External user access to opportunity tracking** (JTBD 11) — details TBD; not in MVP.
- **Public-facing complexity analysis** (JTBD 12) — complexity scores may need to remain private if the dashboard is opened to external users.
- **Full automation accuracy** — 100% accuracy in automated document enrichment (JTBD 6) is not expected; 80% is acceptable for MVP.
- **High availability / scale-out** — not required given the expected low volume of use.
- **MappingEDU feature parity** — this system is not intended to replicate MappingEDU; lessons learned from that project should inform scope decisions.

## 7. Open Questions and Decision Log

| #    | Question                                                                                                                    | Status | Decision / Notes                                                            |
| ---- | --------------------------------------------------------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------- |
| OQ-1 | Could [OpenMetadata](https://open-metadata.org/) satisfy any of these JTBDs? What are the multi-user and cost implications? | Open   | Assumption: a bespoke system will be required, but this should be validated |
| OQ-2 | Which OpenID Connect provider should be used? (Entra ID, Salesforce SSO, Keycloak)                                          | Open   | Keycloak appears most promising given prior experience and flexibility      |
| OQ-3 | Should vector storage be co-located with relational storage (e.g. pgvector) or a separate service?                          | Open   | —                                                                           |
| OQ-4 | What Jira project(s) will track this work?                                                                                  | Open   | —                                                                           |
| OQ-5 | What is the target release timeline / MVP definition by JTBD?                                                               | Open   | —                                                                           |

## 8. Glossary

| Term                | Definition                                                                                                        |
| ------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Ed-Fi Data Standard | The Ed-Fi Alliance's canonical data model for K-12 education data exchange.                                       |
| SEA                 | State Education Agency — a state-level government body responsible for K-12 education policy and data collection. |
| MetaEd              | The Ed-Fi Alliance's domain-specific language for defining data model extensions.                                 |
| OpenAPI             | A specification format for describing REST APIs (formerly Swagger).                                               |
| MappingEDU          | A discontinued Ed-Fi Alliance tool for documenting and discovering data mappings (shut down ~2022).               |
| ETL                 | Extract, Transform, Load — a data integration pattern.                                                            |
| RAG                 | Retrieval-Augmented Generation — an LLM technique that grounds responses in a retrieved document corpus.          |
| F1 Score            | A measure of predictive accuracy combining precision and recall (used in JTBD 1 acceptance criteria).             |
| Cohen's Kappa       | A statistical measure of inter-rater agreement, used here to assess scoring engine consistency.                   |
| JTBD                | Job to Be Done — a framework for describing user goals in terms of outcomes rather than features.                 |
| PII                 | Personally Identifiable Information.                                                                              |
