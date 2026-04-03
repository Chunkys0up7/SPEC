# Knowledge Orchestrator — Product Document

**Version:** 1.0.0
**Status:** Approved for Implementation
**Date:** 2026-04-03

---

## 1. Product Overview

### 1.1 What It Is

The Knowledge Orchestrator is a Python application that takes a BPMN 2.0 process
definition as input and produces a **Knowledge Requirements Specification** — a
comprehensive, structured analysis of every process step showing:

- What knowledge, data, procedures, and decisions each step requires
- What regulatory controls apply to each step and what they mandate
- What knowledge the organization already has (matched against a knowledge store)
- What is missing (gap analysis with actionable recommendations)
- How knowledge flows between steps — both vertically through subprocess nesting
  and horizontally across the entire process journey
- How matched procedures expand into cascading requirements (regulatory, compliance,
  sub-procedures)

The output is delivered in three formats: console (real-time walk-through), JSON
(machine-readable), and HTML (interactive visual map).

### 1.2 What It Is Not

- **Not a BPMN execution engine** — it analyzes process definitions, it does not run them
- **Not a BPMN modeler** — it reads existing BPMN XML, it does not create or edit processes
- **Not a document management system** — it references procedures and knowledge, it does
  not store or manage them
- **Not an AI/ML system (phase 1)** — all inference is rule-based and deterministic.
  Phase 2 will introduce agentic capabilities

### 1.3 Strategic Context

This is **Phase 1** of a two-phase initiative:

| Phase | Purpose | Scope |
|-------|---------|-------|
| **Phase 1 (this build)** | Knowledge readiness analysis | BPMN in → Requirements Spec out. Prove the model. |
| **Phase 2 (future)** | Agentic execution | The orchestrator actively gathers knowledge, makes decisions, and drives process execution using the requirements spec as its work order. |

### 1.4 Three Inputs, Three Outputs

**Inputs:**
1. **BPMN 2.0 XML** — The process definition (any complexity, any nesting depth)
2. **Regulatory Frameworks** — JSON definitions of applicable regulations (ITIL, ISO 27001,
   MISMO, GDPR, SOX, HIPAA — pluggable, add any framework via JSON)
3. **Knowledge Store** — Available procedures, runbooks, policies, FAQs (JSON files for
   phase 1, extensible to databases, vector stores, document management systems)

**Outputs:**
1. **Console** — Real-time step-by-step walk-through with knowledge context
2. **JSON** — Machine-readable structured specification
3. **HTML** — Self-contained interactive visual map (opens in any browser)

---

## 2. Problem Statement

### 2.1 The Knowledge Gap in Process Execution

Organizations define complex processes in BPMN. These processes go many levels deep —
a top-level "Incident Response" process contains subprocesses for Detection, Triage,
Resolution, and Post-Incident Review, each containing their own subprocesses, reaching
4, 5, or more levels of nesting.

At each step in these processes, people need knowledge to execute correctly:
- **Procedures:** How do I perform this step?
- **Data:** What information must be available?
- **Context:** What happened in prior steps that affects this one?
- **Decisions:** What criteria do I use to make choices?
- **Regulatory:** What am I legally required to do, capture, or verify?

Today, this knowledge mapping exists only in people's heads. There is no systematic way
to answer: *"For step 26 in this 47-step process, what exactly do you need to know, where
does it come from, and do we have it?"*

### 2.2 The Regulatory Compliance Challenge

Regulated industries (financial services, healthcare, government) face an additional layer:
regulatory frameworks impose mandatory controls on process steps. MISMO requires specific
data capture at loan origination steps. GDPR mandates lawful basis documentation at any
step processing personal data. SOX requires segregation of duties at approval steps.

These regulatory requirements are not optional — they define the **floor** for what each
step must satisfy. A step might have excellent procedure coverage but be completely
non-compliant if regulatory controls are not addressed.

### 2.3 The Cross-Step Dependency Problem

In deeply nested processes, knowledge from early steps (e.g., "Assess Impact" in Detection)
is needed by later steps (e.g., "Deploy Fix" in Resolution) even though these steps live
in completely separate subprocesses. Without explicit tracking of what each step produces,
these cross-scope dependencies are invisible.

---

## 3. Architecture

### 3.1 System Architecture Diagram

