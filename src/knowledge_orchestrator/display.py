"""
Knowledge Orchestrator — Console Display.

Real-time console output as the orchestrator walks the process. Shows step-by-step
analysis with visual hierarchy matching subprocess nesting. Tree characters, level
markers, and coverage indicators provide at-a-glance status.
"""

from __future__ import annotations

import sys
from typing import Any

from .models import (
    CoverageLevel,
    ExpansionResult,
    ProcessCoverageReport,
    RequirementCoverage,
    RequirementPriority,
    ScopeCoverageSummary,
    StepCoverageReport,
    StepReadiness,
)


# ---------------------------------------------------------------------------
# Coverage indicators
# ---------------------------------------------------------------------------

def _safe_print(*args: object, **kwargs: object) -> None:
    """Print with fallback encoding for Windows terminals."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        text = " ".join(str(a) for a in args)
        safe = text.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(
            sys.stdout.encoding or "utf-8", errors="replace"
        )
        print(safe, **kwargs)  # type: ignore[arg-type]


_COVERAGE_ICON: dict[CoverageLevel, str] = {
    CoverageLevel.MATCHED: "[OK] MATCHED",
    CoverageLevel.PARTIAL: "[~] PARTIAL",
    CoverageLevel.GAP: "[X] GAP",
    CoverageLevel.JOURNEY_SATISFIED: "[J] JOURNEY",
    CoverageLevel.NOT_ASSESSED: "[-] N/A",
}

_PRIORITY_LABEL: dict[RequirementPriority, str] = {
    RequirementPriority.CRITICAL: "CRITICAL",
    RequirementPriority.IMPORTANT: "IMPORTANT",
    RequirementPriority.HELPFUL: "HELPFUL",
}


class ConsoleDisplay:

    def __init__(self, verbose: bool = False) -> None:
        self._verbose = verbose
        self._step_count = 0

    # ------------------------------------------------------------------
    # Callback entry point — used by orchestrator.register_display()
    # ------------------------------------------------------------------

    def on_event(self, event_type: str, data: Any) -> None:
        match event_type:
            case "header":
                self.display_header(**data)
            case "scope_enter":
                self.display_scope_enter(**data)
            case "scope_exit":
                self.display_scope_exit(**data)
            case "step":
                self.display_step(**data)
            case "gateway":
                self.display_gateway(**data)
            case "gateway_path":
                self.display_gateway_path(**data)

    # ------------------------------------------------------------------
    # Display methods
    # ------------------------------------------------------------------

    def display_header(
        self,
        process_name: str,
        node_count: int,
        depth: int,
        knowledge_count: int,
        regulatory_count: int = 0,
    ) -> None:
        sep = "=" * 65
        print()
        print(sep)
        print("  KNOWLEDGE REQUIREMENTS SPECIFICATION")
        print(f"  Process: {process_name}")
        print(f"  Nodes: {node_count} | Max Depth: {depth} | Knowledge: {knowledge_count} items"
              + (f" | Regulatory: {regulatory_count} frameworks" if regulatory_count else ""))
        print(sep)
        print()

    def display_scope_enter(
        self,
        scope_name: str,
        depth: int,
        domain: str = "",
        preloaded_count: int = 0,
    ) -> None:
        indent = "  " * depth
        level = f"[L{depth}]"
        print(f"{indent}{level} > SCOPE ENTER: {scope_name}")
        if domain:
            print(f"{indent}       Domain: {domain}")
        if preloaded_count:
            print(f"{indent}       Scope Knowledge: {preloaded_count} items pre-loaded")
        print()

    def display_scope_exit(
        self,
        scope_name: str,
        depth: int,
        summary: ScopeCoverageSummary | None = None,
    ) -> None:
        indent = "  " * depth
        level = f"[L{depth}]"
        if summary:
            total = summary.total_requirements
            readiness = summary.readiness.knowledge_readiness
            print(f"{indent}{level} < SCOPE EXIT: {scope_name}"
                  f" | {total} reqs | Readiness: {readiness:.0%}")
        else:
            print(f"{indent}{level} < SCOPE EXIT: {scope_name}")
        print()

    def display_step(
        self,
        report: StepCoverageReport,
        depth: int,
    ) -> None:
        self._step_count += 1
        sr = report.step_requirements
        if not sr:
            return

        indent = "  " * depth
        level = f"[L{depth}]"
        node_type_label = sr.node_type.value.upper().replace("_", " ")
        step_num = report.step_number or self._step_count

        print(f"{indent}{level} {node_type_label}: {sr.node_name} (Step {step_num})")
        print(f"{indent}     Scope: {' > '.join(sr.scope_path)}")

        # Requirements by category
        categories = [
            ("Procedures", report.procedure_coverage),
            ("Data Inputs", report.data_coverage),
            ("Context", report.context_coverage),
            ("Decisions", report.decision_coverage),
            ("Regulatory", report.regulatory_requirements),
        ]

        has_any = False
        for cat_name, coverages in categories:
            if not coverages:
                continue
            has_any = True
            print(f"{indent}     |- {cat_name}:")
            for cov in coverages:
                self._print_coverage(cov, depth + 3)

        # Expansions
        if report.expansions:
            print(f"{indent}     |- Procedure Expansions:")
            for exp in report.expansions:
                self._print_expansion(exp, depth + 3)

        # Regulatory controls
        if report.control_evaluations and self._verbose:
            print(f"{indent}     |- Regulatory Controls:")
            for ev in report.control_evaluations:
                icon = "[REG] REGULATORY"
                print(f"{indent}         | {icon} [{ev.framework.name}] "
                      f"{ev.control.title} ({ev.control.severity.value})")
                print(f"{indent}         |   Status: {ev.compliance_status.value}")

        # Readiness
        r = report.readiness
        if has_any:
            print(f"{indent}     `- Readiness: [{r.combined_readiness:.2f}]"
                  f" (knowledge: {r.knowledge_readiness:.2f}"
                  f" | compliance: {r.compliance_readiness:.2f})")

        print()

    def display_gateway(
        self,
        node_name: str,
        depth: int,
        gateway_type: str = "",
    ) -> None:
        indent = "  " * depth
        level = f"[L{depth}]"
        gw_label = gateway_type.upper().replace("_", " ") if gateway_type else "GATEWAY"
        print(f"{indent}{level} * {gw_label}: {node_name}")

    def display_gateway_path(
        self,
        condition: str,
        depth: int,
    ) -> None:
        indent = "  " * depth
        label = condition if condition else "(default)"
        print(f"{indent}     |-> Path: {label}")

    def display_summary(self, report: ProcessCoverageReport) -> None:
        sep = "=" * 65
        print()
        print(sep)
        print("  SUMMARY")
        print(sep)
        print()

        r = report.overall_readiness
        total = report.total_requirements
        print(f"  Process: {report.process_name}")
        print(f"  Steps Analyzed: {report.total_steps_analyzed}")
        print(f"  Total Requirements: {total}")
        print(f"  Matched: {report.total_matched} | Partial: {report.total_partial}"
              f" | Gaps: {report.total_gaps} | Journey: {report.total_journey_satisfied}")
        print(f"  Overall Readiness: [{r.combined_readiness:.2f}]"
              f" (knowledge: {r.knowledge_readiness:.2f}"
              f" | compliance: {r.compliance_readiness:.2f})")
        print()

        # Scope summaries
        if report.scope_summaries:
            print("  By Scope:")
            for ss in report.scope_summaries:
                kr = ss.readiness.knowledge_readiness
                print(f"    {ss.scope_name}: {ss.total_requirements} reqs"
                      f" | M:{ss.matched} P:{ss.partial} G:{ss.gaps} J:{ss.journey_satisfied}"
                      f" | Readiness: {kr:.0%}")
            print()

        # Critical gaps
        if report.critical_gaps:
            print(f"  Critical Gaps ({len(report.critical_gaps)}):")
            for i, cov in enumerate(report.critical_gaps[:10], 1):
                scope_str = ""
                if cov.requirement.source:
                    scope_str = f" [{cov.requirement.source}]"
                print(f"    {i}. {cov.requirement.description}{scope_str}")
                if cov.gap_description:
                    print(f"       {cov.gap_description}")
            print()

        # Compliance
        cs = report.compliance_summary
        if cs.frameworks_evaluated:
            print("  Compliance:")
            print(f"    Frameworks: {len(cs.frameworks_evaluated)}"
                  f" | Controls Triggered: {cs.total_controls_triggered}"
                  f" | Compliant: {cs.total_compliant}"
                  f" | Non-compliant: {cs.total_non_compliant}")
            for fw_id, fc in cs.compliance_by_framework.items():
                print(f"    {fc.framework_name}: {fc.compliance_percentage:.0f}% compliant"
                      f" ({fc.compliant}/{fc.controls_triggered})")
            if cs.critical_violations:
                print(f"    Critical Violations: {len(cs.critical_violations)}")
                for ev in cs.critical_violations[:5]:
                    print(f"      - [{ev.framework.name}] {ev.control.title}")
            print()

        # Journey summary
        js = report.journey_summary
        if js.total_steps > 0:
            print("  Journey:")
            print(f"    Steps: {js.total_steps} | Outputs: {js.outputs_produced}"
                  f" | Decisions: {js.decisions_made}"
                  f" | State Attrs: {js.state_attributes_tracked}")
            if js.scopes_visited:
                print(f"    Scopes: {' > '.join(js.scopes_visited[:6])}"
                      + (" ..." if len(js.scopes_visited) > 6 else ""))
            print()

        print(sep)
        print()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _print_coverage(self, cov: RequirementCoverage, depth: int) -> None:
        indent = "  " * depth
        icon = _COVERAGE_ICON.get(cov.coverage_level, "?")
        pri = _PRIORITY_LABEL.get(cov.requirement.priority, "")
        desc = cov.requirement.description

        # Truncate long descriptions
        if len(desc) > 60:
            desc = desc[:57] + "..."

        print(f"{indent}| [{pri}] {desc}")
        print(f"{indent}|   {icon}", end="")

        if cov.matched_knowledge and cov.coverage_level in (
            CoverageLevel.MATCHED, CoverageLevel.PARTIAL
        ):
            best = cov.matched_knowledge[0]
            print(f" [{best.total_score:.2f}] {best.knowledge_item.title}")
        elif cov.journey_source:
            print(f" (Step {cov.journey_source.produced_at_step})")
        else:
            print()

        if self._verbose and cov.gap_description:
            print(f"{indent}|   {cov.gap_description}")

    def _print_expansion(self, exp: ExpansionResult, depth: int) -> None:
        indent = "  " * depth
        source_title = exp.source_item.title if exp.source_item else "?"
        print(f"{indent}| Expanded from: {source_title}"
              f" ({exp.total_expanded_count} sub-requirements)")

        for cov in exp.expanded_coverage:
            self._print_coverage(cov, depth + 1)

        for sub in exp.sub_expansions:
            self._print_expansion(sub, depth + 1)
