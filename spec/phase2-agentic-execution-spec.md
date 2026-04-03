# Phase 2: Agentic Execution — Specification

**Version:** 0.1.0
**Status:** Roadmap
**Date:** 2026-04-03
**Depends on:** Phase 1 (Knowledge Orchestrator v0.1.0)

---

## 1. Executive Summary

### Phase 1 Recap

Phase 1 built a **knowledge readiness analyzer**. Given a BPMN process, it answers:
- What does each step need? (4-layer inference)
- What do we have? (knowledge store matching + 5-signal ranking)
- What's missing? (gap analysis)
- What does regulation mandate? (regulatory control evaluation)
- What has the process learned so far? (journey context)
- What do matched procedures themselves require? (recursive expansion)

Phase 1 **reports**. It does not **act**.

### Phase 2 Vision

Phase 2 transforms the Knowledge Orchestrator from a readiness analyzer into an
**agentic execution engine**. The Knowledge Requirements Specification produced by
Phase 1 becomes the "work order" that Phase 2's agents consume and execute.

| Capability | Phase 1 | Phase 2 |
|-----------|---------|---------|
| Requirements | Inferred and displayed | Used to drive actions |
| Knowledge gaps | Reported | Resolved (agent searches external systems) |
| Gateway decisions | All paths explored | Paths selected (LLM + state evaluation) |
| Regulatory controls | Evaluated and reported | Enforced (block non-compliant steps) |
| Step execution | Walked and analyzed | Executed (assemble context, call APIs, present to humans) |
| Knowledge matching | Tag-based scoring | Semantic search (vector embeddings + LLM) |
| Process learning | Stateless between runs | Adaptive (learns from execution history) |

### The Fundamental Shift

```
Phase 1:  BPMN  →  "Here's what you need"     (report)
Phase 2:  BPMN  →  "Here's what you need"  →  "Now let me get it and do it"  (execute)
```

---

## 2. Architecture Evolution

### Phase 1 Architecture (Current)

```
BPMN + Regulations + Knowledge Store
         │
    Orchestrator (analyze pipeline)
         │
    Requirements Spec (report)
```

### Phase 2 Architecture (Target)

```
BPMN + Regulations + Knowledge Store + External Systems + LLM
         │
    Orchestrator (analyze pipeline — unchanged)
         │
    Requirements Spec (work order)
         │
    Execution Engine (new)
         │
    ┌────┼──────────────┬──────────────┬──────────────┐
    │    │              │              │              │
┌───▼───┐ ┌────▼─────┐ ┌───▼────┐ ┌───▼────┐ ┌──────▼──────┐
│Knowledge│ │Decision  │ │Compliance│ │Step    │ │Learning    │
│Acquisition│ │Engine  │ │Gates   │ │Executor│ │Store       │
│Agent   │ │(LLM)    │ │        │ │        │ │            │
└───┬───┘ └────┬─────┘ └───┬────┘ └───┬────┘ └──────┬──────┘
    │          │            │          │              │
┌───▼───┐ ┌────▼─────┐ ┌───▼────┐ ┌───▼────┐ ┌──────▼──────┐
│External│ │Human-in- │ │Audit   │ │Service │ │Execution   │
│Systems │ │the-Loop  │ │Trail   │ │APIs    │ │History     │
│(DB,APIs│ │Interface │ │Generator│ │        │ │            │
│docs)   │ │(Web UI)  │ │        │ │        │ │            │
└────────┘ └──────────┘ └────────┘ └────────┘ └─────────────┘
```

### Key Principle: Phase 1 Is Unchanged

Phase 2 is **additive**. Every Phase 1 component continues to work exactly as built.
Phase 2 wraps the orchestrator's output in an execution layer. The `--analyze` flag
runs Phase 1 only (the current behavior). The `--execute` flag runs Phase 1 then
feeds the result into Phase 2's execution engine.

---

## 3. Six Capability Layers

### Layer 1: Knowledge Acquisition Agent

**Problem:** Phase 1 identifies gaps but cannot resolve them. When a step needs the
"Evidence Collection SOP" and it doesn't exist in the store, the system reports
"GAP — recommended: create a procedure covering this area." Useful, but passive.

**Solution:** An agent that actively resolves gaps by searching connected external
systems, retrieving relevant knowledge, validating it, and making it available to
the step.

**Gap Resolution Workflow:**