```
      ┌──────────────┐  ┌───────────────────┐  ┌──────────────────┐
      │  BPMN XML    │  │  Regulatory        │  │  Knowledge       │
      │  (process)   │  │  Frameworks        │  │  Store           │
      │              │  │  (MISMO,GDPR,SOX..)│  │  (procedures)    │
      └──────┬───────┘  └─────────┬─────────┘  └────────┬─────────┘
             │                    │                      │
      ┌──────▼───────┐           │                      │
      │  BPMN Parser │           │                      │
      └──────┬───────┘           │                      │
             │                   │                      │
      ┌──────▼───────┐           │                      │
      │  Walker      │           │                      │
      └──────┬───────┘           │                      │
             │                   │                      │
    ┌────────▼─────────┐  ┌─────▼──────────────┐       │
    │  Requirements    │  │  Regulatory         │       │
    │  Analyzer        │  │  Analyzer           │       │
    │  (4-layer        │  │  (control triggers  │       │
    │   inference)     │  │   → mandatory reqs) │       │
    └────────┬─────────┘  └─────┬──────────────┘       │
             │                  │                       │
             └────────┬─────────┘                       │
                      │  merged requirements            │
       ┌──────────────┼──────────────┐                  │
       │              │              │                   │
  ┌────▼─────┐       │      ┌───────▼──────┐           │
  │ Journey  │       │      │ Knowledge    │           │
  │ Context  │       │      │ Context Mgr  │           │
  │(horizntl)│       │      │ (vertical)   │           │
  └────┬─────┘       │      └───────┬──────┘           │
       │              │              │                   │
       └──────────────┼──────────────┘                  │
                      │                                  │
         ┌────────────▼────────────┐                    │
         │  Knowledge Ranker      ◄─────────────────────┘
         │  + Gap Analyzer        │  Match against store + journey
         └────────────┬───────────┘
                      │
         ┌────────────▼────────────┐
         │  Procedure Expander     │  Cascade procedure requirements
         │  (recursive, depth-3)   │  (regulatory reqs feed back in)
         └────────────┬───────────┘
                      │
         ┌────────────▼────────────┐
         │  Spec Generator         │  Console + JSON + HTML
         │  + HTML Renderer        │  with compliance summary
         └─────────────────────────┘
```

### 3.2 Component Inventory

| # | Component | Module | Purpose |
|---|-----------|--------|---------|
| 1 | Data Models | `models.py` | All shared types: BPMN nodes, knowledge items, requirements, coverage, journey entries, regulatory controls, expansion results |
| 2 | BPMN Parser | `bpmn_parser.py` | Parses BPMN 2.0 XML into a ProcessDefinition tree. Handles arbitrary nesting depth. Extracts structured knowledge/data/output tags from documentation elements. |
| 3 | Requirements Analyzer | `requirements_analyzer.py` | 4-layer inference engine that examines each BPMN node and generates categorized requirements. Layers: explicit (from BPMN docs), journey-aware (from process history), type-based (from node type), contextual (from position/scope). Also infers what each step produces for journey recording. |
| 4 | Knowledge Store | `knowledge_store.py` | Protocol-based interface for knowledge access. In-memory implementation loads from JSON files. Indexed by tags, category, scope, and type. Designed for future DB/vector-store backends. |
| 5 | Knowledge Ranker | `knowledge_ranker.py` | Multi-signal relevance scoring (5 weighted signals: tag overlap, category match, keyword relevance, scope proximity, type fit). Produces ranked matches with transparent score breakdown. |
| 6 | Gap Analyzer | `gap_analyzer.py` | Compares requirements against ranked matches. Produces coverage assessment per requirement (MATCHED >= 0.70, PARTIAL >= 0.40, GAP < 0.40, JOURNEY_SATISFIED from prior steps). Computes readiness scores at step, scope, and process levels. |
| 7 | Knowledge Context Manager | `knowledge_context.py` | Stack-based scoping that mirrors subprocess nesting. Handles vertical knowledge flow: parent-to-child inheritance, local scoping, upward propagation on subprocess exit. |
| 8 | Journey Context | `journey_context.py` | Append-only process ledger for horizontal knowledge flow. Records every step's outputs, decisions, and state changes. Enables cross-scope queries (step 26 can find step 1's outputs even across subprocess boundaries). |
| 9 | Regulatory Analyzer | `regulatory_analyzer.py` | Loads regulatory frameworks from JSON. Evaluates each step against all controls using a trigger system (domain match, tag match, node type, data category). Fires controls that impose mandatory requirements — the compliance floor. |
| 10 | Procedure Expander | `procedure_expander.py` | Recursive expansion engine. When a procedure is matched, inspects its own declared requirements (regulatory, compliance, sub-procedures, data dependencies) and cascades them into the step. Depth-limited (default 3) with cycle detection. |
| 11 | Orchestrator | `orchestrator.py` | Central coordinator. Per-step pipeline: analyze requirements → evaluate regulatory controls → check journey → match against store → expand procedures → assess gaps → record in journey → emit to display. |
| 12 | Spec Generator | `spec_generator.py` | Produces the Knowledge Requirements Specification in JSON format. Structured output covering per-step detail, scope summaries, compliance breakdown, and process-level readiness. |
| 13 | HTML Renderer | `html_renderer.py` | Generates a self-contained HTML file (inline CSS/JS, zero external dependencies). Collapsible subprocess tree, color-coded coverage, expansion cascades, regulatory panels, search, filter, print mode. |
| 14 | Console Display | `display.py` | Real-time console output as the orchestrator walks the process. Visual hierarchy with tree characters, level markers, coverage indicators, journey context panels, and regulatory control sections. |
| 15 | Main Entry Point | `main.py` | CLI entry point. Parses arguments, loads all inputs, initializes all components, runs the orchestrator, produces all outputs. |

