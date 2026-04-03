"""
Knowledge Orchestrator — Requirements Analyzer.

4-layer inference engine that examines each BPMN node and generates categorized
requirements. Also infers what each step produces for journey recording.

Layers:
  1. Explicit — from BPMN documentation tags
  2. Journey-aware — from process history (cross-step dependencies)
  3. Type-based — from BPMN node type (UserTask, ServiceTask, etc.)
  4. Contextual — from position in flow and subprocess scope
"""

from __future__ import annotations

import re
import uuid
from typing import TYPE_CHECKING

from .models import (
    DependencyItem,
    JourneyOutput,
    NodeType,
    ProcessNode,
    RequirementCategory,
    RequirementItem,
    RequirementPriority,
    StepRequirements,
)

if TYPE_CHECKING:
    from .journey_context import JourneyContext


def _make_id() -> str:
    return f"req_{uuid.uuid4().hex[:8]}"


def _tag_to_description(tag: str, category: str) -> str:
    human = tag.replace("-", " ").replace("_", " ").title()
    return f"{human} ({category})"


# ---------------------------------------------------------------------------
# Type-based requirement rules
# ---------------------------------------------------------------------------

_TYPE_RULES: dict[NodeType, dict[str, list[dict]]] = {
    NodeType.USER_TASK: {
        "procedures": [
            {"desc": "Standard operating procedure for this activity",
             "tags": ["sop", "procedure"], "priority": "important",
             "rationale": "UserTasks represent human activities requiring documented procedures"},
        ],
        "decisions": [
            {"desc": "Completion criteria for this task",
             "tags": ["completion-criteria", "quality-check"], "priority": "helpful",
             "rationale": "UserTasks need clear definition of done"},
        ],
    },
    NodeType.SERVICE_TASK: {
        "data_inputs": [
            {"desc": "Input data schema and source",
             "tags": ["input-schema", "data-source"], "priority": "critical",
             "rationale": "ServiceTasks are automated and require well-defined inputs"},
            {"desc": "Error handling and fallback procedure",
             "tags": ["error-handling", "fallback", "retry"], "priority": "important",
             "rationale": "Automated tasks need defined failure modes"},
        ],
    },
    NodeType.SCRIPT_TASK: {
        "data_inputs": [
            {"desc": "Script reference and runtime requirements",
             "tags": ["script", "automation", "runtime"], "priority": "critical",
             "rationale": "ScriptTasks need their script artifact and execution context"},
        ],
    },
    NodeType.MANUAL_TASK: {
        "procedures": [
            {"desc": "Step-by-step procedure and checklist",
             "tags": ["procedure", "checklist", "manual-steps"], "priority": "critical",
             "rationale": "ManualTasks are offline activities requiring detailed documentation"},
        ],
    },
    NodeType.EXCLUSIVE_GATEWAY: {
        "decisions": [
            {"desc": "Decision criteria and routing rules",
             "tags": ["decision-criteria", "routing", "evaluation"], "priority": "critical",
             "rationale": "Exclusive gateways require clear criteria to choose one path"},
        ],
    },
    NodeType.PARALLEL_GATEWAY: {
        "contextual": [
            {"desc": "Parallel execution coordination requirements",
             "tags": ["coordination", "parallel", "synchronization"], "priority": "helpful",
             "rationale": "Parallel gateways may need coordination between branches"},
        ],
    },
    NodeType.INCLUSIVE_GATEWAY: {
        "decisions": [
            {"desc": "Evaluation criteria for inclusive path selection",
             "tags": ["evaluation-criteria", "inclusive-routing"], "priority": "important",
             "rationale": "Inclusive gateways need criteria to determine which paths activate"},
        ],
    },
}

# ---------------------------------------------------------------------------
# Output inference rules by node type
# ---------------------------------------------------------------------------

