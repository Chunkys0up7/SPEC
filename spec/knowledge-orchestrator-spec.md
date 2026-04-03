# Knowledge Orchestrator - Change Spec (v2)

## 1. Summary

**What:** A Python-based Knowledge Orchestrator that takes a BPMN 2.0 XML process definition
as input and **generates a complete Knowledge Requirements Specification** — a structured document
that maps every process step to the knowledge, data, procedures, and contextual information
required to execute it. Where a knowledge store is available, it performs gap analysis: matching
requirements against available knowledge and identifying what's covered vs. what's missing.

**Why:** Organizations have complex processes (often deeply nested) and scattered knowledge.
Today, someone looking at a BPMN must *mentally* figure out what each step needs. This component
automates that analysis — it reads a BPMN and produces a spec that says: "Step X requires
procedures A, B, C; data inputs D, E; context from prior step F; and here's what you have
vs. what's missing." This is the foundation for future agentic execution.

**Size estimate:** Large

---

## 2. Project Context

### Project Aim

Build a **Knowledge Requirements Generator** that, given any BPMN process (no matter how
deeply nested), produces a structured specification answering:

1. **What does each step need?** — Procedures, data, decisions, context from other steps
2. **Where does it come from?** — Which scope level, which source system, which prior step
3. **What do we have?** — Match requirements against available knowledge
4. **What's missing?** — Gap analysis showing unmet requirements
5. **How does knowledge flow?** — What knowledge is inherited, local, or must propagate upward

This is phase 1 of a larger vision:
- **Phase 1 (this build):** BPMN in → Knowledge Requirements Spec out. Prove the model.
- **Phase 2 (future):** Agentic execution — the orchestrator uses the requirements spec to
  actively gather knowledge, make decisions, and drive process execution.

### Current State
- Empty project directory (`C:\Users\camer\Projects\Spec`)
- No existing code, no dependencies, no prior structure
- Conceptual architecture discussed and agreed; first spec written and reviewed