### 3.3 Two Axes of Knowledge Flow

The system maintains two distinct knowledge flow mechanisms that serve different purposes:

```
                    VERTICAL (Knowledge Context Manager)
                    ↕ Subprocess hierarchy
                    ↕ Parent-to-child inheritance
                    ↕ Upward propagation on exit

    ════════════════════════════════════════════════════
    HORIZONTAL (Journey Context)
    → Chronological accumulation across ALL steps
    → Step 1 → Step 2 → ... → Step N
    → Crosses all subprocess boundaries
    → Append-only ledger, persists entire process
    ════════════════════════════════════════════════════
```

| Aspect | Vertical (Scope Stack) | Horizontal (Journey) |
|--------|----------------------|---------------------|
| **Direction** | Parent ↔ Child subprocess | Step → Step (sequential) |
| **Lifetime** | Created on subprocess enter, destroyed on exit | Persists for entire process walk |
| **Visibility** | Current scope + ancestor chain | Global — any step can query any prior step |
| **Content** | Knowledge items (procedures, references) | Step outputs, decisions, accumulated state |
| **Purpose** | "What knowledge is relevant HERE?" | "What has the process LEARNED so far?" |
| **Write pattern** | Push/pop with propagation rules | Append-only ledger |

**Why both are needed:**

A procedure in the "Triage" scope is not relevant when you're in "Post-Incident Review"
(vertical scoping correctly hides it). But the *output* of a triage step (e.g., "severity
classified as S2") is absolutely relevant to Post-Incident Review (horizontal journey
makes it available).

---

## 4. Core Concepts

### 4.1 Requirements Inference (4-Layer Engine)

At each BPMN step, the Requirements Analyzer infers what knowledge is needed using four
layers of inference, from most to least authoritative:

**Layer 1 — Explicit Requirements (from BPMN documentation)**
The BPMN documentation element contains structured declarations:
```xml
<bpmn:documentation>
  knowledge:alerting,monitoring,triage,first-response
  data:alert-source,alert-details,timestamp,affected-system
  context:incident-severity,affected-components
  decision:severity-preliminary,escalation-needed
  output:alert-details,affected-system-id,preliminary-severity
</bpmn:documentation>
```
These are parsed directly into categorized requirements. This is the most precise source.

**Layer 2 — Journey-Aware Requirements (from process history)**
The analyzer checks the journey context to determine:
- Which of this step's context requirements are already satisfied by prior step outputs
- What decisions have been made that affect this step's path
- What accumulated process state is available
- Cross-scope dependencies (what did sibling subprocesses produce?)

**Layer 3 — Node-Type-Based Requirements (from BPMN task type)**
Different task types have inherent knowledge needs:

| Node Type | Inherent Requirements |
|-----------|----------------------|
| UserTask | SOP, role permissions, completion criteria |
| ServiceTask | Input schema, error handling, fallback procedure |
| ScriptTask | Script reference, runtime requirements, input data |
| ManualTask | Step-by-step procedure, checklist, completion criteria |
| ExclusiveGateway | Decision criteria, routing rules, evaluation data |
| ParallelGateway | Coordination requirements, synchronization data |

**Layer 4 — Contextual Requirements (from position and scope)**
The analyzer examines the node's position to infer additional needs:
- First task in a subprocess → needs subprocess context and parent inputs
- Task after a gateway → needs gateway decision outcome
- Task before end event → needs completion/handoff criteria
- Deep nesting (level 3+) → needs escalation path to parent scope
- Subprocess domain → adds domain-specific knowledge tags