```
GAP detected for step N
  │
  ├─ Search knowledge store (already done in Phase 1 — confirmed GAP)
  │
  ├─ Search external systems:
  │    ├─ Document management (SharePoint, Confluence, Google Drive)
  │    ├─ Databases (PostgreSQL, enterprise knowledge bases)
  │    ├─ Vector store (semantic similarity search)
  │    ├─ API endpoints (internal knowledge services)
  │    └─ Indexed file systems (network shares, wikis)
  │
  ├─ If found:
  │    ├─ Validate relevance (LLM scoring + tag matching)
  │    ├─ Ingest into knowledge store (create KnowledgeItem)
  │    ├─ Re-evaluate step coverage (GAP → MATCHED/PARTIAL)
  │    └─ Record acquisition in journey (KNOWLEDGE_DISCOVERED)
  │
  └─ If not found:
       ├─ Generate knowledge template (LLM drafts a procedure outline)
       ├─ Route for human creation/review
       ├─ Mark as UNRESOLVABLE with recommendation
       └─ Escalate if CRITICAL + MANDATORY
```

**KnowledgeStore Protocol Extensions:**

```python
class KnowledgeStore(Protocol):
    # --- Existing Phase 1 methods (unchanged) ---
    def query(self, tags, scope, category) -> list[KnowledgeItem]: ...
    def get_by_id(self, item_id) -> KnowledgeItem | None: ...
    def get_all(self) -> list[KnowledgeItem]: ...
    def get_by_category(self, category) -> list[KnowledgeItem]: ...
    def get_by_scope(self, scope) -> list[KnowledgeItem]: ...
    def get_by_type(self, knowledge_type) -> list[KnowledgeItem]: ...
    def count(self) -> int: ...

    # --- Phase 2 additions ---
    def search_semantic(self, query_text: str, top_k: int = 10) -> list[KnowledgeItem]: ...
    def ingest(self, item: KnowledgeItem) -> str: ...  # Returns item ID
    def search_external(self, tags: list[str], query: str) -> list[ExternalSearchResult]: ...
```

**New Backend Implementations:**

| Backend | Purpose | Key Method |
|---------|---------|-----------|
| `PostgresKnowledgeStore` | Persistent storage with full-text search | `query()` with SQL, `ingest()` with INSERT |
| `VectorKnowledgeStore` | Semantic similarity search | `search_semantic()` via embeddings |
| `CompositeKnowledgeStore` | Chains multiple backends | Routes queries to appropriate backend |
| `ExternalSearchAgent` | Searches SharePoint, Confluence, etc. | `search_external()` via API connectors |

**New Models:**

```python
@dataclass
class ExternalSearchResult:
    source_system: str          # "sharepoint", "confluence", "database"
    source_url: str             # Link to original document
    title: str
    content_preview: str        # First 500 chars
    relevance_score: float      # 0.0-1.0
    tags: list[str]             # Extracted/inferred tags
    retrievable: bool           # Can we pull the full content?

@dataclass
class AcquisitionResult:
    requirement_id: str         # Which requirement was this resolving?
    search_results: list[ExternalSearchResult]
    selected_result: ExternalSearchResult | None
    ingested_item: KnowledgeItem | None
    resolution: str             # "resolved", "partial", "unresolvable"
    resolution_notes: str
```

---

### Layer 2: Gateway Decision Engine

**Problem:** Phase 1 explores ALL gateway paths because it's mapping knowledge needs,
not making decisions. In execution mode, the system must choose which path to take at
exclusive gateways, determine which paths activate at inclusive gateways, and coordinate
parallel execution.

**Solution:** A decision engine that evaluates gateway conditions against the accumulated
journey state, optionally consulting an LLM for complex decisions, with human-in-the-loop
for high-stakes choices.

**Decision Flow:**

