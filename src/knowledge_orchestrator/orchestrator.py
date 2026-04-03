"""
Knowledge Orchestrator — Main Coordinator.

Central component wiring the walker, requirements analyzer, knowledge store,
ranker, gap analyzer, scope context manager, journey context, procedure expander,
and regulatory analyzer into a single pipeline.

For each BPMN node: gather context -> analyze requirements -> evaluate regulatory
controls -> check journey -> match store -> rank -> gap analysis -> expand
procedures -> record in journey -> emit to display.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .models import (
    CoverageLevel,
    JourneyEntryType,
    JourneyOutput,
    NodeType,
    ProcessCoverageReport,
    ProcessDefinition,
    ProcessNode,
    ScopeCoverageSummary,
    StepCoverageReport,
    SubProcess,
    WalkerEvent,
    WalkerEventType,
)
from .gap_analyzer import GapAnalyzer
from .journey_context import JourneyContext
from .knowledge_context import KnowledgeContextManager
from .knowledge_ranker import KnowledgeRanker
from .knowledge_store import KnowledgeStore
from .procedure_expander import ProcedureExpander
from .regulatory_analyzer import RegulatoryAnalyzer
from .requirements_analyzer import RequirementsAnalyzer
from .walker import ProcessWalker


class KnowledgeOrchestrator:

    def __init__(
        self,
        knowledge_store: KnowledgeStore,
        requirements_analyzer: RequirementsAnalyzer,
        knowledge_ranker: KnowledgeRanker,
        gap_analyzer: GapAnalyzer,
        context_manager: KnowledgeContextManager,
        journey_context: JourneyContext,
        procedure_expander: ProcedureExpander | None = None,
        regulatory_analyzer: RegulatoryAnalyzer | None = None,
    ) -> None:
        self._store = knowledge_store
        self._req_analyzer = requirements_analyzer
        self._ranker = knowledge_ranker
        self._gap_analyzer = gap_analyzer
        self._context_mgr = context_manager
        self._journey = journey_context
        self._expander = procedure_expander
        self._reg_analyzer = regulatory_analyzer

        self._display_cb: Callable[[str, Any], None] | None = None
        self._step_reports: list[StepCoverageReport] = []
        self._prior_nodes_by_scope: dict[str, list[ProcessNode]] = {}
        self._step_number = 0
        self._process_name = ""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register_display(self, callback: Callable[[str, Any], None]) -> None:
        self._display_cb = callback

    def run(self, process: ProcessDefinition) -> ProcessCoverageReport:
        self._step_reports = []
        self._prior_nodes_by_scope = {}
        self._step_number = 0
        self._process_name = process.name

        # Initialize context manager with global knowledge
        global_items = [
            item for item in self._store.get_all()
            if item.scope_level == "global"
        ]
        self._context_mgr.initialize_global(global_items)

        # Walk the process
        walker = ProcessWalker()
        walker.walk(process, self._on_event)

        # Build process-level report
        report = self._gap_analyzer.analyze_process(self._step_reports, process.name)
        report.journey_summary = self._journey.get_journey_summary()

        return report

    # ------------------------------------------------------------------
    # Walker event handler
    # ------------------------------------------------------------------

    def _on_event(self, event: WalkerEvent) -> None:
        match event.event_type:
            case WalkerEventType.ENTER_PROCESS:
                self._handle_enter_process(event)
            case WalkerEventType.EXIT_PROCESS:
                self._handle_exit_process(event)
            case WalkerEventType.ENTER_SCOPE:
                self._handle_enter_scope(event)
            case WalkerEventType.EXIT_SCOPE:
                self._handle_exit_scope(event)
            case WalkerEventType.ENTER_NODE:
                self._handle_enter_node(event)
            case WalkerEventType.ENTER_GATEWAY:
                self._handle_enter_gateway(event)
            case WalkerEventType.GATEWAY_PATH:
                self._handle_gateway_path(event)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _handle_enter_process(self, event: WalkerEvent) -> None:
        name = event.metadata.get("process_name", "Process")

        # Count nodes for header (rough estimate from top-level)
        knowledge_count = self._store.count()
        reg_count = 0
        if self._reg_analyzer:
            summary = self._reg_analyzer.get_frameworks_summary()
            reg_count = len(summary.get("frameworks", []))

        self._emit("header", {
            "process_name": name,
            "node_count": 0,  # filled at end
            "depth": 0,
            "knowledge_count": knowledge_count,
            "regulatory_count": reg_count,
        })

    def _handle_exit_process(self, event: WalkerEvent) -> None:
        pass  # Summary is displayed by main.py calling display.display_summary()

    def _handle_enter_scope(self, event: WalkerEvent) -> None:
        node = event.node
        if node is None:
            return

        scope_name = node.name
        depth = event.depth
        scope_path = event.scope_path

        # Determine domain
        domain = scope_name.lower().replace(" ", "-").replace("&", "and")
        if isinstance(node, SubProcess) and node.scope_domain:
            domain = node.scope_domain

        # Push scope in context manager
        self._context_mgr.push_scope(scope_name, depth, domain)

        # Pre-load scope-relevant knowledge
        scope_items = self._store.get_by_scope(domain)
        preloaded = 0
        for item in scope_items:
            self._context_mgr.add_to_current_scope(item)
            preloaded += 1

        # Initialize prior-nodes tracker for this scope
        scope_key = "/".join(scope_path)
        self._prior_nodes_by_scope[scope_key] = []

        # Record in journey
        self._journey.record_step(
            node_id=node.id,
            node_name=scope_name,
            scope_path=scope_path,
            scope_depth=depth,
            entry_type=JourneyEntryType.SCOPE_ENTERED,
        )

        self._emit("scope_enter", {
            "scope_name": scope_name,
            "depth": depth,
            "domain": domain,
            "preloaded_count": preloaded,
        })

    def _handle_exit_scope(self, event: WalkerEvent) -> None:
        node = event.node
        if node is None:
            return

        scope_name = node.name
        depth = event.depth

        # Pop scope from context manager (propagates discovered items)
        self._context_mgr.pop_scope()

        # Build a scope summary from step reports in this scope
        scope_reports = [
            r for r in self._step_reports
            if r.step_requirements and scope_name in r.step_requirements.scope_path
        ]
        summary = None
        if scope_reports:
            total = sum(r.total_requirements for r in scope_reports)
            matched = sum(r.matched_count for r in scope_reports)
            partial = sum(r.partial_count for r in scope_reports)
            gaps = sum(r.gap_count for r in scope_reports)
            journey = sum(r.journey_satisfied_count for r in scope_reports)
            kr = (matched + journey + partial * 0.5) / total if total else 0.0
            from .models import StepReadiness
            summary = ScopeCoverageSummary(
                scope_name=scope_name,
                scope_level=depth,
                total_requirements=total,
                matched=matched,
                partial=partial,
                gaps=gaps,
                journey_satisfied=journey,
                readiness=StepReadiness(knowledge_readiness=round(kr, 4)),
            )

        # Record in journey
        self._journey.record_step(
            node_id=node.id,
            node_name=scope_name,
            scope_path=event.scope_path,
            scope_depth=depth,
            entry_type=JourneyEntryType.SCOPE_EXITED,
        )

        self._emit("scope_exit", {
            "scope_name": scope_name,
            "depth": depth,
            "summary": summary,
        })

    def _handle_enter_node(self, event: WalkerEvent) -> None:
        node = event.node
        if node is None:
            return

        # Skip start/end events for requirement analysis
        if node.node_type in (NodeType.START_EVENT, NodeType.END_EVENT):
            return

        # Skip gateways — handled by ENTER_GATEWAY
        if node.node_type in (
            NodeType.EXCLUSIVE_GATEWAY, NodeType.PARALLEL_GATEWAY,
            NodeType.INCLUSIVE_GATEWAY,
        ):
            return

        # Skip subprocesses (they are handled via scope enter/exit)
        if node.node_type == NodeType.SUB_PROCESS:
            return

        self._step_number += 1
        depth = event.depth
        scope_path = event.scope_path

        # --- Step A: Gather context ---
        scope_key = "/".join(scope_path)
        prior_nodes = self._prior_nodes_by_scope.get(scope_key, [])

        # --- Step B: Analyze requirements ---
        step_reqs = self._req_analyzer.analyze_node(
            node=node,
            scope_path=scope_path,
            scope_depth=depth,
            prior_nodes=prior_nodes,
            journey=self._journey,
        )

        # --- Step B.5: Evaluate regulatory controls ---
        control_evaluations = []
        if self._reg_analyzer:
            all_tags = (
                [t for r in step_reqs.procedures for t in r.tags]
                + [t for r in step_reqs.contextual for t in r.tags]
                + [t for r in step_reqs.decision_criteria for t in r.tags]
            )
            data_tags = [t for r in step_reqs.data_inputs for t in r.tags]

            control_evaluations = self._reg_analyzer.evaluate_step(
                node=node,
                scope_path=scope_path,
                scope_depth=depth,
                step_tags=all_tags,
                step_data_tags=data_tags,
            )

            # Add regulatory requirements to step_reqs
            for ev in control_evaluations:
                step_reqs.regulatory.extend(ev.requirements)

        # --- Step C: Check journey satisfaction ---
        journey_matches: dict[str, JourneyOutput] = {}
        for req_list in [step_reqs.contextual, step_reqs.data_inputs]:
            for req in req_list:
                if req.tags:
                    prior = self._journey.query_prior_outputs(req.tags)
                    if prior:
                        journey_matches[req.requirement_id] = prior[0]

        # --- Step D: Match remaining against knowledge store ---
        # Build a broad tag set from the node for wider candidate retrieval
        node_all_tags = list(set(
            node.knowledge_tags + node.data_tags + node.context_tags
            + node.decision_tags + node.output_tags
        ))

        ranked_matches: dict[str, list] = {}
        all_requirements = (
            step_reqs.procedures
            + step_reqs.contextual
            + step_reqs.decision_criteria
            + step_reqs.regulatory
        )
        for req in all_requirements:
            if req.requirement_id in journey_matches:
                continue
            # Query with both the requirement's own tags AND the broader node tags
            query_tags = list(set(req.tags + node_all_tags))
            candidates = self._store.query(tags=query_tags)
            if candidates:
                ranked = self._ranker.rank(
                    items=candidates,
                    requirement=req,
                    scope_path=scope_path,
                    scope_depth=depth,
                    node_type=node.node_type,
                )
                ranked_matches[req.requirement_id] = ranked

        # --- Step E: Gap analysis ---
        step_report = self._gap_analyzer.analyze_step(
            step_reqs=step_reqs,
            ranked_matches=ranked_matches,
            journey_matches=journey_matches,
            control_evaluations=control_evaluations,
        )
        step_report.step_number = self._step_number

        # --- Step F: Expand matched procedures ---
        if self._expander:
            for cov in step_report.procedure_coverage:
                if cov.coverage_level in (CoverageLevel.MATCHED, CoverageLevel.PARTIAL):
                    if (cov.matched_knowledge
                            and cov.matched_knowledge[0].knowledge_item.own_requirements):
                        expansion = self._expander.expand(
                            matched_item=cov.matched_knowledge[0].knowledge_item,
                            step_context=step_reqs,
                            knowledge_store=self._store,
                            knowledge_ranker=self._ranker,
                            journey=self._journey,
                            scope_path=scope_path,
                        )
                        step_report.expansions.append(expansion)
                        step_report.total_expanded_requirements += expansion.total_expanded_count

                        # Collect expanded gaps
                        for exp_cov in expansion.expanded_coverage:
                            if exp_cov.coverage_level == CoverageLevel.GAP:
                                step_report.expanded_gaps.append(exp_cov)

        # --- Step G: Record in journey ---
        outputs = self._req_analyzer.infer_outputs(node, scope_path)
        self._journey.record_step(
            node_id=node.id,
            node_name=node.name,
            scope_path=scope_path,
            scope_depth=depth,
            entry_type=JourneyEntryType.TASK_COMPLETED,
            outputs=outputs,
        )

        # --- Step H: Store and emit ---
        self._step_reports.append(step_report)
        prior_nodes.append(node)

        self._emit("step", {
            "report": step_report,
            "depth": depth,
        })

    def _handle_enter_gateway(self, event: WalkerEvent) -> None:
        node = event.node
        if node is None:
            return

        self._step_number += 1
        depth = event.depth
        scope_path = event.scope_path

        # Gateways get requirement analysis too
        scope_key = "/".join(scope_path)
        prior_nodes = self._prior_nodes_by_scope.get(scope_key, [])

        step_reqs = self._req_analyzer.analyze_node(
            node=node,
            scope_path=scope_path,
            scope_depth=depth,
            prior_nodes=prior_nodes,
            journey=self._journey,
        )

        # Journey check for gateway
        journey_matches: dict[str, JourneyOutput] = {}
        for req in step_reqs.decision_criteria:
            if req.tags:
                prior = self._journey.query_prior_outputs(req.tags)
                if prior:
                    journey_matches[req.requirement_id] = prior[0]

        # Knowledge matching
        ranked_matches: dict[str, list] = {}
        for req in step_reqs.procedures + step_reqs.decision_criteria + step_reqs.contextual:
            if req.requirement_id in journey_matches:
                continue
            candidates = self._store.query(tags=req.tags)
            if candidates:
                ranked = self._ranker.rank(
                    items=candidates,
                    requirement=req,
                    scope_path=scope_path,
                    scope_depth=depth,
                    node_type=node.node_type,
                )
                ranked_matches[req.requirement_id] = ranked

        step_report = self._gap_analyzer.analyze_step(
            step_reqs=step_reqs,
            ranked_matches=ranked_matches,
            journey_matches=journey_matches,
        )
        step_report.step_number = self._step_number

        # Record gateway in journey
        from .models import JourneyDecision
        decisions = [JourneyDecision(
            decision_id=f"gw_{node.id}",
            description=f"Gateway evaluation: {node.name}",
            criteria_used=[t for r in step_reqs.decision_criteria for t in r.tags],
            gateway_id=node.id,
        )]
        self._journey.record_step(
            node_id=node.id,
            node_name=node.name,
            scope_path=scope_path,
            scope_depth=depth,
            entry_type=JourneyEntryType.GATEWAY_EVALUATED,
            decisions=decisions,
        )

        self._step_reports.append(step_report)
        prior_nodes.append(node)

        self._emit("gateway", {
            "node_name": node.name,
            "depth": depth,
            "gateway_type": node.node_type.value,
        })

        self._emit("step", {
            "report": step_report,
            "depth": depth,
        })

    def _handle_gateway_path(self, event: WalkerEvent) -> None:
        condition = event.metadata.get("condition", "")
        self._emit("gateway_path", {
            "condition": condition,
            "depth": event.depth,
        })

    # ------------------------------------------------------------------
    # Display emission
    # ------------------------------------------------------------------

    def _emit(self, event_type: str, data: Any) -> None:
        if self._display_cb:
            self._display_cb(event_type, data)