### 4.2 Regulatory Control System

Regulatory frameworks are loaded as structured JSON configurations. Each framework declares
**controls** — rules with triggers that activate based on what a step does.

**Control trigger types:**

| Trigger | Activates When... | Example |
|---------|-------------------|---------|
| `domain_match` | Step is in a subprocess matching named domains | "detection", "loan-origination" |
| `tag_match` | Step's knowledge/data tags include specified values | "personal-data", "financial-data" |
| `node_type` | Step is a specific BPMN node type | "exclusive_gateway" (approval points) |
| `data_category` | Step handles data in specified categories | "borrower-data", "system-credentials" |
| `name_pattern` | Step name matches a regex | "Verify.*", "Approve.*" |
| `scope_depth` | Step is at or beyond a nesting depth | depth >= 3 |
| `any` | Always fires | Global controls |

**Control severity levels:**

| Severity | Meaning | Impact on Readiness |
|----------|---------|-------------------|
| **MANDATORY** | Legal/regulatory requirement — MUST comply | Non-compliance = compliance readiness 0% for this control |
| **RECOMMENDED** | Industry best practice — SHOULD comply | Non-compliance noted but doesn't block |
| **ADVISORY** | Guidance — MAY comply | Informational only |

**How regulation differs from inference:**

| Source | Direction | Authority | Example |
|--------|-----------|-----------|---------|
| Requirements Analyzer | Bottom-up (from BPMN) | Inferred — "this step should have..." | "Log Analysis step should have a runbook" |
| Procedure Expansion | Bottom-up (from procedure) | Declared — "this procedure requires..." | "Rollback Procedure requires backup verification" |
| **Regulatory Analyzer** | **Top-down (from framework)** | **Mandated — "this step MUST have..."** | "MISMO mandates SSN verification at identity steps" |

### 4.3 Recursive Procedure Expansion

When a procedure is matched to a step, the system inspects the procedure's own declared
requirements and recursively expands them:

```
Step: "Apply Temporary Fix"
  └─ Requirement: Containment procedure
       └─ MATCHED: Rollback Procedure [score: 0.82]
            ├─ Requires: Change management approval (mandatory)
            │    └─ Check store → MATCHED
            ├─ Requires: Backup verification (mandatory)
            │    └─ Check journey → JOURNEY_SATISFIED (Step 19)
            ├─ Requires: SOX audit trail (regulatory, mandatory)
            │    └─ Check store → GAP ← CRITICAL FINDING
            └─ Requires: Data retention check (sub-procedure)
                 └─ Check store → PARTIAL [0.55]
                      └─ Recurse: Data Retention Policy itself requires...
                           └─ (depth limit reached — stop)
```

**Depth limiting:** Maximum recursion depth of 3 (configurable). Prevents infinite chains.
**Cycle detection:** Tracks expanded item IDs. Same procedure cannot appear twice in one chain.

### 4.4 Coverage Levels

Every requirement receives a coverage assessment:

| Level | Meaning | Indicator | Score |
|-------|---------|-----------|-------|
| **MATCHED** | Fully covered by knowledge store (score >= 0.70) | ✓ | 1.0 |
| **PARTIAL** | Partially covered (score 0.40 - 0.69) | ~ | 0.5 |
| **GAP** | No matching knowledge found (score < 0.40) | ✗ | 0.0 |
| **JOURNEY_SATISFIED** | Covered by a prior step's output | ⟲ | 1.0 |
| **NOT_ASSESSED** | Not assessable (e.g., data requirements) | n/a | excluded |

### 4.5 Two-Dimensional Readiness

Each step has two readiness dimensions:

| Dimension | What it measures | Weight |
|-----------|-----------------|--------|
| **Knowledge Readiness** | Procedures, data, context coverage from inference + store matching | 0.4 |
| **Compliance Readiness** | Regulatory control coverage from framework evaluation | 0.6 |

Compliance is weighted heavier because regulatory gaps are legally required, not
discretionary. A step can be 90% knowledge-ready but 30% compliance-ready.

```
Knowledge:  75% ████████░░
Compliance: 25% ███░░░░░░░  ← 3 of 4 mandatory controls non-compliant
Combined:   45% █████░░░░░  (0.4 × 75% + 0.6 × 25%)
```

### 4.6 Knowledge Ranking (5-Signal Scoring)

When matching requirements against the knowledge store, each candidate is scored using
five weighted signals:

| Signal | Weight | Calculation |
|--------|--------|-------------|
| Tag overlap | 0.30 | Jaccard similarity of requirement tags vs. knowledge item tags |
| Category match | 0.25 | Does the item's category match the subprocess domain? |
| Keyword relevance | 0.20 | Word overlap between requirement description and item title/summary |
| Scope proximity | 0.15 | Is the item scoped to the current subprocess? Parent? Global? |
| Type fit | 0.10 | Does the knowledge type (runbook, policy, reference) fit the requirement category? |

Each signal produces 0.0–1.0. Total = weighted sum. Thresholds: >= 0.70 = MATCHED,
>= 0.40 = PARTIAL, < 0.40 = GAP.

---

## 5. Data Model Reference

### 5.1 BPMN Process Model

```
ProcessDefinition
  ├── id: str
  ├── name: str
  ├── description: str
  ├── nodes: dict[str, ProcessNode]
  └── flows: dict[str, SequenceFlow]

ProcessNode
  ├── id: str
  ├── name: str
  ├── node_type: NodeType (enum)
  ├── documentation: str | None
  ├── knowledge_tags: list[str]       ← from "knowledge:" line
  ├── data_tags: list[str]            ← from "data:" line
  ├── metadata: dict[str, str]
  ├── incoming_flows: list[str]
  ├── outgoing_flows: list[str]
  └── parent_subprocess: str | None

SubProcess (extends ProcessNode)
  ├── child_nodes: dict[str, ProcessNode]
  ├── child_flows: dict[str, SequenceFlow]
  └── scope_domain: str

SequenceFlow
  ├── id: str
  ├── name: str | None
  ├── source_ref: str
  ├── target_ref: str
  └── condition_expression: str | None
```

**Node type hierarchy:**
```
NodeType (enum)
  ├── START_EVENT, END_EVENT
  ├── TASK, USER_TASK, SERVICE_TASK, SCRIPT_TASK, MANUAL_TASK
  ├── EXCLUSIVE_GATEWAY, PARALLEL_GATEWAY, INCLUSIVE_GATEWAY
  └── SUB_PROCESS
```

### 5.2 Knowledge Model

```
KnowledgeItem
  ├── id: str
  ├── title: str
  ├── content_summary: str
  ├── category: str
  ├── tags: list[str]
  ├── knowledge_type: KnowledgeType (PROCEDURE|RUNBOOK|POLICY|REFERENCE|FAQ|CHECKLIST)
  ├── source: str
  ├── metadata: dict[str, str]
  ├── applicable_scopes: list[str]
  ├── scope_level: str
  └── own_requirements: list[KnowledgeRequirement]   ← triggers expansion

KnowledgeRequirement (declared by a procedure)
  ├── requirement_type: str (procedure|data|regulatory|approval|sub-procedure|compliance)
  ├── description: str
  ├── tags: list[str]
  ├── priority: RequirementPriority
  ├── regulatory_framework: str | None
  └── mandatory: bool
```

### 5.3 Requirements Model

```
StepRequirements (generated per BPMN step)
  ├── node_id, node_name, node_type
  ├── scope_path: list[str]
  ├── scope_depth: int
  ├── procedures: list[RequirementItem]
  ├── data_inputs: list[RequirementItem]
  ├── contextual: list[RequirementItem]
  ├── decision_criteria: list[RequirementItem]
  ├── dependencies: list[DependencyItem]
  ├── inference_sources: list[str]
  └── confidence: float

RequirementItem
  ├── requirement_id: str
  ├── description: str
  ├── category: RequirementCategory (PROCEDURE|DATA|CONTEXT|DECISION|REGULATORY)
  ├── tags: list[str]
  ├── priority: RequirementPriority (CRITICAL|IMPORTANT|HELPFUL)
  ├── source: str (explicit|type-rule|contextual|journey-check|regulatory|expanded)
  └── rationale: str

DependencyItem
  ├── depends_on_node_id: str
  ├── depends_on_node_name: str
  ├── data_needed: str
  └── scope_relationship: str (same-level|parent-scope|child-scope|cross-scope)
```

### 5.4 Coverage Model