_OUTPUT_RULES: dict[NodeType, list[tuple[str, str]]] = {
    NodeType.USER_TASK: [
        ("task-output", "Human task completion output"),
        ("human-decision", "Decision or judgment made by human"),
    ],
    NodeType.SERVICE_TASK: [
        ("service-response", "Automated service response data"),
    ],
    NodeType.SCRIPT_TASK: [
        ("computed-result", "Script computation result"),
    ],
    NodeType.EXCLUSIVE_GATEWAY: [
        ("routing-decision", "Path selection decision"),
    ],
    NodeType.INCLUSIVE_GATEWAY: [
        ("routing-decision", "Inclusive path selection"),
    ],
    NodeType.MANUAL_TASK: [
        ("task-output", "Manual task completion output"),
    ],
}

# Domain tag inference from scope names
_DOMAIN_TAGS: dict[str, list[str]] = {
    "detection": ["detection", "monitoring", "alerting", "event-identification"],
    "classification": ["classification", "categorization", "severity"],
    "triage": ["triage", "initial-assessment", "prioritization"],
    "investigation": ["investigation", "analysis", "evidence", "troubleshooting"],
    "resolution": ["fix", "remediation", "restoration", "resolution"],
    "containment": ["containment", "isolation", "mitigation", "temporary-fix"],
    "deployment": ["deployment", "release", "rollout", "go-live"],
    "post-incident": ["post-mortem", "review", "lessons-learned", "improvement"],
    "root-cause-analysis": ["rca", "root-cause", "hypothesis", "evidence"],
    "fix-implementation": ["development", "fix", "testing", "deployment"],
}


