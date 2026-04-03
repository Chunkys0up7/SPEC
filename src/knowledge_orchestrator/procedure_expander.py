"""
Knowledge Orchestrator — Procedure Expander.

Recursive expansion engine. When a matched procedure declares its own requirements
(regulatory compliance, sub-procedures, data dependencies), this component cascades
them into the step's requirement set. Depth-limited and cycle-aware to prevent
infinite expansion.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from .models import (
    CoverageLevel,
    ExpansionResult,
    KnowledgeItem,
    KnowledgeRequirement,
    KnowledgeRequirementType,
    KnowledgeScore,
    RequirementCategory,
    RequirementCoverage,
    RequirementItem,
    RequirementPriority,
    StepRequirements,
)

if TYPE_CHECKING:
    from .journey_context import JourneyContext
    from .knowledge_ranker import KnowledgeRanker
    from .knowledge_store import KnowledgeStore


# ---------------------------------------------------------------------------
# Requirement type → RequirementCategory mapping
# ---------------------------------------------------------------------------

_TYPE_TO_CATEGORY: dict[str, RequirementCategory] = {
    "regulatory": RequirementCategory.REGULATORY,
    "approval": RequirementCategory.PROCEDURE,
    "data": RequirementCategory.DATA,
    "sub-procedure": RequirementCategory.PROCEDURE,
    "procedure": RequirementCategory.PROCEDURE,
    "compliance": RequirementCategory.REGULATORY,
    "certification": RequirementCategory.REGULATORY,
}


def _make_id() -> str:
    return f"exp_{uuid.uuid4().hex[:8]}"


class ProcedureExpander:

    def __init__(self, max_depth: int = 3) -> None:
        self._max_depth = max_depth

    def expand(
        self,
        matched_item: KnowledgeItem,
        step_context: StepRequirements,
        knowledge_store: KnowledgeStore,
        knowledge_ranker: KnowledgeRanker,
        journey: JourneyContext | None = None,
        scope_path: list[str] | None = None,
        depth: int = 0,
        _visited: set[str] | None = None,
    ) -> ExpansionResult:
        scope_path = scope_path or []
        visited = _visited if _visited is not None else set()

        # Depth limit
        if depth >= self._max_depth:
            return ExpansionResult(
                source_item=matched_item,
                expansion_depth=depth,
            )

        # Cycle detection
        if matched_item.id in visited:
            return ExpansionResult(
                source_item=matched_item,
                expansion_depth=depth,
            )

        visited.add(matched_item.id)

        expanded_requirements: list[RequirementItem] = []
        expanded_coverage: list[RequirementCoverage] = []
        sub_expansions: list[ExpansionResult] = []

        for own_req in matched_item.own_requirements:
            req_item = self._convert_requirement(own_req, matched_item)
            expanded_requirements.append(req_item)

            # Check journey first
            journey_source = None
            if journey and req_item.tags:
                prior_outputs = journey.query_prior_outputs(req_item.tags)
                if prior_outputs:
                    journey_source = prior_outputs[0]

            if journey_source:
                expanded_coverage.append(RequirementCoverage(
                    requirement=req_item,
                    coverage_level=CoverageLevel.JOURNEY_SATISFIED,
                    journey_source=journey_source,
                    coverage_notes=(
                        f"Satisfied by Step {journey_source.produced_at_step} "
                        f"({journey_source.produced_by_node})"
                    ),
                ))
                continue

            # Check knowledge store
            candidates = knowledge_store.query(
                tags=req_item.tags,
                scope=scope_path[-1] if scope_path else None,
            )

            if candidates:
                ranked: list[KnowledgeScore] = knowledge_ranker.rank(
                    items=candidates,
                    requirement=req_item,
                    scope_path=scope_path,
                    scope_depth=len(scope_path),
                    node_type=step_context.node_type,
                )
            else:
                ranked = []

            if ranked:
                best = ranked[0].total_score
                if best >= 0.70:
                    level = CoverageLevel.MATCHED
                elif best >= 0.40:
                    level = CoverageLevel.PARTIAL
                else:
                    level = CoverageLevel.GAP
            else:
                best = 0.0
                level = CoverageLevel.GAP

            gap_desc = None
            if level == CoverageLevel.GAP:
                tag_str = ", ".join(req_item.tags[:3]) if req_item.tags else "untagged"
                gap_desc = (
                    f"No matching knowledge for expanded requirement: "
                    f"'{req_item.description}'. Tags: [{tag_str}]. "
                    f"Source: {matched_item.title}"
                )

            expanded_coverage.append(RequirementCoverage(
                requirement=req_item,
                coverage_level=level,
                matched_knowledge=ranked if ranked else None,
                coverage_notes=f"Best score: {best:.2f}" if ranked else "No matches found",
                gap_description=gap_desc,
            ))

            # Recurse if matched and the matched item also has own_requirements
            if level == CoverageLevel.MATCHED and ranked and depth + 1 < self._max_depth:
                sub_item = ranked[0].knowledge_item
                if sub_item.own_requirements:
                    sub_result = self.expand(
                        matched_item=sub_item,
                        step_context=step_context,
                        knowledge_store=knowledge_store,
                        knowledge_ranker=knowledge_ranker,
                        journey=journey,
                        scope_path=scope_path,
                        depth=depth + 1,
                        _visited=visited,
                    )
                    sub_expansions.append(sub_result)

        # Remove from visited to allow re-expansion in different chains
        visited.discard(matched_item.id)

        total_count = len(expanded_requirements)
        for sub in sub_expansions:
            total_count += sub.total_expanded_count

        return ExpansionResult(
            source_item=matched_item,
            expanded_requirements=expanded_requirements,
            expanded_coverage=expanded_coverage,
            sub_expansions=sub_expansions,
            expansion_depth=depth,
            total_expanded_count=total_count,
        )

    def _convert_requirement(
        self,
        own_req: KnowledgeRequirement,
        source_item: KnowledgeItem,
    ) -> RequirementItem:
        category = _TYPE_TO_CATEGORY.get(
            own_req.requirement_type, RequirementCategory.PROCEDURE
        )
        priority = own_req.priority
        if own_req.mandatory:
            priority = RequirementPriority.CRITICAL

        return RequirementItem(
            requirement_id=_make_id(),
            description=own_req.description,
            category=category,
            tags=list(own_req.tags),
            priority=priority,
            source=f"expanded from {source_item.title}",
            rationale=(
                f"Requirement declared by procedure '{source_item.title}'"
                + (f" (framework: {own_req.regulatory_framework})"
                   if own_req.regulatory_framework else "")
            ),
        )