```
RequirementCoverage
  ├── requirement: RequirementItem
  ├── coverage_level: CoverageLevel (MATCHED|PARTIAL|GAP|JOURNEY_SATISFIED|NOT_ASSESSED)
  ├── matched_knowledge: list[KnowledgeScore] | None
  ├── journey_source: JourneyOutput | None
  ├── coverage_notes: str
  └── gap_description: str | None

KnowledgeScore
  ├── knowledge_item: KnowledgeItem
  ├── total_score: float
  ├── signal_scores: dict[str, float]
  ├── signal_contributions: dict[str, float]
  └── match_explanation: str

StepCoverageReport
  ├── step_requirements: StepRequirements
  ├── procedure_coverage: list[RequirementCoverage]
  ├── data_coverage, context_coverage, decision_coverage
  ├── regulatory_requirements: list[RequirementCoverage]
  ├── expansions: list[ExpansionResult]
  ├── total_requirements, matched_count, partial_count, gap_count
  └── readiness: StepReadiness (knowledge_readiness, compliance_readiness, combined)

ProcessCoverageReport
  ├── process_name, total_steps_analyzed
  ├── total_requirements, total_matched, total_partial, total_gaps
  ├── overall_readiness: float
  ├── critical_gaps: list[RequirementCoverage]
  ├── scope_summaries: list[ScopeCoverageSummary]
  ├── compliance_summary: ComplianceSummary
  └── step_reports: list[StepCoverageReport]
```

### 5.5 Journey Model

```
JourneyContext (append-only ledger)
  ├── entries: list[JourneyEntry]
  ├── step_counter: int
  ├── outputs_by_tag: dict → list[JourneyOutput]     (inverted index)
  ├── outputs_by_node: dict → list[JourneyOutput]
  ├── decisions: list[JourneyDecision]
  ├── state: dict[str, str]                           (current accumulated state)
  └── state_history: list[tuple[int, JourneyStateChange]]

JourneyEntry
  ├── step_number: int
  ├── node_id, node_name
  ├── scope_path: list[str]
  ├── entry_type: JourneyEntryType
  ├── outputs: list[JourneyOutput]
  ├── decisions: list[JourneyDecision]
  └── state_changes: list[JourneyStateChange]

JourneyOutput
  ├── output_id: str
  ├── description: str
  ├── data_type: str
  ├── tags: list[str]
  ├── produced_by_node: str
  ├── produced_at_step: int
  └── available_to: str (all|same-scope|child-scopes)
```

### 5.6 Regulatory Model

```
RegulatoryFramework
  ├── id, name, version, description
  ├── jurisdiction: str
  └── controls: list[RegulatoryControl]

RegulatoryControl
  ├── control_id, title, description
  ├── framework_id: str
  ├── section_reference: str
  ├── severity: ControlSeverity (MANDATORY|RECOMMENDED|ADVISORY)
  ├── applies_to: list[ControlTrigger]
  ├── requirements: list[ControlRequirement]
  ├── evidence_requirements: list[str]
  └── failure_consequence: str

ControlTrigger
  ├── trigger_type: ControlTriggerType
  ├── trigger_values: list[str]
  └── match_mode: str (any|all)

ControlEvaluation (result per control per step)
  ├── control: RegulatoryControl
  ├── framework: RegulatoryFramework
  ├── triggered_by: list[ControlTrigger]
  ├── requirements: list[RequirementItem]
  ├── evidence_needed: list[str]
  └── compliance_status: ComplianceStatus

ComplianceSummary (process-level)
  ├── frameworks_evaluated: list[str]
  ├── total_controls_triggered: int
  ├── compliance_by_framework: dict[str, FrameworkCompliance]
  └── critical_violations: list[ControlEvaluation]
```

### 5.7 Expansion Model

```
ExpansionResult (from a single matched procedure)
  ├── source_item: KnowledgeItem
  ├── expanded_requirements: list[RequirementItem]
  ├── expanded_coverage: list[RequirementCoverage]
  ├── sub_expansions: list[ExpansionResult]     (recursive)
  ├── expansion_depth: int
  └── total_expanded_count: int
```

---

## 6. Orchestration Pipeline

When the walker arrives at a BPMN node, the orchestrator executes the following pipeline:

```
Step A: Gather Context
  ├── Get scope path and depth from Knowledge Context Manager (vertical)
  ├── Get prior nodes in current scope
  └── Get Journey Context reference (horizontal)

Step B: Analyze Requirements (4-layer inference)
  └── RequirementsAnalyzer.analyze_node() → StepRequirements

Step B.5: Evaluate Regulatory Controls
  ├── RegulatoryAnalyzer.evaluate_step()
  ├── Convert fired controls to RequirementItems (category=REGULATORY)
  └── Merge into StepRequirements.regulatory

Step C: Check Journey Satisfaction
  ├── For each CONTEXT and DATA requirement:
  │   └── query_prior_outputs(tags) → match found? → JOURNEY_SATISFIED
  └── Skip knowledge store lookup for journey-satisfied items

Step D: Match Remaining Requirements Against Knowledge Store
  ├── Query store with requirement tags + current scope
  └── Rank results using 5-signal scoring

Step E: Assess Coverage
  └── GapAnalyzer → MATCHED / PARTIAL / GAP per requirement

Step F: Expand Matched Procedures
  ├── For each MATCHED/PARTIAL procedure with own_requirements:
  │   └── ProcedureExpander.expand() → cascading requirements
  ├── Expanded regulatory items added to regulatory section
  └── Recalculate readiness including expanded requirements

Step G: Record in Journey
  ├── Infer what this step produces (outputs, decisions, state changes)
  └── JourneyContext.record_step() → available to all subsequent steps

Step H: Store and Emit
  ├── Store StepCoverageReport
  └── Emit to display callback (console, HTML data collection)
```