```
Arrive at ExclusiveGateway
  │
  ├─ Collect decision context:
  │    ├─ Journey state: get_current_state()
  │    ├─ Prior step outputs: query_prior_outputs()
  │    ├─ Decision criteria: step_requirements.decision_criteria
  │    ├─ Regulatory constraints: control_evaluations
  │    └─ Gateway conditions: outgoing flow condition_expressions
  │
  ├─ Evaluate conditions:
  │    ├─ Rule-based: parse condition_expression against state
  │    │   e.g., "${incident_severity} == 'S1'" → check state["incident_severity"]
  │    ├─ LLM-assisted: if condition is complex or natural language
  │    │   e.g., "Critical systems affected" → LLM evaluates against journey context
  │    └─ Human-in-the-loop: if decision.risk_level == "high"
  │         Present context + options to human, await selection
  │
  ├─ Select path(s):
  │    ├─ ExclusiveGateway: exactly one path
  │    ├─ InclusiveGateway: one or more paths
  │    └─ ParallelGateway: all paths (unchanged from Phase 1)
  │
  └─ Record decision:
       ├─ JourneyDecision with criteria_used, outcome, rationale
       ├─ JourneyStateChange for decision outcome
       └─ Only walk selected path(s) — not all paths
```

**Walker Changes:**

```python
class ProcessWalker:
    def walk(
        self,
        process: ProcessDefinition,
        callback: Callable[[WalkerEvent], None],
        execution_mode: bool = False,           # NEW
        decision_engine: DecisionEngine | None = None,  # NEW
    ) -> None: ...

    def _walk_from(self, node, nodes, flows, depth, scope_path, visited, callback,
                   execution_mode=False, decision_engine=None):
        # ...
        if is_gateway and execution_mode and decision_engine:
            # Phase 2: evaluate conditions, walk only selected paths
            selected = decision_engine.evaluate(node, flows, nodes, scope_path)
            for flow, target in selected:
                callback(WalkerEvent(GATEWAY_PATH, metadata={"condition": flow.name, "selected": True}))
                self._walk_from(target, ...)
        elif is_gateway:
            # Phase 1: explore all paths (unchanged)
            for flow, target in self._get_outgoing_targets(node, flows, nodes):
                callback(WalkerEvent(GATEWAY_PATH, ...))
                self._walk_from(target, ...)
```

**New Models:**

```python
@dataclass
class DecisionContext:
    gateway_node: ProcessNode
    outgoing_flows: list[SequenceFlow]
    journey_state: dict[str, str]
    prior_outputs: list[JourneyOutput]
    decision_criteria: list[RequirementItem]
    regulatory_constraints: list[ControlEvaluation]

@dataclass
class GatewayDecisionResult:
    gateway_id: str
    selected_flows: list[SequenceFlow]       # Which paths to take
    decision_method: str                     # "rule", "llm", "human"
    rationale: str                           # Why this path was chosen
    confidence: float                        # 0.0-1.0
    human_override: bool                     # Was this overridden by human?

class DecisionEngine:
    def evaluate(self, gateway: ProcessNode, flows: dict, nodes: dict,
                 scope_path: list[str], journey: JourneyContext) -> list[tuple[SequenceFlow, ProcessNode]]: ...
```

---

### Layer 3: Regulatory Compliance Gates

**Problem:** Phase 1 evaluates regulatory controls and reports compliance status. A step
with MANDATORY controls that are NON_COMPLIANT is flagged but not blocked. In execution
mode, non-compliant steps must not proceed — regulation is the floor, not a suggestion.

**Solution:** A compliance gate layer that sits between requirements analysis and step
execution. It checks all MANDATORY controls, blocks execution if non-compliant, and
manages evidence collection.

**Enforcement Logic:**

```
Step ready for execution
  │
  ├─ Evaluate regulatory controls (existing Phase 1 logic)
  │
  ├─ Check compliance status per control:
  │    ├─ All MANDATORY controls COMPLIANT → PROCEED
  │    ├─ Any MANDATORY control PARTIALLY_COMPLIANT → PROCEED WITH WARNING
  │    │   (evidence collection required)
  │    ├─ Any MANDATORY control NON_COMPLIANT → BLOCK
  │    │   ├─ Attempt gap resolution (Layer 1: Knowledge Acquisition)
  │    │   ├─ If resolved → re-evaluate → may proceed
  │    │   ├─ If unresolvable → escalate to compliance officer
  │    │   └─ Log compliance violation in audit trail
  │    └─ RECOMMENDED controls: log warnings, do not block
  │
  ├─ Evidence collection:
  │    ├─ For each fired control: gather evidence_requirements
  │    ├─ Automated: pull from journey context, system logs, timestamps
  │    ├─ Manual: request from human (checklist of evidence needed)
  │    └─ Attach evidence to ControlEvaluation
  │
  └─ Audit trail:
       ├─ Generated automatically from journey entries
       ├─ Includes: who, what, when, why, evidence, decision rationale
       ├─ Exportable per regulatory framework
       └─ Tamper-proof (append-only journal, hash chain optional)
```

