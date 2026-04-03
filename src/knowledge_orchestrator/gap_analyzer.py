"""
Knowledge Orchestrator — Gap Analyzer.

Compares inferred requirements against ranked knowledge matches and journey
context to produce coverage assessments: MATCHED, PARTIAL, GAP, JOURNEY_SATISFIED.
Computes readiness scores at step, scope, and process levels.
"""

from __future__ import annotations

from .models import (
    ComplianceStatus,
    ComplianceSummary,
    ControlEvaluation,
    CoverageLevel,
    FrameworkCompliance,
    JourneyOutput,
    KnowledgeScore,
    ProcessCoverageReport,
    RequirementCategory,
    RequirementCoverage,
    RequirementItem,
    RequirementPriority,
    ScopeCoverageSummary,
    StepCoverageReport,
    StepReadiness,
    StepRequirements,
)


class GapAnalyzer:

    def __init__(
        self,
        match_threshold: float = 0.70,
        partial_threshold: float = 0.40,
    ) -> None:
        self._match_threshold = match_threshold
        self._partial_threshold = partial_threshold

    def analyze_step(
        self,
        step_reqs: StepRequirements,
        ranked_matches: dict[str, list[KnowledgeScore]],
        journey_matches: dict[str, JourneyOutput] | None = None,
        control_evaluations: list[ControlEvaluation] | None = None,
    ) -> StepCoverageReport:
        journey_matches = journey_matches or {}
        control_evaluations = control_evaluations or []

        procedure_cov = self._assess_category(step_reqs.procedures, ranked_matches, journey_matches)
        data_cov = self._assess_category(step_reqs.data_inputs, ranked_matches, journey_matches, is_data=True)
        context_cov = self._assess_category(step_reqs.contextual, ranked_matches, journey_matches)
        decision_cov = self._assess_category(step_reqs.decision_criteria, ranked_matches, journey_matches)
        regulatory_cov = self._assess_category(step_reqs.regulatory, ranked_matches, journey_matches)

        # Update compliance status on control evaluations
        self._update_compliance_status(control_evaluations, regulatory_cov)

        all_coverages = procedure_cov + context_cov + decision_cov + regulatory_cov
        # Data is NOT_ASSESSED so excluded from counts
        matched = sum(1 for c in all_coverages if c.coverage_level == CoverageLevel.MATCHED)
        partial = sum(1 for c in all_coverages if c.coverage_level == CoverageLevel.PARTIAL)
        gap = sum(1 for c in all_coverages if c.coverage_level == CoverageLevel.GAP)
        journey = sum(1 for c in all_coverages if c.coverage_level == CoverageLevel.JOURNEY_SATISFIED)
        total = matched + partial + gap + journey

        knowledge_readiness = (matched + journey + partial * 0.5) / total if total else 0.0

        # Compliance readiness: based only on regulatory requirements
        reg_assessable = [c for c in regulatory_cov if c.coverage_level != CoverageLevel.NOT_ASSESSED]
        reg_matched = sum(1 for c in reg_assessable if c.coverage_level in (CoverageLevel.MATCHED, CoverageLevel.JOURNEY_SATISFIED))
        reg_total = len(reg_assessable)
        compliance_readiness = reg_matched / reg_total if reg_total else 1.0

        combined = knowledge_readiness * 0.4 + compliance_readiness * 0.6

        return StepCoverageReport(
            step_requirements=step_reqs,
            procedure_coverage=procedure_cov,
            data_coverage=data_cov,
            context_coverage=context_cov,
            decision_coverage=decision_cov,
            regulatory_requirements=regulatory_cov,
            control_evaluations=control_evaluations,
            total_requirements=total,
            matched_count=matched,
            partial_count=partial,
            gap_count=gap,
            journey_satisfied_count=journey,
            readiness=StepReadiness(
                knowledge_readiness=round(knowledge_readiness, 4),
                compliance_readiness=round(compliance_readiness, 4),
                combined_readiness=round(combined, 4),
            ),
        )

    def analyze_process(
        self,
        step_reports: list[StepCoverageReport],
        process_name: str,
    ) -> ProcessCoverageReport:
        total_reqs = sum(r.total_requirements for r in step_reports)
        total_matched = sum(r.matched_count for r in step_reports)
        total_partial = sum(r.partial_count for r in step_reports)
        total_gaps = sum(r.gap_count for r in step_reports)
        total_journey = sum(r.journey_satisfied_count for r in step_reports)

        if total_reqs > 0:
            kr = (total_matched + total_journey + total_partial * 0.5) / total_reqs
        else:
            kr = 0.0

        # Build compliance summary from all control evaluations
        compliance_summary = self._build_compliance_summary(step_reports)

        # Overall compliance readiness
        cs = compliance_summary
        reg_total = cs.total_controls_triggered
        if reg_total > 0:
            cr = cs.total_compliant / reg_total
        else:
            cr = 1.0

        combined = kr * 0.4 + cr * 0.6

        # Collect critical gaps
        critical_gaps: list[RequirementCoverage] = []
        for report in step_reports:
            for cov_list in [report.procedure_coverage, report.context_coverage,
                             report.decision_coverage, report.regulatory_requirements]:
                for cov in cov_list:
                    if (cov.coverage_level == CoverageLevel.GAP
                            and cov.requirement.priority == RequirementPriority.CRITICAL):
                        critical_gaps.append(cov)

        # Build scope summaries
        scope_summaries = self._build_scope_summaries(step_reports)

        return ProcessCoverageReport(
            process_name=process_name,
            total_steps_analyzed=len(step_reports),
            total_requirements=total_reqs,
            total_matched=total_matched,
            total_partial=total_partial,
            total_gaps=total_gaps,
            total_journey_satisfied=total_journey,
            overall_readiness=StepReadiness(
                knowledge_readiness=round(kr, 4),
                compliance_readiness=round(cr, 4),
                combined_readiness=round(combined, 4),
            ),
            critical_gaps=critical_gaps,
            scope_summaries=scope_summaries,
            compliance_summary=compliance_summary,
            step_reports=step_reports,
        )

    # --- Internal helpers ---

    def _assess_category(
        self,
        requirements: list[RequirementItem],
        ranked_matches: dict[str, list[KnowledgeScore]],
        journey_matches: dict[str, JourneyOutput],
        is_data: bool = False,
    ) -> list[RequirementCoverage]:
        coverages: list[RequirementCoverage] = []

        for req in requirements:
            # Check journey first
            journey_source = journey_matches.get(req.requirement_id)
            if journey_source:
                coverages.append(RequirementCoverage(
                    requirement=req,
                    coverage_level=CoverageLevel.JOURNEY_SATISFIED,
                    journey_source=journey_source,
                    coverage_notes=f"Satisfied by Step {journey_source.produced_at_step} ({journey_source.produced_by_node})",
                ))
                continue

            # Data requirements are not assessed against knowledge store
            if is_data:
                coverages.append(RequirementCoverage(
                    requirement=req,
                    coverage_level=CoverageLevel.NOT_ASSESSED,
                    coverage_notes="Data requirement — assessed at runtime, not in knowledge store",
                ))
                continue

            # Check knowledge store matches
            matches = ranked_matches.get(req.requirement_id, [])
            if matches:
                best_score = matches[0].total_score
                if best_score >= self._match_threshold:
                    level = CoverageLevel.MATCHED
                elif best_score >= self._partial_threshold:
                    level = CoverageLevel.PARTIAL
                else:
                    level = CoverageLevel.GAP
            else:
                best_score = 0.0
                level = CoverageLevel.GAP

            gap_desc = None
            if level == CoverageLevel.GAP:
                gap_desc = self._generate_gap_description(req)

            coverages.append(RequirementCoverage(
                requirement=req,
                coverage_level=level,
                matched_knowledge=matches if matches else None,
                coverage_notes=f"Best score: {best_score:.2f}" if matches else "No matches found",
                gap_description=gap_desc,
            ))

        return coverages

    def _generate_gap_description(self, requirement: RequirementItem) -> str:
        tag_str = ", ".join(requirement.tags[:3]) if requirement.tags else "untagged"
        return (
            f"No matching knowledge found for: '{requirement.description}'. "
            f"Tags: [{tag_str}]. "
            f"Recommended: Create a {requirement.category.value} covering this area."
        )

    def _update_compliance_status(
        self,
        evaluations: list[ControlEvaluation],
        regulatory_coverage: list[RequirementCoverage],
    ) -> None:
        # Group coverage by source control
        for evaluation in evaluations:
            control_req_ids = {r.requirement_id for r in evaluation.requirements}
            relevant = [c for c in regulatory_coverage if c.requirement.requirement_id in control_req_ids]

            if not relevant:
                evaluation.compliance_status = ComplianceStatus.NOT_ASSESSED
                continue

            mandatory_reqs = [c for c in relevant if c.requirement.priority == RequirementPriority.CRITICAL]
            if not mandatory_reqs:
                mandatory_reqs = relevant

            all_met = all(c.coverage_level in (CoverageLevel.MATCHED, CoverageLevel.JOURNEY_SATISFIED)
                         for c in mandatory_reqs)
            any_met = any(c.coverage_level in (CoverageLevel.MATCHED, CoverageLevel.JOURNEY_SATISFIED)
                         for c in mandatory_reqs)

            if all_met:
                evaluation.compliance_status = ComplianceStatus.COMPLIANT
            elif any_met:
                evaluation.compliance_status = ComplianceStatus.PARTIALLY_COMPLIANT
            else:
                evaluation.compliance_status = ComplianceStatus.NON_COMPLIANT

    def _build_compliance_summary(self, step_reports: list[StepCoverageReport]) -> ComplianceSummary:
        by_framework: dict[str, FrameworkCompliance] = {}
        all_evaluations: list[ControlEvaluation] = []
        critical_violations: list[ControlEvaluation] = []

        for report in step_reports:
            for ev in report.control_evaluations:
                all_evaluations.append(ev)
                fw_id = ev.framework.id
                fw_name = ev.framework.name

                if fw_id not in by_framework:
                    by_framework[fw_id] = FrameworkCompliance(
                        framework_id=fw_id, framework_name=fw_name)

                fc = by_framework[fw_id]
                fc.controls_triggered += 1

                match ev.compliance_status:
                    case ComplianceStatus.COMPLIANT:
                        fc.compliant += 1
                    case ComplianceStatus.PARTIALLY_COMPLIANT:
                        fc.partially_compliant += 1
                    case ComplianceStatus.NON_COMPLIANT:
                        fc.non_compliant += 1
                        fc.non_compliant_controls.append(ev)
                        if ev.control.severity.value == "mandatory":
                            critical_violations.append(ev)

        for fc in by_framework.values():
            total = fc.controls_triggered
            fc.compliance_percentage = round(fc.compliant / total * 100, 1) if total else 0.0

        return ComplianceSummary(
            frameworks_evaluated=list(by_framework.keys()),
            total_controls_triggered=len(all_evaluations),
            total_compliant=sum(fc.compliant for fc in by_framework.values()),
            total_partially_compliant=sum(fc.partially_compliant for fc in by_framework.values()),
            total_non_compliant=sum(fc.non_compliant for fc in by_framework.values()),
            compliance_by_framework=by_framework,
            critical_violations=critical_violations,
        )

    def _build_scope_summaries(self, step_reports: list[StepCoverageReport]) -> list[ScopeCoverageSummary]:
        by_scope: dict[str, list[StepCoverageReport]] = {}

        for report in step_reports:
            if report.step_requirements and report.step_requirements.scope_path:
                # Use the L1 scope (first subprocess) for grouping
                scope_key = report.step_requirements.scope_path[1] if len(report.step_requirements.scope_path) > 1 else report.step_requirements.scope_path[0]
                by_scope.setdefault(scope_key, []).append(report)

        summaries: list[ScopeCoverageSummary] = []
        for scope_name, reports in by_scope.items():
            total = sum(r.total_requirements for r in reports)
            matched = sum(r.matched_count for r in reports)
            partial = sum(r.partial_count for r in reports)
            gaps = sum(r.gap_count for r in reports)
            journey = sum(r.journey_satisfied_count for r in reports)
            kr = (matched + journey + partial * 0.5) / total if total else 0.0

            summaries.append(ScopeCoverageSummary(
                scope_name=scope_name,
                total_requirements=total,
                matched=matched,
                partial=partial,
                gaps=gaps,
                journey_satisfied=journey,
                readiness=StepReadiness(knowledge_readiness=round(kr, 4)),
            ))

        return summaries