---

## 7. Output Formats

### 7.1 Console Output (excerpt)

```
═══════════════════════════════════════════════════════════════
  KNOWLEDGE REQUIREMENTS SPECIFICATION
  Process: Incident Response Process
  Analyzed: 47 nodes | 4 levels | 10 procedures | 2 frameworks
  Overall: Knowledge 73% | Compliance 58% | Combined 64%
═══════════════════════════════════════════════════════════════

[L0] ► SCOPE ENTER: Detection & Classification
       Domain: detection, classification
       Regulatory: ITIL-IM-001, ISO27001-A5.25 active

  [L1] TASK: Receive Alert (Step 1 of 47)
       Scope: Incident Response > Detection & Classification

       REGULATORY CONTROLS:
       ┌─ ITIL v4 ──────────────────────────────────────────┐
       │  ITIL-IM-001: Incident Logging and Classification   │
       │    Severity: MANDATORY                              │
       │    [MANDATORY] Log with unique ID → ✗ GAP           │
       │    [MANDATORY] Classification scheme → ✓ MATCHED    │
       │      → Severity Matrix [0.89]                       │
       └────────────────────────────────────────────────────┘

       REQUIREMENTS:
       ┌─ Procedures ───────────────────────────────────────┐
       │  [CRITICAL] Alert handling procedure               │
       │    Coverage: ✓ MATCHED → Monitoring Setup [0.87]   │
       └────────────────────────────────────────────────────┘
       ┌─ Context (from journey) ──────────────────────────┐
       │  None (first step — journey is empty)              │
       └────────────────────────────────────────────────────┘

       Readiness: Knowledge 75% | Compliance 50% | Combined 60%
```

### 7.2 HTML Output

A self-contained HTML file with:
- Collapsible subprocess tree matching BPMN hierarchy
- Color-coded coverage (green/yellow/red/blue/purple for matched/partial/gap/journey/regulatory)
- Expansion cascades as nested accordions
- Regulatory compliance panels with framework badges
- Journey context showing prior outputs and accumulated state
- Readiness score bars (knowledge + compliance + combined)
- Interactive: expand/collapse all, filter by coverage level, search, step navigator, print mode
- Embedded JSON data for downstream tooling
- Zero external dependencies (inline CSS + JS)

### 7.3 JSON Export

Machine-readable structured output containing the complete ProcessCoverageReport,
ComplianceSummary, JourneySummary, and all step-level detail.

---

## 8. Sample Domain: IT Incident Response

The demonstration uses an IT Incident Response process:

```
L0: Incident Response Process (root — 47 nodes, 4 levels)
  ├── L1: Detection & Classification
  │   ├── Receive Alert
  │   └── L2: Classify Severity
  │       ├── Assess Impact → Assess Urgency → Severity Gateway
  │       ├── [Critical] → Escalate Immediately
  │       └── [Non-Critical] → Standard Queue
  ├── L1: Triage
  │   ├── L2: Initial Investigation
  │   │   ├── Gather Context → Check Known Issues
  │   │   ├── L3: Analyze Logs (Collect → Filter → Identify → Correlate)
  │   │   └── Verify Systems
  │   └── Assignment Gateway → [T1/T2/T3]
  │       └── L2: Assign T3 (Identify → Check → Assign)
  ├── L1: Resolution
  │   ├── L2: Containment (Immediate Actions → Parallel[Fix, Isolate] → Validate)
  │   ├── L2: Root Cause Analysis
  │   │   ├── Collect Evidence → Hypothesize
  │   │   ├── L3: Test Hypothesis (Design → Execute → Evaluate)
  │   │   └── Document Findings
  │   ├── L2: Fix Implementation
  │   │   ├── Develop → Peer Review
  │   │   ├── L3: Test Fix (Unit → Integration → Staging → Smoke)
  │   │   └── Deploy
  │   └── Verify Fix
  └── L1: Post-Incident
      └── Document → Review → Improvements → Action Items
```