**RegulatoryAnalyzer Extension:**

```python
class RegulatoryAnalyzer:
    # --- Existing Phase 1 methods ---
    def evaluate_step(self, node, scope_path, scope_depth, step_tags, step_data_tags) -> list[ControlEvaluation]: ...

    # --- Phase 2 additions ---
    def enforce_step(self, node, scope_path, scope_depth, step_tags, step_data_tags,
                     knowledge_coverage: list[RequirementCoverage]) -> EnforcementResult: ...

    def collect_evidence(self, control: RegulatoryControl, journey: JourneyContext,
                         step_report: StepCoverageReport) -> list[EvidenceItem]: ...

    def generate_audit_trail(self, journey: JourneyContext,
                             framework_id: str) -> AuditTrail: ...
```

**New Models:**

```python
class EnforcementAction(Enum):
    PROCEED = "proceed"
    PROCEED_WITH_WARNING = "proceed_with_warning"
    BLOCK = "block"
    ESCALATE = "escalate"

@dataclass
class EnforcementResult:
    action: EnforcementAction
    blocking_controls: list[ControlEvaluation]     # Controls causing BLOCK
    warnings: list[ControlEvaluation]              # Controls causing WARNING
    evidence_collected: list[EvidenceItem]
    escalation_target: str | None                  # Who to escalate to
    rationale: str

@dataclass
class EvidenceItem:
    evidence_id: str
    control_id: str
    description: str
    evidence_type: str        # "automated", "manual", "document", "timestamp"
    content: str              # The evidence itself
    collected_at: str         # ISO timestamp
    collected_by: str         # "system" or user ID
    verified: bool

@dataclass
class AuditTrail:
    framework_id: str
    framework_name: str
    process_name: str
    execution_id: str
    entries: list[AuditEntry]
    generated_at: str

@dataclass
class AuditEntry:
    step_number: int
    node_name: str
    timestamp: str
    controls_evaluated: list[str]       # Control IDs
    compliance_status: ComplianceStatus
    evidence: list[EvidenceItem]
    enforcement_action: EnforcementAction
    decision_rationale: str
```

---

### Layer 4: Step Execution Orchestration

**Problem:** Phase 1 walks through steps and analyzes what they need. Phase 2 must
actually *execute* each step — calling APIs for ServiceTasks, presenting work packages
to humans for UserTasks, and running scripts for ScriptTasks.

**Solution:** A step executor that assembles an execution package from the knowledge
context, journey state, and regulatory clearance, then dispatches to the appropriate
execution handler.