### Desired State
A working Python application where you can:
1. Feed it any BPMN 2.0 XML file (including 5+ levels of subprocess nesting)
2. It parses the full process tree with all nesting levels
3. It analyzes every node and **infers what knowledge/data that step requires**
4. It checks those requirements against an available knowledge store
5. It produces a **Knowledge Requirements Specification** showing:
   - Per-step requirements (categorized: procedures, data, context, decisions)
   - Per-step coverage (what's available, what's partially covered, what's a gap)
   - Cross-step dependencies (step X needs output from step Y)
   - Scope-level summaries (what does this entire subprocess need?)
   - Process-level summary (total requirements, total coverage, critical gaps)
6. Console output walks the process step by step showing this analysis
7. Optionally exports the full spec as structured data (JSON)

### Success Criteria
1. **Parses valid BPMN 2.0 XML** including: start/end events, tasks (user, service, script,
   manual), exclusive/inclusive/parallel gateways, subprocesses (nested to arbitrary depth),
   sequence flows, documentation elements, data objects
2. **Generates knowledge requirements** for every task node based on: node name, node type,
   subprocess context, documentation/annotations, position in flow, and configurable
   requirement inference rules
3. **Categorizes requirements** into: Procedures, Data Inputs, Contextual Knowledge,
   Decision Criteria, and Dependencies
4. **Performs gap analysis** when a knowledge store is available — MATCHED, PARTIAL, GAP
5. **Knowledge scoping works** — subprocess entry creates a new scope, exit propagates
   discoveries upward, parent context is inherited downward
6. **Demo runs end-to-end** — sample BPMN + sample procedures → full requirements spec
7. **Extensible** — knowledge store interface supports future backends; requirement inference
   rules are configurable; output format is pluggable

---

## 3. Blast Radius Analysis

### Files Created

```
Spec/
├── src/
│   └── knowledge_orchestrator/
│       ├── __init__.py                    # Package init, version, public API
│       ├── models.py                      # All data models — detailed below
│       ├── bpmn_parser.py                 # BPMN 2.0 XML → ProcessDefinition
│       ├── requirements_analyzer.py       # Infers knowledge requirements per step
│       ├── walker.py                      # Process tree traversal engine
│       ├── knowledge_store.py             # Knowledge store interface + in-memory impl
│       ├── knowledge_ranker.py            # Relevance scoring and ranking
│       ├── gap_analyzer.py               # Requirements vs. available → coverage report
│       ├── knowledge_context.py           # Scoped context manager (scope stack)
│       ├── journey_context.py             # Process journey ledger (horizontal knowledge flow)
│       ├── procedure_expander.py           # Recursive procedure requirement expansion
│       ├── regulatory_analyzer.py         # Regulatory framework evaluation engine
│       ├── orchestrator.py                # Main coordinator
│       ├── spec_generator.py              # Produces the Knowledge Requirements Spec output
│       ├── html_renderer.py               # Self-contained HTML visual output
│       └── display.py                     # Console output formatting
├── samples/
│   ├── incident_response.bpmn            # Primary demo: deeply nested process
│   ├── regulations/                       # Sample regulatory frameworks
│   │   ├── itil_v4.json                  # ITIL v4 incident management controls
│   │   └── iso27001.json                 # ISO 27001 information security controls
│   └── procedures/                        # Sample procedure knowledge base (10 files)
│       ├── severity_matrix.json
│       ├── escalation_procedure.json
│       ├── log_analysis_runbook.json
│       ├── rollback_procedure.json
│       ├── communication_template.json
│       ├── root_cause_analysis.json
│       ├── deployment_checklist.json
│       ├── post_incident_review.json
│       ├── monitoring_setup.json
│       └── sla_definitions.json
├── main.py                                # Entry point / demo runner
└── requirements.txt                       # Dependencies (stdlib only)
```

### New Components vs. Original Spec

New modules added vs. original v1 spec:
- **`requirements_analyzer.py`** (NEW) — Analyzes each BPMN node and infers what
  knowledge/data it requires. This is the "BPMN → requirements" engine.
- **`gap_analyzer.py`** (NEW) — Compares inferred requirements against available knowledge.
  Produces coverage assessment: MATCHED, PARTIAL, GAP, JOURNEY_SATISFIED.
- **`journey_context.py`** (NEW) — The process journey ledger. Maintains a chronological,
  cross-scope record of every step's outputs, decisions, and state changes. Enables step 26
  to access what step 1 produced, even across subprocess boundaries.
- **`procedure_expander.py`** (NEW) — Recursive expansion engine. When a procedure is
  matched, inspects its own requirements (regulatory, sub-procedures, data dependencies)
  and cascades them into the step's requirement set. Depth-limited to prevent infinite loops.
- **`regulatory_analyzer.py`** (NEW) — Loads regulatory frameworks (MISMO, GDPR, SOX, ITIL,
  ISO27001, etc.) as structured input. Evaluates each BPMN step against all loaded controls.
  Fires controls based on domain, tags, node type, and data categories. Generates mandatory
  regulatory requirements that define the compliance floor for each step.
- **`spec_generator.py`** (NEW) — Produces the structured Knowledge Requirements Specification
  output — step-by-step detail and process-level summary.
- **`html_renderer.py`** (NEW) — Generates a self-contained HTML file (inline CSS/JS, zero
  dependencies) providing a visual, interactive, collapsible map of the full spec with
  color-coded coverage, expansion cascades, and regulatory highlighting.
- **`orchestrator.py`** (EXPANDED) — Now coordinates: parse → walk → analyze requirements →
  check journey → rank matches → expand procedures → assess gaps → generate spec + HTML.

### Interfaces Affected
- None (greenfield project)

### Downstream Dependents
- Phase 2 (agentic execution) will consume the Knowledge Requirements Specification as its
  input — the spec becomes the "work order" for the agent.
- The `KnowledgeStore` interface is designed for future DB/vector-store backends.
- The `RequirementsAnalyzer` rule system is designed for future domain-specific plugins.

### Side Effects
- None. Read-only system — parses XML, reads knowledge JSON, produces console output and
  optionally a JSON export. No external state modified.

---

## 4. Design

### 4.0 Conceptual Flow

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

### 4.1 Approach: Layer-by-Layer Build

Build from data models outward:
1. **Models** — all shared types (BPMN, knowledge, requirements, journey, regulatory, expansion)
2. **BPMN Parser** — XML → process tree
3. **Requirements Analyzer** — process node → knowledge requirements (4-layer inference)
4. **Knowledge Store** — available knowledge source
5. **Knowledge Ranker** — score/rank matches
6. **Gap Analyzer** — requirements vs. available + journey → coverage
7. **Knowledge Context** — scope stack (vertical flow)
8. **Journey Context** — process journey ledger (horizontal flow)
9. **Regulatory Analyzer** — framework loading + control evaluation per step (NEW, CRITICAL)
10. **Procedure Expander** — recursive requirement cascade from matched procedures
11. **Walker** — traversal engine
12. **Orchestrator** — wires everything (coordinates all subsystems)
13. **Spec Generator** — produces the requirements spec output
14. **Display** — console formatting (with regulatory compliance sections)
15. **HTML Renderer** — visual interactive HTML output
16. **Samples** — BPMN XML + procedures + regulatory frameworks
17. **Main** — entry point

### 4.2 Key Design Decisions

#### Decision 1: Process Tree Representation

**Choice:** A composite tree of typed node objects (not a flat graph)

**Why:** BPMN processes are inherently hierarchical. A subprocess *contains* its children —
it's not just connected to them via sequence flows. A tree naturally represents scope boundaries,
which we need for knowledge scoping. Sequence flows within a level define execution order;
parent-child relationships define nesting.

**Node hierarchy:**
```
ProcessNode (base)
  ├── EventNode (base for events)
  │   ├── StartEvent
  │   └── EndEvent
  ├── TaskNode (base for tasks)
  │   ├── UserTask      — human performs action, needs procedures + decision criteria
  │   ├── ServiceTask   — system performs action, needs data inputs + API specs
  │   ├── ScriptTask    — automated script, needs data inputs + script reference
  │   └── ManualTask    — offline action, needs procedures + checklists
  ├── GatewayNode (base for gateways)
  │   ├── ExclusiveGateway  — one path chosen, needs decision criteria
  │   ├── ParallelGateway   — all paths taken, needs coordination data
  │   └── InclusiveGateway  — one or more paths, needs evaluation criteria
  └── SubProcess — contains child nodes + flows, defines a scope boundary
```

Each node carries:
- `id: str` — unique identifier from BPMN XML
- `name: str` — human-readable name from BPMN XML
- `node_type: NodeType` — enum identifying the type
- `documentation: str | None` — raw text from `<bpmn:documentation>`
- `knowledge_tags: list[str]` — extracted from documentation (lines starting `knowledge:`)
- `data_tags: list[str]` — extracted from documentation (lines starting `data:`)
- `metadata: dict[str, str]` — any extension attributes
- `incoming_flows: list[str]` — IDs of incoming sequence flows
- `outgoing_flows: list[str]` — IDs of outgoing sequence flows
- `parent_subprocess: str | None` — ID of containing subprocess (None for top level)

**SubProcess additionally carries:**
- `child_nodes: dict[str, ProcessNode]` — contained nodes
- `child_flows: dict[str, SequenceFlow]` — contained sequence flows
- `scope_domain: str` — the knowledge domain this subprocess represents (derived from name)

**Alternative rejected:** Flat adjacency list (as used by most BPMN libraries). Loses the
hierarchical scoping information. We'd have to reconstruct it, adding complexity and fragility.

#### Decision 2: Requirements Inference Strategy

**Choice:** Rule-based inference engine with node-type-specific analyzers

**Why:** This is the core conceptual addition. When a BPMN says "Analyze Logs", a human
understands this step needs log access procedures, monitoring tool guides, and data about
which systems are affected. The Requirements Analyzer codifies this reasoning.

**How it works — three layers of inference:**

**Layer 1: Explicit Requirements (from BPMN documentation)**
The BPMN documentation element can contain structured requirement declarations:
```xml
<bpmn:documentation>
  knowledge:log-analysis,monitoring,troubleshooting
  data:system-logs,affected-systems,time-window
  context:incident-severity,affected-components
  decision:escalation-needed,specialist-required
</bpmn:documentation>
```
These are parsed directly into requirement categories. This is the most precise source.

**Layer 2: Node-Type-Based Requirements (from task type)**
Different BPMN task types have inherent knowledge needs:
```
UserTask    → always needs: procedures, role-permissions, decision-criteria
ServiceTask → always needs: api-specification, input-schema, error-handling
ScriptTask  → always needs: script-reference, input-data, output-schema
ManualTask  → always needs: step-by-step-procedure, checklist, completion-criteria
Gateway     → always needs: decision-criteria, evaluation-data, routing-rules
```
These are baseline requirements that apply regardless of the specific task.

**Layer 3: Contextual Requirements (from position and scope)**
The analyzer examines the node's position in the process to infer additional needs:
- **First task in a subprocess** → needs subprocess-level context (what is this subprocess for?)
- **Task after a gateway** → needs the decision outcome from the gateway
- **Task before an end event** → needs completion/validation criteria
- **Deep nesting (level 3+)** → needs escalation path back to parent scope
- **Subprocess domain** → the parent subprocess name implies a domain, which maps to
  domain-specific knowledge categories

**Output per node — a `StepRequirements` object:**
```python
@dataclass
class StepRequirements:
    node_id: str
    node_name: str
    node_type: NodeType
    scope_path: list[str]          # e.g., ["Incident Response", "Triage", "Log Analysis"]
    scope_depth: int

    # Categorized requirements — each is a list of RequirementItem
    procedures: list[RequirementItem]      # SOPs, runbooks, checklists needed
    data_inputs: list[RequirementItem]     # Data that must be available
    contextual: list[RequirementItem]      # Context from prior steps or parent scopes
    decision_criteria: list[RequirementItem]  # Criteria for decisions at this step
    dependencies: list[DependencyItem]     # Explicit dependencies on other steps' outputs

    # Metadata
    inference_sources: list[str]   # Which layers contributed ("explicit", "type-based", "contextual")
    confidence: float              # 0.0-1.0 — how confident are we in these requirements
```

```python
@dataclass
class RequirementItem:
    requirement_id: str            # Unique ID for tracking
    description: str               # Human-readable description of what's needed
    category: RequirementCategory  # Enum: PROCEDURE, DATA, CONTEXT, DECISION
    tags: list[str]                # Tags for matching against knowledge store
    priority: RequirementPriority  # Enum: CRITICAL, IMPORTANT, HELPFUL
    source: str                    # How was this inferred ("explicit", "type-rule", "context")
    rationale: str                 # Why this requirement was identified
```

```python
@dataclass
class DependencyItem:
    depends_on_node_id: str        # Which other node's output is needed
    depends_on_node_name: str      # Human-readable name of that node
    data_needed: str               # What specific output is needed
    scope_relationship: str        # "same-level", "parent-scope", "child-scope"
```

**Alternative rejected:** Free-text natural language inference (e.g., using an LLM to analyze
step names). Reason: adds unpredictability, latency, and a heavy dependency for phase 1.
The rule-based approach is deterministic, fast, and transparent. LLM-enhanced inference is
a clear phase 2 enhancement.

#### Decision 3: Gap Analysis Model

**Choice:** Three-tier coverage assessment (MATCHED, PARTIAL, GAP) with detailed rationale

**Why:** Knowing what's needed is only half the value. The other half is knowing what you
*have* vs. what you're *missing*. This transforms the output from a wish list into an
actionable readiness assessment.

**Coverage levels:**
```python
class CoverageLevel(Enum):
    MATCHED = "matched"       # Requirement fully covered by available knowledge
    PARTIAL = "partial"       # Requirement partially covered — some aspects missing
    GAP = "gap"               # No matching knowledge found in the store
    NOT_ASSESSED = "n/a"      # No knowledge store provided — requirements only
```

**Per-requirement coverage:**
```python
@dataclass
class RequirementCoverage:
    requirement: RequirementItem
    coverage_level: CoverageLevel
    matched_knowledge: list[KnowledgeScore] | None  # Ranked matches (if any)
    coverage_notes: str                              # What's covered vs. missing
    gap_description: str | None                      # If GAP — what specifically is missing
```

**Per-step coverage summary:**
```python
@dataclass
class StepCoverageReport:
    step_requirements: StepRequirements
    procedure_coverage: list[RequirementCoverage]
    data_coverage: list[RequirementCoverage]
    context_coverage: list[RequirementCoverage]
    decision_coverage: list[RequirementCoverage]
    dependency_status: list[DependencyStatus]

    # Computed summaries
    total_requirements: int
    matched_count: int
    partial_count: int
    gap_count: int
    readiness_score: float          # 0.0-1.0 overall readiness for this step
```

**Process-level gap summary:**
```python
@dataclass
class ProcessCoverageReport:
    process_name: str
    total_steps_analyzed: int
    total_requirements: int
    total_matched: int
    total_partial: int
    total_gaps: int
    overall_readiness: float        # 0.0-1.0

    critical_gaps: list[RequirementCoverage]    # CRITICAL priority items that are GAPs
    scope_summaries: list[ScopeCoverageSummary] # Per-subprocess rollup
    step_reports: list[StepCoverageReport]      # Full detail
```

#### Decision 4: Knowledge Matching Strategy

**Choice:** Multi-signal relevance scoring with weighted factors

**Why:** Simple keyword matching is too brittle. A step named "Analyze Logs" should match
the "Log Analysis Runbook" even if exact keywords don't overlap. Real knowledge relevance
is a spectrum, not binary.

**Scoring signals (each weighted, each producing 0.0-1.0):**

| Signal | Weight | What it measures | How it's calculated |
|--------|--------|-----------------|-------------------|
| Tag overlap | 0.30 | Do the requirement's tags match the knowledge item's tags? | Jaccard similarity: `len(A ∩ B) / len(A ∪ B)` |
| Category match | 0.25 | Does the knowledge item's category match the subprocess domain? | 1.0 if exact match, 0.5 if related domain, 0.0 otherwise |
| Keyword relevance | 0.20 | Text similarity between requirement description and knowledge title/summary | Normalized word overlap: `len(words_A ∩ words_B) / max(len(words_A), len(words_B))` |
| Scope proximity | 0.15 | How close is the knowledge item's applicable scope to the current scope? | 1.0 if same scope, 0.7 if parent, 0.4 if grandparent, 0.2 if global |
| Type fit | 0.10 | Does the knowledge type match what this requirement category needs? | 1.0 if runbook↔procedure requirement, 0.5 if partial fit, 0.0 if mismatch |

**Scoring output:**
```python
@dataclass
class KnowledgeScore:
    knowledge_item: KnowledgeItem
    total_score: float                          # Weighted sum, 0.0-1.0
    signal_scores: dict[str, float]             # Each signal's raw score
    signal_contributions: dict[str, float]      # Each signal's weighted contribution
    match_explanation: str                       # Human-readable: "Matched on tags: log-analysis, monitoring"
```

**Threshold for coverage levels:**
- `total_score >= 0.70` → MATCHED
- `0.40 <= total_score < 0.70` → PARTIAL
- `total_score < 0.40` (or no candidates) → GAP

#### Decision 5: Knowledge Scoping Model

**Choice:** Stack-based scoping that mirrors subprocess nesting

**Scope stack visualization:**
```
┌────────────────────────────────────────────────┐
│ GLOBAL SCOPE                                   │
│   Visibility: All levels, always               │
│   Contains: Org-wide procedures, SLA defs,     │
│             compliance policies                │
│   Knowledge flows: ↓ only (downward always)    │
├────────────────────────────────────────────────┤
│ SCOPE 0: "Incident Response" (process root)    │
│   Visibility: This level + all children        │
│   Contains: Incident-specific procedures,      │
│             escalation matrix, comms templates  │
│   Inherits from: Global                        │
│   Knowledge flows: ↓ to children, ↑ receives   │
│                    propagated items from L1     │
├────────────────────────────────────────────────┤
│ SCOPE 1: "Triage" (subprocess)                 │
│   Visibility: This level + children            │
│   Contains: Triage runbooks, assignment rules   │
│   Inherits from: Scope 0, Global               │
│   Knowledge flows: ↓ to children, ↑ propagates │
│                    key findings to Scope 0     │
├────────────────────────────────────────────────┤
│ SCOPE 2: "Initial Investigation" (subprocess)  │
│   Visibility: This level + children            │
│   Contains: Investigation procedures           │
│   Inherits from: Scope 1, Scope 0, Global      │
│   Knowledge flows: ↓ to children, ↑ propagates │
├────────────────────────────────────────────────┤
│ SCOPE 3: "Analyze Logs" (subprocess)           │
│   Visibility: This level only                  │
│   Contains: Log analysis runbook, pattern DB   │
│   Inherits from: Scope 2, 1, 0, Global         │
│   Knowledge flows: ↑ propagates findings       │
└────────────────────────────────────────────────┘
```

**Scope operations:**
- `push_scope(name, level)` — enter subprocess. Creates new scope inheriting from parent chain.
  Queries knowledge store for items with `applicable_scopes` matching this subprocess domain.
  Pre-loads relevant knowledge into the new scope.
- `pop_scope()` → returns the scope's state. Items marked `propagate_up=True` are added to
  the parent scope's `discovered_items`. The scope's requirements summary propagates upward
  as a dependency.
- `current_context()` → returns merged view: local + inherited + global (deduplicated, with
  source tracking so you know WHERE each item came from in the scope chain).

**Knowledge inheritance rules:**
1. A child scope can always READ parent scope items (inherited)
2. A child scope CANNOT MODIFY parent scope items
3. Items added to a child scope are LOCAL to that scope by default
4. Items explicitly marked `propagate_up=True` surface to parent on scope exit
5. Global scope items are always readable from any level
6. Requirements discovered in child scopes are summarized and attached to the parent
   subprocess node as a "subprocess requirements summary"

#### Decision 6: Walker Execution Strategy

**Choice:** Depth-first traversal following sequence flows, with subprocess entry/exit events

**Why:** BPMN execution follows sequence flows within a level. When a sequence flow leads to a
subprocess, we enter it (push scope), execute its internal flows depth-first, then exit (pop
scope). This naturally matches knowledge scoping.

**Critical design choice: we explore ALL gateway paths.**

We are not simulating execution — we are **mapping knowledge requirements for the entire process**.
At an exclusive gateway, both the "Critical" path and the "Non-Critical" path need knowledge.
We must analyze all of them.

**Gateway handling detail:**
```
ExclusiveGateway (XOR):
  Walk ALL outgoing paths. Each path's requirements are tagged with the
  gateway condition label so the spec shows: "IF Critical THEN need X;
  IF Non-Critical THEN need Y"

ParallelGateway (AND):
  Walk ALL outgoing paths. All paths execute, so all requirements are
  unconditional. Track the join point to avoid re-walking nodes after
  convergence.

InclusiveGateway (OR):
  Walk ALL outgoing paths. Requirements are tagged as "conditional" since
  any subset of paths may execute.
```

**Cycle detection:**
The walker maintains a `visited: set[str]` per scope level. If a node ID is encountered
again, the walker emits a `cycle_detected` event with the cycle path and skips the node.
This prevents infinite recursion from BPMN loop patterns.

**Walker event types:**
```python
class WalkerEventType(Enum):
    ENTER_PROCESS = "enter_process"     # Starting the top-level process
    EXIT_PROCESS = "exit_process"       # Finished the top-level process
    ENTER_SCOPE = "enter_scope"         # Entering a subprocess (push scope)
    EXIT_SCOPE = "exit_scope"           # Exiting a subprocess (pop scope)
    ENTER_NODE = "enter_node"           # Arriving at a node (analysis happens here)
    EXIT_NODE = "exit_node"             # Leaving a node
    ENTER_GATEWAY = "enter_gateway"     # Arriving at a gateway
    GATEWAY_PATH = "gateway_path"       # Starting a gateway branch (includes condition label)
    CYCLE_DETECTED = "cycle_detected"   # Loop found, node skipped
```

#### Decision 7: Spec Generator Output

**Choice:** Dual output — console display (human-readable) + JSON export (machine-readable)

**Console output structure:**
```
═══════════════════════════════════════════════════════════════
  KNOWLEDGE REQUIREMENTS SPECIFICATION
  Generated from: incident_response.bpmn
  Analyzed: 47 nodes | 4 nesting levels | 10 knowledge items available
═══════════════════════════════════════════════════════════════

PROCESS: Incident Response Process
Overall Readiness: 73% (68 of 93 requirements covered)
Critical Gaps: 4

────────────────────────────────────────────────────────────────
[L0] ► SCOPE ENTER: Detection & Classification
       Domain: detection, classification
       Scope Knowledge: 2 procedures pre-loaded
────────────────────────────────────────────────────────────────
  [L1] TASK: Receive Alert
       Scope Path: Incident Response > Detection & Classification

       REQUIREMENTS:
       ┌─ Procedures ──────────────────────────────────────────┐
       │  [CRITICAL] Alert handling procedure                  │
       │    Tags: alerting, monitoring, triage                 │
       │    Source: explicit (BPMN documentation)              │
       │    Coverage: ✓ MATCHED                                │
       │      → Monitoring Setup Guide [score: 0.87]           │
       │        Matched on: monitoring, alerting               │
       │                                                       │
       │  [IMPORTANT] Initial response checklist               │
       │    Tags: first-response, checklist                    │
       │    Source: type-rule (UserTask → needs procedure)     │
       │    Coverage: ✗ GAP                                    │
       │      → No matching procedure in knowledge store       │
       │      → Recommended: Create "Initial Response SOP"     │
       └───────────────────────────────────────────────────────┘
       ┌─ Data Inputs ────────────────────────────────────────┐
       │  [CRITICAL] Alert source and details                  │
       │    Tags: alert-data, source-system, timestamp         │
       │    Source: explicit (BPMN documentation)              │
       │    Coverage: n/a (data — not in knowledge store)     │
       │                                                       │
       │  [IMPORTANT] Affected system identifier               │
       │    Tags: system-id, infrastructure                    │
       │    Source: contextual (first task needs input data)   │
       │    Coverage: n/a (data — not in knowledge store)     │
       └───────────────────────────────────────────────────────┘
       ┌─ Dependencies ───────────────────────────────────────┐
       │  None (first task in subprocess)                      │
       └───────────────────────────────────────────────────────┘

       Step Readiness: 50% (1 of 2 procedure requirements met)

  [L1] ► SCOPE ENTER: Classify Severity
  ...

═══════════════════════════════════════════════════════════════
  SUMMARY
═══════════════════════════════════════════════════════════════

  By Category:
    Procedures:  34 requirements | 24 matched | 5 partial | 5 gaps
    Data Inputs: 28 requirements | n/a (data layer)
    Context:     19 requirements | 14 from scope chain | 5 need prior step
    Decisions:   12 requirements | 8 have criteria | 4 gaps

  By Scope Level:
    L0 Incident Response:      12 reqs | 83% ready
    L1 Detection:               8 reqs | 75% ready
    L1 Triage:                 15 reqs | 67% ready
    L1 Resolution:             22 reqs | 72% ready
    L1 Post-Incident:           8 reqs | 88% ready

  Critical Gaps (4):
    1. [L2] Initial Investigation — Missing: "Evidence Collection SOP"
    2. [L3] Analyze Logs — Missing: "Known Error Database"
    3. [L2] Containment — Missing: "Rollback Verification Checklist"
    4. [L3] Test Fix — Missing: "Staging Environment Setup Guide"
```

**JSON export structure:**
```json
{
  "spec_version": "1.0",
  "generated_from": "incident_response.bpmn",
  "generated_at": "2026-04-03T10:30:00Z",
  "process": {
    "name": "Incident Response Process",
    "total_nodes": 47,
    "max_depth": 4,
    "overall_readiness": 0.73
  },
  "steps": [
    {
      "node_id": "task_receive_alert",
      "node_name": "Receive Alert",
      "scope_path": ["Incident Response", "Detection & Classification"],
      "depth": 1,
      "requirements": {
        "procedures": [...],
        "data_inputs": [...],
        "contextual": [...],
        "decision_criteria": [...],
        "dependencies": [...]
      },
      "coverage": {
        "procedures": [...],
        "readiness_score": 0.50
      }
    }
  ],
  "summary": {
    "by_category": {...},
    "by_scope": {...},
    "critical_gaps": [...]
  }
}
```

#### Decision 8: BPMN Sample Domain

**Choice:** IT Incident Response Process

**Why:** Naturally nests deeply, is procedure-heavy, is universally understandable,
demonstrates all BPMN node types, and has clear knowledge requirements at each step.

**Target:** 4 levels of subprocess nesting, ~47 total nodes, all BPMN element types used.

#### Decision 9: Minimal External Dependencies

**Choice:** Standard library only (`xml.etree.ElementTree`, `dataclasses`, `typing`, `json`,
`argparse`, `pathlib`, `enum`). No external packages.

**Why:** Phase 1 proves the model. External dependencies add installation friction. All
interfaces are designed for easy swapping (e.g., replace `InMemoryKnowledgeStore` with
`PostgresKnowledgeStore` without touching orchestrator code).

#### Decision 10: Process Journey Context (Horizontal Knowledge Flow)

**Choice:** A dedicated `JourneyContext` that maintains a chronological, cross-scope record
of the entire process walk — every step's outputs, decisions, discoveries, and state changes
— accessible to any subsequent step regardless of subprocess boundaries.

**Why:** The scope stack (Decision 5) handles *vertical* knowledge flow — parent↔child
subprocess inheritance. But a real process is also a *journey*. Step 1 ("Receive Alert")
produces knowledge (alert details, affected system, preliminary severity) that step 26
("Deploy Fix") absolutely needs — even though they live in completely different subprocesses
("Detection" vs "Resolution > Fix Implementation") with no parent-child relationship.

Without journey context, when the walker exits "Detection & Classification" and enters "Triage",
everything learned in Detection is only available via scope propagation (which only sends
explicitly marked items upward one level). The full picture of what happened, what was decided,
what data was gathered — that's lost to sibling subprocesses.

**The journey context solves this by maintaining a process-wide, append-only knowledge ledger
that every step can read from and write to.**

**Conceptual model — two axes of knowledge flow:**
```
                    VERTICAL (scope stack)
                    ↕ Inheritance + Propagation
                    ↕ Parent ↔ Child subprocesses

    ════════════════════════════════════════════════
    HORIZONTAL (journey context)
    → Chronological accumulation across ALL steps
    → Step 1 → Step 2 → ... → Step N
    → Every step can read the full journey history
    → Crosses subprocess boundaries
    ════════════════════════════════════════════════
```

**Data model — `JourneyEntry`:**
```python
@dataclass
class JourneyEntry:
    step_number: int                    # Sequential position in the walk (1, 2, 3, ...)
    node_id: str                        # Which BPMN node produced this entry
    node_name: str                      # Human-readable node name
    scope_path: list[str]               # Full scope path at time of entry
    scope_depth: int                    # Nesting depth at time of entry
    entry_type: JourneyEntryType        # What kind of entry (see enum below)

    # What was produced/decided/discovered at this step
    outputs: list[JourneyOutput]        # Data/knowledge outputs from this step
    decisions: list[JourneyDecision]    # Decisions made at this step
    state_changes: list[JourneyStateChange]  # Process state mutations

    # Metadata
    timestamp: str                      # ISO format
    gateway_condition: str | None       # If this step is on a conditional path
```

```python
class JourneyEntryType(Enum):
    TASK_COMPLETED = "task_completed"         # A task was analyzed/would execute
    GATEWAY_EVALUATED = "gateway_evaluated"   # A gateway decision point
    SCOPE_ENTERED = "scope_entered"           # Entered a subprocess
    SCOPE_EXITED = "scope_exited"             # Exited a subprocess (with summary)
    KNOWLEDGE_DISCOVERED = "knowledge_discovered"  # New knowledge surfaced
```

```python
@dataclass
class JourneyOutput:
    output_id: str                      # Unique ID for referencing
    description: str                    # What was produced ("Alert details captured")
    data_type: str                      # Type of output ("data", "document", "decision", "status")
    tags: list[str]                     # Tags for matching by downstream steps
    produced_by_node: str               # Node ID that produced this
    produced_at_step: int               # Step number in the journey
    available_to: str                   # "all" (any step), "same-scope", "child-scopes"
```

```python
@dataclass
class JourneyDecision:
    decision_id: str                    # Unique ID
    description: str                    # What was decided ("Severity classified as S2")
    criteria_used: list[str]            # What knowledge/data informed this decision
    outcome: str                        # The decision result
    affects_steps: list[str]            # Node IDs of steps that depend on this decision
    gateway_id: str | None              # If from a gateway, which one
```

```python
@dataclass
class JourneyStateChange:
    attribute: str                      # What changed ("incident_severity", "assigned_team")
    old_value: str | None               # Previous value (None if new)
    new_value: str                      # New value
    reason: str                         # Why it changed
```

**The `JourneyContext` class:**
```python
class JourneyContext:
    _entries: list[JourneyEntry]                    # Chronological ledger (append-only)
    _step_counter: int                              # Auto-incrementing step number
    _outputs_by_tag: dict[str, list[JourneyOutput]] # Index: tag → outputs
    _outputs_by_node: dict[str, list[JourneyOutput]]# Index: node_id → outputs
    _decisions: list[JourneyDecision]               # All decisions in order
    _state: dict[str, str]                          # Current process state (mutable)
    _state_history: list[JourneyStateChange]        # Full state mutation history
```

**Key methods:**

- `record_step(node, scope_path, scope_depth, outputs, decisions, state_changes) -> JourneyEntry`
  - Creates a new `JourneyEntry` with auto-incremented step number
  - Appends to `_entries`
  - Indexes all outputs by tags and node_id
  - Appends decisions to `_decisions`
  - Applies state changes to `_state` and records in `_state_history`
  - Returns the entry

- `get_journey_so_far() -> list[JourneyEntry]`
  - Returns the full chronological ledger (read-only copy)

- `get_step_count() -> int`
  - Returns current step number

- `query_prior_outputs(tags: list[str]) -> list[JourneyOutput]`
  - Searches the output index for outputs matching any of the given tags
  - Returns matched outputs sorted by step number (most recent first)
  - This is how step 26 finds what step 1 produced

- `query_outputs_from_node(node_id: str) -> list[JourneyOutput]`
  - Returns all outputs produced by a specific node
  - Useful when a requirement explicitly depends on a named prior step

- `query_outputs_from_scope(scope_name: str) -> list[JourneyOutput]`
  - Returns all outputs produced by any step within a named subprocess
  - Useful for subprocess-level dependency resolution

- `get_decision_trail() -> list[JourneyDecision]`
  - Returns all decisions made so far, in order
  - Useful for understanding "how did we get here?"

- `get_current_state() -> dict[str, str]`
  - Returns the current accumulated process state
  - E.g., {"incident_severity": "S2", "assigned_team": "Tier 2", "containment_status": "active"}

- `get_state_at_step(step_number: int) -> dict[str, str]`
  - Reconstructs the process state as it was at a given step
  - Replays `_state_history` up to `step_number`

- `get_journey_summary() -> JourneySummary`
  - Produces a summary: total steps, scopes visited, decisions made,
    knowledge accumulated, state progression

**How journey context integrates with requirements analysis:**

When the `RequirementsAnalyzer` analyzes step 26, it now has access to:

1. **Prior step outputs** — "What data/knowledge has the process already produced?"
   The analyzer calls `journey.query_prior_outputs(requirement_tags)` to check if
   a requirement can be satisfied by a prior step's output rather than the knowledge store.

2. **Decision trail** — "What decisions have already been made that affect this step?"
   The analyzer calls `journey.get_decision_trail()` to understand the path taken.

3. **Accumulated state** — "What is the current process state?"
   The analyzer calls `journey.get_current_state()` to know things like
   "severity is S2" or "assigned to Tier 2" without re-deriving them.

4. **Cross-scope dependencies** — "What did the Detection subprocess produce that
   Resolution needs?" The analyzer calls `journey.query_outputs_from_scope("Detection")`
   to find outputs from completed sibling subprocesses.

**New requirement coverage type — `JOURNEY_SATISFIED`:**
A requirement can now be covered not just by the knowledge store (MATCHED/PARTIAL/GAP)
but also by a prior step's output:

```python
class CoverageLevel(Enum):
    MATCHED = "matched"               # Covered by knowledge store
    PARTIAL = "partial"               # Partially covered by knowledge store
    GAP = "gap"                       # Not covered at all
    JOURNEY_SATISFIED = "journey"     # Covered by a prior step's output
    NOT_ASSESSED = "n/a"              # Not assessed (e.g., data requirements)
```

```python
@dataclass
class RequirementCoverage:
    requirement: RequirementItem
    coverage_level: CoverageLevel
    matched_knowledge: list[KnowledgeScore] | None
    journey_source: JourneyOutput | None          # NEW: if satisfied by journey
    coverage_notes: str
    gap_description: str | None
```

**Example — how this works in practice:**

```
Step 3: "Assess Impact" (in Detection > Classify Severity)
  - Produces output: {tags: ["impact-level", "affected-systems", "business-impact"],
                      description: "Impact assessment completed: 3 systems affected,
                      revenue impact estimated at $50k/hour"}
  - Journey records this as JourneyOutput

... 15 steps later ...

Step 18: "Immediate Actions" (in Resolution > Containment)
  - Requirements Analyzer identifies requirement:
    [CRITICAL] "Impact assessment data for containment prioritization"
    Tags: ["impact-level", "affected-systems", "business-impact"]
  - Journey Context query: query_prior_outputs(["impact-level", "affected-systems"])
    → Returns Step 3's output (exact tag match)
  - Coverage: JOURNEY_SATISFIED
    → "Satisfied by Step 3 (Assess Impact) in Detection > Classify Severity"
    → No need to look in knowledge store — the process itself produced this data

Step 26: "Deploy Fix" (in Resolution > Fix Implementation)
  - Requirements Analyzer identifies requirement:
    [CRITICAL] "Current incident severity and affected systems for deployment risk assessment"
    Tags: ["incident-severity", "affected-systems", "deployment-risk"]
  - Journey Context:
    → get_current_state() returns {"incident_severity": "S2", "affected_systems": "3",
       "containment_status": "contained"}
    → query_prior_outputs(["affected-systems"]) returns Step 3's output
    → query_prior_outputs(["deployment-risk"]) returns nothing
  - Coverage: JOURNEY_SATISFIED for severity/systems context,
              GAP for deployment risk assessment procedure
```

**Console output addition — Journey Context section per step:**
```
  [L2] TASK: Immediate Actions (Step 18 of 47)
       Scope Path: Incident Response > Resolution > Containment

       JOURNEY CONTEXT:
       ┌─ Available from Prior Steps ─────────────────────────────┐
       │  From Step 3 (Assess Impact):                            │
       │    → Impact level, affected systems, business impact     │
       │  From Step 5 (Determine Severity):                       │
       │    → Severity classification: S2                          │
       │  From Step 8 (Gather Context):                           │
       │    → Investigation context, timeline, initial findings   │
       │  Current Process State:                                   │
       │    incident_severity: S2                                  │
       │    assigned_team: Tier 2                                  │
       │    investigation_status: complete                         │
       │    containment_status: pending                            │
       └──────────────────────────────────────────────────────────┘

       REQUIREMENTS:
       ┌─ Procedures ──────────────────────────────────────────┐
       │  [CRITICAL] Containment procedure for S2 incidents    │
       │    Coverage: ✓ MATCHED                                │
       │      → Rollback Procedure [score: 0.82]               │
       └───────────────────────────────────────────────────────┘
       ┌─ Context (from journey) ─────────────────────────────┐
       │  [CRITICAL] Impact assessment data                    │
       │    Coverage: ✓ JOURNEY (Step 3: Assess Impact)        │
       │  [CRITICAL] Current severity level                    │
       │    Coverage: ✓ JOURNEY (State: incident_severity=S2)  │
       │  [IMPORTANT] Investigation findings                   │
       │    Coverage: ✓ JOURNEY (Step 8: Gather Context)       │
       └───────────────────────────────────────────────────────┘
```

**How outputs are inferred per step (for phase 1):**

Since we're not actually executing the process, step outputs are *inferred* from:

1. **Explicit output declarations** in BPMN documentation:
   ```xml
   <bpmn:documentation>
     knowledge:severity,impact-assessment
     data:affected-systems,user-count
     output:impact-level,business-impact,affected-system-list
     decision:impact-classification
   </bpmn:documentation>
   ```
   A new `output:` tag line declares what this step produces.

2. **Type-based output inference:**
   - UserTask → produces: task-output, human-decision
   - ServiceTask → produces: service-response, processed-data
   - ScriptTask → produces: computed-result, transformed-data
   - ExclusiveGateway → produces: routing-decision, selected-path

3. **Name-based output inference:**
   - "Assess Impact" → produces: impact-assessment, impact-level
   - "Collect Logs" → produces: collected-logs, log-data
   - "Classify Severity" → produces: severity-classification, severity-level
   - Pattern: verb-noun task names → output is the noun in completed form

**Relationship to scope stack:**

The journey context and scope stack serve different purposes and coexist:

| Aspect | Scope Stack | Journey Context |
|--------|------------|----------------|
| **Flow direction** | Vertical (parent↔child) | Horizontal (step→step) |
| **Lifetime** | Created on subprocess enter, destroyed on exit | Persists for entire process |
| **Visibility** | Scoped to current + ancestors | Global — any step can query |
| **Content** | Knowledge items (procedures, references) | Step outputs, decisions, state |
| **Purpose** | "What knowledge is relevant HERE?" | "What has the process LEARNED so far?" |
| **Write pattern** | Push/pop with propagation rules | Append-only ledger |

Both feed into the `RequirementsAnalyzer`:
- Scope stack answers: "What procedures/knowledge apply to this subprocess?"
- Journey context answers: "What has already been done/decided/produced?"

**Alternative rejected:** Flattening everything into the scope stack (adding journey data
as scope items). Reason: conflates two different concepts. Scope is about relevance
(what knowledge applies here?). Journey is about accumulation (what has happened so far?).
A procedure that's irrelevant to the current scope is still irrelevant even if a prior step
used it. But a prior step's *output* is relevant even if it came from a different scope.

**Alternative rejected:** Only tracking explicit cross-step dependencies declared in BPMN.
Reason: too brittle — requires every dependency to be manually declared. The journey context
automatically makes all prior outputs queryable, so implicit dependencies are caught.

#### Decision 11: Recursive Procedure Expansion

**Choice:** When a procedure is matched to a step, the system inspects the procedure's own
declared requirements (regulatory, compliance, sub-procedures, data dependencies) and
recursively expands them into the step's requirement set.

**Why:** A procedure is not just an answer to a requirement — it's a *source* of new
requirements. When the system matches "Rollback Procedure" to the "Apply Temporary Fix"
step, that's not the end of the analysis. The Rollback Procedure itself mandates:
- Change management approval before any rollback
- Backup verification of current state
- Regulatory: Change audit trail (SOX compliance)
- Sub-procedure: "Data Retention Check" before purging rollback artifacts
- Data: Current deployment version, rollback target version, affected service map

These cascading requirements are invisible if we stop at "procedure matched." They
represent the real-world complexity where one procedure pulls in entire webs of
additional knowledge, compliance, and data needs.

**How it works — the expansion cascade:**

```
Step: "Apply Temporary Fix"
  └─ Requirement: Containment procedure
       └─ MATCHED: Rollback Procedure [score: 0.82]
            │
            ├─ Procedure requires: change-management-approval
            │    └─ Expands to: new PROCEDURE requirement
            │         "Change Management Approval Process"
            │         Tags: [change-management, approval, authorization]
            │         Priority: CRITICAL
            │         Source: "expanded from Rollback Procedure"
            │         └─ Check store → MATCHED: Change Management Policy [0.71]
            │
            ├─ Procedure requires: backup-verification
            │    └─ Expands to: new DATA requirement
            │         "Current system backup status and verification"
            │         Tags: [backup, verification, system-state]
            │         Priority: CRITICAL
            │         Source: "expanded from Rollback Procedure"
            │         └─ Check journey → JOURNEY_SATISFIED (Step 12 produced backup-status)
            │
            ├─ Procedure regulatory: sox-compliance
            │    └─ Expands to: new REGULATORY requirement (new category)
            │         "SOX-compliant change audit trail"
            │         Tags: [sox, audit-trail, compliance, change-tracking]
            │         Priority: CRITICAL
            │         Source: "regulatory requirement from Rollback Procedure"
            │         └─ Check store → GAP: No SOX compliance procedure found
            │
            └─ Procedure sub-procedure: data-retention-check
                 └─ Expands to: new PROCEDURE requirement
                      "Data Retention Check before artifact purge"
                      Tags: [data-retention, compliance, purge-policy]
                      Priority: IMPORTANT
                      Source: "sub-procedure from Rollback Procedure"
                      └─ Check store → PARTIAL [0.55]: matches Data Retention Policy
                           │
                           └─ Recurse: Data Retention Policy itself requires...
                                └─ (expansion depth limit reached — stop here)
```

**New data on KnowledgeItem — procedure requirements:**

Knowledge items in the store gain a new field: `own_requirements`:
```python
@dataclass
class KnowledgeItem:
    # ... existing fields ...

    own_requirements: list[KnowledgeRequirement]  # NEW: what this procedure itself requires
```

```python
@dataclass
class KnowledgeRequirement:
    requirement_type: str              # "procedure", "data", "regulatory", "approval",
                                       # "sub-procedure", "compliance", "certification"
    description: str                   # Human-readable description
    tags: list[str]                    # Tags for matching against store/journey
    priority: RequirementPriority      # CRITICAL, IMPORTANT, HELPFUL
    regulatory_framework: str | None   # E.g., "SOX", "GDPR", "HIPAA", "ITIL", "ISO27001"
    mandatory: bool                    # True = cannot proceed without this, False = recommended
```

**New requirement category — REGULATORY:**
```python
class RequirementCategory(Enum):
    PROCEDURE = "procedure"
    DATA = "data"
    CONTEXT = "context"
    DECISION = "decision"
    REGULATORY = "regulatory"         # NEW: compliance, audit, legal requirements
```

**Expansion engine — `ProcedureExpander` class:**

```python
class ProcedureExpander:
    def __init__(self, max_depth: int = 3):
        self._max_depth = max_depth    # Prevent infinite recursion

    def expand(self, matched_item: KnowledgeItem, step_context: StepRequirements,
               knowledge_store: KnowledgeStore, knowledge_ranker: KnowledgeRanker,
               journey: JourneyContext | None = None,
               depth: int = 0) -> ExpansionResult:
        """
        Given a matched knowledge item, inspect its own_requirements and
        recursively expand them into additional requirements for the step.
        """
```

**`ExpansionResult`:**
```python
@dataclass
class ExpansionResult:
    source_item: KnowledgeItem         # The procedure that triggered expansion
    expanded_requirements: list[RequirementItem]  # New requirements generated
    expanded_coverage: list[RequirementCoverage]  # Coverage for each expanded req
    sub_expansions: list[ExpansionResult]          # Recursive expansions (if any)
    expansion_depth: int               # How deep in the recursion chain
    total_expanded_count: int          # Total requirements across all depths
```

**Expansion logic:**
1. For each `KnowledgeRequirement` in `matched_item.own_requirements`:
   a. Convert to a `RequirementItem` with source="expanded from {item.title}"
   b. Set category based on requirement_type (procedure→PROCEDURE, regulatory→REGULATORY, etc.)
   c. Mark priority from the procedure's declaration (or elevate to CRITICAL if mandatory=True)
   d. **First check journey context** — is this already satisfied by a prior step?
   e. **Then check knowledge store** — match and rank
   f. **If matched AND depth < max_depth** — recursively expand the matched item
   g. Collect all results into `ExpansionResult`

2. **Depth limiting:** `max_depth=3` by default. At depth 3, stop recursing and log
   "expansion depth limit reached." This prevents infinite chains.

3. **Cycle detection:** Track expanded item IDs. If the same procedure appears again
   in the recursion chain, stop and log "circular expansion detected."

**How this changes the step report:**

The `StepCoverageReport` gains an `expansions` field:
```python
@dataclass
class StepCoverageReport:
    # ... existing fields ...
    expansions: list[ExpansionResult]   # NEW: cascading requirements from matched procedures
    total_expanded_requirements: int    # Count across all expansions
    expanded_gaps: list[RequirementCoverage]  # Gaps found in expanded requirements
    regulatory_requirements: list[RequirementCoverage]  # All regulatory items (new category)
```

**Console output addition — Expansion section per step:**
```
  [L2] TASK: Apply Temporary Fix (Step 22 of 47)
       Scope Path: Incident Response > Resolution > Containment

       REQUIREMENTS:
       ┌─ Procedures ──────────────────────────────────────────┐
       │  [CRITICAL] Containment/rollback procedure            │
       │    Coverage: ✓ MATCHED                                │
       │      → Rollback Procedure [score: 0.82]               │
       │                                                       │
       │    ┌─ EXPANDED FROM: Rollback Procedure ─────────────┐│
       │    │  [CRITICAL] Change management approval process   ││
       │    │    Source: procedure requirement (mandatory)      ││
       │    │    Coverage: ✓ MATCHED                           ││
       │    │      → Change Management Policy [0.71]           ││
       │    │                                                  ││
       │    │  [CRITICAL] Backup verification                  ││
       │    │    Source: data requirement                       ││
       │    │    Coverage: ✓ JOURNEY (Step 19: System Backup)  ││
       │    │                                                  ││
       │    │  [CRITICAL] SOX-compliant audit trail            ││
       │    │    Source: regulatory (SOX)                       ││
       │    │    Coverage: ✗ GAP                               ││
       │    │      → No SOX compliance procedure found         ││
       │    │      → REGULATORY GAP — may block execution      ││
       │    │                                                  ││
       │    │  [IMPORTANT] Data retention check                ││
       │    │    Source: sub-procedure                          ││
       │    │    Coverage: ~ PARTIAL [0.55]                    ││
       │    │      → Data Retention Policy (partial match)     ││
       │    └──────────────────────────────────────────────────┘│
       └───────────────────────────────────────────────────────┘
       ┌─ Regulatory ─────────────────────────────────────────┐
       │  [CRITICAL] SOX: Change audit trail (from expansion)  │
       │    Coverage: ✗ GAP                                    │
       │  Total regulatory requirements for this step: 1       │
       │  Regulatory readiness: 0%                             │
       └───────────────────────────────────────────────────────┘

       Step Readiness: 67% (expanded: 45%)
       ↑ Readiness drops when expanded requirements are included
```

**Impact on the process-level summary:**

The summary gains a regulatory section:
```
  By Category:
    Procedures:   34 requirements | 24 matched | 5 partial | 5 gaps
    Data Inputs:  28 requirements | n/a (data layer)
    Context:      19 requirements | 14 from scope chain | 5 need prior step
    Decisions:    12 requirements | 8 have criteria | 4 gaps
    Regulatory:   11 requirements | 3 matched | 2 partial | 6 gaps  ← NEW
    Expanded:     23 requirements | 12 matched | 5 partial | 6 gaps ← NEW

  Regulatory Compliance Summary:
    SOX:   2 requirements | 0 met | 2 GAPS ← CRITICAL
    ITIL:  4 requirements | 3 met | 1 gap
    GDPR:  3 requirements | 0 met | 3 GAPS ← CRITICAL
    ISO27001: 2 requirements | 2 met | 0 gaps ✓
```

**Alternative rejected:** Treating procedure requirements as static metadata only (display
them but don't expand into the requirements tree). Reason: defeats the purpose. If a
regulatory requirement exists in a procedure and we don't flag it as a gap, the whole
system's value proposition weakens. The user specifically needs to know: "this step needs
procedure X, AND procedure X requires compliance Y, AND we don't have Y documented."

**Alternative rejected:** Unlimited recursion depth. Reason: real-world procedure chains
can reference each other circularly. Max depth of 3 covers the practical cases
(procedure → sub-procedure → sub-sub-procedure) without risk.

#### Decision 12: Visual HTML Output Layer

**Choice:** A self-contained HTML file (inline CSS + inline JS, zero external dependencies)
that renders the full Knowledge Requirements Specification as an interactive, visual map.

**Why:** Console output is functional but limited — deep nesting becomes hard to follow at
80 characters, you can't collapse/expand sections, and you can't see the whole process at
a glance. An HTML file provides:
- Visual hierarchy matching subprocess nesting (collapsible tree)
- Color-coded coverage at a glance (green/yellow/red/blue)
- Click to expand/collapse any subprocess level
- Regulatory requirements highlighted distinctly
- The expansion cascade visible as nested accordions
- Process state timeline
- A file you can share with stakeholders, open in any browser

**What it is NOT:**
- Not a web application (no server, no framework, no build step)
- Not a full BPMN diagram renderer (we're not recreating Camunda Modeler)
- Not interactive editing (read-only visualization)

**Structure — a single HTML file containing:**
```
knowledge_requirements_spec.html
├── <style> block — all CSS inline (no external stylesheets)
│   ├── Layout: tree/accordion structure for subprocess nesting
│   ├── Colors: --matched (#2d7d46), --partial (#c48a1a), --gap (#c0392b),
│   │          --journey (#2980b9), --regulatory (#8e44ad), --expanded (#7f8c8d)
│   ├── Typography: monospace for scores/tags, sans-serif for descriptions
│   ├── Print styles: collapsible sections default open for printing
│   └── Responsive: readable at 768px+ width
│
├── <body> — structured HTML
│   ├── Header section
│   │   ├── Process name, generation timestamp
│   │   ├── Overview stats bar (nodes, depth, knowledge items, readiness %)
│   │   └── Legend (color key for coverage levels)
│   │
│   ├── Process map section (main content)
│   │   ├── Each subprocess as a collapsible <details> element
│   │   │   ├── <summary> = subprocess name + readiness badge
│   │   │   └── Contents = child nodes and nested subprocesses
│   │   │
│   │   ├── Each task node as a card
│   │   │   ├── Header: node name, type badge, step number
│   │   │   ├── Scope path breadcrumb
│   │   │   ├── Journey Context panel (collapsible)
│   │   │   │   ├── Available prior outputs (with source step links)
│   │   │   │   └── Current process state table
│   │   │   ├── Requirements panels (one per category)
│   │   │   │   ├── Each requirement: description, tags, coverage indicator
│   │   │   │   ├── Matched items with score bars
│   │   │   │   └── Expansion cascade (nested <details> for each expanded procedure)
│   │   │   ├── Regulatory panel (if any regulatory requirements)
│   │   │   └── Readiness score bar
│   │   │
│   │   └── Gateway nodes with path labels
│   │
│   ├── Summary section
│   │   ├── Category breakdown table
│   │   ├── Scope readiness chart (horizontal bar per scope)
│   │   ├── Regulatory compliance summary
│   │   ├── Critical gaps list
│   │   └── Journey summary (steps, outputs, decisions, state progression)
│   │
│   └── Data section (hidden, for machine use)
│       └── <script type="application/json" id="spec-data">
│           Full JSON spec embedded for potential downstream use
│           </script>
│
└── <script> block — all JS inline (no external libraries)
    ├── Toggle expand/collapse all
    ├── Filter by coverage level (show only gaps, show only regulatory)
    ├── Search/filter by node name or tag
    ├── Jump-to-step navigation (step number input)
    └── Print-friendly mode toggle
```

**Visual elements detail:**

**Readiness score bars:**
```html
<div class="readiness-bar">
  <div class="readiness-fill" style="width: 67%; background: var(--partial)"></div>
  <span class="readiness-label">67%</span>
</div>
```
- 80-100%: green
- 50-79%: amber/yellow
- 0-49%: red

**Coverage badges:**
```html
<span class="badge matched">✓ MATCHED [0.87]</span>
<span class="badge partial">~ PARTIAL [0.55]</span>
<span class="badge gap">✗ GAP</span>
<span class="badge journey">⟲ JOURNEY (Step 3)</span>
<span class="badge regulatory">⚖ REGULATORY GAP</span>
```

**Expansion cascade (nested accordions):**
```html
<details class="expansion">
  <summary>
    <span class="expansion-source">Expanded from: Rollback Procedure</span>
    <span class="expansion-count">4 additional requirements</span>
  </summary>
  <div class="expansion-requirements">
    <!-- Each expanded requirement rendered same as top-level -->
    <div class="requirement expanded">
      <span class="badge gap">✗ GAP</span>
      <span class="regulatory-flag">SOX</span>
      SOX-compliant change audit trail
    </div>
  </div>
</details>
```

**Subprocess nesting (collapsible tree):**
```html
<details class="scope" open>
  <summary class="scope-header depth-1">
    <span class="scope-name">Detection & Classification</span>
    <span class="readiness-badge amber">75%</span>
    <span class="node-count">8 nodes</span>
  </summary>
  <div class="scope-body">
    <!-- Task cards and nested subprocesses here -->
    <details class="scope" open>
      <summary class="scope-header depth-2">
        <span class="scope-name">Classify Severity</span>
        ...
```

Depth is indicated by left border color (L0=blue, L1=green, L2=amber, L3=red, L4+=purple)
and increasing left margin.

**Interactive features (all in inline JS, no dependencies):**

1. **Expand/Collapse All** — button to toggle all `<details>` elements
2. **Filter by Coverage** — buttons: "Show All", "Gaps Only", "Regulatory Only",
   "Journey Satisfied" — toggles visibility via CSS classes
3. **Search** — text input that filters nodes by name or tag match, scrolls to match
4. **Step Navigator** — number input, jumps to step N
5. **Print Mode** — opens all collapsed sections, hides interactive controls

**File generation approach:**

The `SpecGenerator` class gains a new method:
```python
def generate_html(self, report: ProcessCoverageReport,
                  journey_summary: JourneySummary | None = None) -> str:
    """Generate a self-contained HTML string for the full spec."""
```

This builds the HTML string using Python string templates (no Jinja2 or external
templating — stdlib only). The method:
1. Generates the CSS block from a template
2. Walks the `ProcessCoverageReport` tree, generating HTML for each scope and step
3. Generates the JS block from a template
4. Embeds the full JSON spec in a `<script type="application/json">` block
5. Returns the complete HTML string

The `main.py` gains a `--export-html` flag:
```
python main.py --export-html spec_output.html
```

**Alternative rejected:** Using a templating library (Jinja2). Reason: adds an external
dependency. Python f-strings and string concatenation handle this fine for a single-file
generator. The HTML structure is regular (repeating card/scope patterns).

**Alternative rejected:** React/Vue SPA. Reason: massive overkill. The data is static
(generated once, read many times). A server-rendered HTML file with vanilla JS for
interactivity is the right tool.

**Alternative rejected:** SVG flowchart rendering. Reason: extremely complex to implement
correctly (layout algorithms, arrow routing, etc.) and not necessary — the tree/accordion
view communicates the hierarchy equally well without the layout complexity. BPMN diagram
viewing is a solved problem (Camunda Modeler, bpmn.io) — we don't need to reimplement it.
Our value add is the knowledge layer, not the process visualization.

#### Decision 13: Regulatory Frameworks as First-Class Input

**Choice:** Regulatory frameworks (MISMO, GDPR, SOX, ITIL, ISO27001, HIPAA, etc.) are loaded
as structured input alongside the BPMN and knowledge store. Each framework declares a set of
**controls** — rules that activate based on what a step does, what data it touches, or what
domain it operates in. Controls impose mandatory requirements on the step regardless of what
procedures exist. Regulation defines the **floor** — procedures can add to it, never subtract.

**Why:** In regulated industries, the process isn't just "what do we need to know?" — it's
"what are we *legally required* to know, capture, verify, and retain?" A mortgage origination
step doesn't merely *benefit* from having an identity verification procedure — MISMO *mandates*
it. SOX doesn't suggest audit trails — it *requires* them. The orchestrator must distinguish
between:
- **Discretionary requirements** — "this step would benefit from procedure X" (from inference)
- **Mandatory regulatory requirements** — "this step MUST have control X per framework Y" (from regulation)

This distinction affects:
- **Readiness scoring** — regulatory gaps are weighted heavier than discretionary gaps
- **Gap severity** — a missing discretionary procedure is a risk; a missing regulatory
  control is a compliance violation
- **Reporting** — stakeholders need to see regulatory compliance separately from general
  knowledge readiness
- **Process validation** — some regulations mandate that certain steps MUST EXIST in the
  process; the orchestrator can flag missing steps

**Conceptual model — regulation as an overlay:**

```
BPMN Process (what we do)
  Step: "Verify Borrower Identity"
  │
  ├── Requirements Analyzer says:    "needs identity verification procedure"
  │                                  (inference-based, IMPORTANT priority)
  │
  ├── MISMO Framework says:          "MUST capture SSN verification per MISMO 3.6 §4.2.1"
  │                                  (regulatory, CRITICAL, mandatory, evidence required)
  │                                  "MUST retain verification for 7 years per §4.2.3"
  │                                  "MUST use approved verification source per §4.2.2"
  │
  ├── GDPR Framework says:           "Personal data processing requires legal basis (Art. 6)"
  │                                  "Data minimization — capture only what's necessary (Art. 5)"
  │                                  "Right to explanation if automated (Art. 22)"
  │
  └── SOX Framework says:            "Financial data access requires segregation of duties"
                                     "Audit trail of who accessed what, when"

  Combined requirements for this step:
    Procedures:  3 (1 inferred + 2 regulatory)
    Data:        5 (2 inferred + 3 regulatory)
    Regulatory:  6 (from MISMO + GDPR + SOX)
    Controls:    8 (all mandatory regulatory controls that fired)
```

**Data model — Regulatory Framework:**

```python
@dataclass
class RegulatoryFramework:
    id: str                         # "MISMO", "GDPR", "SOX", "HIPAA"
    name: str                       # Full name
    version: str                    # "3.6", "2016/679", etc.
    description: str                # What this framework governs
    jurisdiction: str               # "US", "EU", "global", "industry-specific"
    controls: list[RegulatoryControl]
```

```python
@dataclass
class RegulatoryControl:
    control_id: str                 # "MISMO-3.6-LO-001", "GDPR-Art6-1", "SOX-404-3"
    title: str                      # Short name: "Borrower Identity Verification"
    description: str                # Full description of what's required
    framework_id: str               # Which framework this belongs to
    section_reference: str          # "§4.2.1", "Article 6(1)", "Section 404"
    severity: ControlSeverity       # MANDATORY, RECOMMENDED, ADVISORY
    applies_to: list[ControlTrigger]  # When does this control activate?
    requirements: list[ControlRequirement]  # What does it demand?
    evidence_requirements: list[str]  # What evidence of compliance is needed?
    failure_consequence: str        # What happens if this control is not met?
```

```python
class ControlSeverity(Enum):
    MANDATORY = "mandatory"         # Legal/regulatory requirement — MUST comply
    RECOMMENDED = "recommended"     # Industry best practice — SHOULD comply
    ADVISORY = "advisory"           # Guidance — MAY comply
```

**Control trigger system — when does a control activate?**

```python
@dataclass
class ControlTrigger:
    trigger_type: ControlTriggerType
    trigger_values: list[str]       # Values to match against
    match_mode: str                 # "any" (OR) or "all" (AND)
```

```python
class ControlTriggerType(Enum):
    DOMAIN_MATCH = "domain_match"       # Step is in a subprocess matching these domains
    TAG_MATCH = "tag_match"             # Step's knowledge/data tags include any of these
    NODE_TYPE_MATCH = "node_type"       # Step is this type of BPMN node
    DATA_CATEGORY = "data_category"     # Step handles data in these categories
    STEP_NAME_PATTERN = "name_pattern"  # Step name matches a regex pattern
    SCOPE_DEPTH = "scope_depth"         # Step is at or beyond this nesting depth
    ANY_STEP = "any"                    # Applies to every step in the process
```

**Examples of control trigger configurations:**

```json
{
  "control_id": "MISMO-LO-001",
  "title": "Borrower Identity Verification",
  "applies_to": [
    {"trigger_type": "domain_match", "trigger_values": ["loan-origination", "underwriting", "identity-verification"], "match_mode": "any"},
    {"trigger_type": "tag_match", "trigger_values": ["borrower-data", "identity", "ssn", "personal-data"], "match_mode": "any"}
  ],
  "requirements": [
    {"description": "SSN verification through approved source", "category": "PROCEDURE",
     "tags": ["ssn-verification", "identity-check", "approved-source"], "mandatory": true},
    {"description": "Verification result retention for 7 years", "category": "DATA",
     "tags": ["data-retention", "verification-record", "7-year-retention"], "mandatory": true}
  ],
  "evidence_requirements": ["Verification timestamp", "Source system ID", "Operator ID"],
  "failure_consequence": "Loan cannot proceed to underwriting; regulatory citation risk"
}
```

```json
{
  "control_id": "GDPR-Art6-1",
  "title": "Lawful Basis for Processing",
  "applies_to": [
    {"trigger_type": "tag_match", "trigger_values": ["personal-data", "pii", "customer-data"], "match_mode": "any"}
  ],
  "requirements": [
    {"description": "Documented lawful basis for processing personal data", "category": "REGULATORY",
     "tags": ["lawful-basis", "consent", "legitimate-interest", "legal-obligation"], "mandatory": true},
    {"description": "Data minimization verification — only necessary data collected", "category": "DECISION",
     "tags": ["data-minimization", "necessity-check"], "mandatory": true}
  ],
  "evidence_requirements": ["Lawful basis documentation", "Data processing record (Art. 30)"],
  "failure_consequence": "GDPR violation — potential fine up to 4% of global annual turnover"
}
```

```json
{
  "control_id": "SOX-404-AuditTrail",
  "title": "Financial Data Access Audit Trail",
  "applies_to": [
    {"trigger_type": "tag_match", "trigger_values": ["financial-data", "transaction", "revenue-impact", "monetary"], "match_mode": "any"},
    {"trigger_type": "domain_match", "trigger_values": ["financial", "billing", "accounting"], "match_mode": "any"}
  ],
  "requirements": [
    {"description": "Complete audit trail of data access and modifications", "category": "DATA",
     "tags": ["audit-trail", "access-log", "modification-history"], "mandatory": true},
    {"description": "Segregation of duties — preparer cannot be approver", "category": "DECISION",
     "tags": ["segregation-of-duties", "dual-control", "four-eyes"], "mandatory": true}
  ],
  "evidence_requirements": ["Access log with timestamps", "Role separation documentation"],
  "failure_consequence": "SOX non-compliance — material weakness finding, SEC reporting required"
}
```

**The Regulatory Engine — `RegulatoryAnalyzer` class:**

```python
class RegulatoryAnalyzer:
    _frameworks: list[RegulatoryFramework]
    _control_index: dict[ControlTriggerType, dict[str, list[RegulatoryControl]]]
```

**Loading:**
- `load_frameworks(directory: str) -> int`
  - Reads all `*.json` framework files from a directory
  - Parses into `RegulatoryFramework` objects
  - Builds inverted trigger index for fast matching:
    - `_control_index[DOMAIN_MATCH]["loan-origination"] = [control1, control2, ...]`
    - `_control_index[TAG_MATCH]["personal-data"] = [control3, control4, ...]`
  - Returns count of frameworks loaded

**Evaluation — called per BPMN step:**
- `evaluate_step(node: ProcessNode, scope_path: list[str], scope_depth: int,
  step_tags: list[str]) -> list[ControlEvaluation]`
  - For each loaded framework:
    - For each control in the framework:
      - Check if ANY of the control's triggers match the current step:
        - `DOMAIN_MATCH`: check if scope_path (lowercased) contains any trigger_value
        - `TAG_MATCH`: check if step_tags overlap with trigger_values
        - `NODE_TYPE_MATCH`: check if node.node_type matches
        - `DATA_CATEGORY`: check if step's data tags overlap
        - `STEP_NAME_PATTERN`: regex match against node.name
        - `SCOPE_DEPTH`: check if scope_depth >= trigger_value
        - `ANY_STEP`: always matches
      - If matched → create `ControlEvaluation` with all the control's requirements
  - Deduplicate controls (same control can match via multiple triggers)
  - Return list of evaluations

**`ControlEvaluation`:**
```python
@dataclass
class ControlEvaluation:
    control: RegulatoryControl          # The control that fired
    framework: RegulatoryFramework      # Which framework it's from
    triggered_by: list[ControlTrigger]  # Which triggers matched
    requirements: list[RequirementItem] # Converted to standard RequirementItems
    evidence_needed: list[str]          # What evidence must be produced
    compliance_status: ComplianceStatus # COMPLIANT, NON_COMPLIANT, NEEDS_REVIEW, NOT_ASSESSED
```

```python
class ComplianceStatus(Enum):
    COMPLIANT = "compliant"             # All control requirements are MATCHED
    PARTIALLY_COMPLIANT = "partial"     # Some requirements met, some not
    NON_COMPLIANT = "non_compliant"     # Critical requirements not met
    NEEDS_REVIEW = "needs_review"       # Cannot determine automatically
    NOT_ASSESSED = "not_assessed"       # No knowledge store to check against
```

**How regulatory evaluation integrates into the orchestrator flow:**

The orchestrator's ENTER_NODE handler gains a new step between requirements analysis
and knowledge matching:

```
Step A: Gather context (scope + journey)
Step B: Analyze requirements (4-layer inference)
Step B.5: Evaluate regulatory controls ← NEW
  - Call regulatory_analyzer.evaluate_step(node, scope_path, depth, all_tags)
  - For each control that fires:
    - Convert control requirements to RequirementItems (category=REGULATORY)
    - Add to step_requirements.regulatory list
    - Mark as mandatory where control.severity == MANDATORY
    - Attach evidence_requirements as metadata
  - These regulatory requirements then flow through Steps C-H normally
    (journey check, knowledge store match, expansion, gap analysis)
Step C: Check journey satisfaction
Step D: Match against knowledge store
Step E: Assess coverage
Step F: Expand matched procedures
Step G: Record in journey
Step H: Store and emit
```

**Impact on readiness scoring:**

Readiness now has two dimensions:
```python
@dataclass
class StepReadiness:
    knowledge_readiness: float      # 0.0-1.0 — procedures, data, context coverage
    compliance_readiness: float     # 0.0-1.0 — regulatory control coverage
    combined_readiness: float       # Weighted: 0.4 * knowledge + 0.6 * compliance
                                    # (compliance weighted heavier — it's legally required)
```

A step can be 90% knowledge-ready but 30% compliance-ready if it has matched procedures
but is missing regulatory controls. The combined score reflects that compliance gaps are
more severe than knowledge gaps.

**Process-level compliance summary:**
```python
@dataclass
class ComplianceSummary:
    frameworks_evaluated: list[str]     # ["MISMO 3.6", "GDPR", "SOX"]
    total_controls_triggered: int       # How many controls fired across all steps
    total_compliant: int
    total_partially_compliant: int
    total_non_compliant: int
    compliance_by_framework: dict[str, FrameworkCompliance]
    critical_violations: list[ControlEvaluation]  # MANDATORY controls that are NON_COMPLIANT
```

```python
@dataclass
class FrameworkCompliance:
    framework_id: str
    framework_name: str
    controls_triggered: int
    compliant: int
    partially_compliant: int
    non_compliant: int
    compliance_percentage: float
    non_compliant_controls: list[ControlEvaluation]  # Detail of failures
```

**Console output — regulatory compliance section per step:**
```
  [L2] TASK: Verify Borrower Identity (Step 5 of 47)
       Scope Path: Loan Processing > Origination > Identity Verification

       REGULATORY CONTROLS:
       ┌─ MISMO 3.6 ──────────────────────────────────────────┐
       │  MISMO-LO-001: Borrower Identity Verification        │
       │    Severity: MANDATORY                                │
       │    Triggered by: domain=identity-verification,        │
       │                  tags=borrower-data,personal-data     │
       │    Requirements:                                      │
       │      [MANDATORY] SSN verification through approved    │
       │        source → ✗ NON-COMPLIANT (no procedure found)  │
       │      [MANDATORY] Verification retention (7 years)     │
       │        → ✗ NON-COMPLIANT (no retention policy found)  │
       │    Evidence needed:                                   │
       │      - Verification timestamp                         │
       │      - Source system ID                               │
       │      - Operator ID                                    │
       │    Consequence: Loan cannot proceed to underwriting   │
       └───────────────────────────────────────────────────────┘
       ┌─ GDPR ───────────────────────────────────────────────┐
       │  GDPR-Art6-1: Lawful Basis for Processing            │
       │    Severity: MANDATORY                                │
       │    Triggered by: tags=personal-data                   │
       │    Requirements:                                      │
       │      [MANDATORY] Documented lawful basis              │
       │        → ✓ COMPLIANT (matched: Privacy Policy v2.1)   │
       │      [MANDATORY] Data minimization verification       │
       │        → ✗ NON-COMPLIANT (no procedure found)         │
       │    Consequence: Fine up to 4% global annual turnover  │
       └───────────────────────────────────────────────────────┘

       READINESS:
         Knowledge:  75% ████████░░
         Compliance: 25% ███░░░░░░░  ← 3 of 4 mandatory controls non-compliant
         Combined:   45% █████░░░░░
```

**Process-level compliance summary:**
```
  REGULATORY COMPLIANCE SUMMARY
  ═══════════════════════════════════════════════════════

    MISMO 3.6:   12 controls triggered | 4 compliant | 3 partial | 5 NON-COMPLIANT
    GDPR:         8 controls triggered | 5 compliant | 1 partial | 2 NON-COMPLIANT
    SOX:          6 controls triggered | 3 compliant | 2 partial | 1 NON-COMPLIANT
    ITIL v4:      4 controls triggered | 4 compliant | 0 partial | 0 non-compliant ✓

    Critical Violations (MANDATORY + NON-COMPLIANT):
      1. [Step 5] MISMO-LO-001: SSN verification source not documented
      2. [Step 5] MISMO-LO-001: Verification retention policy missing
      3. [Step 12] GDPR-Art6-1: Data minimization check not documented
      4. [Step 22] SOX-404: Segregation of duties not enforced
         ...
```

**Sample regulatory frameworks for the incident response demo:**

Create 2 sample framework files in `samples/regulations/`:

1. **itil_v4.json** — ITIL v4 incident management controls:
   - Change management at any deployment step
   - Problem record at root cause analysis steps
   - Known error database check at investigation steps
   - Service level monitoring at all incident steps

2. **iso27001.json** — ISO 27001 information security controls:
   - Incident classification per severity matrix
   - Evidence preservation at investigation steps
   - Communication controls at notification steps
   - Access control at any step handling system credentials
   - Audit trail at all steps modifying system state

These demonstrate the regulatory overlay without requiring domain-specific knowledge
(like MISMO would need a mortgage BPMN). The incident response domain maps naturally
to ITIL and ISO 27001.

**Relationship to procedure expansion (Decision 11):**

Regulatory controls and procedure expansion work at different levels:
- **Regulatory controls** impose requirements from the TOP DOWN (framework → step)
- **Procedure expansion** discovers requirements from the BOTTOM UP (matched procedure → its needs)

Both can reference the same regulations (e.g., SOX), but the source is different:
- A SOX control firing because the step handles financial data → top-down
- A procedure's own_requirements including SOX audit trail → bottom-up

The system deduplicates: if the same regulatory requirement appears from both sources,
it's counted once but attributed to both. The regulatory analyzer is authoritative — if
it says a control applies, it applies regardless of whether a procedure also mentions it.

**Alternative rejected:** Hardcoding regulatory rules into the requirements analyzer.
Reason: regulations change, new frameworks get added, different organizations care about
different frameworks. External framework definitions (JSON files) allow customization
without code changes. An organization can define their own internal compliance framework
using the same format.

**Alternative rejected:** Treating regulation as just another type of knowledge in the store.
Reason: knowledge items are *answers* to requirements. Regulatory controls are *generators*
of requirements. They sit at a different level of the architecture. A control doesn't satisfy
a requirement — it creates one.

### 4.3 Constraints & Assumptions

**Constraints:**
- Python 3.10+ (for `match`/`case`, `str | None` union syntax, modern `dataclass` features)
- No external dependencies for the core engine
- Must run from command line: `python main.py` (with optional args)
- Console output must be readable at 80+ character terminal width
- JSON export must be valid, parseable JSON

**Assumptions:**
- BPMN XML uses the BPMN 2.0 namespace: `http://www.omg.org/spec/BPMN/20100524/MODEL`
- Knowledge items are loaded from JSON files (in-memory store for phase 1)
- Knowledge requirements per BPMN node are expressed via `<bpmn:documentation>` elements
  using a structured line format (`knowledge:tag1,tag2`, `data:tag1,tag2`, etc.)
- Gateway condition evaluation is out of scope — all paths are analyzed
- The requirements analyzer's inference rules are deterministic and configurable, not ML-based

---

## 5. Task Breakdown

### Task 1: Project Scaffolding
**Context:** Sets up the directory structure, Python package, and entry point. Everything else
depends on this being in place. Establishes the project as an importable package.
**Action:**
- Create directory tree: `src/knowledge_orchestrator/`, `samples/`, `samples/procedures/`
- Create `src/knowledge_orchestrator/__init__.py` with `__version__ = "0.1.0"` and docstring
- Create directory: `samples/regulations/`
- Create empty module files: `models.py`, `bpmn_parser.py`, `requirements_analyzer.py`,
  `walker.py`, `knowledge_store.py`, `knowledge_ranker.py`, `gap_analyzer.py`,
  `knowledge_context.py`, `journey_context.py`, `procedure_expander.py`,
  `regulatory_analyzer.py`, `orchestrator.py`, `spec_generator.py`, `html_renderer.py`,
  `display.py`
- Create `main.py` skeleton with `if __name__ == "__main__": print("Knowledge Orchestrator v0.1.0")`
- Create `requirements.txt` with comment: `# No external dependencies — stdlib only`
**Verify:** `python main.py` prints version. `python -c "from src.knowledge_orchestrator import __version__; print(__version__)"` prints "0.1.0".
**Depends:** None

### Task 2: Data Models (Comprehensive)
**Context:** All components share types. Getting models right prevents interface mismatches later.
This is the most critical foundation — every module imports from here.
**Action:** Create `models.py` with all dataclasses and enums specified in Decision 1, Decision 2,
Decision 3, and Decision 4 above. Specifically:

**Enums:**
- `NodeType`: START_EVENT, END_EVENT, TASK, USER_TASK, SERVICE_TASK, SCRIPT_TASK, MANUAL_TASK,
  EXCLUSIVE_GATEWAY, PARALLEL_GATEWAY, INCLUSIVE_GATEWAY, SUB_PROCESS
- `KnowledgeType`: PROCEDURE, RUNBOOK, POLICY, REFERENCE, FAQ, CHECKLIST
- `RequirementCategory`: PROCEDURE, DATA, CONTEXT, DECISION, REGULATORY
- `RequirementPriority`: CRITICAL, IMPORTANT, HELPFUL
- `KnowledgeRequirementType`: PROCEDURE, DATA, REGULATORY, APPROVAL, SUB_PROCEDURE,
  COMPLIANCE, CERTIFICATION
- `CoverageLevel`: MATCHED, PARTIAL, GAP, JOURNEY_SATISFIED, NOT_ASSESSED
- `WalkerEventType`: ENTER_PROCESS, EXIT_PROCESS, ENTER_SCOPE, EXIT_SCOPE, ENTER_NODE,
  EXIT_NODE, ENTER_GATEWAY, GATEWAY_PATH, CYCLE_DETECTED
- `JourneyEntryType`: TASK_COMPLETED, GATEWAY_EVALUATED, SCOPE_ENTERED, SCOPE_EXITED,
  KNOWLEDGE_DISCOVERED
- `ControlSeverity`: MANDATORY, RECOMMENDED, ADVISORY
- `ControlTriggerType`: DOMAIN_MATCH, TAG_MATCH, NODE_TYPE_MATCH, DATA_CATEGORY,
  STEP_NAME_PATTERN, SCOPE_DEPTH, ANY_STEP
- `ComplianceStatus`: COMPLIANT, PARTIALLY_COMPLIANT, NON_COMPLIANT, NEEDS_REVIEW,
  NOT_ASSESSED

**BPMN model dataclasses:**
- `SequenceFlow(id, name, source_ref, target_ref, condition_expression)`
- `ProcessNode(id, name, node_type, documentation, knowledge_tags, data_tags, metadata,
  incoming_flows, outgoing_flows, parent_subprocess)`
- `SubProcess(ProcessNode)` + `child_nodes, child_flows, scope_domain`
- `ProcessDefinition(id, name, nodes, flows, description)`

**Knowledge model dataclasses:**
- `KnowledgeItem(id, title, content_summary, category, tags, knowledge_type, source,
  metadata, applicable_scopes, scope_level, own_requirements)` — note: `own_requirements`
  is a `list[KnowledgeRequirement]` declaring what this procedure itself requires
- `KnowledgeRequirement(requirement_type, description, tags, priority,
  regulatory_framework, mandatory)` — a requirement declared by a knowledge item
- `KnowledgeScore(knowledge_item, total_score, signal_scores, signal_contributions,
  match_explanation)`

**Requirements model dataclasses:**
- `RequirementItem(requirement_id, description, category, tags, priority, source, rationale)`
- `DependencyItem(depends_on_node_id, depends_on_node_name, data_needed, scope_relationship)`
- `StepRequirements(node_id, node_name, node_type, scope_path, scope_depth, procedures,
  data_inputs, contextual, decision_criteria, dependencies, inference_sources, confidence)`

**Coverage model dataclasses:**
- `RequirementCoverage(requirement, coverage_level, matched_knowledge, coverage_notes,
  gap_description)`
- `StepCoverageReport(step_requirements, procedure_coverage, data_coverage, context_coverage,
  decision_coverage, dependency_status, total_requirements, matched_count, partial_count,
  gap_count, readiness_score)`
- `ProcessCoverageReport(process_name, total_steps_analyzed, total_requirements, total_matched,
  total_partial, total_gaps, overall_readiness, critical_gaps, scope_summaries, step_reports)`

**Context model dataclasses:**
- `KnowledgeContext(scope_name, scope_level, scope_domain, local_items, inherited_items,
  discovered_items)`
- `ScopeCoverageSummary(scope_name, scope_level, total_requirements, matched, partial,
  gaps, readiness)`

**Journey model dataclasses:**
- `JourneyEntry(step_number, node_id, node_name, scope_path, scope_depth, entry_type,
  outputs, decisions, state_changes, timestamp, gateway_condition)`
- `JourneyOutput(output_id, description, data_type, tags, produced_by_node,
  produced_at_step, available_to)`
- `JourneyDecision(decision_id, description, criteria_used, outcome, affects_steps,
  gateway_id)`
- `JourneyStateChange(attribute, old_value, new_value, reason)`
- `JourneySummary(total_steps, scopes_visited, decisions_made, outputs_produced,
  state_attributes_tracked, journey_entries)`

**Walker model dataclasses:**
- `WalkerEvent(event_type, node, depth, scope_path, metadata)`

**Updated coverage model (adds journey source + expansion):**
- `RequirementCoverage` now includes `journey_source: JourneyOutput | None` for
  requirements satisfied by prior step outputs rather than the knowledge store.

**Regulatory model dataclasses:**
- `RegulatoryFramework(id, name, version, description, jurisdiction, controls)`
- `RegulatoryControl(control_id, title, description, framework_id, section_reference,
  severity, applies_to, requirements, evidence_requirements, failure_consequence)`
- `ControlTrigger(trigger_type, trigger_values, match_mode)`
- `ControlRequirement(description, category, tags, mandatory, evidence_required)`
- `ControlEvaluation(control, framework, triggered_by, requirements, evidence_needed,
  compliance_status)`
- `ComplianceSummary(frameworks_evaluated, total_controls_triggered, total_compliant,
  total_partially_compliant, total_non_compliant, compliance_by_framework,
  critical_violations)`
- `FrameworkCompliance(framework_id, framework_name, controls_triggered, compliant,
  partially_compliant, non_compliant, compliance_percentage, non_compliant_controls)`
- `StepReadiness(knowledge_readiness, compliance_readiness, combined_readiness)` — two
  dimensions of readiness, weighted (compliance at 0.6, knowledge at 0.4)

**Expansion model dataclasses:**
- `ExpansionResult(source_item, expanded_requirements, expanded_coverage,
  sub_expansions, expansion_depth, total_expanded_count)` — result of recursively
  expanding a matched procedure's own requirements
- `StepCoverageReport` gains: `expansions: list[ExpansionResult]`,
  `total_expanded_requirements: int`, `expanded_gaps: list[RequirementCoverage]`,
  `regulatory_requirements: list[RequirementCoverage]`
- `ProcessCoverageReport` gains: `total_regulatory: int`, `regulatory_matched: int`,
  `regulatory_gaps: int`, `regulatory_by_framework: dict[str, dict]` (per-framework summary)

**Verify:** All dataclasses instantiate with sample data without error. Enum values accessible.
Type hints consistent — no forward reference issues. No circular imports. JourneyEntry
can hold multiple outputs and decisions. JourneySummary computes from entry list.
KnowledgeRequirement and ExpansionResult can nest recursively up to depth 3.
**Depends:** Task 1

### Task 3: BPMN XML Parser
**Context:** Transforms BPMN 2.0 XML into our ProcessDefinition tree. Must handle arbitrary
nesting depth. This is the input pipeline — everything downstream depends on correct parsing.

**Action:** Create `bpmn_parser.py` with class `BPMNParser`:

**Constants:**
- `BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"` — the BPMN 2.0 namespace
- `NS_MAP = {"bpmn": BPMN_NS}` — for ElementTree namespace resolution
- `ELEMENT_TYPE_MAP` — maps XML tag names to `NodeType` enum values:
  ```python
  {
      "startEvent": NodeType.START_EVENT,
      "endEvent": NodeType.END_EVENT,
      "task": NodeType.TASK,
      "userTask": NodeType.USER_TASK,
      "serviceTask": NodeType.SERVICE_TASK,
      "scriptTask": NodeType.SCRIPT_TASK,
      "manualTask": NodeType.MANUAL_TASK,
      "exclusiveGateway": NodeType.EXCLUSIVE_GATEWAY,
      "parallelGateway": NodeType.PARALLEL_GATEWAY,
      "inclusiveGateway": NodeType.INCLUSIVE_GATEWAY,
      "subProcess": NodeType.SUB_PROCESS,
  }
  ```

**Public method:**
- `parse(xml_path: str) -> ProcessDefinition`
  - Read and parse XML file using `xml.etree.ElementTree`
  - Find the `<bpmn:process>` element
  - Extract process id, name
  - Call `_parse_level(process_element)` to recursively build the tree
  - Return `ProcessDefinition` with the fully built node/flow dictionaries

**Private methods:**
- `_parse_level(parent_element) -> tuple[dict[str, ProcessNode], dict[str, SequenceFlow]]`
  - Iterate over child elements of the parent
  - For each recognized element type: create the appropriate `ProcessNode` subclass
  - For `subProcess` elements: recursively call `_parse_level` on the subprocess element,
    creating a `SubProcess` node with `child_nodes` and `child_flows`
  - Parse all `sequenceFlow` elements at this level
  - Wire up `incoming_flows` and `outgoing_flows` on each node by scanning flows
  - Return the nodes dict and flows dict for this level

- `_parse_node(element, node_type: NodeType) -> ProcessNode`
  - Extract `id` and `name` attributes
  - Parse `<bpmn:documentation>` child element if present
  - Call `_extract_knowledge_tags(documentation)` to get knowledge requirement tags
  - Call `_extract_data_tags(documentation)` to get data requirement tags
  - Construct and return the appropriate `ProcessNode` (or subclass)

- `_extract_knowledge_tags(doc_text: str) -> list[str]`
  - Find lines starting with `knowledge:` in the documentation text
  - Split on commas, strip whitespace
  - Return list of tags

- `_extract_data_tags(doc_text: str) -> list[str]`
  - Same pattern for lines starting with `data:`

- `_extract_context_tags(doc_text: str) -> list[str]`
  - Same pattern for lines starting with `context:`

- `_extract_decision_tags(doc_text: str) -> list[str]`
  - Same pattern for lines starting with `decision:`

- `_parse_sequence_flow(element) -> SequenceFlow`
  - Extract `id`, `name`, `sourceRef`, `targetRef`
  - Extract condition expression from `<bpmn:conditionExpression>` child if present

**Error handling:**
- Unknown element types: log a warning, skip the element (don't crash)
- Missing `id` attribute: raise `BPMNParseError` with element details
- Missing `name` attribute: default to `"Unnamed {node_type}"`
- Malformed XML: let `ElementTree.parse()` raise its own exception

**Verify:** Create a minimal test BPMN (inline in a test or a small file) with:
- 1 process containing: start → task → subprocess → end
- Subprocess containing: start → task → end
- Parse it, verify: 2 levels, correct node types, correct flow wiring, documentation extracted.
**Depends:** Task 2

### Task 4: Sample BPMN XML — Incident Response Process
**Context:** The primary demo artifact. Must be realistic, deeply nested, and exercise all
parser features. Each task node needs structured documentation declaring its knowledge and
data requirements.

**Action:** Create `samples/incident_response.bpmn` with the full process tree as specified
in Decision 8. The file must be valid BPMN 2.0 XML.

**Structure (47 nodes across 4 levels):**

```
L0: Incident Response Process (root)
    Nodes: StartEvent, 4 SubProcesses (Detection, Triage, Resolution, PostIncident),
           1 EndEvent
    Flows: start → Detection → Triage → Resolution → PostIncident → end

  L1: Detection & Classification (SubProcess)
      Nodes: StartEvent, Receive Alert (UserTask), Classify Severity (SubProcess), EndEvent
      Flows: start → Receive Alert → Classify Severity → end

    L2: Classify Severity (SubProcess)
        Nodes: StartEvent, Assess Impact (UserTask), Assess Urgency (UserTask),
               Determine Severity (ExclusiveGateway), Escalate Immediately (ServiceTask),
               Standard Queue (ServiceTask), EndEvent
        Flows: start → Assess Impact → Assess Urgency → gateway →
               [Critical] Escalate → end, [Non-Critical] Standard Queue → end

  L1: Triage (SubProcess)
      Nodes: StartEvent, Initial Investigation (SubProcess), Assignment (ExclusiveGateway),
             Assign T1 (UserTask), Assign T2 (UserTask), Assign T3 (SubProcess), EndEvent
      Flows: start → Initial Investigation → Assignment gateway →
             [Tier1] Assign T1 → end, [Tier2] Assign T2 → end, [Tier3] Assign T3 → end

    L2: Initial Investigation (SubProcess)
        Nodes: StartEvent, Gather Context (UserTask), Check Known Issues (UserTask),
               Analyze Logs (SubProcess), Verify Systems (UserTask), EndEvent
        Flows: start → Gather Context → Check Known Issues → Analyze Logs → Verify Systems → end

      L3: Analyze Logs (SubProcess)
          Nodes: StartEvent, Collect Logs (ServiceTask), Filter Relevant (ScriptTask),
                 Identify Patterns (UserTask), Correlate Events (UserTask), EndEvent
          Flows: start → Collect → Filter → Identify → Correlate → end

    L2: Assign T3 - Specialist Assignment (SubProcess)
        Nodes: StartEvent, Identify Specialists (UserTask), Check Availability (ServiceTask),
               Assign & Notify (ServiceTask), EndEvent
        Flows: start → Identify → Check → Assign → end

  L1: Resolution (SubProcess)
      Nodes: StartEvent, Containment (SubProcess), Root Cause Analysis (SubProcess),
             Fix Implementation (SubProcess), Verify Fix (UserTask), EndEvent
      Flows: start → Containment → RCA → Fix Implementation → Verify Fix → end

    L2: Containment (SubProcess)
        Nodes: StartEvent, Immediate Actions (UserTask), Fork (ParallelGateway),
               Apply Temporary Fix (UserTask), Isolate Affected Systems (ServiceTask),
               Join (ParallelGateway), Validate Containment (UserTask), EndEvent
        Flows: start → Immediate Actions → Fork →
               [path1] Apply Fix, [path2] Isolate Systems → Join → Validate → end

    L2: Root Cause Analysis (SubProcess)
        Nodes: StartEvent, Collect Evidence (UserTask), Hypothesize (UserTask),
               Test Hypothesis (SubProcess), Document Findings (UserTask), EndEvent
        Flows: start → Collect → Hypothesize → Test → Document → end

      L3: Test Hypothesis (SubProcess)
          Nodes: StartEvent, Design Test (UserTask), Execute Test (ServiceTask),
                 Evaluate Results (ExclusiveGateway), Confirm (EndEvent),
                 Revise Hypothesis (UserTask), Revise End (EndEvent)
          Flows: start → Design → Execute → Evaluate →
                 [Confirmed] → Confirm end, [Rejected] → Revise → Revise end

    L2: Fix Implementation (SubProcess)
        Nodes: StartEvent, Develop Fix (UserTask), Peer Review (UserTask),
               Test Fix (SubProcess), Deploy (ServiceTask), EndEvent
        Flows: start → Develop → Peer Review → Test Fix → Deploy → end

      L3: Test Fix (SubProcess)
          Nodes: StartEvent, Unit Test (ScriptTask), Integration Test (ScriptTask),
                 Staging Deploy (ServiceTask), Smoke Test (UserTask), EndEvent
          Flows: start → Unit Test → Integration Test → Staging Deploy → Smoke Test → end

  L1: Post-Incident (SubProcess)
      Nodes: StartEvent, Document Incident (UserTask), Conduct Review (UserTask),
             Identify Improvements (UserTask), Create Action Items (UserTask), EndEvent
      Flows: start → Document → Conduct Review → Identify Improvements → Create Actions → end
```

**Documentation annotations per task** (examples — now including `output:` tags for journey
context recording):
```xml
<bpmn:userTask id="task_receive_alert" name="Receive Alert">
  <bpmn:documentation>
    knowledge:alerting,monitoring,triage,first-response
    data:alert-source,alert-details,timestamp,affected-system
    context:none
    decision:severity-preliminary,escalation-needed
    output:alert-details,affected-system-id,preliminary-severity,alert-timestamp
  </bpmn:documentation>
</bpmn:userTask>

<bpmn:userTask id="task_assess_impact" name="Assess Impact">
  <bpmn:documentation>
    knowledge:severity,impact-assessment,classification,business-impact
    data:affected-systems,user-count,revenue-impact,service-dependencies
    context:alert-details,preliminary-severity
    decision:impact-level
    output:impact-level,affected-system-count,business-impact-estimate,impact-classification
  </bpmn:documentation>
</bpmn:userTask>

<bpmn:serviceTask id="task_collect_logs" name="Collect Logs">
  <bpmn:documentation>
    knowledge:log-analysis,log-collection,monitoring,system-access
    data:system-logs,log-locations,time-window,affected-components
    context:incident-severity,affected-systems,investigation-scope
    output:collected-logs,log-timespan,log-sources-accessed
  </bpmn:documentation>
</bpmn:serviceTask>

<bpmn:userTask id="task_immediate_actions" name="Immediate Actions">
  <bpmn:documentation>
    knowledge:containment,first-response,rollback,isolation
    data:affected-systems,current-impact,service-dependencies
    context:incident-severity,affected-systems,investigation-findings,triage-outcome
    decision:containment-strategy,rollback-needed
    output:containment-actions-taken,systems-isolated,temporary-mitigations
  </bpmn:documentation>
</bpmn:userTask>
```

Every task node gets documentation with all five tag categories (`knowledge`, `data`, `context`,
`decision`, `output`). The `output:` tags declare what data/knowledge this step produces,
which feeds into the journey context for downstream steps. Gateways get `decision:` and
`output:` tags. SubProcess nodes get `knowledge:` tags indicating their domain.

**Verify:** Valid XML parseable by `xml.etree.ElementTree`. 47 nodes across 4 nesting levels.
All task nodes have structured documentation. All sequence flows have valid sourceRef/targetRef.
**Depends:** None (parallel with Tasks 2-3)

### Task 5: Sample Procedure Knowledge Base
**Context:** The knowledge store needs realistic data. These procedures match the incident
response BPMN, demonstrating both good matches and intentional gaps (to show gap analysis).

**Action:** Create 10 JSON files in `samples/procedures/`. Each file follows this schema:

```json
{
  "id": "proc_severity_matrix",
  "title": "Incident Severity Classification Matrix",
  "content_summary": "Defines severity levels (S1-S4) based on business impact and urgency.
    Includes criteria for each level, escalation thresholds, and SLA response/resolution
    times per severity. Used during initial classification and when severity changes during
    an incident.",
  "category": "classification",
  "tags": ["severity", "classification", "impact", "urgency", "sla", "escalation-threshold"],
  "knowledge_type": "procedure",
  "source": "IT Service Management Handbook v3.2",
  "metadata": {
    "last_updated": "2025-11-15",
    "owner": "IT Service Desk",
    "review_cycle": "quarterly",
    "compliance": "ITIL v4"
  },
  "applicable_scopes": ["detection", "classification", "triage"],
  "scope_level": "process"
}
```

**The 10 procedures:**

1. **severity_matrix.json**
   - Category: classification
   - Tags: severity, classification, impact, urgency, sla, escalation-threshold
   - Type: procedure
   - Scopes: detection, classification, triage
   - Purpose: Severity level definitions and classification criteria

2. **escalation_procedure.json**
   - Category: escalation
   - Tags: escalation, notification, critical, management, communication, chain-of-command
   - Type: procedure
   - Scopes: detection, triage, resolution (global-ish)
   - Purpose: When and how to escalate, notification chains

3. **log_analysis_runbook.json**
   - Category: investigation
   - Tags: log-analysis, monitoring, troubleshooting, patterns, log-collection, correlation
   - Type: runbook
   - Scopes: triage, investigation, log-analysis
   - Purpose: Step-by-step log collection, filtering, pattern identification

4. **rollback_procedure.json**
   - Category: containment
   - Tags: rollback, deployment, containment, recovery, system-restore, change-reversal
   - Type: procedure
   - Scopes: resolution, containment, fix-implementation
   - Purpose: How to safely rollback changes, restore service

5. **communication_template.json**
   - Category: communication
   - Tags: communication, stakeholder, status-update, notification, template, reporting
   - Type: reference
   - Scopes: all (global)
   - Purpose: Stakeholder update templates for different audiences/severity levels

6. **root_cause_analysis.json**
   - Category: investigation
   - Tags: rca, investigation, hypothesis, evidence, root-cause, five-whys, fishbone
   - Type: procedure
   - Scopes: resolution, root-cause-analysis
   - Purpose: RCA methodology, evidence collection framework

7. **deployment_checklist.json**
   - Category: deployment
   - Tags: deployment, release, testing, staging, go-live, checklist, approval
   - Type: checklist
   - Scopes: resolution, fix-implementation
   - Purpose: Pre-deployment and post-deployment verification steps

8. **post_incident_review.json**
   - Category: review
   - Tags: post-mortem, review, improvements, lessons-learned, action-items, blameless
   - Type: procedure
   - Scopes: post-incident
   - Purpose: Blameless post-mortem process, template for review meetings

9. **monitoring_setup.json**
   - Category: detection
   - Tags: monitoring, alerting, dashboards, thresholds, observability, metrics
   - Type: runbook
   - Scopes: detection, post-incident (for improvement)
   - Purpose: How monitoring is configured, dashboard locations, alert thresholds

10. **sla_definitions.json**
    - Category: governance
    - Tags: sla, response-time, resolution-time, priority, compliance, reporting
    - Type: reference
    - Scopes: all (global)
    - Purpose: SLA targets per severity, compliance requirements, reporting cadence

**Procedure own_requirements** (examples — these trigger recursive expansion):

1. **rollback_procedure.json** `own_requirements`:
   - `{type: "approval", desc: "Change management approval before rollback",
      tags: ["change-management", "approval", "authorization"],
      priority: CRITICAL, mandatory: true}`
   - `{type: "data", desc: "Current system backup verification",
      tags: ["backup", "verification", "system-state"],
      priority: CRITICAL, mandatory: true}`
   - `{type: "regulatory", desc: "SOX-compliant change audit trail",
      tags: ["sox", "audit-trail", "compliance", "change-tracking"],
      regulatory_framework: "SOX", priority: CRITICAL, mandatory: true}`
   - `{type: "sub-procedure", desc: "Data retention check before artifact purge",
      tags: ["data-retention", "compliance", "purge-policy"],
      priority: IMPORTANT, mandatory: false}`

2. **escalation_procedure.json** `own_requirements`:
   - `{type: "data", desc: "Current on-call roster and contact details",
      tags: ["on-call", "roster", "contacts"],
      priority: CRITICAL, mandatory: true}`
   - `{type: "regulatory", desc: "GDPR-compliant notification for personal data incidents",
      tags: ["gdpr", "notification", "personal-data", "breach-notification"],
      regulatory_framework: "GDPR", priority: CRITICAL, mandatory: true}`

3. **deployment_checklist.json** `own_requirements`:
   - `{type: "approval", desc: "Release manager sign-off",
      tags: ["release-approval", "sign-off", "authorization"],
      priority: CRITICAL, mandatory: true}`
   - `{type: "data", desc: "Staging environment test results",
      tags: ["staging", "test-results", "qa-sign-off"],
      priority: CRITICAL, mandatory: true}`
   - `{type: "compliance", desc: "ITIL change management record",
      tags: ["itil", "change-record", "change-management"],
      regulatory_framework: "ITIL", priority: IMPORTANT, mandatory: false}`

4. **severity_matrix.json** `own_requirements`:
   - `{type: "regulatory", desc: "ISO 27001 incident classification compliance",
      tags: ["iso27001", "incident-classification", "compliance"],
      regulatory_framework: "ISO27001", priority: IMPORTANT, mandatory: false}`

5. **post_incident_review.json** `own_requirements`:
   - `{type: "data", desc: "Complete incident timeline with all actions taken",
      tags: ["timeline", "incident-log", "action-history"],
      priority: CRITICAL, mandatory: true}`
   - `{type: "procedure", desc: "Blameless post-mortem facilitation guide",
      tags: ["facilitation", "blameless", "post-mortem-guide"],
      priority: IMPORTANT, mandatory: false}`

The remaining 5 procedures have empty `own_requirements: []` for simplicity.

**Intentional gaps** (procedures NOT in the store, to demonstrate gap analysis):
- No "Initial Response SOP" → gap for "Receive Alert" step
- No "Known Error Database" → gap for "Check Known Issues" step
- No "Evidence Collection Guide" → gap for "Collect Evidence" step
- No "Staging Environment Guide" → gap for "Staging Deploy" step

**Intentional regulatory gaps** (from expansion, to demonstrate regulatory gap analysis):
- No SOX compliance procedure → regulatory gap when Rollback Procedure is expanded
- No GDPR breach notification procedure → regulatory gap when Escalation Procedure is expanded

**Verify:** All 10 JSON files parse correctly. Tags cover the majority of BPMN documentation
requirements. The 4 intentional gaps are confirmed absent.
**Depends:** None (parallel with Tasks 2-4)

### Task 6: Knowledge Store Interface + In-Memory Implementation
**Context:** Provides access to available knowledge. Clean interface so future backends
(PostgreSQL, vector store, Elasticsearch) can swap in without changing the orchestrator.

**Action:** Create `knowledge_store.py` with:

**Abstract interface (`KnowledgeStore` using Protocol):**
```python
class KnowledgeStore(Protocol):
    def query(self, tags: list[str], scope: str | None = None,
              category: str | None = None) -> list[KnowledgeItem]: ...
    def get_by_id(self, item_id: str) -> KnowledgeItem | None: ...
    def get_all(self) -> list[KnowledgeItem]: ...
    def get_by_category(self, category: str) -> list[KnowledgeItem]: ...
    def get_by_scope(self, scope: str) -> list[KnowledgeItem]: ...
    def get_by_type(self, knowledge_type: KnowledgeType) -> list[KnowledgeItem]: ...
    def count(self) -> int: ...
```

**In-memory implementation (`InMemoryKnowledgeStore`):**
- `__init__(self)` — initializes empty store with index structures
- `load_from_directory(self, dir_path: str) -> int` — reads all `*.json` files from
  directory, parses each into `KnowledgeItem`, builds indices, returns count loaded
- `_build_indices(self)` — creates:
  - `_by_id: dict[str, KnowledgeItem]` — primary lookup
  - `_by_tag: dict[str, list[KnowledgeItem]]` — inverted tag index
  - `_by_category: dict[str, list[KnowledgeItem]]` — category index
  - `_by_scope: dict[str, list[KnowledgeItem]]` — scope applicability index
  - `_by_type: dict[KnowledgeType, list[KnowledgeItem]]` — type index
- `query(self, tags, scope, category)` — returns all items matching ANY of the provided
  tags. If scope is provided, filters to items with that scope in `applicable_scopes` or
  with scope_level="global". If category provided, additional filter. Results deduplicated.
  Returns items sorted by number of matching tags (most matches first, as a basic pre-rank).

**Verify:** Load 10 sample procedures. `count()` returns 10. Query by tag "monitoring" returns
Monitoring Setup + Log Analysis Runbook. Query by scope "post-incident" returns Post Incident
Review + SLA Definitions (global). `get_by_id("proc_severity_matrix")` returns correct item.
**Depends:** Task 2, Task 5

### Task 7: Requirements Analyzer
**Context:** This is the **core new component** — the conceptual heart of the system. It
examines each BPMN node and infers what knowledge, data, context, and decisions are needed.
This is what turns "BPMN in" into "requirements spec out."

**Action:** Create `requirements_analyzer.py` with class `RequirementsAnalyzer`:

**Constructor:**
- Takes optional `type_rules: dict` and `context_rules: dict` for configurability
- Initializes default rule sets if none provided

**Public methods:**

- `analyze_node(node: ProcessNode, scope_path: list[str], scope_depth: int,
  prior_nodes: list[ProcessNode] | None = None,
  journey: JourneyContext | None = None) -> StepRequirements`
  - Calls all three inference layers
  - If journey is provided, calls Layer 4 (journey-aware requirements)
  - Merges and deduplicates requirements
  - Sets confidence based on how many layers contributed
  - Returns `StepRequirements`

- `infer_outputs(node: ProcessNode, scope_path: list[str]) -> list[JourneyOutput]`
  - Infers what this step PRODUCES (for recording in the journey context)
  - Three sources: explicit `output:` tags in documentation, type-based inference,
    name-based inference (verb-noun → completed noun)
  - Returns list of `JourneyOutput` objects for the journey ledger

**Layer 1 — Explicit requirements extraction:**
- `_extract_explicit_requirements(node) -> tuple[list, list, list, list]`
  - Reads `node.knowledge_tags` → creates `RequirementItem` entries with
    `category=PROCEDURE`, `source="explicit"`, `priority=CRITICAL`
  - Reads `node.data_tags` → creates `RequirementItem` entries with
    `category=DATA`, `source="explicit"`, `priority=CRITICAL`
  - Reads context tags from documentation → creates `RequirementItem` entries with
    `category=CONTEXT`, `source="explicit"`, `priority=IMPORTANT`
  - Reads decision tags from documentation → creates `RequirementItem` entries with
    `category=DECISION`, `source="explicit"`, `priority=IMPORTANT`
  - For each tag, generates a human-readable description from the tag name
    (e.g., "log-analysis" → "Log analysis procedure or runbook")

**Layer 2 — Node-type-based requirements:**
- `_infer_type_requirements(node) -> tuple[list, list, list, list]`
  - Based on `node.node_type`, adds baseline requirements:
  ```python
  TYPE_RULES = {
      NodeType.USER_TASK: {
          "procedures": [
              RequirementItem(desc="Standard operating procedure for this activity",
                            tags=["sop", "procedure"], priority=IMPORTANT,
                            source="type-rule",
                            rationale="UserTasks represent human activities requiring documented procedures")
          ],
          "decisions": [
              RequirementItem(desc="Completion criteria for this task",
                            tags=["completion-criteria", "quality-check"],
                            priority=HELPFUL, source="type-rule",
                            rationale="UserTasks need clear definition of done")
          ]
      },
      NodeType.SERVICE_TASK: {
          "data_inputs": [
              RequirementItem(desc="Input data schema and source",
                            tags=["input-schema", "data-source"], priority=CRITICAL,
                            source="type-rule",
                            rationale="ServiceTasks are automated and require well-defined inputs"),
              RequirementItem(desc="Error handling and fallback procedure",
                            tags=["error-handling", "fallback", "retry"],
                            priority=IMPORTANT, source="type-rule",
                            rationale="Automated tasks need defined failure modes")
          ]
      },
      NodeType.SCRIPT_TASK: {
          "data_inputs": [
              RequirementItem(desc="Script reference and runtime requirements",
                            tags=["script", "automation", "runtime"],
                            priority=CRITICAL, source="type-rule",
                            rationale="ScriptTasks need their script artifact and execution context")
          ]
      },
      NodeType.EXCLUSIVE_GATEWAY: {
          "decisions": [
              RequirementItem(desc="Decision criteria and routing rules",
                            tags=["decision-criteria", "routing", "evaluation"],
                            priority=CRITICAL, source="type-rule",
                            rationale="Exclusive gateways require clear criteria to choose one path")
          ]
      },
      NodeType.PARALLEL_GATEWAY: {
          "contextual": [
              RequirementItem(desc="Parallel execution coordination requirements",
                            tags=["coordination", "parallel", "synchronization"],
                            priority=HELPFUL, source="type-rule",
                            rationale="Parallel gateways may need coordination between branches")
          ]
      },
      # ... similar for other types
  }
  ```
  - These are additive — they don't replace explicit requirements, they supplement them.
  - Only adds a type-rule requirement if no explicit requirement with overlapping tags exists
    (avoids duplication).

**Layer 3 — Contextual requirements:**
- `_infer_contextual_requirements(node, scope_path, scope_depth, prior_nodes) -> tuple[list, list, list, list]`
  - **First task in scope** (no prior nodes in this subprocess):
    - Adds: "Subprocess-level context and objectives" (CONTEXT, IMPORTANT)
    - Adds: "Inputs from parent scope needed to begin this subprocess" (DATA, IMPORTANT)
  - **Task after gateway** (prior node is a gateway):
    - Adds: "Gateway decision outcome (which path was taken and why)" (CONTEXT, CRITICAL)
  - **Task before end event** (next node via outgoing flow is EndEvent):
    - Adds: "Completion and handoff criteria for subprocess" (DECISION, IMPORTANT)
  - **Deep nesting (depth >= 3)**:
    - Adds: "Escalation path to parent scope if blocked" (PROCEDURE, HELPFUL)
  - **Subprocess domain inference**:
    - Looks at `scope_path[-1]` (current subprocess name) and adds domain-specific tags
    - E.g., scope "Triage" → adds tags: triage, initial-assessment, prioritization
    - E.g., scope "Resolution" → adds tags: fix, remediation, restoration

**Layer 4 — Journey-aware requirements (NEW):**
- `_infer_journey_requirements(node, scope_path, journey: JourneyContext) -> tuple[list, list, list, list]`
  - Only runs if a `JourneyContext` is provided
  - **Check what the journey already provides:**
    - For each explicit `context:` tag on the node, query `journey.query_prior_outputs(tags)`
    - If found → create a CONTEXT requirement with `source="journey-check"` and note
      which prior step provides it
    - If NOT found → create a CONTEXT requirement with `source="journey-gap"` flagging
      that this context is needed but no prior step has produced it
  - **Check accumulated process state:**
    - Call `journey.get_current_state()` to see what state attributes exist
    - For each state attribute that matches the node's context needs → mark as available
    - If node needs state that hasn't been set yet → create requirement noting the gap
  - **Cross-scope dependency detection:**
    - If this node is in a different subprocess than where its context was produced,
      create an explicit `DependencyItem` noting the cross-scope data flow
    - E.g., "Immediate Actions" in Resolution depends on "Assess Impact" output from Detection
  - **Decision trail awareness:**
    - If the node is on a conditional gateway path, check journey for what decisions
      led to this path being taken
    - Create CONTEXT requirement: "Decision outcome from [gateway name]"

**Output inference (for journey recording):**
- `infer_outputs(node: ProcessNode, scope_path: list[str]) -> list[JourneyOutput]`
  - **Explicit outputs:** Parse `output:` lines from documentation
    - `output:impact-level,business-impact` → two JourneyOutput entries
    - Each gets: output_id (auto-generated), description (from tag name),
      data_type="data", tags=[tag], produced_by_node=node.id
  - **Type-based outputs:**
    ```python
    OUTPUT_RULES = {
        NodeType.USER_TASK: [("task-output", "Human task completion output"),
                            ("human-decision", "Decision or judgment made by human")],
        NodeType.SERVICE_TASK: [("service-response", "Automated service response data")],
        NodeType.SCRIPT_TASK: [("computed-result", "Script computation result")],
        NodeType.EXCLUSIVE_GATEWAY: [("routing-decision", "Path selection decision")],
    }
    ```
  - **Name-based outputs:**
    - Parse task name as verb-noun pattern
    - "Assess Impact" → output tag: "impact-assessment"
    - "Collect Logs" → output tag: "collected-logs"
    - "Classify Severity" → output tag: "severity-classification"
    - Heuristic: split on space, if first word is a verb, output = noun + past-participle-verb
  - Deduplicates across all three sources by tag overlap

**Dependencies detection:**
- `_detect_dependencies(node, prior_nodes, scope_path, journey) -> list[DependencyItem]`
  - If node has `context:` tags referencing known prior step outputs → create DependencyItem
  - If node is not the first in its scope → the prior node's outputs are a dependency
  - If scope_depth > 0 → parent scope's accumulated context is a dependency
  - **NEW: If journey is available**, query for outputs matching this node's context tags.
    For each match, create explicit DependencyItem linking this step to the producing step,
    even if they're in different subprocesses (cross-scope dependency)
  - Each dependency specifies: which node, what data, and scope relationship

**Merge and deduplication:**
- `_merge_requirements(explicit, type_based, contextual, journey_aware) -> tuple[...]`
  - Combines all four layers
  - Deduplicates by comparing tag sets (if >50% tag overlap → merge, keep higher priority)
  - Preserves source attribution for each requirement
  - Sets confidence: 1.0 if explicit, 0.8 if journey-confirmed, 0.7 if type+contextual,
    0.5 if contextual only

**Verify:** Analyze the "Collect Logs" ServiceTask node with scope_path=["Incident Response",
"Triage", "Initial Investigation", "Analyze Logs"]. Confirm: explicit requirements from
documentation are present, type-based requirements for ServiceTask are added (input schema,
error handling), contextual requirements for deep nesting are added (escalation path).
Dependencies include prior step "Check Known Issues" output. With journey context loaded,
confirm that "incident-severity" context requirement is marked JOURNEY_SATISFIED from
earlier "Determine Severity" step. Output inference produces "collected-logs" and
"service-response" outputs for recording in the journey.
**Depends:** Task 2

### Task 8: Knowledge Ranker
**Context:** Scores and ranks available knowledge items against a specific requirement.
The ranker transforms "here's what exists" into "here's what's relevant, in order, with
explanation."

**Action:** Create `knowledge_ranker.py` with class `KnowledgeRanker`:

**Constructor:**
- Takes optional `weights: dict[str, float]` to override default signal weights
- Default weights: tag_overlap=0.30, category_match=0.25, keyword_relevance=0.20,
  scope_proximity=0.15, type_fit=0.10

**Public method:**
- `rank(items: list[KnowledgeItem], requirement: RequirementItem,
  scope_path: list[str], scope_depth: int,
  node_type: NodeType) -> list[KnowledgeScore]`
  - Scores each item against the requirement using all 5 signals
  - Returns sorted list (highest score first)
  - Each `KnowledgeScore` includes the signal breakdown and match explanation

**Scoring signals (private methods):**

1. `_score_tag_overlap(item: KnowledgeItem, requirement: RequirementItem) -> float`
   - Computes Jaccard similarity: `len(item.tags ∩ req.tags) / len(item.tags ∪ req.tags)`
   - Returns 0.0 if no overlap, 1.0 if identical tag sets
   - Also considers partial tag matches (e.g., "log-analysis" partially matches "log-collection")
     using word-level overlap within tags

2. `_score_category_match(item: KnowledgeItem, scope_path: list[str]) -> float`
   - Checks if `item.category` matches any element in `scope_path` (lowercased, normalized)
   - Returns 1.0 for exact match with current scope, 0.7 for match with parent scope,
     0.3 for match with grandparent+, 0.0 for no match
   - Also checks `item.applicable_scopes` against scope_path elements

3. `_score_keyword_relevance(item: KnowledgeItem, requirement: RequirementItem) -> float`
   - Tokenizes: item.title + item.content_summary → word set A
   - Tokenizes: requirement.description → word set B
   - Computes: `len(A ∩ B) / max(len(A), len(B))`
   - Strips common stop words (the, a, an, is, for, of, to, in, and, or)
   - Normalizes to lowercase

4. `_score_scope_proximity(item: KnowledgeItem, scope_path: list[str],
   scope_depth: int) -> float`
   - If item.scope_level == "global": return 0.5 (always somewhat relevant)
   - Check item.applicable_scopes against scope_path:
     - Match at current level → 1.0
     - Match at parent level → 0.7
     - Match at grandparent → 0.4
     - No scope match → 0.1
   - This rewards knowledge that's scoped to the current subprocess

5. `_score_type_fit(item: KnowledgeItem, requirement_category: RequirementCategory,
   node_type: NodeType) -> float`
   - Fit matrix:
     ```
     Knowledge Type    │ PROCEDURE req │ DATA req │ CONTEXT req │ DECISION req
     ─────────────────┼──────────────┼──────────┼────────────┼────────────
     PROCEDURE         │     1.0       │   0.3    │    0.3      │    0.5
     RUNBOOK           │     0.9       │   0.4    │    0.3      │    0.3
     CHECKLIST         │     0.8       │   0.2    │    0.2      │    0.6
     POLICY            │     0.5       │   0.2    │    0.5      │    0.8
     REFERENCE         │     0.3       │   0.7    │    0.6      │    0.4
     FAQ               │     0.4       │   0.3    │    0.7      │    0.3
     ```
   - Returns the matrix value for the item's type vs. the requirement's category

**Match explanation generation:**
- `_build_explanation(item, requirement, signal_scores) -> str`
  - Constructs: "Matched on tags: X, Y | Category: Z fits scope | Score: 0.XX"
  - Highlights the strongest signal: "Primary match: tag overlap (0.85)"

**Verify:** Rank all 10 sample procedures against a requirement with tags ["log-analysis",
"monitoring"]. "Log Analysis Runbook" must rank #1. "SLA Definitions" must rank in bottom 3.
Each result has a non-empty explanation. Signal scores are between 0.0 and 1.0.
**Depends:** Task 2

### Task 9: Gap Analyzer
**Context:** Compares the inferred requirements against ranked knowledge matches to produce
a coverage assessment. This is what answers "what do we have vs. what's missing?"

**Action:** Create `gap_analyzer.py` with class `GapAnalyzer`:

**Constructor:**
- Takes `match_threshold: float = 0.70` (score >= this = MATCHED)
- Takes `partial_threshold: float = 0.40` (score >= this = PARTIAL)

**Public methods:**

- `analyze_step(step_reqs: StepRequirements,
  ranked_matches: dict[str, list[KnowledgeScore]]) -> StepCoverageReport`
  - For each requirement in each category (procedures, data, context, decisions):
    - Look up ranked matches for that requirement (by requirement_id)
    - If best match score >= match_threshold → MATCHED
    - If best match score >= partial_threshold → PARTIAL
    - If no matches or best < partial_threshold → GAP
    - For DATA requirements: mark as NOT_ASSESSED (data lives in systems, not knowledge store)
    - Create `RequirementCoverage` with coverage level, matches, and notes
  - Compute step readiness score:
    `matched*1.0 + partial*0.5 + gap*0.0) / total_assessable_requirements`
  - Return `StepCoverageReport`

- `analyze_process(step_reports: list[StepCoverageReport],
  process_name: str) -> ProcessCoverageReport`
  - Aggregate across all steps
  - Compute totals: total_requirements, total_matched, total_partial, total_gaps
  - Compute overall_readiness as weighted average of step readiness scores
  - Identify critical_gaps: any GAP where requirement.priority == CRITICAL
  - Build scope_summaries: group step reports by scope_path[0] (L1 subprocesses),
    compute per-scope readiness
  - Return `ProcessCoverageReport`

- `_generate_gap_description(requirement: RequirementItem, scope_path: list[str]) -> str`
  - Creates human-readable description of what's missing:
    "No procedure found for 'Evidence Collection' in scope 'Root Cause Analysis'.
     Recommended: Create an evidence collection SOP covering chain-of-custody requirements,
     data preservation steps, and documentation standards."
  - Uses requirement tags and scope context to generate the recommendation

**Verify:** Given a step with 3 procedure requirements where 1 has a match at 0.85
(MATCHED), 1 at 0.55 (PARTIAL), and 1 with no matches (GAP): readiness = (1.0+0.5+0.0)/3
= 0.50. Critical gap correctly identified if the GAP requirement was CRITICAL priority.
**Depends:** Task 2

### Task 10: Knowledge Context Manager (Scope Stack)
**Context:** Manages knowledge scoping across subprocess nesting. Ensures knowledge flows
correctly: inherited downward, local to scope, propagated upward on exit.

**Action:** Create `knowledge_context.py` with class `KnowledgeContextManager`:

**State:**
- `_scope_stack: list[KnowledgeContext]` — the scope stack, grows on push, shrinks on pop
- `_global_scope: KnowledgeContext` — global-level knowledge, always accessible
- `_scope_history: list[KnowledgeContext]` — completed scopes (for reporting)

**Public methods:**

- `initialize_global(items: list[KnowledgeItem])` — set up global scope with org-wide
  knowledge items (items where scope_level == "global" or applicable_scopes includes "all")

- `push_scope(scope_name: str, scope_level: int, scope_domain: str) -> KnowledgeContext`
  - Create new `KnowledgeContext` with:
    - scope_name, scope_level, scope_domain
    - `inherited_items` = copy of parent scope's local + inherited + parent's inherited chain
    - `local_items` = empty list (will be populated as step analysis proceeds)
    - `discovered_items` = empty list (will be populated with propagate-up items)
  - Push onto `_scope_stack`
  - Return the new scope

- `pop_scope() -> KnowledgeContext`
  - Pop the top scope off `_scope_stack`
  - For any items in popped scope's `discovered_items` marked `propagate_up=True`:
    - Add them to the new top scope's `discovered_items`
  - Add popped scope to `_scope_history`
  - Return the popped scope (for reporting)

- `current_scope() -> KnowledgeContext`
  - Return top of `_scope_stack`

- `add_to_current_scope(item: KnowledgeItem, propagate_up: bool = False)`
  - Add item to current scope's `local_items`
  - If `propagate_up`, also add to current scope's `discovered_items`

- `get_all_accessible_knowledge() -> list[KnowledgeItem]`
  - Returns merged, deduplicated list of:
    - Current scope's local_items
    - Current scope's inherited_items
    - All parent scopes' local_items (walking up the stack)
    - Global scope items
  - Deduplicates by item ID
  - Each item annotated with which scope it came from

- `get_scope_path() -> list[str]`
  - Returns list of scope names from bottom to top of stack
  - E.g., ["Incident Response", "Triage", "Initial Investigation", "Analyze Logs"]

- `get_scope_depth() -> int`
  - Returns current stack depth (0 = process root)

- `get_full_state_snapshot() -> dict`
  - Returns serializable snapshot of entire scope stack for display/export

**Verify:** Initialize with 2 global items. Push "Incident Response" scope, add 2 local items.
Push "Triage" scope, add 1 local item. `get_all_accessible_knowledge()` returns 5 items
(2 global + 2 inherited from L0 + 1 local). Pop "Triage" — if 1 item marked propagate_up,
current scope (Incident Response) now has it in discovered_items.
**Depends:** Task 2

### Task 11: Journey Context (Process Journey Ledger)
**Context:** This is the **horizontal knowledge flow** mechanism — the counterpart to the
scope stack's vertical flow. It maintains a chronological, append-only ledger of everything
the process has done, decided, and produced. Any step can query the journey to find outputs
from any prior step, regardless of subprocess boundaries. This is what makes step 1's outputs
accessible to step 26.

**Action:** Create `journey_context.py` with class `JourneyContext`:

**State:**
- `_entries: list[JourneyEntry]` — chronological ledger (append-only)
- `_step_counter: int` — auto-incrementing step number (starts at 1)
- `_outputs_by_tag: dict[str, list[JourneyOutput]]` — inverted index: tag → outputs
- `_outputs_by_node: dict[str, list[JourneyOutput]]` — index: node_id → outputs
- `_outputs_by_scope: dict[str, list[JourneyOutput]]` — index: scope_name → outputs
- `_decisions: list[JourneyDecision]` — all decisions in chronological order
- `_state: dict[str, str]` — current accumulated process state (mutable)
- `_state_history: list[tuple[int, JourneyStateChange]]` — (step_number, change) pairs

**Public methods:**

- `record_step(node_id: str, node_name: str, scope_path: list[str],
  scope_depth: int, entry_type: JourneyEntryType,
  outputs: list[JourneyOutput] | None = None,
  decisions: list[JourneyDecision] | None = None,
  state_changes: list[JourneyStateChange] | None = None,
  gateway_condition: str | None = None) -> JourneyEntry`
  - Increments `_step_counter`
  - Creates `JourneyEntry` with all provided data
  - For each output: indexes by tags, node_id, and scope_path[-1]
  - For each decision: appends to `_decisions`
  - For each state_change: applies to `_state`, records in `_state_history`
  - Appends entry to `_entries`
  - Returns the entry (includes step_number for reference)

- `query_prior_outputs(tags: list[str]) -> list[JourneyOutput]`
  - For each tag, looks up `_outputs_by_tag[tag]`
  - Returns union of all matching outputs, deduplicated by output_id
  - Sorted by step number descending (most recent first)
  - Each output carries its producing step number and node name for traceability

- `query_outputs_from_node(node_id: str) -> list[JourneyOutput]`
  - Returns `_outputs_by_node.get(node_id, [])`

- `query_outputs_from_scope(scope_name: str) -> list[JourneyOutput]`
  - Returns all outputs from any step within the named subprocess
  - Matches against scope_path elements, not just the innermost scope
  - E.g., `query_outputs_from_scope("Detection")` returns outputs from all steps
    within the Detection subprocess and its children

- `get_decision_trail() -> list[JourneyDecision]`
  - Returns `_decisions` (full list, chronological order)

- `get_current_state() -> dict[str, str]`
  - Returns copy of `_state`
  - E.g., {"incident_severity": "S2", "assigned_team": "Tier 2",
           "containment_status": "active"}

- `get_state_at_step(step_number: int) -> dict[str, str]`
  - Starts with empty dict
  - Replays `_state_history` up to and including `step_number`
  - Returns the reconstructed state at that point

- `get_step_count() -> int`
  - Returns `_step_counter`

- `get_journey_so_far() -> list[JourneyEntry]`
  - Returns copy of `_entries`

- `get_journey_summary() -> JourneySummary`
  - Computes: total_steps, unique scopes visited, decisions made count,
    outputs produced count, state attributes tracked count
  - Includes the full entry list for detailed access

- `get_outputs_available_at_step(step_number: int) -> list[JourneyOutput]`
  - Returns all outputs produced by steps with step_number < given step_number
  - Useful for answering: "What was available when step N executed?"

**State inference from BPMN (for phase 1):**

Since we're not executing the process, state changes are inferred:
- Gateway decisions → state change: `{"gateway_[name]_outcome": "[condition_label]"}`
- Steps in specific scopes → state change by domain:
  - Detection steps → may set `incident_severity`, `affected_systems`
  - Triage steps → may set `assigned_team`, `triage_outcome`
  - Resolution steps → may set `containment_status`, `fix_status`
- Explicit `output:` tags that look like state attributes → state change

**Verify:**
1. Record 5 steps across 2 different subprocesses
2. Step 1 produces output with tag "impact-level"
3. Step 5 (in a different subprocess) queries `query_prior_outputs(["impact-level"])`
   → returns Step 1's output
4. Record a state change at step 2: `incident_severity = "S2"`
5. `get_current_state()` returns `{"incident_severity": "S2"}`
6. `get_state_at_step(1)` returns `{}` (before the change)
7. `get_state_at_step(2)` returns `{"incident_severity": "S2"}`
8. `query_outputs_from_scope("Detection")` returns only outputs from Detection steps
9. `get_journey_summary()` returns correct counts
**Depends:** Task 2

### Task 12: Process Tree Walker
**Context:** Traverses the BPMN process tree in execution order, emitting events that the
orchestrator coordinates. Handles subprocess entry/exit, gateway branching, and cycle detection.

**Action:** Create `walker.py` with class `ProcessWalker`:

**Public method:**
- `walk(process: ProcessDefinition,
  callback: Callable[[WalkerEvent], None]) -> None`
  - Emit `ENTER_PROCESS` event
  - Find the start event in top-level nodes
  - Call `_walk_level(process.nodes, process.flows, depth=0, scope_path=[process.name], callback)`
  - Emit `EXIT_PROCESS` event

**Private methods:**

- `_walk_level(nodes, flows, depth, scope_path, callback)`
  - `visited: set[str]` — tracks visited node IDs within this level
  - Find start event node (type == START_EVENT)
  - Call `_walk_from(start_node, nodes, flows, depth, scope_path, visited, callback)`

- `_walk_from(node, nodes, flows, depth, scope_path, visited, callback)`
  - If `node.id` in `visited`: emit `CYCLE_DETECTED`, return
  - Add `node.id` to `visited`
  - **If SubProcess:**
    - Emit `ENTER_SCOPE` event with scope_name=node.name, depth=depth
    - Emit `ENTER_NODE` event for the subprocess node itself
    - Recursively: `_walk_level(node.child_nodes, node.child_flows, depth+1,
      scope_path + [node.name], callback)`
    - Emit `EXIT_NODE` event for the subprocess node
    - Emit `EXIT_SCOPE` event
  - **If Gateway:**
    - Emit `ENTER_GATEWAY` event
    - Emit `ENTER_NODE` event for the gateway itself
    - For each outgoing flow:
      - Get condition label from the flow
      - Emit `GATEWAY_PATH` event with the condition
      - Find target node, recursively `_walk_from(target, ...)`
    - Emit `EXIT_NODE` event for the gateway
    - Note: nodes after gateway convergence (join point) should only be walked once.
      The `visited` set handles this — the join node gets visited by the first path
      to reach it, subsequent paths see it in `visited` and skip.
  - **If regular node (Task, Event):**
    - Emit `ENTER_NODE` event
    - Emit `EXIT_NODE` event
  - **Follow sequence flows:**
    - For each outgoing flow from this node (unless already handled by gateway logic):
      - Find target node
      - Recursively `_walk_from(target, ...)`

- `_find_start_event(nodes: dict) -> ProcessNode`
  - Scan nodes for type == START_EVENT
  - If none found: raise `WalkerError("No start event found at this level")`

- `_get_outgoing_targets(node, flows, nodes) -> list[tuple[SequenceFlow, ProcessNode]]`
  - For each flow where flow.source_ref == node.id:
    - Find target node by flow.target_ref
    - Return list of (flow, target_node) tuples

**Verify:** Walk the sample BPMN. Count: all 47 nodes visited (check via callback counter).
Scope enter/exit events balance (every ENTER_SCOPE has matching EXIT_SCOPE). Depth reaches 4.
No infinite loops. Gateway paths all explored. Visited tracking prevents re-walking after joins.
**Depends:** Task 2, Task 3

### Task 13: Orchestrator (Main Coordinator)
**Context:** The central component that wires walker, requirements analyzer, knowledge store,
ranker, gap analyzer, scope context manager, AND journey context together. Coordinates the
full pipeline: parse → walk → analyze (with journey) → rank → gap-assess (including journey
satisfaction) → report.

**Action:** Create `orchestrator.py` with class `KnowledgeOrchestrator`:

**Constructor:**
```python
def __init__(self,
    knowledge_store: KnowledgeStore,
    requirements_analyzer: RequirementsAnalyzer,
    knowledge_ranker: KnowledgeRanker,
    gap_analyzer: GapAnalyzer,
    context_manager: KnowledgeContextManager,
    journey_context: JourneyContext,
    procedure_expander: ProcedureExpander | None = None
)
```

**Public method:**
- `run(process: ProcessDefinition) -> ProcessCoverageReport`
  - Initialize context manager with global knowledge from store
  - Journey context starts empty (will accumulate as we walk)
  - Create walker, set `self._on_event` as callback
  - Walk the process
  - After walk completes: call `gap_analyzer.analyze_process()` on accumulated step reports
  - Attach `journey_context.get_journey_summary()` to the report
  - Return `ProcessCoverageReport`

**Event handler — `_on_event(event: WalkerEvent)`:**

- `ENTER_PROCESS`:
  - Log process start
  - Query knowledge store for all global-scope items
  - Initialize context manager global scope

- `ENTER_SCOPE`:
  - Extract scope domain from the subprocess node name (normalize: lowercase, strip spaces)
  - Push scope on context manager
  - Query knowledge store for items applicable to this scope domain
  - Pre-load matching items into the scope's local knowledge
  - Record scope entry in journey context (entry_type=SCOPE_ENTERED)

- `ENTER_NODE` (for task/event nodes — the main analysis point):
  This is where both context systems converge. The orchestrator:

  **Step A: Gather context from both axes**
  - Get scope path and depth from context manager (vertical)
  - Get prior nodes in this scope (tracked internally)
  - Get journey context reference (horizontal)

  **Step B: Analyze requirements (with journey awareness)**
  - Call `requirements_analyzer.analyze_node(node, scope_path, depth, prior_nodes,
    journey=self._journey_context)` → produces `StepRequirements`
  - The analyzer now checks journey context for CONTEXT requirements that can be
    satisfied by prior step outputs (marks them accordingly)

  **Step C: Check journey satisfaction FIRST**
  - For each CONTEXT and DATA requirement:
    - Query `journey_context.query_prior_outputs(requirement.tags)`
    - If match found → mark as JOURNEY_SATISFIED (skip knowledge store lookup for this one)
    - If not found → proceed to knowledge store matching

  **Step D: Match remaining requirements against knowledge store**
  - For each requirement NOT journey-satisfied:
    - Query knowledge store with the requirement's tags + current scope
    - Call `knowledge_ranker.rank()` on the results against the requirement
    - Store ranked results keyed by requirement_id

  **Step E: Assess coverage**
  - Call `gap_analyzer.analyze_step(step_requirements, ranked_matches, journey_matches)`
    → produces `StepCoverageReport`
  - Coverage now has three sources: knowledge store (MATCHED/PARTIAL), journey (JOURNEY_SATISFIED),
    or nothing (GAP)

  **Step F: Expand matched procedures (if expander enabled)**
  - For each MATCHED or PARTIAL procedure coverage result:
    - If the matched knowledge item has `own_requirements` (non-empty):
      - Call `procedure_expander.expand(matched_item, step_requirements,
        knowledge_store, ranker, journey, scope_path)`
      - Append the `ExpansionResult` to the step coverage report
      - Any REGULATORY requirements get added to the step's regulatory section
      - Recalculate step readiness score including expanded requirements

  **Step G: Record this step in the journey**
  - Call `requirements_analyzer.infer_outputs(node, scope_path)` to determine what this
    step produces
  - Infer any state changes from the step (severity classification, assignment, etc.)
  - Call `journey_context.record_step(...)` with:
    - The node info
    - Inferred outputs (available to all subsequent steps)
    - Any decisions (if this is a gateway or decision task)
    - Any state changes

  **Step H: Store and emit**
  - Store the StepCoverageReport
  - Emit to display callback (includes journey context section)
  - Track this node as a "prior node" for subsequent analysis

- `EXIT_NODE`:
  - Hook for phase 2 (no action in phase 1 beyond what ENTER_NODE already handles)

- `EXIT_SCOPE`:
  - Pop scope from context manager
  - Propagate discovered items upward
  - Record scope exit in journey context (entry_type=SCOPE_EXITED, includes scope summary)
  - Log scope exit with summary of scope-level coverage

- `EXIT_PROCESS`:
  - Log completion
  - Log journey summary (total steps, outputs produced, decisions made, state accumulated)

**Display callback registration:**
- `register_display(callback: Callable[[str, Any], None])` — the display module
  registers here to receive events for formatting (now includes journey context data)

**Verify:** Run orchestrator with sample BPMN and sample procedures. Returns a
`ProcessCoverageReport` with:
- All 47 nodes analyzed, step reports for every task node
- Non-zero readiness scores
- At least 4 critical gaps identified from knowledge store
- At least 3 JOURNEY_SATISFIED requirements (context from prior steps)
- Scope summaries for all L1 subprocesses
- Journey summary showing step count, output count, decision trail
- Cross-scope dependencies resolved (e.g., Resolution steps accessing Detection outputs)
- Procedure expansions produce regulatory gaps (SOX, GDPR) in expanded requirements
- Expanded readiness scores reflect the additional requirements
**Depends:** Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12, Task 17

### Task 14: Spec Generator (Report Output)
**Context:** Produces the Knowledge Requirements Specification in both human-readable (console)
and machine-readable (JSON) formats. This is the user-facing output.

**Action:** Create `spec_generator.py` with class `SpecGenerator`:

**Public methods:**

- `generate_console_report(report: ProcessCoverageReport) -> str`
  - Builds the full console output string as shown in Decision 7
  - Sections:
    1. Header: process name, stats (nodes, depth, knowledge items)
    2. Per-step detail: requirements by category, coverage, gaps
    3. Summary: by category, by scope, critical gaps list
  - Returns the formatted string

- `generate_json_report(report: ProcessCoverageReport) -> dict`
  - Converts the `ProcessCoverageReport` into a serializable dict structure
  - Follows the JSON schema shown in Decision 7
  - Returns dict (caller can `json.dumps()` it)

- `export_json(report: ProcessCoverageReport, output_path: str) -> None`
  - Calls `generate_json_report()`, writes to file with `json.dump()` with indent=2

**Verify:** Generate console report for sample data — readable, correctly structured.
Generate JSON report — valid JSON, parseable, contains all sections.
**Depends:** Task 2

### Task 15: Console Display Formatter
**Context:** Real-time console output as the orchestrator walks the process. Shows the
step-by-step analysis with visual hierarchy matching subprocess nesting.

**Action:** Create `display.py` with class `ConsoleDisplay`:

**Formatting methods:**

- `display_header(process_name: str, node_count: int, depth: int,
  knowledge_count: int)` — prints the header banner

- `display_scope_enter(scope_name: str, depth: int, domain: str,
  preloaded_count: int)` — prints scope entry with indent

- `display_step(report: StepCoverageReport, depth: int,
  journey_context: JourneyContext | None = None)` — prints full step analysis:
  - Node name, type, and **step number** (e.g., "Step 18 of 47")
  - Scope path
  - **Journey Context section** (if journey available): prior step outputs available,
    current process state, cross-scope data sources
  - Requirements by category with coverage indicators (checkmark/X/~/J)
  - Ranked matches with scores
  - Journey-satisfied items with source step reference
  - Gap descriptions
  - Step readiness score

- `display_scope_exit(scope_name: str, depth: int, scope_summary: ScopeCoverageSummary)`
  — prints scope exit with summary

- `display_gateway(node_name: str, depth: int, gateway_type: str)` — prints gateway marker

- `display_gateway_path(condition: str, depth: int)` — prints path label

- `display_summary(report: ProcessCoverageReport)` — prints the final summary section

**Visual elements:**
- Indentation: `"  " * depth` for nesting
- Tree characters: `│`, `├─`, `└─`, `►` for flow visualization
- Coverage indicators: `[checkmark] MATCHED`, `[~] PARTIAL`, `[X] GAP`, `[J] JOURNEY`
- Score display: `[0.87]` format
- Section boxes: `┌─`, `│`, `└─` for requirement category groups
- Level markers: `[L0]`, `[L1]`, `[L2]`, `[L3]`

**Verify:** Output is readable at 80-char width. Indentation correctly reflects depth.
All coverage levels have distinct visual markers. Scope transitions are visually clear.
**Depends:** Task 2

### Task 16: Main Entry Point + End-to-End Wiring
**Context:** The user-facing entry point. Ties all components together, parses CLI args,
loads data, runs the orchestrator, and produces output.

**Action:** Update `main.py`:

```python
def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Knowledge Orchestrator")
    parser.add_argument("--bpmn", default="samples/incident_response.bpmn",
                       help="Path to BPMN XML file")
    parser.add_argument("--knowledge", default="samples/procedures",
                       help="Path to knowledge/procedures directory")
    parser.add_argument("--regulations", default="samples/regulations",
                       help="Path to regulatory framework definitions directory")
    parser.add_argument("--export-json", default=None,
                       help="Path to export JSON requirements spec")
    parser.add_argument("--export-html", default=None,
                       help="Path to export interactive HTML visual spec")
    parser.add_argument("--verbose", action="store_true",
                       help="Show detailed scoring breakdown")
    parser.add_argument("--no-expand", action="store_true",
                       help="Disable recursive procedure expansion")
    parser.add_argument("--expand-depth", type=int, default=3,
                       help="Max recursion depth for procedure expansion (default: 3)")
    args = parser.parse_args()

    # 1. Load knowledge store
    store = InMemoryKnowledgeStore()
    count = store.load_from_directory(args.knowledge)
    print(f"Loaded {count} knowledge items")

    # 2. Parse BPMN
    bpmn_parser = BPMNParser()
    process = bpmn_parser.parse(args.bpmn)
    print(f"Parsed process: {process.name} ({len(process.nodes)} top-level nodes)")

    # 3. Load regulatory frameworks
    reg_analyzer = RegulatoryAnalyzer()
    reg_count = reg_analyzer.load_frameworks(args.regulations)
    print(f"Loaded {reg_count} regulatory frameworks")

    # 4. Initialize components
    analyzer = RequirementsAnalyzer()
    ranker = KnowledgeRanker()
    gap = GapAnalyzer()
    expander = ProcedureExpander(max_depth=args.expand_depth) if not args.no_expand else None
    context = KnowledgeContextManager()
    journey = JourneyContext()        # The process journey ledger
    display = ConsoleDisplay(verbose=args.verbose)

    # 5. Create orchestrator, register display
    orchestrator = KnowledgeOrchestrator(
        store, analyzer, ranker, gap, context, journey,
        procedure_expander=expander,
        regulatory_analyzer=reg_analyzer
    )
    orchestrator.register_display(display.on_event)

    # 6. Run
    report = orchestrator.run(process)

    # 7. Display summary
    display.display_summary(report)

    # 8. Optional JSON export
    if args.export_json:
        spec_gen = SpecGenerator()
        spec_gen.export_json(report, args.export_json)
        print(f"JSON spec exported to: {args.export_json}")

    # 9. Optional HTML export
    if args.export_html:
        renderer = HTMLRenderer()
        renderer.export_html(report, journey.get_journey_summary(), args.export_html)
        print(f"HTML spec exported to: {args.export_html}")
```

**Verify:** `python main.py` runs end-to-end with no arguments (uses defaults). Produces
full console output. `python main.py --export-json output.json` creates valid JSON file.
`python main.py --export-html spec.html` creates valid HTML file.
**Depends:** All previous tasks

### Task 17: Procedure Expander (Recursive Requirement Expansion)
**Context:** When a procedure is matched to a step, the procedure itself may declare
requirements — regulatory compliance, sub-procedures, data dependencies, approvals. These
must be recursively expanded into the step's requirement set. Without this, critical
regulatory and compliance gaps remain invisible.

**Action:** Create `procedure_expander.py` with class `ProcedureExpander`:

**Constructor:**
- `max_depth: int = 3` — maximum recursion depth
- `_visited_ids: set[str]` — cycle detection within a single expansion chain

**Public method:**
- `expand(matched_item: KnowledgeItem, step_context: StepRequirements,
  knowledge_store: KnowledgeStore, knowledge_ranker: KnowledgeRanker,
  journey: JourneyContext | None = None,
  scope_path: list[str] = None,
  depth: int = 0) -> ExpansionResult`

**Expansion logic:**
1. If `depth >= max_depth`: return empty `ExpansionResult` with note "depth limit reached"
2. If `matched_item.id` in `_visited_ids`: return empty with note "circular reference detected"
3. Add `matched_item.id` to `_visited_ids`
4. For each `KnowledgeRequirement` in `matched_item.own_requirements`:
   a. Convert to `RequirementItem`:
      - `category` = map requirement_type to RequirementCategory
        (regulatory→REGULATORY, approval→PROCEDURE, data→DATA, sub-procedure→PROCEDURE,
         compliance→REGULATORY, certification→REGULATORY)
      - `source` = `"expanded from {matched_item.title}"`
      - `priority` = use the KnowledgeRequirement's priority; if mandatory=True, force CRITICAL
      - `tags` = from the KnowledgeRequirement
   b. **Check journey first:** `journey.query_prior_outputs(tags)` → if found, mark
      JOURNEY_SATISFIED
   c. **Check knowledge store:** `store.query(tags, scope)` → rank results
   d. Determine coverage: MATCHED/PARTIAL/GAP using ranker scores and thresholds
   e. **If MATCHED and depth+1 < max_depth:** recursively call `expand()` on the
      matched item (the sub-procedure itself may have requirements)
   f. Collect into `expanded_requirements`, `expanded_coverage`, `sub_expansions`
5. Remove `matched_item.id` from `_visited_ids` (allow re-expansion in different chains)
6. Compute `total_expanded_count` = sum across all depths
7. Return `ExpansionResult`

**Integration with orchestrator:**
The orchestrator calls the expander after initial gap analysis:
```python
# After ranking/gap analysis for a step:
for coverage in step_coverage.procedure_coverage:
    if coverage.coverage_level in (CoverageLevel.MATCHED, CoverageLevel.PARTIAL):
        if coverage.matched_knowledge and coverage.matched_knowledge[0].knowledge_item.own_requirements:
            expansion = expander.expand(
                matched_item=coverage.matched_knowledge[0].knowledge_item,
                step_context=step_requirements,
                knowledge_store=self._store,
                knowledge_ranker=self._ranker,
                journey=self._journey,
                scope_path=scope_path
            )
            step_coverage.expansions.append(expansion)
```

**Verify:**
1. Load rollback_procedure.json (has 4 own_requirements)
2. Call expand() with it
3. Confirm: 4 expanded requirements generated
4. Confirm: SOX requirement creates REGULATORY category gap (no SOX procedure in store)
5. Confirm: backup verification checks journey context
6. Confirm: data retention sub-procedure triggers recursive expansion (depth 2)
7. Confirm: depth limit stops at 3
8. Confirm: if rollback_procedure references itself, cycle detection prevents infinite loop
**Depends:** Task 2, Task 6, Task 8

### Task 18: HTML Visual Renderer
**Context:** Console output works but deep nesting is hard to follow in text. An HTML file
provides a visual, interactive, stakeholder-friendly view of the complete Knowledge
Requirements Specification. Self-contained — single file, no external dependencies,
opens in any browser.

**Action:** Create `html_renderer.py` with class `HTMLRenderer`:

**Public method:**
- `render(report: ProcessCoverageReport,
  journey_summary: JourneySummary | None = None) -> str`
  - Returns complete HTML string for the spec

**Internal structure:**

- `_render_css() -> str`
  - Complete CSS block: layout, colors, typography, responsive, print styles
  - CSS variables for coverage colors:
    `--matched: #2d7d46; --partial: #c48a1a; --gap: #c0392b;
     --journey: #2980b9; --regulatory: #8e44ad; --expanded: #7f8c8d`
  - Depth-based left borders (L0=blue, L1=green, L2=amber, L3=red)
  - Collapsible `<details>` styling
  - Readiness bar component
  - Card layout for step nodes
  - Print mode: all details open, controls hidden

- `_render_header(report: ProcessCoverageReport) -> str`
  - Process name, generation timestamp
  - Stats bar: nodes, depth, knowledge items, overall readiness
  - Color-coded legend

- `_render_process_map(report: ProcessCoverageReport) -> str`
  - Walks `step_reports` grouped by scope path
  - For each scope: `<details>` element with summary showing name + readiness badge
  - For each step: calls `_render_step_card()`
  - For gateways: path labels with condition
  - Nesting via recursive scope grouping

- `_render_step_card(step_report: StepCoverageReport, depth: int) -> str`
  - Card with: step name, type badge, step number
  - Scope path breadcrumb
  - Journey context panel (collapsible `<details>`):
    - Prior outputs table (step#, node, output description)
    - Current state key-value table
  - Requirements panels (one per category):
    - Each requirement: description, tags, coverage badge
    - Matched items with visual score bars
    - JOURNEY_SATISFIED with source step link
    - GAP with red highlight and recommendation
  - Expansion cascades (nested `<details class="expansion">`):
    - Source procedure name
    - Each expanded requirement with coverage
    - Regulatory items with framework badge (SOX, GDPR, ITIL, ISO27001)
    - Sub-expansions nested further
  - Readiness score bar at bottom

- `_render_summary(report: ProcessCoverageReport) -> str`
  - Category breakdown table
  - Scope readiness (horizontal bars per scope)
  - Regulatory compliance summary per framework
  - Critical gaps list
  - Journey summary stats

- `_render_javascript() -> str`
  - Expand/collapse all toggle
  - Coverage filter buttons (All, Gaps Only, Regulatory Only, Journey Satisfied)
  - Text search (filters nodes by name/tag, scrolls to match)
  - Step number navigator (input field, jumps to step)
  - Print mode toggle

- `_render_data_embed(report: ProcessCoverageReport) -> str`
  - `<script type="application/json" id="spec-data">`
  - Full JSON spec embedded for downstream tooling

**File export:**
- `export_html(report, journey_summary, output_path: str) -> None`
  - Calls `render()`, writes to file

**Key HTML patterns:**

Score bar:
```html
<div class="score-bar"><div class="score-fill" style="width:82%"></div></div>
```

Coverage badge:
```html
<span class="badge matched">✓ MATCHED [0.82]</span>
<span class="badge gap">✗ GAP</span>
<span class="badge journey">⟲ JOURNEY (Step 3)</span>
<span class="badge regulatory-gap">⚖ SOX GAP</span>
```

Expansion accordion:
```html
<details class="expansion">
  <summary>Expanded from: Rollback Procedure (4 requirements)</summary>
  <div class="expanded-requirements">...</div>
</details>
```

**Verify:**
1. Generate HTML from sample run
2. Open in browser — renders without errors
3. All subprocess levels visible and collapsible
4. Coverage colors correct (green/yellow/red/blue/purple)
5. Expansion cascades render as nested accordions
6. Regulatory gaps highlighted with framework badges
7. Search works (type "Rollback" → highlights matching steps)
8. Expand/collapse all works
9. Print mode shows all sections expanded
10. File is self-contained (no external requests in browser network tab)
**Depends:** Task 2

### Task 19: Sample Regulatory Frameworks
**Context:** The regulatory analyzer needs framework definitions to evaluate against. These
sample frameworks demonstrate the trigger/control system and produce realistic compliance
results against the incident response BPMN.

**Action:** Create 2 JSON files in `samples/regulations/`:

**1. `itil_v4.json` — ITIL v4 Incident Management Controls:**
```json
{
  "id": "ITIL_V4",
  "name": "ITIL v4 Incident Management",
  "version": "4.0",
  "description": "IT Infrastructure Library framework for IT service management",
  "jurisdiction": "global",
  "controls": [
    {
      "control_id": "ITIL-IM-001",
      "title": "Incident Logging and Classification",
      "section_reference": "ITIL4 §5.2.5",
      "severity": "mandatory",
      "applies_to": [
        {"trigger_type": "domain_match", "trigger_values": ["detection", "classification"], "match_mode": "any"}
      ],
      "requirements": [
        {"description": "All incidents must be logged with unique ID, timestamp, reporter, and initial category",
         "category": "DATA", "tags": ["incident-log", "unique-id", "timestamp", "classification"], "mandatory": true},
        {"description": "Incidents must be classified using agreed categorization scheme",
         "category": "PROCEDURE", "tags": ["categorization", "classification-scheme", "severity-matrix"], "mandatory": true}
      ],
      "evidence_requirements": ["Incident record with all mandatory fields", "Classification timestamp"],
      "failure_consequence": "Non-compliance with ITIL incident management practice"
    },
    {
      "control_id": "ITIL-IM-002",
      "title": "Incident Prioritization",
      "section_reference": "ITIL4 §5.2.5",
      "severity": "mandatory",
      "applies_to": [
        {"trigger_type": "tag_match", "trigger_values": ["severity", "priority", "urgency", "impact"], "match_mode": "any"}
      ],
      "requirements": [
        {"description": "Priority must be determined using impact × urgency matrix",
         "category": "PROCEDURE", "tags": ["priority-matrix", "impact-urgency", "sla-mapping"], "mandatory": true}
      ],
      "evidence_requirements": ["Priority assignment record", "SLA clock start timestamp"],
      "failure_consequence": "SLA breach risk — incorrect priority leads to wrong response times"
    },
    {
      "control_id": "ITIL-CM-001",
      "title": "Change Management for Incident Resolution",
      "section_reference": "ITIL4 §5.2.4",
      "severity": "mandatory",
      "applies_to": [
        {"trigger_type": "domain_match", "trigger_values": ["resolution", "fix-implementation", "deployment", "containment"], "match_mode": "any"},
        {"trigger_type": "tag_match", "trigger_values": ["deployment", "rollback", "system-change", "fix"], "match_mode": "any"}
      ],
      "requirements": [
        {"description": "All changes to resolve incidents must be recorded as change records",
         "category": "DATA", "tags": ["change-record", "change-id", "change-log"], "mandatory": true},
        {"description": "Emergency changes must follow expedited change approval process",
         "category": "PROCEDURE", "tags": ["emergency-change", "expedited-approval", "cab-notification"], "mandatory": true}
      ],
      "evidence_requirements": ["Change record ID", "Approval timestamp", "CAB notification (if applicable)"],
      "failure_consequence": "Uncontrolled changes — risk of further service degradation"
    },
    {
      "control_id": "ITIL-KM-001",
      "title": "Known Error Database Check",
      "section_reference": "ITIL4 §5.2.6",
      "severity": "recommended",
      "applies_to": [
        {"trigger_type": "domain_match", "trigger_values": ["investigation", "triage", "root-cause-analysis"], "match_mode": "any"}
      ],
      "requirements": [
        {"description": "Known error database must be consulted before investigation",
         "category": "PROCEDURE", "tags": ["known-error-db", "kedb", "known-issues", "workaround"], "mandatory": false}
      ],
      "evidence_requirements": ["KEDB search record", "Search timestamp"],
      "failure_consequence": "Wasted investigation time on already-known issues"
    },
    {
      "control_id": "ITIL-PIR-001",
      "title": "Post-Incident Review",
      "section_reference": "ITIL4 §5.2.5",
      "severity": "mandatory",
      "applies_to": [
        {"trigger_type": "domain_match", "trigger_values": ["post-incident"], "match_mode": "any"}
      ],
      "requirements": [
        {"description": "Major incidents must have formal post-incident review within 5 business days",
         "category": "PROCEDURE", "tags": ["post-incident-review", "major-incident", "formal-review"], "mandatory": true},
        {"description": "Review must document root cause, timeline, and improvement actions",
         "category": "DATA", "tags": ["root-cause-documentation", "timeline", "improvement-actions", "action-items"], "mandatory": true}
      ],
      "evidence_requirements": ["PIR report", "Action items with owners and deadlines"],
      "failure_consequence": "Failure to learn from incidents — recurring service disruptions"
    }
  ]
}
```

**2. `iso27001.json` — ISO 27001 Information Security Controls:**
```json
{
  "id": "ISO27001",
  "name": "ISO/IEC 27001 Information Security",
  "version": "2022",
  "description": "Information security management system standard",
  "jurisdiction": "global",
  "controls": [
    {
      "control_id": "ISO27001-A5.25",
      "title": "Assessment and Decision on Information Security Events",
      "section_reference": "Annex A §5.25",
      "severity": "mandatory",
      "applies_to": [
        {"trigger_type": "domain_match", "trigger_values": ["detection", "classification", "triage"], "match_mode": "any"}
      ],
      "requirements": [
        {"description": "Security events must be assessed using defined criteria to determine if they qualify as security incidents",
         "category": "PROCEDURE", "tags": ["security-assessment", "event-classification", "incident-criteria"], "mandatory": true},
        {"description": "Assessment decision must be recorded with rationale",
         "category": "DATA", "tags": ["assessment-record", "classification-rationale"], "mandatory": true}
      ],
      "evidence_requirements": ["Assessment record with criteria applied", "Assessor identification"],
      "failure_consequence": "ISO 27001 non-conformity — audit finding"
    },
    {
      "control_id": "ISO27001-A5.26",
      "title": "Response to Information Security Incidents",
      "section_reference": "Annex A §5.26",
      "severity": "mandatory",
      "applies_to": [
        {"trigger_type": "domain_match", "trigger_values": ["resolution", "containment", "investigation"], "match_mode": "any"}
      ],
      "requirements": [
        {"description": "Incidents must be responded to according to documented procedures",
         "category": "PROCEDURE", "tags": ["incident-response-procedure", "documented-procedure"], "mandatory": true},
        {"description": "Evidence must be collected and preserved following forensic procedures",
         "category": "PROCEDURE", "tags": ["evidence-collection", "forensic-procedure", "chain-of-custody", "evidence-preservation"], "mandatory": true}
      ],
      "evidence_requirements": ["Response procedure reference", "Evidence handling log", "Chain of custody records"],
      "failure_consequence": "ISO 27001 non-conformity — evidence may be inadmissible, audit finding"
    },
    {
      "control_id": "ISO27001-A5.28",
      "title": "Collection of Evidence",
      "section_reference": "Annex A §5.28",
      "severity": "mandatory",
      "applies_to": [
        {"trigger_type": "tag_match", "trigger_values": ["evidence", "investigation", "log-analysis", "forensic"], "match_mode": "any"}
      ],
      "requirements": [
        {"description": "Evidence collection and preservation must follow procedures that ensure admissibility",
         "category": "PROCEDURE", "tags": ["evidence-admissibility", "preservation-procedure", "forensic-standard"], "mandatory": true}
      ],
      "evidence_requirements": ["Evidence log with timestamps", "Preservation method documentation"],
      "failure_consequence": "Evidence inadmissible in legal or disciplinary proceedings"
    },
    {
      "control_id": "ISO27001-A8.15",
      "title": "Logging",
      "section_reference": "Annex A §8.15",
      "severity": "mandatory",
      "applies_to": [
        {"trigger_type": "tag_match", "trigger_values": ["system-access", "system-change", "deployment", "rollback", "system-restore"], "match_mode": "any"}
      ],
      "requirements": [
        {"description": "Activities involving system access or changes must produce audit logs",
         "category": "DATA", "tags": ["audit-log", "access-log", "system-log", "activity-record"], "mandatory": true},
        {"description": "Logs must be protected from tampering and unauthorized access",
         "category": "PROCEDURE", "tags": ["log-protection", "log-integrity", "tamper-proof"], "mandatory": true}
      ],
      "evidence_requirements": ["Log configuration record", "Log protection mechanism documentation"],
      "failure_consequence": "ISO 27001 non-conformity — security controls cannot be verified"
    }
  ]
}
```

**Verify:** Both JSON files parse correctly. Controls cover key areas of the incident response
process: detection triggers ITIL classification + ISO assessment controls; investigation triggers
ITIL KEDB + ISO evidence controls; resolution triggers ITIL change management + ISO logging
controls; post-incident triggers ITIL PIR. Total: ~9 controls across 2 frameworks. Multiple
controls should fire per step (demonstrating control overlap).
**Depends:** None (parallel with other tasks)

### Task 20: Regulatory Analyzer Engine
**Context:** Loads regulatory frameworks from JSON and evaluates each BPMN step against all
loaded controls. This is what makes regulation a first-class input rather than a side-effect.

**Action:** Create `regulatory_analyzer.py` with class `RegulatoryAnalyzer`:

**State:**
- `_frameworks: list[RegulatoryFramework]` — loaded frameworks
- `_control_index: dict[ControlTriggerType, dict[str, list[RegulatoryControl]]]` — inverted
  trigger index for fast matching

**Public methods:**

- `load_frameworks(directory: str) -> int`
  - Read all `*.json` files from directory
  - Parse each into `RegulatoryFramework`
  - Build trigger index:
    ```python
    # For each control's triggers:
    # _control_index[DOMAIN_MATCH]["detection"] = [control1, control5, ...]
    # _control_index[TAG_MATCH]["personal-data"] = [control3, control7, ...]
    ```
  - Returns count of frameworks loaded

- `load_framework(file_path: str) -> RegulatoryFramework`
  - Parse single framework file, add to `_frameworks`, update index

- `evaluate_step(node: ProcessNode, scope_path: list[str], scope_depth: int,
  step_tags: list[str], step_data_tags: list[str]) -> list[ControlEvaluation]`
  - Build the step's match context:
    - `domains` = [s.lower().replace(" ", "-") for s in scope_path] +
      [node.name.lower().replace(" ", "-")]
    - `tags` = step_tags + step_data_tags + node.knowledge_tags + node.data_tags
    - `node_type` = node.node_type.value
  - For each control across all frameworks:
    - Check ALL of the control's triggers:
      - `DOMAIN_MATCH`: any trigger_value in domains?
      - `TAG_MATCH`: any trigger_value in tags?
      - `NODE_TYPE_MATCH`: node_type matches?
      - `DATA_CATEGORY`: any trigger_value in step_data_tags?
      - `STEP_NAME_PATTERN`: regex match on node.name?
      - `SCOPE_DEPTH`: scope_depth >= trigger_value?
      - `ANY_STEP`: always True
    - For each trigger with `match_mode="any"`: matches if ANY value matches
    - For each trigger with `match_mode="all"`: matches if ALL values match
    - A control fires if ANY of its triggers match (OR logic across triggers)
  - For each fired control:
    - Convert `ControlRequirement` items to `RequirementItem` objects:
      - category from control requirement
      - priority = CRITICAL if mandatory, IMPORTANT if recommended, HELPFUL if advisory
      - source = f"regulatory:{framework.id}:{control.control_id}"
      - rationale = f"{control.title} ({framework.name} {control.section_reference})"
    - Create `ControlEvaluation` with compliance_status=NOT_ASSESSED (assessed later by
      gap analyzer when matched against store)
  - Deduplicate: same control can match via multiple triggers — keep one evaluation,
    record all triggered_by
  - Return list of evaluations

- `get_frameworks_summary() -> dict`
  - Returns summary: framework names, versions, total controls per framework

- `get_controls_for_domain(domain: str) -> list[RegulatoryControl]`
  - Returns all controls that would fire for a given domain (useful for reporting)

**Integration with orchestrator:**
The orchestrator calls `evaluate_step()` after requirements analysis (Step B.5 in the
ENTER_NODE handler). The resulting regulatory requirements are merged into the step's
requirement set with source attribution. They then flow through the same ranking, gap
analysis, and expansion pipeline as inferred requirements — but with higher priority
weighting and distinct display formatting.

**Compliance status resolution (done by gap analyzer):**
After knowledge matching, the gap analyzer updates each `ControlEvaluation`:
- All MANDATORY requirements MATCHED → COMPLIANT
- Some MANDATORY requirements MATCHED → PARTIALLY_COMPLIANT
- Any MANDATORY requirement is GAP → NON_COMPLIANT
- Only RECOMMENDED/ADVISORY gaps → COMPLIANT (but with notes)

**Verify:**
1. Load both sample frameworks (ITIL + ISO27001)
2. Evaluate step "Receive Alert" in scope ["Incident Response", "Detection"]:
   - Should trigger ITIL-IM-001 (domain=detection) and ISO27001-A5.25 (domain=detection)
   - Should NOT trigger ITIL-CM-001 (domain=resolution)
3. Evaluate step "Collect Logs" in scope ["Incident Response", "Triage", "Investigation", "Analyze Logs"]:
   - Should trigger ISO27001-A5.28 (tags=log-analysis, investigation) and ISO27001-A8.15 (tags=system-access)
   - Should trigger ITIL-KM-001 (domain=investigation)
4. Evaluate step "Deploy" in scope ["Incident Response", "Resolution", "Fix Implementation"]:
   - Should trigger ITIL-CM-001 (domain=resolution, tags=deployment) and ISO27001-A8.15 (tags=deployment)
5. Confirm deduplication: same control firing via multiple triggers counted once
6. Confirm conversion to RequirementItem preserves framework/control ID traceability
**Depends:** Task 2

### Task 21: Integration Testing + Edge Cases + Final Verification
**Context:** Full system verification. Confirm all components work together — including
procedure expansion and HTML rendering — edge cases are handled, and all three output
formats (console, JSON, HTML) are correct and useful.

**Action:**
- Run `python main.py` and capture full output
- Verify: all ~47 nodes from sample BPMN appear in output
- Verify: knowledge requirements generated for every task node
- Verify: coverage levels (MATCHED, PARTIAL, GAP) appear correctly
- Verify: the 4 intentional gaps are identified in the critical gaps summary
- Verify: scope transitions (enter/exit) balance correctly
- Verify: knowledge inheritance works (L3 node can see L0 global knowledge)
- Verify: readiness scores are between 0.0 and 1.0, and process-level readiness is
  a reasonable aggregate
- Verify: JSON export contains all sections, is valid JSON
- **Journey context verification:**
  - Verify: step numbers increment correctly (Step 1 through Step N)
  - Verify: outputs from early steps (e.g., "Assess Impact" in Detection) are queryable
    by later steps (e.g., "Immediate Actions" in Resolution) — cross-scope resolution works
  - Verify: JOURNEY_SATISFIED coverage level appears for context requirements that match
    prior step outputs
  - Verify: process state accumulates correctly (e.g., severity set during Detection is
    visible during Resolution)
  - Verify: decision trail shows gateway decisions in chronological order
  - Verify: journey summary in final output shows correct totals
  - Verify: the "Journey Context" section appears in step display output showing available
    prior outputs and current state
- **Procedure expansion verification:**
  - Verify: Rollback Procedure match triggers expansion of 4 sub-requirements
  - Verify: SOX regulatory gap appears in expanded requirements
  - Verify: GDPR regulatory gap appears when Escalation Procedure is expanded
  - Verify: expansion depth limit prevents infinite recursion
  - Verify: cycle detection works if a procedure references itself
  - Verify: expanded requirements appear nested under their source procedure in console output
  - Verify: regulatory summary in process report shows per-framework breakdown
  - Verify: readiness score drops when expanded requirements are included
    (expanded readiness < base readiness for steps with regulatory gaps)
- **HTML output verification:**
  - Verify: `--export-html spec.html` produces a valid HTML file
  - Verify: HTML opens in browser without errors (no console errors in dev tools)
  - Verify: all subprocess levels render as collapsible sections
  - Verify: coverage colors are correct (green/yellow/red/blue/purple)
  - Verify: expansion cascades render as nested accordions
  - Verify: regulatory gaps have framework badges
  - Verify: search/filter works (type a node name → matches highlight)
  - Verify: expand/collapse all button works
  - Verify: file is self-contained (no external network requests)
  - Verify: embedded JSON data section is valid JSON
- Test edge cases:
  - Task with no documentation tags (should still get type-based requirements)
  - Empty subprocess (start → end, no tasks)
  - Gateway with single outgoing path
  - Maximum nesting depth (4 levels) — verify indentation doesn't break display or HTML
  - First step in process (journey is empty — no prior outputs, no state)
  - Step with context requirement that exactly matches a prior output tag (JOURNEY_SATISFIED)
  - Step with context requirement that has NO prior output match (remains GAP or needs store)
  - Procedure with empty own_requirements (no expansion triggered)
  - Procedure with own_requirements but max_depth already reached (expansion skipped gracefully)
- Fix any issues found

**Verify:** Clean run with no errors. All three output formats (console, JSON, HTML) are
correct and complete. Journey context tracks full process history. Procedure expansion
produces regulatory and compliance gaps. HTML is interactive and stakeholder-ready.
**Depends:** Task 18

---

## 6. Risks & Mitigations

### Risk 1: Requirements Inference Quality
**Risk:** The rule-based analyzer may produce requirements that feel generic or miss
domain-specific nuances.
**Likelihood:** Medium
**Impact:** Medium (reduces demo impact, but framework is extensible)
**Mitigation:** Four-layer approach (explicit > journey-aware > type-based > contextual) ensures
explicit BPMN annotations always take priority. Journey context automatically resolves cross-step
dependencies. Sample BPMN has rich documentation annotations including output tags.
Phase 2 can add LLM-enhanced inference. Rules are configurable dictionaries, easy to tune.

### Risk 2: BPMN XML Parsing Edge Cases
**Risk:** Real-world BPMN from Camunda, Bizagi, Signavio has vendor extensions, alternative
namespaces, or structural variations.
**Likelihood:** Medium (for future use — our sample is controlled)
**Impact:** Low (phase 1 uses our own sample)
**Mitigation:** Parser ignores unknown elements (logs warning, doesn't crash). Namespace
handling is explicit. Parser can be extended with new element handlers.

### Risk 3: Gateway Path Explosion
**Risk:** BPMN with many nested gateways could produce combinatorial explosion of paths,
each generating requirements.
**Likelihood:** Low (sample has moderate gateway use)
**Impact:** Medium (excessive output, slow execution)
**Mitigation:** Walker uses `visited` set per scope. Requirements for shared post-gateway
nodes are only generated once. Display truncates if step count exceeds threshold.

### Risk 4: Knowledge Scoping Complexity
**Risk:** The scope stack + inheritance + propagation model may produce confusing results
when knowledge appears at unexpected levels.
**Likelihood:** Low
**Impact:** Medium (confusing output)
**Mitigation:** Every knowledge item in the output is annotated with its source scope.
The display shows scope transitions clearly. Scope rules are deterministic and documented.

### Risk 5: Display Output Readability at Deep Nesting
**Risk:** At 4+ levels of nesting, the indentation and tree characters may make the console
output hard to read.
**Likelihood:** Medium
**Impact:** Low (functional but ugly)
**Mitigation:** Maximum indent depth is capped visually. Level markers `[L0]`-`[L3]` provide
orientation regardless of visual indent. JSON and HTML exports provide alternative views.

### Risk 6: Recursive Expansion Depth
**Risk:** Deeply chained procedure requirements could produce overwhelming numbers of
expanded requirements, making the output noisy and the readiness scores misleadingly low.
**Likelihood:** Low (max_depth=3 limits this)
**Impact:** Medium (noisy output, confusing scores)
**Mitigation:** Default max_depth=3 covers practical cases. `--expand-depth` flag allows
tuning. `--no-expand` flag disables entirely. Expanded requirements are visually nested
under their source procedure, keeping the hierarchy clear. Readiness scores show both
base and expanded values.

### Risk 7: HTML File Size
**Risk:** With 47+ nodes, each with requirements, expansions, and journey context, the
generated HTML could be very large (multiple MB).
**Likelihood:** Low (sample is moderate size)
**Impact:** Low (modern browsers handle large HTML fine)
**Mitigation:** HTML uses collapsible `<details>` elements — most content is collapsed by
default. Inline CSS/JS are small (no framework overhead). The embedded JSON data section
can be excluded via a flag if file size is a concern.

---

## 7. Verification Plan

### Integration Check
- `python main.py` runs end-to-end without errors on the sample data
- Console output shows: header, per-step analysis, journey context, scope transitions,
  expansion cascades, regulatory gaps, summary
- JSON export (via `--export-json`) produces valid, complete JSON
- HTML export (via `--export-html`) produces valid, self-contained HTML
- All ~47 nodes appear in the output in correct traversal order with step numbers
- Nesting reaches 4 levels with correct scope paths
- Requirements categories (procedures, data, context, decisions, regulatory) appear per step
- Coverage levels (MATCHED, PARTIAL, GAP, JOURNEY_SATISFIED) appear with correct indicators
- Procedure expansion triggers for procedures with own_requirements
- Regulatory controls fire correctly per step based on domain/tag triggers
- ITIL controls fire at detection, investigation, resolution, post-incident steps
- ISO 27001 controls fire at evidence handling, system access, logging steps
- Compliance status computed per control: COMPLIANT/PARTIALLY_COMPLIANT/NON_COMPLIANT
- Critical gaps include: 4 knowledge store gaps + regulatory control gaps
- Two-dimensional readiness scores (knowledge + compliance) computed per step and process
- Compliance summary shows per-framework breakdown (ITIL, ISO27001)
- Journey context shows prior step outputs and accumulated state per step
- Cross-scope data flow works (Detection outputs accessible in Resolution steps)
- HTML renders correctly in browser with all interactive features working

### Regression Check
- N/A (greenfield project)

### Acceptance Criteria
1. **BPMN → Requirements:** Given a BPMN XML, the system generates a Knowledge Requirements
   Specification without any pre-existing knowledge store. (Requirements analysis works
   independently of knowledge matching.)
2. **Requirements + Store → Gap Analysis:** When a knowledge store is also provided, the
   system produces coverage assessment showing what's met vs. what's missing.
3. **Deep Nesting:** Parser and walker correctly handle 4+ levels of subprocess nesting.
4. **Knowledge Scoping (Vertical):** Items at different scope levels are correctly inherited,
   isolated, and propagated through the subprocess hierarchy.
5. **Journey Context (Horizontal):** Step outputs, decisions, and state accumulate across the
   entire process walk. A step in "Resolution" can access outputs from "Detection" even though
   they are sibling subprocesses with no parent-child relationship. The journey ledger persists
   for the full process lifetime.
6. **Cross-Scope Data Flow:** Context requirements that match prior step outputs from any
   subprocess are marked JOURNEY_SATISFIED, not GAP. The system distinguishes between "we
   need knowledge/procedures" (from the store) and "we need data from a prior step" (from
   the journey).
7. **Ranking Relevance:** Same procedure ranks differently in different step contexts
   (contextual ranking, not just keyword matching).
8. **Actionable Gaps:** Gap descriptions include specific recommendations for what knowledge
   should be created.
9. **Process State Tracking:** Accumulated state (severity, assignment, containment status)
   is queryable at any step and shows correct values based on the journey history.
10. **Procedure Expansion:** Matched procedures with own_requirements trigger recursive
    expansion. Regulatory, compliance, and sub-procedure requirements cascade into the step.
    Expansion is depth-limited (default 3) with cycle detection.
11. **Regulatory Frameworks as First-Class Input:** Regulatory frameworks (ITIL, ISO27001,
    and extensible to MISMO, GDPR, SOX, HIPAA, etc.) are loaded from JSON config files and
    evaluated against every step. Controls fire based on domain, tags, node type, and data
    categories. Mandatory controls create CRITICAL requirements that define the compliance
    floor. Regulation is separate from procedures — it's a *generator* of requirements, not
    an answer to them.
12. **Two-Dimensional Readiness:** Each step has both knowledge readiness (procedures, data,
    context) and compliance readiness (regulatory controls met). Combined readiness weights
    compliance at 0.6 — because regulatory gaps are legally required, not discretionary.
13. **Compliance Reporting:** Process-level compliance summary shows per-framework breakdown
    (controls triggered, compliant, non-compliant, percentage). Critical violations
    (MANDATORY + NON_COMPLIANT) are listed with control IDs, section references, and
    failure consequences.
14. **HTML Visual Output:** `--export-html` produces a self-contained HTML file (inline
    CSS/JS, no external dependencies) with collapsible subprocess tree, color-coded coverage,
    expansion cascades, regulatory compliance panels, search, and print mode.
15. **Extensibility:** `KnowledgeStore` interface allows future backend implementations.
    `RequirementsAnalyzer` rules are configurable. Regulatory frameworks are pluggable JSON
    files — add MISMO by creating a `mismo.json` with controls. Journey context provides
    the data layer for phase 2 agentic execution.
16. **Runnable Demo:** `python main.py` with no arguments demonstrates the full capability
    end-to-end — including journey-satisfied requirements, procedure expansion, regulatory
    compliance evaluation, and all output formats (console, JSON, HTML).