**Sample knowledge store:** 10 procedures (severity matrix, escalation, log analysis
runbook, rollback, communication templates, RCA, deployment checklist, post-incident
review, monitoring setup, SLA definitions). 5 procedures carry `own_requirements` for
expansion testing. 4 intentional gaps demonstrate gap analysis.

**Sample regulatory frameworks:** ITIL v4 (5 controls) + ISO 27001 (4 controls)
covering detection, investigation, resolution, and post-incident phases.

---

## 9. Configuration

### 9.1 Command Line Interface

```
python main.py [options]

Options:
  --bpmn PATH          Path to BPMN XML file (default: samples/incident_response.bpmn)
  --knowledge PATH     Path to knowledge/procedures directory (default: samples/procedures)
  --regulations PATH   Path to regulatory framework definitions (default: samples/regulations)
  --export-json PATH   Export JSON requirements spec to file
  --export-html PATH   Export interactive HTML visual spec to file
  --verbose            Show detailed scoring breakdown per requirement
  --no-expand          Disable recursive procedure expansion
  --expand-depth N     Max recursion depth for procedure expansion (default: 3)
```

### 9.2 Adding a New Regulatory Framework

Create a JSON file in the regulations directory:

```json
{
  "id": "MISMO",
  "name": "Mortgage Industry Standards Maintenance Organization",
  "version": "3.6",
  "description": "Standards for mortgage industry data exchange",
  "jurisdiction": "US",
  "controls": [
    {
      "control_id": "MISMO-LO-001",
      "title": "Borrower Identity Verification",
      "section_reference": "§4.2.1",
      "severity": "mandatory",
      "applies_to": [
        {"trigger_type": "tag_match",
         "trigger_values": ["borrower-data", "identity", "ssn"],
         "match_mode": "any"}
      ],
      "requirements": [
        {"description": "SSN verification through approved source",
         "category": "PROCEDURE",
         "tags": ["ssn-verification", "identity-check"],
         "mandatory": true}
      ],
      "evidence_requirements": ["Verification timestamp", "Source system ID"],
      "failure_consequence": "Loan cannot proceed to underwriting"
    }
  ]
}
```

The framework is automatically loaded and evaluated against all BPMN steps.

### 9.3 Adding Knowledge to the Store

Create a JSON file in the procedures directory:

```json
{
  "id": "proc_example",
  "title": "Example Procedure",
  "content_summary": "Description of what this procedure covers...",
  "category": "investigation",
  "tags": ["relevant", "tags", "for", "matching"],
  "knowledge_type": "procedure",
  "source": "Source Document v1.0",
  "metadata": {"last_updated": "2026-01-15", "owner": "Team Name"},
  "applicable_scopes": ["triage", "investigation"],
  "scope_level": "process",
  "own_requirements": []
}
```

---

## 10. Technical Constraints

| Constraint | Value |
|-----------|-------|
| Python version | 3.10+ |
| External dependencies | None (stdlib only) |
| BPMN standard | BPMN 2.0 (`http://www.omg.org/spec/BPMN/20100524/MODEL`) |
| Max subprocess nesting | Unlimited (tested to 4+, limited only by Python recursion limit of 1000) |
| Knowledge store | In-memory (phase 1); protocol-based interface for future backends |
| Regulatory frameworks | JSON files, pluggable, unlimited frameworks |
| Output formats | Console, JSON, HTML (self-contained) |
| Terminal width | 80+ characters |

---

## 11. Phase 2 Roadmap (Future)

Phase 2 transforms the Knowledge Orchestrator from a *readiness analyzer* into an
*execution engine*:

| Capability | Phase 1 (Current) | Phase 2 (Future) |
|-----------|-------------------|-------------------|
| Requirements | Inferred and displayed | Used to drive actions |
| Knowledge matching | Score and rank | Actively retrieve and assemble |
| Gap resolution | Report gaps | Trigger knowledge acquisition workflows |
| Process execution | Walk and analyze | Make decisions, route paths, execute tasks |
| Knowledge store | In-memory JSON | DB, vector store, document management integration |
| Inference | Rule-based, deterministic | LLM-enhanced, adaptive |
| Regulatory | Evaluate and report | Enforce and gate (block non-compliant steps) |

The Phase 1 Journey Context and Requirements Specification become the data layer that
Phase 2's agents consume as their "work order."
