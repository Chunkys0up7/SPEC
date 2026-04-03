"""
Knowledge Orchestrator — Data Models.

All shared types used across components: BPMN process nodes, knowledge items,
requirements, coverage, journey entries, regulatory controls, and expansion results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class NodeType(Enum):
    START_EVENT = "start_event"
    END_EVENT = "end_event"
    TASK = "task"
    USER_TASK = "user_task"
    SERVICE_TASK = "service_task"
    SCRIPT_TASK = "script_task"
    MANUAL_TASK = "manual_task"
    EXCLUSIVE_GATEWAY = "exclusive_gateway"
    PARALLEL_GATEWAY = "parallel_gateway"
    INCLUSIVE_GATEWAY = "inclusive_gateway"
    SUB_PROCESS = "sub_process"


class KnowledgeType(Enum):
    PROCEDURE = "procedure"
    RUNBOOK = "runbook"
    POLICY = "policy"
    REFERENCE = "reference"
    FAQ = "faq"
    CHECKLIST = "checklist"


class RequirementCategory(Enum):
    PROCEDURE = "procedure"
    DATA = "data"
    CONTEXT = "context"
    DECISION = "decision"
    REGULATORY = "regulatory"


class RequirementPriority(Enum):
    CRITICAL = "critical"
    IMPORTANT = "important"
    HELPFUL = "helpful"


class CoverageLevel(Enum):
    MATCHED = "matched"
    PARTIAL = "partial"
    GAP = "gap"
    JOURNEY_SATISFIED = "journey"
    NOT_ASSESSED = "n/a"


class WalkerEventType(Enum):
    ENTER_PROCESS = "enter_process"
    EXIT_PROCESS = "exit_process"
    ENTER_SCOPE = "enter_scope"
    EXIT_SCOPE = "exit_scope"
    ENTER_NODE = "enter_node"
    EXIT_NODE = "exit_node"
    ENTER_GATEWAY = "enter_gateway"
    GATEWAY_PATH = "gateway_path"
    CYCLE_DETECTED = "cycle_detected"


class JourneyEntryType(Enum):
    TASK_COMPLETED = "task_completed"
    GATEWAY_EVALUATED = "gateway_evaluated"
    SCOPE_ENTERED = "scope_entered"
    SCOPE_EXITED = "scope_exited"
    KNOWLEDGE_DISCOVERED = "knowledge_discovered"


class KnowledgeRequirementType(Enum):
    PROCEDURE = "procedure"
    DATA = "data"
    REGULATORY = "regulatory"
    APPROVAL = "approval"
    SUB_PROCEDURE = "sub-procedure"
    COMPLIANCE = "compliance"
    CERTIFICATION = "certification"


class ControlSeverity(Enum):
    MANDATORY = "mandatory"
    RECOMMENDED = "recommended"
    ADVISORY = "advisory"


class ControlTriggerType(Enum):
    DOMAIN_MATCH = "domain_match"
    TAG_MATCH = "tag_match"
    NODE_TYPE_MATCH = "node_type"
    DATA_CATEGORY = "data_category"
    STEP_NAME_PATTERN = "name_pattern"
    SCOPE_DEPTH = "scope_depth"
    ANY_STEP = "any"


class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partial"
    NON_COMPLIANT = "non_compliant"
    NEEDS_REVIEW = "needs_review"
    NOT_ASSESSED = "not_assessed"


# ---------------------------------------------------------------------------
# BPMN Process Model
# ---------------------------------------------------------------------------

@dataclass
class SequenceFlow:
    id: str
    name: str | None
    source_ref: str
    target_ref: str
    condition_expression: str | None = None


@dataclass
class ProcessNode:
    id: str
    name: str
    node_type: NodeType
    documentation: str | None = None
    knowledge_tags: list[str] = field(default_factory=list)
    data_tags: list[str] = field(default_factory=list)
    context_tags: list[str] = field(default_factory=list)
    decision_tags: list[str] = field(default_factory=list)
    output_tags: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
    incoming_flows: list[str] = field(default_factory=list)
    outgoing_flows: list[str] = field(default_factory=list)
    parent_subprocess: str | None = None


@dataclass
class SubProcess(ProcessNode):
    child_nodes: dict[str, ProcessNode] = field(default_factory=dict)
    child_flows: dict[str, SequenceFlow] = field(default_factory=dict)
    scope_domain: str = ""


@dataclass
class ProcessDefinition:
    id: str
    name: str
    nodes: dict[str, ProcessNode] = field(default_factory=dict)
    flows: dict[str, SequenceFlow] = field(default_factory=dict)
    description: str = ""


# ---------------------------------------------------------------------------
# Knowledge Model
# ---------------------------------------------------------------------------

@dataclass
class KnowledgeRequirement:
    """A requirement declared by a knowledge item (procedure's own needs)."""
    requirement_type: str
    description: str
    tags: list[str] = field(default_factory=list)
    priority: RequirementPriority = RequirementPriority.IMPORTANT
    regulatory_framework: str | None = None
    mandatory: bool = False


@dataclass
class KnowledgeItem:
    id: str
    title: str
    content_summary: str
    category: str
    tags: list[str] = field(default_factory=list)
    knowledge_type: KnowledgeType = KnowledgeType.PROCEDURE
    source: str = ""
    metadata: dict[str, str] = field(default_factory=dict)
    applicable_scopes: list[str] = field(default_factory=list)
    scope_level: str = "process"
    own_requirements: list[KnowledgeRequirement] = field(default_factory=list)


@dataclass
class KnowledgeScore:
    knowledge_item: KnowledgeItem
    total_score: float
    signal_scores: dict[str, float] = field(default_factory=dict)
    signal_contributions: dict[str, float] = field(default_factory=dict)
    match_explanation: str = ""


# ---------------------------------------------------------------------------
# Requirements Model
# ---------------------------------------------------------------------------

@dataclass
class RequirementItem:
    requirement_id: str
    description: str
    category: RequirementCategory
    tags: list[str] = field(default_factory=list)
    priority: RequirementPriority = RequirementPriority.IMPORTANT
    source: str = ""
    rationale: str = ""


@dataclass
class DependencyItem:
    depends_on_node_id: str
    depends_on_node_name: str
    data_needed: str
    scope_relationship: str = "same-level"


@dataclass
class StepRequirements:
    node_id: str
    node_name: str
    node_type: NodeType
    scope_path: list[str] = field(default_factory=list)
    scope_depth: int = 0
    procedures: list[RequirementItem] = field(default_factory=list)
    data_inputs: list[RequirementItem] = field(default_factory=list)
    contextual: list[RequirementItem] = field(default_factory=list)
    decision_criteria: list[RequirementItem] = field(default_factory=list)
    regulatory: list[RequirementItem] = field(default_factory=list)
    dependencies: list[DependencyItem] = field(default_factory=list)
    inference_sources: list[str] = field(default_factory=list)
    confidence: float = 0.0


# ---------------------------------------------------------------------------
# Journey Model
# ---------------------------------------------------------------------------

@dataclass
class JourneyOutput:
    output_id: str
    description: str
    data_type: str = "data"
    tags: list[str] = field(default_factory=list)
    produced_by_node: str = ""
    produced_at_step: int = 0
    available_to: str = "all"


@dataclass
class JourneyDecision:
    decision_id: str
    description: str
    criteria_used: list[str] = field(default_factory=list)
    outcome: str = ""
    affects_steps: list[str] = field(default_factory=list)
    gateway_id: str | None = None


@dataclass
class JourneyStateChange:
    attribute: str
    old_value: str | None
    new_value: str
    reason: str = ""


@dataclass
class JourneyEntry:
    step_number: int
    node_id: str
    node_name: str
    scope_path: list[str] = field(default_factory=list)
    scope_depth: int = 0
    entry_type: JourneyEntryType = JourneyEntryType.TASK_COMPLETED
    outputs: list[JourneyOutput] = field(default_factory=list)
    decisions: list[JourneyDecision] = field(default_factory=list)
    state_changes: list[JourneyStateChange] = field(default_factory=list)
    timestamp: str = ""
    gateway_condition: str | None = None


@dataclass
class JourneySummary:
    total_steps: int = 0
    scopes_visited: list[str] = field(default_factory=list)
    decisions_made: int = 0
    outputs_produced: int = 0
    state_attributes_tracked: int = 0
    journey_entries: list[JourneyEntry] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Regulatory Model
# ---------------------------------------------------------------------------

@dataclass
class ControlTrigger:
    trigger_type: ControlTriggerType
    trigger_values: list[str] = field(default_factory=list)
    match_mode: str = "any"


@dataclass
class ControlRequirement:
    description: str
    category: str = "REGULATORY"
    tags: list[str] = field(default_factory=list)
    mandatory: bool = True
    evidence_required: str | None = None


@dataclass
class RegulatoryControl:
    control_id: str
    title: str
    description: str = ""
    framework_id: str = ""
    section_reference: str = ""
    severity: ControlSeverity = ControlSeverity.MANDATORY
    applies_to: list[ControlTrigger] = field(default_factory=list)
    requirements: list[ControlRequirement] = field(default_factory=list)
    evidence_requirements: list[str] = field(default_factory=list)
    failure_consequence: str = ""


@dataclass
class RegulatoryFramework:
    id: str
    name: str
    version: str = ""
    description: str = ""
    jurisdiction: str = "global"
    controls: list[RegulatoryControl] = field(default_factory=list)


@dataclass
class ControlEvaluation:
    control: RegulatoryControl
    framework: RegulatoryFramework
    triggered_by: list[ControlTrigger] = field(default_factory=list)
    requirements: list[RequirementItem] = field(default_factory=list)
    evidence_needed: list[str] = field(default_factory=list)
    compliance_status: ComplianceStatus = ComplianceStatus.NOT_ASSESSED


@dataclass
class FrameworkCompliance:
    framework_id: str
    framework_name: str
    controls_triggered: int = 0
    compliant: int = 0
    partially_compliant: int = 0
    non_compliant: int = 0
    compliance_percentage: float = 0.0
    non_compliant_controls: list[ControlEvaluation] = field(default_factory=list)


@dataclass
class ComplianceSummary:
    frameworks_evaluated: list[str] = field(default_factory=list)
    total_controls_triggered: int = 0
    total_compliant: int = 0
    total_partially_compliant: int = 0
    total_non_compliant: int = 0
    compliance_by_framework: dict[str, FrameworkCompliance] = field(default_factory=dict)
    critical_violations: list[ControlEvaluation] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Coverage Model
# ---------------------------------------------------------------------------

@dataclass
class RequirementCoverage:
    requirement: RequirementItem
    coverage_level: CoverageLevel = CoverageLevel.NOT_ASSESSED
    matched_knowledge: list[KnowledgeScore] | None = None
    journey_source: JourneyOutput | None = None
    coverage_notes: str = ""
    gap_description: str | None = None


@dataclass
class StepReadiness:
    knowledge_readiness: float = 0.0
    compliance_readiness: float = 0.0
    combined_readiness: float = 0.0


@dataclass
class ExpansionResult:
    source_item: KnowledgeItem | None = None
    expanded_requirements: list[RequirementItem] = field(default_factory=list)
    expanded_coverage: list[RequirementCoverage] = field(default_factory=list)
    sub_expansions: list[ExpansionResult] = field(default_factory=list)
    expansion_depth: int = 0
    total_expanded_count: int = 0


@dataclass
class ScopeCoverageSummary:
    scope_name: str
    scope_level: int = 0
    total_requirements: int = 0
    matched: int = 0
    partial: int = 0
    gaps: int = 0
    journey_satisfied: int = 0
    readiness: StepReadiness = field(default_factory=StepReadiness)


@dataclass
class StepCoverageReport:
    step_requirements: StepRequirements | None = None
    procedure_coverage: list[RequirementCoverage] = field(default_factory=list)
    data_coverage: list[RequirementCoverage] = field(default_factory=list)
    context_coverage: list[RequirementCoverage] = field(default_factory=list)
    decision_coverage: list[RequirementCoverage] = field(default_factory=list)
    regulatory_requirements: list[RequirementCoverage] = field(default_factory=list)
    control_evaluations: list[ControlEvaluation] = field(default_factory=list)
    expansions: list[ExpansionResult] = field(default_factory=list)
    total_requirements: int = 0
    matched_count: int = 0
    partial_count: int = 0
    gap_count: int = 0
    journey_satisfied_count: int = 0
    total_expanded_requirements: int = 0
    expanded_gaps: list[RequirementCoverage] = field(default_factory=list)
    readiness: StepReadiness = field(default_factory=StepReadiness)
    step_number: int = 0


@dataclass
class ProcessCoverageReport:
    process_name: str = ""
    total_steps_analyzed: int = 0
    total_requirements: int = 0
    total_matched: int = 0
    total_partial: int = 0
    total_gaps: int = 0
    total_journey_satisfied: int = 0
    overall_readiness: StepReadiness = field(default_factory=StepReadiness)
    critical_gaps: list[RequirementCoverage] = field(default_factory=list)
    scope_summaries: list[ScopeCoverageSummary] = field(default_factory=list)
    compliance_summary: ComplianceSummary = field(default_factory=ComplianceSummary)
    step_reports: list[StepCoverageReport] = field(default_factory=list)
    journey_summary: JourneySummary = field(default_factory=JourneySummary)


# ---------------------------------------------------------------------------
# Walker Model
# ---------------------------------------------------------------------------

@dataclass
class WalkerEvent:
    event_type: WalkerEventType
    node: ProcessNode | None = None
    depth: int = 0
    scope_path: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Knowledge Context Model
# ---------------------------------------------------------------------------

@dataclass
class KnowledgeContext:
    scope_name: str
    scope_level: int = 0
    scope_domain: str = ""
    local_items: list[KnowledgeItem] = field(default_factory=list)
    inherited_items: list[KnowledgeItem] = field(default_factory=list)
    discovered_items: list[KnowledgeItem] = field(default_factory=list)