**Execution Pipeline (extends Phase 1's A-H pipeline):**

```
Phase 1 Pipeline (A-H): analyze requirements, evaluate controls, match knowledge,
                         assess gaps, expand procedures, record journey

Phase 2 Pipeline (continues from H):

Step I: Compliance Gate
  └─ enforcement_result = compliance_gate.enforce(step_report)
  └─ IF BLOCK → halt, escalate, skip to next step or abort process

Step J: Knowledge Acquisition (if gaps remain)
  └─ FOR each GAP in step_report:
       └─ acquisition_agent.resolve(gap, external_systems)
       └─ Re-evaluate coverage

Step K: Assemble Execution Package
  └─ package = {
       knowledge: matched procedures + journey context,
       data: data inputs from journey + external sources,
       decisions: criteria + prior decisions,
       regulatory: evidence requirements + compliance status,
       context: full scope chain + journey state,
     }

Step L: Execute
  └─ MATCH node.node_type:
       ServiceTask → service_executor.call(package.api_config, package.inputs)
       UserTask → ui_presenter.present(package) → await human response
       ScriptTask → script_executor.run(package.script_ref, package.inputs)
       ManualTask → ui_presenter.present(package) → await human confirmation

Step M: Capture Output
  └─ Parse execution result
  └─ Create JourneyOutputs from actual outputs (not inferred)
  └─ Record state changes
  └─ Update journey context with real data

Step N: Verify & Record
  └─ Verify outputs against expected schema
  └─ Collect execution evidence for regulatory compliance
  └─ Record in journey with execution metadata
  └─ Emit to display/UI
```

**New Models:**

```python
@dataclass
class ExecutionPackage:
    step_number: int
    node: ProcessNode
    knowledge_context: list[KnowledgeItem]      # Matched procedures
    data_inputs: dict[str, Any]                 # Available data
    journey_state: dict[str, str]               # Current state
    decision_criteria: list[RequirementItem]     # Decision guidance
    regulatory_clearance: EnforcementResult      # Compliance gate result
    prior_outputs: list[JourneyOutput]          # Relevant prior outputs
    scope_path: list[str]

@dataclass
class ExecutionResult:
    step_number: int
    node_id: str
    status: str                     # "completed", "failed", "skipped", "blocked"
    outputs: dict[str, Any]         # Actual output data
    duration_ms: int
    executor: str                   # "service", "human", "script", "manual"
    error: str | None
    evidence: list[EvidenceItem]    # Execution evidence for audit

class StepExecutor(Protocol):
    def execute(self, package: ExecutionPackage) -> ExecutionResult: ...

class ServiceTaskExecutor:
    """Calls external APIs based on the execution package."""
    def execute(self, package: ExecutionPackage) -> ExecutionResult: ...

class UserTaskPresenter:
    """Presents the execution package to a human via web UI, awaits response."""
    def execute(self, package: ExecutionPackage) -> ExecutionResult: ...

class ScriptTaskExecutor:
    """Runs scripts with assembled inputs."""
    def execute(self, package: ExecutionPackage) -> ExecutionResult: ...
```

---

### Layer 5: LLM-Enhanced Inference

**Problem:** Phase 1's inference is rule-based and deterministic. Tag matching is
precise but brittle — "alerting" doesn't match "monitoring-setup" even though they're
semantically related. Type-based rules are generic — every UserTask gets the same
baseline requirements regardless of its actual purpose.

**Solution:** Add LLM-powered intelligence at four integration points, augmenting
(not replacing) the existing rule-based system.

**Integration Point 1: Semantic Knowledge Ranking**

Replace tag-only matching with hybrid tag + semantic scoring:

```python
class HybridKnowledgeRanker(KnowledgeRanker):
    """Extends the 5-signal ranker with a 6th signal: semantic similarity."""

    def __init__(self, weights=None, embedding_model=None):
        super().__init__(weights)
        self._embedder = embedding_model
        # Default weights shift to accommodate 6th signal:
        # tag_overlap: 0.20, category_match: 0.20, keyword_relevance: 0.10,
        # scope_proximity: 0.15, type_fit: 0.10, semantic_similarity: 0.25

    def _score_semantic_similarity(self, item: KnowledgeItem,
                                    requirement: RequirementItem) -> float:
        """Embed requirement description + item summary, compute cosine similarity."""
        ...
```

**Integration Point 2: Requirements Inference Layer 5**

A new inference layer that reads the BPMN node's documentation and name, then uses
an LLM to infer requirements that rules can't catch:

```python
class LLMRequirementsLayer:
    """Layer 5: LLM reads node documentation and infers requirements."""

    def infer(self, node: ProcessNode, scope_path: list[str],
              existing_requirements: StepRequirements) -> StepRequirements:
        """
        Prompt: "Given a BPMN step named '{node.name}' of type '{node.node_type}'
        in the subprocess path '{scope_path}', with documentation: '{node.documentation}',
        and already-identified requirements: {existing_requirements},
        what additional knowledge, data, context, or decision criteria would a
        practitioner need to execute this step correctly?"
        """
        ...
```

**Integration Point 3: Intelligent Gap Descriptions**

Replace template-based gap descriptions with LLM-generated recommendations:

```python
# Phase 1: "No matching knowledge found for 'Evidence Collection'.
#           Recommended: Create a procedure covering this area."

# Phase 2: "No evidence collection procedure found. Based on the step context
#           (Root Cause Analysis > Collect Evidence, ISO 27001 A5.28 compliance
#           required), recommend creating a procedure covering: chain of custody
#           requirements, digital evidence preservation standards, forensic imaging
#           procedures, evidence labeling and cataloging, and admissibility criteria
#           per your jurisdiction's legal requirements."
```

**Integration Point 4: Intelligent Output Inference**

Replace verb-noun heuristic with LLM understanding:

```python
# Phase 1: "Assess Impact" → infers output tag "impact-assessed"

# Phase 2: LLM infers: "This step produces: impact severity level (S1-S4),
#           affected system count, estimated revenue impact per hour,
#           business unit impact assessment, customer-facing impact flag"
```

---

### Layer 6: Adaptive Process Learning

**Problem:** Phase 1 is stateless between runs. Every execution starts from zero
knowledge about how previous runs went, what gaps were resolved, what decisions
were made, and what worked well or poorly.

**Solution:** A learning store that persists execution history across runs, enabling
the system to improve over time.

**What Gets Learned:**

```python
@dataclass
class ExecutionHistory:
    execution_id: str
    process_id: str
    started_at: str
    completed_at: str
    total_steps: int
    outcome: str                           # "completed", "aborted", "blocked"
    gap_resolutions: list[GapResolution]   # Gaps that were resolved
    decision_history: list[DecisionRecord] # Gateway decisions with outcomes
    override_history: list[OverrideRecord] # Human overrides of agent decisions
    performance_metrics: dict[str, float]  # Step durations, resolution times, etc.

@dataclass
class GapResolution:
    requirement_id: str
    requirement_description: str
    resolution_source: str              # Where the knowledge was found
    resolution_item_id: str             # KnowledgeItem that resolved it
    resolution_quality: float           # 0.0-1.0 (human-rated or inferred)
    reusable: bool                      # Can this resolution be applied to future runs?

@dataclass
class DecisionRecord:
    gateway_id: str
    decision_method: str                # "rule", "llm", "human"
    selected_path: str
    context_snapshot: dict              # Journey state at decision time
    outcome_quality: float              # 0.0-1.0 (was this the right path?)
    feedback: str | None                # Human feedback if overridden

@dataclass
class OverrideRecord:
    step_number: int
    original_action: str                # What the agent proposed
    override_action: str                # What the human chose instead
    rationale: str                      # Why the override happened
    incorporated: bool                  # Has this override been learned?
```

**How Learning Applies:**

1. **Gap Resolution Memory:** When a gap is resolved in execution N, the resolution
   is cached. In execution N+1, if the same gap pattern appears, the cached resolution
   is offered immediately (skipping external search).

2. **Decision Quality Feedback:** When a human overrides an LLM gateway decision,
   the override rationale is stored. Future decisions at similar gateways incorporate
   this feedback into the LLM prompt.

3. **Regulatory Override Tracking:** When compliance controls are repeatedly overridden
   with human approval, the system flags these controls for framework review — they
   may be misconfigured or the regulation may have changed.

4. **Step Duration Baselines:** Execution timing data enables the system to predict
   process duration and flag steps that are taking unusually long.

5. **Knowledge Quality Scoring:** Over time, procedures that are frequently matched
   but overridden or supplemented get lower quality scores, signaling they need updating.

---

## 4. Phase 1 Interface Changes

Every Phase 1 component continues to work unchanged. Phase 2 **extends** them.

### models.py — New Types Added

| Dataclass | Purpose |
|-----------|---------|
| `ExternalSearchResult` | Result from external system search |
| `AcquisitionResult` | Gap resolution outcome |
| `DecisionContext` | Input to gateway decision engine |
| `GatewayDecisionResult` | Output from gateway decision engine |
| `EnforcementResult` | Compliance gate decision |
| `EvidenceItem` | Compliance evidence artifact |
| `AuditTrail` / `AuditEntry` | Regulatory audit report |
| `ExecutionPackage` | Assembled step execution context |
| `ExecutionResult` | Step execution outcome |
| `ExecutionHistory` | Cross-run execution record |
| `GapResolution` / `DecisionRecord` / `OverrideRecord` | Learning data |

### New Enums

| Enum | Values |
|------|--------|
| `EnforcementAction` | PROCEED, PROCEED_WITH_WARNING, BLOCK, ESCALATE |
| `ExecutionStatus` | COMPLETED, FAILED, SKIPPED, BLOCKED, AWAITING_HUMAN |
| `DecisionMethod` | RULE, LLM, HUMAN, HYBRID |

### Existing Interface Extensions

| Component | Phase 1 Interface | Phase 2 Extension |
|-----------|------------------|-------------------|
| `KnowledgeStore` | 7 query methods | + `search_semantic()`, `ingest()`, `search_external()` |
| `RegulatoryAnalyzer` | `evaluate_step()` | + `enforce_step()`, `collect_evidence()`, `generate_audit_trail()` |
| `ProcessWalker` | `walk(process, callback)` | + `execution_mode`, `decision_engine` parameters |
| `KnowledgeRanker` | 5-signal scoring | + 6th signal: `_score_semantic_similarity()` |
| `RequirementsAnalyzer` | 4 inference layers | + Layer 5: `LLMRequirementsLayer` |
| `Orchestrator` | Steps A-H (analyze) | + Steps I-N (execute) |

---

## 5. New Components

| Module | Class | Purpose |
|--------|-------|---------|
| `execution_engine.py` | `ExecutionEngine` | Wraps orchestrator output, runs Steps I-N |
| `knowledge_agent.py` | `KnowledgeAcquisitionAgent` | Searches external systems, resolves gaps |
| `decision_engine.py` | `DecisionEngine` | LLM-assisted gateway routing with human-in-the-loop |
| `compliance_gate.py` | `ComplianceGate` | Enforcement layer — block/allow/escalate |
| `evidence_collector.py` | `EvidenceCollector` | Gathers compliance evidence from journey + systems |
| `audit_generator.py` | `AuditTrailGenerator` | Produces per-framework audit reports |
| `vector_store.py` | `VectorKnowledgeStore` | Semantic search backend (implements KnowledgeStore) |
| `postgres_store.py` | `PostgresKnowledgeStore` | Persistent storage backend (implements KnowledgeStore) |
| `composite_store.py` | `CompositeKnowledgeStore` | Chains multiple store backends |
| `llm_inference.py` | `LLMRequirementsLayer` | LLM-powered requirement inference (Layer 5) |
| `hybrid_ranker.py` | `HybridKnowledgeRanker` | Extends ranker with semantic similarity signal |
| `learning_store.py` | `LearningStore` | Persists execution history, gap resolutions, decisions |
| `execution_ui.py` | `ExecutionUI` | Web interface for UserTask execution and human-in-the-loop |
| `service_executor.py` | `ServiceTaskExecutor` | API caller for ServiceTasks |
| `script_executor.py` | `ScriptTaskExecutor` | Script runner for ScriptTasks |

---

## 6. Implementation Roadmap

### Phase 2.1: Real Knowledge Store Backends
**Scope:** PostgreSQL and vector store implementations of KnowledgeStore Protocol
**Dependencies:** None (standalone backend work)
**Deliverables:**
- `postgres_store.py` — full KnowledgeStore implementation with SQL
- `vector_store.py` — embedding-based semantic search
- `composite_store.py` — chains InMemory + Postgres + Vector
- Migration tooling: JSON → PostgreSQL
**Verification:** Same integration tests pass with Postgres backend as with InMemory

### Phase 2.2: Gateway Decision Engine
**Scope:** Conditional path selection replacing "explore all paths"
**Dependencies:** Phase 2.1 (for knowledge-informed decisions)
**Deliverables:**
- `decision_engine.py` — rule-based condition evaluation + LLM fallback
- Walker changes: `execution_mode` parameter
- Journey state comparison for condition evaluation
- Decision recording in journey with rationale
**Verification:** Gateway with condition `severity == S1` routes correctly based on journey state

### Phase 2.3: Regulatory Compliance Gates
**Scope:** Enforcement mode that blocks non-compliant steps
**Dependencies:** Phase 2.1
**Deliverables:**
- `compliance_gate.py` — enforce_step() with PROCEED/BLOCK/ESCALATE logic
- `evidence_collector.py` — automated evidence gathering from journey
- `audit_generator.py` — per-framework audit trail export
- Orchestrator pipeline extension: Step I between H and current execution
**Verification:** Step with MANDATORY NON_COMPLIANT control is blocked; evidence collected for COMPLIANT steps

### Phase 2.4: Knowledge Acquisition Agent
**Scope:** Active gap resolution from external systems
**Dependencies:** Phase 2.1 (composite store for ingestion), Phase 2.3 (compliance context)
**Deliverables:**
- `knowledge_agent.py` — search + acquire + validate + ingest workflow
- External system connectors: SharePoint, Confluence, generic REST API
- Re-evaluation pipeline: after acquisition, re-run gap analysis
- Template generation for unresolvable gaps (LLM-assisted)
**Verification:** GAP for "Evidence Collection SOP" → agent finds document in Confluence → ingests → coverage becomes MATCHED

### Phase 2.5: Step Execution Orchestration
**Scope:** Actually execute steps (call APIs, present to humans, run scripts)
**Dependencies:** Phase 2.2 (decision engine), Phase 2.3 (compliance gates), Phase 2.4 (gap resolution)
**Deliverables:**
- `execution_engine.py` — Steps I-N pipeline
- `service_executor.py` — API calling for ServiceTasks
- `script_executor.py` — script running for ScriptTasks
- Execution package assembly from knowledge context + journey + compliance
- Output capture and journey recording with actual (not inferred) outputs
**Verification:** Full process execution: analyze → decide → check compliance → execute → record

### Phase 2.6: Human-in-the-Loop Interface
**Scope:** Web UI for UserTask execution and human decision override
**Dependencies:** Phase 2.5 (execution orchestration)
**Deliverables:**
- `execution_ui.py` — lightweight web server (Flask or FastAPI)
- UserTask view: assembled knowledge context, procedures, data, decision criteria
- Gateway override view: agent's recommendation + override option
- Evidence submission view: manual evidence upload for compliance
- Execution dashboard: process progress, blocked steps, pending tasks
**Verification:** Human can view step context, make decision at gateway, submit evidence, mark UserTask complete

### Phase 2.7: LLM-Enhanced Inference
**Scope:** Semantic search, intelligent requirement inference, smart gap descriptions
**Dependencies:** Phase 2.1 (vector store), Phase 2.5 (execution context)
**Deliverables:**
- `hybrid_ranker.py` — 6-signal ranking with semantic similarity
- `llm_inference.py` — Layer 5 requirement inference from documentation
- Enhanced gap descriptions with domain-specific recommendations
- Intelligent output inference from step context
**Verification:** Semantic search finds "Monitoring Setup Runbook" for tag "alerting" (which tag matching misses); LLM infers additional requirements from step documentation

### Phase 2.8: Adaptive Process Learning
**Scope:** Cross-run learning from execution history
**Dependencies:** Phase 2.5 (execution), Phase 2.6 (human feedback), Phase 2.7 (LLM)
**Deliverables:**
- `learning_store.py` — persists execution history, gap resolutions, decision records
- Gap resolution cache: resolved gaps offered immediately in future runs
- Decision quality feedback loop: human overrides improve future LLM decisions
- Regulatory override tracking: frequently overridden controls flagged for review
- Knowledge quality scoring: under-performing procedures flagged for update
**Verification:** Run process twice — second run resolves previously-resolved gaps immediately from cache; overridden decision is incorporated into next run's LLM prompt

---

## 7. Technical Requirements

### New Dependencies

| Dependency | Purpose | Phase |
|-----------|---------|-------|
| `psycopg2` or `asyncpg` | PostgreSQL client | 2.1 |
| `pgvector` | PostgreSQL vector extension | 2.1 |
| `sentence-transformers` or `openai` | Embedding generation | 2.1 |
| `anthropic` or `openai` | LLM API client | 2.2+ |
| `flask` or `fastapi` | Web UI server | 2.6 |
| `jinja2` | UI templating | 2.6 |

### Infrastructure Requirements

| Component | Purpose |
|-----------|---------|
| PostgreSQL 15+ with pgvector | Persistent knowledge store + semantic search |
| LLM API access | Claude or GPT for decision engine + inference |
| External system credentials | SharePoint, Confluence, etc. API keys |
| Web server | For human-in-the-loop interface |

### Security Considerations

- LLM API calls must not leak sensitive process data (PII, financial data)
- External system connectors need credential management (vault/env vars)
- Audit trails must be tamper-resistant
- Compliance evidence must be integrity-protected
- Human-in-the-loop interface needs authentication
- Execution engine must sandbox script execution (ScriptTasks)

---

## 8. CLI Changes

```bash
# Phase 1 (unchanged)
python main.py                              # Analyze only (current behavior)
python main.py --export-json spec.json
python main.py --export-html spec.html

# Phase 2 additions
python main.py --execute                    # Execute the process (Phase 2)
python main.py --execute --dry-run          # Execute pipeline without side effects
python main.py --execute --human-loop       # Enable human-in-the-loop UI
python main.py --execute --enforce          # Enable regulatory enforcement (blocking)
python main.py --execute --learn            # Enable learning store
python main.py --execute --llm claude       # Use Claude for decisions + inference
python main.py --audit ITIL_V4             # Generate audit trail for framework
python main.py --store postgres             # Use PostgreSQL backend
python main.py --store vector               # Use vector store backend
```

The `--execute` flag is the master switch. Without it, the system behaves exactly
as Phase 1 — analyze and report only.
