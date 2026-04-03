"""
Knowledge Orchestrator — Spec Generator.

Converts a ProcessCoverageReport into a serializable dict for JSON export.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .models import (
    ComplianceStatus,
    ControlEvaluation,
    CoverageLevel,
    ExpansionResult,
    ProcessCoverageReport,
    RequirementCoverage,
    RequirementItem,
    ScopeCoverageSummary,
    StepCoverageReport,
    StepReadiness,
)


class SpecGenerator:

    # ------------------------------------------------------------------
    # JSON export
    # ------------------------------------------------------------------

    def generate_json_report(self, report: ProcessCoverageReport) -> dict:
        return {
            "spec_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "process": {
                "name": report.process_name,
                "total_steps_analyzed": report.total_steps_analyzed,
                "total_requirements": report.total_requirements,
                "overall_readiness": self._readiness_dict(report.overall_readiness),
            },
            "summary": {
                "total_matched": report.total_matched,
                "total_partial": report.total_partial,
                "total_gaps": report.total_gaps,
                "total_journey_satisfied": report.total_journey_satisfied,
                "critical_gaps": [
                    self._coverage_dict(c) for c in report.critical_gaps
                ],
                "scope_summaries": [
                    self._scope_summary_dict(s) for s in report.scope_summaries
                ],
            },
            "compliance": self._compliance_dict(report),
            "journey": self._journey_dict(report),
            "steps": [
                self._step_dict(s) for s in report.step_reports
            ],
        }

    def export_json(self, report: ProcessCoverageReport, output_path: str) -> None:
        data = self.generate_json_report(report)
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    # ------------------------------------------------------------------
    # Internal serializers
    # ------------------------------------------------------------------

    def _readiness_dict(self, r: StepReadiness) -> dict:
        return {
            "knowledge_readiness": r.knowledge_readiness,
            "compliance_readiness": r.compliance_readiness,
            "combined_readiness": r.combined_readiness,
        }

    def _requirement_dict(self, req: RequirementItem) -> dict:
        return {
            "requirement_id": req.requirement_id,
            "description": req.description,
            "category": req.category.value,
            "tags": req.tags,
            "priority": req.priority.value,
            "source": req.source,
            "rationale": req.rationale,
        }

    def _coverage_dict(self, cov: RequirementCoverage) -> dict:
        d: dict = {
            "requirement": self._requirement_dict(cov.requirement),
            "coverage_level": cov.coverage_level.value,
            "coverage_notes": cov.coverage_notes,
        }
        if cov.matched_knowledge:
            d["matched_knowledge"] = [
                {
                    "item_id": ks.knowledge_item.id,
                    "item_title": ks.knowledge_item.title,
                    "total_score": ks.total_score,
                    "match_explanation": ks.match_explanation,
                }
                for ks in cov.matched_knowledge[:3]  # top 3
            ]
        if cov.journey_source:
            d["journey_source"] = {
                "output_id": cov.journey_source.output_id,
                "description": cov.journey_source.description,
                "produced_at_step": cov.journey_source.produced_at_step,
                "produced_by_node": cov.journey_source.produced_by_node,
            }
        if cov.gap_description:
            d["gap_description"] = cov.gap_description
        return d

    def _scope_summary_dict(self, s: ScopeCoverageSummary) -> dict:
        return {
            "scope_name": s.scope_name,
            "scope_level": s.scope_level,
            "total_requirements": s.total_requirements,
            "matched": s.matched,
            "partial": s.partial,
            "gaps": s.gaps,
            "journey_satisfied": s.journey_satisfied,
            "readiness": self._readiness_dict(s.readiness),
        }

    def _expansion_dict(self, exp: ExpansionResult) -> dict:
        d: dict = {
            "source_item": exp.source_item.id if exp.source_item else None,
            "source_title": exp.source_item.title if exp.source_item else None,
            "depth": exp.expansion_depth,
            "total_expanded_count": exp.total_expanded_count,
            "expanded_requirements": [
                self._requirement_dict(r) for r in exp.expanded_requirements
            ],
            "expanded_coverage": [
                self._coverage_dict(c) for c in exp.expanded_coverage
            ],
        }
        if exp.sub_expansions:
            d["sub_expansions"] = [
                self._expansion_dict(s) for s in exp.sub_expansions
            ]
        return d

    def _control_eval_dict(self, ev: ControlEvaluation) -> dict:
        return {
            "control_id": ev.control.control_id,
            "title": ev.control.title,
            "framework_id": ev.framework.id,
            "framework_name": ev.framework.name,
            "severity": ev.control.severity.value,
            "compliance_status": ev.compliance_status.value,
            "triggered_by": [
                {
                    "type": t.trigger_type.value,
                    "values": t.trigger_values,
                    "match_mode": t.match_mode,
                }
                for t in ev.triggered_by
            ],
            "requirements": [self._requirement_dict(r) for r in ev.requirements],
            "evidence_needed": ev.evidence_needed,
        }

    def _step_dict(self, step: StepCoverageReport) -> dict:
        sr = step.step_requirements
        d: dict = {
            "step_number": step.step_number,
            "node_id": sr.node_id if sr else "",
            "node_name": sr.node_name if sr else "",
            "node_type": sr.node_type.value if sr else "",
            "scope_path": sr.scope_path if sr else [],
            "scope_depth": sr.scope_depth if sr else 0,
            "total_requirements": step.total_requirements,
            "matched_count": step.matched_count,
            "partial_count": step.partial_count,
            "gap_count": step.gap_count,
            "journey_satisfied_count": step.journey_satisfied_count,
            "readiness": self._readiness_dict(step.readiness),
            "coverage": {
                "procedures": [self._coverage_dict(c) for c in step.procedure_coverage],
                "data_inputs": [self._coverage_dict(c) for c in step.data_coverage],
                "contextual": [self._coverage_dict(c) for c in step.context_coverage],
                "decision_criteria": [self._coverage_dict(c) for c in step.decision_coverage],
                "regulatory": [self._coverage_dict(c) for c in step.regulatory_requirements],
            },
        }

        if step.control_evaluations:
            d["regulatory_controls"] = [
                self._control_eval_dict(ev) for ev in step.control_evaluations
            ]

        if step.expansions:
            d["expansions"] = [
                self._expansion_dict(exp) for exp in step.expansions
            ]

        return d

    def _compliance_dict(self, report: ProcessCoverageReport) -> dict:
        cs = report.compliance_summary
        return {
            "frameworks_evaluated": cs.frameworks_evaluated,
            "total_controls_triggered": cs.total_controls_triggered,
            "total_compliant": cs.total_compliant,
            "total_partially_compliant": cs.total_partially_compliant,
            "total_non_compliant": cs.total_non_compliant,
            "by_framework": {
                fw_id: {
                    "name": fc.framework_name,
                    "controls_triggered": fc.controls_triggered,
                    "compliant": fc.compliant,
                    "partially_compliant": fc.partially_compliant,
                    "non_compliant": fc.non_compliant,
                    "compliance_percentage": fc.compliance_percentage,
                }
                for fw_id, fc in cs.compliance_by_framework.items()
            },
            "critical_violations": [
                self._control_eval_dict(ev) for ev in cs.critical_violations
            ],
        }

    def _journey_dict(self, report: ProcessCoverageReport) -> dict:
        js = report.journey_summary
        return {
            "total_steps": js.total_steps,
            "scopes_visited": js.scopes_visited,
            "decisions_made": js.decisions_made,
            "outputs_produced": js.outputs_produced,
            "state_attributes_tracked": js.state_attributes_tracked,
        }