class RequirementsAnalyzer:

    def __init__(
        self,
        type_rules: dict | None = None,
        context_rules: dict | None = None,
    ) -> None:
        self._type_rules = type_rules or _TYPE_RULES
        self._output_rules = _OUTPUT_RULES
        self._domain_tags = context_rules or _DOMAIN_TAGS

    def analyze_node(
        self,
        node: ProcessNode,
        scope_path: list[str],
        scope_depth: int,
        prior_nodes: list[ProcessNode] | None = None,
        journey: JourneyContext | None = None,
    ) -> StepRequirements:
        prior_nodes = prior_nodes or []

        # Layer 1: Explicit
        l1_procs, l1_data, l1_ctx, l1_dec = self._extract_explicit_requirements(node)

        # Layer 2: Journey-aware
        l2_procs, l2_data, l2_ctx, l2_dec = [], [], [], []
        if journey:
            l2_procs, l2_data, l2_ctx, l2_dec = self._infer_journey_requirements(node, scope_path, journey)

        # Layer 3: Type-based
        l3_procs, l3_data, l3_ctx, l3_dec = self._infer_type_requirements(node, l1_procs + l2_procs)

        # Layer 4: Contextual
        l4_procs, l4_data, l4_ctx, l4_dec = self._infer_contextual_requirements(
            node, scope_path, scope_depth, prior_nodes)

        # Merge and deduplicate
        procedures = self._merge(l1_procs, l2_procs, l3_procs, l4_procs)
        data_inputs = self._merge(l1_data, l2_data, l3_data, l4_data)
        contextual = self._merge(l1_ctx, l2_ctx, l3_ctx, l4_ctx)
        decisions = self._merge(l1_dec, l2_dec, l3_dec, l4_dec)

        # Dependencies
        dependencies = self._detect_dependencies(node, prior_nodes, scope_path, journey)

        # Determine inference sources and confidence
        sources = []
        if l1_procs or l1_data or l1_ctx or l1_dec:
            sources.append("explicit")
        if l2_procs or l2_data or l2_ctx or l2_dec:
            sources.append("journey-aware")
        if l3_procs or l3_data or l3_ctx or l3_dec:
            sources.append("type-based")
        if l4_procs or l4_data or l4_ctx or l4_dec:
            sources.append("contextual")

        confidence = 1.0 if "explicit" in sources else (0.8 if "journey-aware" in sources else 0.7 if "type-based" in sources else 0.5)

        return StepRequirements(
            node_id=node.id,
            node_name=node.name,
            node_type=node.node_type,
            scope_path=list(scope_path),
            scope_depth=scope_depth,
            procedures=procedures,
            data_inputs=data_inputs,
            contextual=contextual,
            decision_criteria=decisions,
            dependencies=dependencies,
            inference_sources=sources,
            confidence=confidence,
        )

    def infer_outputs(self, node: ProcessNode, scope_path: list[str]) -> list[JourneyOutput]:
        outputs: list[JourneyOutput] = []
        seen_tags: set[str] = set()

        # 1. Explicit output tags from documentation
        for tag in node.output_tags:
            if tag not in seen_tags:
                seen_tags.add(tag)
                outputs.append(JourneyOutput(
                    output_id=f"out_{node.id}_{tag}",
                    description=_tag_to_description(tag, "output"),
                    data_type="data",
                    tags=[tag],
                    produced_by_node=node.id,
                ))

        # 2. Type-based outputs
        for tag, desc in self._output_rules.get(node.node_type, []):
            if tag not in seen_tags:
                seen_tags.add(tag)
                outputs.append(JourneyOutput(
                    output_id=f"out_{node.id}_{tag}",
                    description=desc,
                    data_type="inferred",
                    tags=[tag],
                    produced_by_node=node.id,
                ))

        # 3. Name-based outputs (verb-noun pattern)
        name_output_tag = self._infer_output_from_name(node.name)
        if name_output_tag and name_output_tag not in seen_tags:
            seen_tags.add(name_output_tag)
            outputs.append(JourneyOutput(
                output_id=f"out_{node.id}_{name_output_tag}",
                description=f"Output from: {node.name}",
                data_type="inferred",
                tags=[name_output_tag],
                produced_by_node=node.id,
            ))

        return outputs

    # --- Layer 1: Explicit ---

    def _extract_explicit_requirements(
        self, node: ProcessNode
    ) -> tuple[list[RequirementItem], list[RequirementItem], list[RequirementItem], list[RequirementItem]]:
        procs = [RequirementItem(
            requirement_id=_make_id(), description=_tag_to_description(tag, "procedure"),
            category=RequirementCategory.PROCEDURE, tags=[tag],
            priority=RequirementPriority.CRITICAL, source="explicit",
            rationale="Declared in BPMN documentation"
        ) for tag in node.knowledge_tags]

        data = [RequirementItem(
            requirement_id=_make_id(), description=_tag_to_description(tag, "data"),
            category=RequirementCategory.DATA, tags=[tag],
            priority=RequirementPriority.CRITICAL, source="explicit",
            rationale="Declared in BPMN documentation"
        ) for tag in node.data_tags]

        ctx = [RequirementItem(
            requirement_id=_make_id(), description=_tag_to_description(tag, "context"),
            category=RequirementCategory.CONTEXT, tags=[tag],
            priority=RequirementPriority.IMPORTANT, source="explicit",
            rationale="Declared in BPMN documentation"
        ) for tag in node.context_tags if tag.lower() != "none"]

        dec = [RequirementItem(
            requirement_id=_make_id(), description=_tag_to_description(tag, "decision"),
            category=RequirementCategory.DECISION, tags=[tag],
            priority=RequirementPriority.IMPORTANT, source="explicit",
            rationale="Declared in BPMN documentation"
        ) for tag in node.decision_tags]

        return procs, data, ctx, dec

    # --- Layer 2: Journey-aware ---

    def _infer_journey_requirements(
        self, node: ProcessNode, scope_path: list[str], journey: JourneyContext
    ) -> tuple[list[RequirementItem], list[RequirementItem], list[RequirementItem], list[RequirementItem]]:
        ctx: list[RequirementItem] = []

        # Check context tags against journey outputs
        for tag in node.context_tags:
            if tag.lower() == "none":
                continue
            prior = journey.query_prior_outputs([tag])
            source_note = "journey-check"
            if prior:
                source_note = f"journey-satisfied:step-{prior[0].produced_at_step}"

            ctx.append(RequirementItem(
                requirement_id=_make_id(),
                description=f"Context from process journey: {_tag_to_description(tag, 'context')}",
                category=RequirementCategory.CONTEXT,
                tags=[tag],
                priority=RequirementPriority.IMPORTANT,
                source=source_note,
                rationale=f"Context tag '{tag}' checked against journey history",
            ))

        # Check accumulated state for relevant context
        state = journey.get_current_state()
        if state:
            ctx.append(RequirementItem(
                requirement_id=_make_id(),
                description=f"Accumulated process state ({len(state)} attributes available)",
                category=RequirementCategory.CONTEXT,
                tags=list(state.keys()),
                priority=RequirementPriority.HELPFUL,
                source="journey-state",
                rationale="Process state accumulated from prior steps",
            ))

        return [], [], ctx, []

    # --- Layer 3: Type-based ---

    def _infer_type_requirements(
        self, node: ProcessNode, existing_procs: list[RequirementItem]
    ) -> tuple[list[RequirementItem], list[RequirementItem], list[RequirementItem], list[RequirementItem]]:
        rules = self._type_rules.get(node.node_type, {})
        existing_tags = set()
        for req in existing_procs:
            existing_tags.update(t.lower() for t in req.tags)

        procs, data, ctx, dec = [], [], [], []
        category_map = {
            "procedures": (procs, RequirementCategory.PROCEDURE),
            "data_inputs": (data, RequirementCategory.DATA),
            "contextual": (ctx, RequirementCategory.CONTEXT),
            "decisions": (dec, RequirementCategory.DECISION),
        }

        for cat_key, rule_list in rules.items():
            target_list, cat_enum = category_map.get(cat_key, (None, None))
            if target_list is None:
                continue

            for rule in rule_list:
                rule_tags = set(t.lower() for t in rule["tags"])
                # Skip if overlapping with explicit tags
                if rule_tags & existing_tags:
                    continue

                priority = RequirementPriority(rule.get("priority", "important"))
                target_list.append(RequirementItem(
                    requirement_id=_make_id(),
                    description=rule["desc"],
                    category=cat_enum,
                    tags=rule["tags"],
                    priority=priority,
                    source="type-rule",
                    rationale=rule.get("rationale", f"Inferred from {node.node_type.value}"),
                ))

        return procs, data, ctx, dec

    # --- Layer 4: Contextual ---

    def _infer_contextual_requirements(
        self, node: ProcessNode, scope_path: list[str],
        scope_depth: int, prior_nodes: list[ProcessNode]
    ) -> tuple[list[RequirementItem], list[RequirementItem], list[RequirementItem], list[RequirementItem]]:
        procs, data, ctx, dec = [], [], [], []

        # First task in scope
        if not prior_nodes:
            ctx.append(RequirementItem(
                requirement_id=_make_id(),
                description="Subprocess-level context and objectives",
                category=RequirementCategory.CONTEXT,
                tags=["subprocess-context", "objectives"],
                priority=RequirementPriority.IMPORTANT,
                source="contextual",
                rationale="First task in subprocess needs scope-level context",
            ))
            data.append(RequirementItem(
                requirement_id=_make_id(),
                description="Inputs from parent scope needed to begin this subprocess",
                category=RequirementCategory.DATA,
                tags=["parent-inputs", "scope-entry-data"],
                priority=RequirementPriority.IMPORTANT,
                source="contextual",
                rationale="First task in subprocess needs inputs from parent",
            ))

        # Task after gateway
        if prior_nodes and prior_nodes[-1].node_type in (
            NodeType.EXCLUSIVE_GATEWAY, NodeType.INCLUSIVE_GATEWAY
        ):
            ctx.append(RequirementItem(
                requirement_id=_make_id(),
                description=f"Decision outcome from gateway: {prior_nodes[-1].name}",
                category=RequirementCategory.CONTEXT,
                tags=["gateway-decision", "routing-outcome"],
                priority=RequirementPriority.CRITICAL,
                source="contextual",
                rationale="Task follows a gateway — needs to know which path was taken",
            ))

        # Deep nesting
        if scope_depth >= 3:
            procs.append(RequirementItem(
                requirement_id=_make_id(),
                description="Escalation path to parent scope if blocked",
                category=RequirementCategory.PROCEDURE,
                tags=["escalation", "parent-scope", "blocked-resolution"],
                priority=RequirementPriority.HELPFUL,
                source="contextual",
                rationale=f"Deep nesting (level {scope_depth}) — escalation path needed",
            ))

        # Subprocess domain tags
        if scope_path:
            current_scope = scope_path[-1].lower().replace(" ", "-").replace("&", "and")
            domain_tags = self._domain_tags.get(current_scope, [])
            if domain_tags:
                ctx.append(RequirementItem(
                    requirement_id=_make_id(),
                    description=f"Domain knowledge for: {scope_path[-1]}",
                    category=RequirementCategory.CONTEXT,
                    tags=domain_tags,
                    priority=RequirementPriority.HELPFUL,
                    source="contextual",
                    rationale=f"Subprocess domain '{scope_path[-1]}' implies domain knowledge needs",
                ))

        return procs, data, ctx, dec

    # --- Dependencies ---

    def _detect_dependencies(
        self, node: ProcessNode, prior_nodes: list[ProcessNode],
        scope_path: list[str], journey: JourneyContext | None
    ) -> list[DependencyItem]:
        deps: list[DependencyItem] = []

        # Prior node output dependency
        if prior_nodes:
            prior = prior_nodes[-1]
            deps.append(DependencyItem(
                depends_on_node_id=prior.id,
                depends_on_node_name=prior.name,
                data_needed=f"Output from prior step: {prior.name}",
                scope_relationship="same-level",
            ))

        # Cross-scope dependencies from journey
        if journey and node.context_tags:
            for tag in node.context_tags:
                if tag.lower() == "none":
                    continue
                prior_outputs = journey.query_prior_outputs([tag])
                for output in prior_outputs:
                    if output.produced_by_node != node.id:
                        deps.append(DependencyItem(
                            depends_on_node_id=output.produced_by_node,
                            depends_on_node_name=f"Step {output.produced_at_step}",
                            data_needed=output.description,
                            scope_relationship="cross-scope",
                        ))

        return deps

    # --- Merge & Dedup ---

    def _merge(self, *layers: list[RequirementItem]) -> list[RequirementItem]:
        result: list[RequirementItem] = []
        seen_tag_sets: list[set[str]] = []

        for layer in layers:
            for req in layer:
                req_tags = set(t.lower() for t in req.tags)
                is_dup = False
                for existing_tags in seen_tag_sets:
                    if not req_tags or not existing_tags:
                        continue
                    overlap = len(req_tags & existing_tags) / len(req_tags | existing_tags)
                    if overlap > 0.5:
                        is_dup = True
                        break
                if not is_dup:
                    result.append(req)
                    seen_tag_sets.append(req_tags)

        return result

    # --- Output Inference Helpers ---

    def _infer_output_from_name(self, name: str) -> str | None:
        words = re.split(r"[\s\-_]+", name.strip())
        if len(words) < 2:
            return None

        verbs = {"assess", "collect", "classify", "identify", "gather", "analyze",
                 "check", "verify", "evaluate", "determine", "create", "assign",
                 "document", "conduct", "develop", "review", "deploy", "filter",
                 "correlate", "hypothesize", "design", "execute", "isolate",
                 "validate", "apply", "notify", "receive"}

        first = words[0].lower()
        if first in verbs:
            noun_parts = [w.lower() for w in words[1:]]
            return "-".join(noun_parts) + "-" + first + "ed"

        return None
