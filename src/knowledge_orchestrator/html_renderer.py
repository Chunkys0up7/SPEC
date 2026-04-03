"""
Knowledge Orchestrator -- HTML Renderer.

Generates a self-contained HTML file (inline CSS + inline JS, zero external
dependencies) from a ProcessCoverageReport.  Opens in any modern browser.
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
    JourneySummary,
    ProcessCoverageReport,
    RequirementCoverage,
    RequirementCategory,
    RequirementPriority,
    ScopeCoverageSummary,
    StepCoverageReport,
    StepReadiness,
)
from .spec_generator import SpecGenerator


class HTMLRenderer:
    """Render a ProcessCoverageReport as a self-contained HTML document."""

    # Scope-depth colors for left borders
    _DEPTH_COLORS = ["#2980b9", "#27ae60", "#e67e22", "#c0392b"]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(
        self,
        report: ProcessCoverageReport,
        journey_summary: JourneySummary | None = None,
    ) -> str:
        """Return a complete HTML string for *report*."""
        spec_gen = SpecGenerator()
        json_data = json.dumps(
            spec_gen.generate_json_report(report), indent=2, default=str
        )
        generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        parts: list[str] = []
        parts.append(self._head(report, generated))
        parts.append('<body>\n<div class="container">\n')
        parts.append(self._header(report, generated))
        parts.append(self._legend())
        parts.append(self._controls())
        parts.append(self._process_map(report))
        parts.append(self._step_cards(report, journey_summary))
        parts.append(self._summary_section(report, journey_summary))
        parts.append(self._embedded_json(json_data))
        parts.append("</div>\n")
        parts.append(self._script())
        parts.append("</body>\n</html>")
        return "\n".join(parts)

    def export_html(
        self,
        report: ProcessCoverageReport,
        journey_summary: JourneySummary | None = None,
        output_path: str = "spec_report.html",
    ) -> None:
        """Write the rendered HTML to *output_path*."""
        html = self.render(report, journey_summary)
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _esc(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    def _depth_color(self, depth: int) -> str:
        return self._DEPTH_COLORS[min(depth, len(self._DEPTH_COLORS) - 1)]

    @staticmethod
    def _coverage_class(level: CoverageLevel) -> str:
        return {
            CoverageLevel.MATCHED: "badge-matched",
            CoverageLevel.PARTIAL: "badge-partial",
            CoverageLevel.GAP: "badge-gap",
            CoverageLevel.JOURNEY_SATISFIED: "badge-journey",
            CoverageLevel.NOT_ASSESSED: "badge-na",
        }.get(level, "badge-na")

    @staticmethod
    def _coverage_label(level: CoverageLevel) -> str:
        return {
            CoverageLevel.MATCHED: "Matched",
            CoverageLevel.PARTIAL: "Partial",
            CoverageLevel.GAP: "Gap",
            CoverageLevel.JOURNEY_SATISFIED: "Journey",
            CoverageLevel.NOT_ASSESSED: "N/A",
        }.get(level, "N/A")

    @staticmethod
    def _readiness_pct(r: StepReadiness) -> float:
        return round(r.combined_readiness * 100, 1)

    @staticmethod
    def _bar_color(pct: float) -> str:
        if pct >= 80:
            return "var(--matched)"
        if pct >= 50:
            return "var(--partial)"
        return "var(--gap)"

    # ------------------------------------------------------------------
    # HTML sections
    # ------------------------------------------------------------------

    def _head(self, report: ProcessCoverageReport, generated: str) -> str:
        return (
            '<!DOCTYPE html>\n'
            '<html lang="en">\n'
            '<head>\n'
            '<meta charset="UTF-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f'<title>Knowledge Spec: {self._esc(report.process_name)}</title>\n'
            '<style>\n'
            ':root {\n'
            '  --matched: #2d7d46;\n'
            '  --partial: #c48a1a;\n'
            '  --gap: #c0392b;\n'
            '  --journey: #2980b9;\n'
            '  --regulatory: #8e44ad;\n'
            '  --bg: #f8f9fa;\n'
            '  --card-bg: #ffffff;\n'
            '  --border: #dee2e6;\n'
            '  --text: #212529;\n'
            '  --text-muted: #6c757d;\n'
            '  --radius: 6px;\n'
            '}\n'
            '*, *::before, *::after { box-sizing: border-box; }\n'
            'body {\n'
            '  margin: 0; padding: 0;\n'
            '  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;\n'
            '  background: var(--bg); color: var(--text);\n'
            '  line-height: 1.5; font-size: 14px;\n'
            '}\n'
            '.container { max-width: 1200px; margin: 0 auto; padding: 16px; }\n'
            '\n'
            '/* Header */\n'
            '.report-header {\n'
            '  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);\n'
            '  color: #fff; padding: 24px 28px; border-radius: var(--radius);\n'
            '  margin-bottom: 16px;\n'
            '}\n'
            '.report-header h1 { margin: 0 0 8px 0; font-size: 22px; font-weight: 600; }\n'
            '.report-header .subtitle { opacity: 0.75; font-size: 12px; }\n'
            '.stat-row { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 16px; }\n'
            '.stat-box {\n'
            '  background: rgba(255,255,255,0.1); border-radius: var(--radius);\n'
            '  padding: 10px 14px; min-width: 120px; text-align: center;\n'
            '}\n'
            '.stat-box .val { font-size: 22px; font-weight: 700; }\n'
            '.stat-box .lbl { font-size: 11px; text-transform: uppercase; opacity: 0.7; }\n'
            '\n'
            '/* Legend */\n'
            '.legend {\n'
            '  display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 16px;\n'
            '  padding: 10px 14px; background: var(--card-bg); border: 1px solid var(--border);\n'
            '  border-radius: var(--radius); font-size: 12px;\n'
            '}\n'
            '.legend-item { display: flex; align-items: center; gap: 6px; }\n'
            '.legend-swatch {\n'
            '  display: inline-block; width: 14px; height: 14px; border-radius: 3px;\n'
            '}\n'
            '\n'
            '/* Controls */\n'
            '.controls {\n'
            '  display: flex; flex-wrap: wrap; gap: 8px; align-items: center;\n'
            '  margin-bottom: 16px; padding: 10px 14px;\n'
            '  background: var(--card-bg); border: 1px solid var(--border); border-radius: var(--radius);\n'
            '}\n'
            '.controls button {\n'
            '  background: #e9ecef; border: 1px solid var(--border); border-radius: var(--radius);\n'
            '  padding: 5px 12px; cursor: pointer; font-size: 12px; font-family: inherit;\n'
            '}\n'
            '.controls button:hover { background: #dee2e6; }\n'
            '.controls button.active { background: #495057; color: #fff; border-color: #495057; }\n'
            '.controls input[type="text"] {\n'
            '  border: 1px solid var(--border); border-radius: var(--radius);\n'
            '  padding: 5px 10px; font-size: 12px; min-width: 200px; font-family: inherit;\n'
            '}\n'
            '\n'
            '/* Cards */\n'
            '.card {\n'
            '  background: var(--card-bg); border: 1px solid var(--border);\n'
            '  border-radius: var(--radius); margin-bottom: 12px; overflow: hidden;\n'
            '}\n'
            '.card-header {\n'
            '  padding: 12px 16px; font-weight: 600; font-size: 14px;\n'
            '  border-bottom: 1px solid var(--border); background: #f1f3f5;\n'
            '  display: flex; justify-content: space-between; align-items: center;\n'
            '}\n'
            '\n'
            '/* Step card */\n'
            '.step-card {\n'
            '  background: var(--card-bg); border: 1px solid var(--border);\n'
            '  border-radius: var(--radius); margin-bottom: 10px; overflow: hidden;\n'
            '}\n'
            '.step-card[data-has-gap="true"] { border-left: 3px solid var(--gap); }\n'
            '.step-card[data-has-regulatory="true"]:not([data-has-gap="true"]) {\n'
            '  border-left: 3px solid var(--regulatory);\n'
            '}\n'
            '.step-header {\n'
            '  padding: 10px 14px; display: flex; flex-wrap: wrap;\n'
            '  justify-content: space-between; align-items: center; gap: 8px;\n'
            '  cursor: pointer; user-select: none;\n'
            '}\n'
            '.step-header:hover { background: #f8f9fa; }\n'
            '.step-title { font-weight: 600; font-size: 14px; }\n'
            '.step-meta { font-size: 11px; color: var(--text-muted); }\n'
            '.scope-breadcrumb {\n'
            '  font-size: 11px; color: var(--text-muted); margin-top: 2px;\n'
            '}\n'
            '.step-body { padding: 0 14px 14px; }\n'
            '\n'
            '/* Badges */\n'
            '.badge {\n'
            '  display: inline-block; padding: 2px 8px; border-radius: 10px;\n'
            '  font-size: 11px; font-weight: 600; color: #fff; white-space: nowrap;\n'
            '}\n'
            '.badge-matched { background: var(--matched); }\n'
            '.badge-partial { background: var(--partial); }\n'
            '.badge-gap { background: var(--gap); }\n'
            '.badge-journey { background: var(--journey); }\n'
            '.badge-regulatory { background: var(--regulatory); }\n'
            '.badge-na { background: #adb5bd; }\n'
            '\n'
            '/* Score bar */\n'
            '.score-bar-wrap {\n'
            '  display: flex; align-items: center; gap: 8px; margin: 4px 0;\n'
            '}\n'
            '.score-bar {\n'
            '  flex: 1; height: 10px; background: #e9ecef; border-radius: 5px; overflow: hidden;\n'
            '}\n'
            '.score-bar-fill {\n'
            '  height: 100%; border-radius: 5px; transition: width 0.3s ease;\n'
            '}\n'
            '.score-bar-label { font-size: 11px; font-weight: 600; min-width: 42px; text-align: right; }\n'
            '\n'
            '/* Requirements table */\n'
            '.req-table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 6px; }\n'
            '.req-table th {\n'
            '  text-align: left; padding: 4px 8px; background: #f1f3f5;\n'
            '  border-bottom: 1px solid var(--border); font-size: 11px; text-transform: uppercase;\n'
            '  color: var(--text-muted);\n'
            '}\n'
            '.req-table td { padding: 4px 8px; border-bottom: 1px solid #f1f3f5; vertical-align: top; }\n'
            '\n'
            '/* Details styling */\n'
            'details { margin: 6px 0; }\n'
            'details > summary {\n'
            '  cursor: pointer; font-weight: 600; font-size: 13px; padding: 4px 0;\n'
            '  list-style: none;\n'
            '}\n'
            'details > summary::before { content: "\\25B6  "; font-size: 10px; }\n'
            'details[open] > summary::before { content: "\\25BC  "; }\n'
            'details > summary::-webkit-details-marker { display: none; }\n'
            '\n'
            '/* Scope nesting */\n'
            '.scope-block { margin-left: 0; margin-bottom: 8px; }\n'
            '.scope-block-inner {\n'
            '  padding-left: 14px; border-left: 3px solid #ccc;\n'
            '}\n'
            '.scope-label { font-weight: 600; font-size: 13px; margin-bottom: 4px; }\n'
            '\n'
            '/* Journey panel */\n'
            '.journey-panel {\n'
            '  background: #eaf4fb; border: 1px solid #b8d9f0; border-radius: var(--radius);\n'
            '  padding: 10px 12px; margin-bottom: 8px; font-size: 12px;\n'
            '}\n'
            '.journey-panel h4 { margin: 0 0 6px; font-size: 13px; color: var(--journey); }\n'
            '\n'
            '/* Regulatory section */\n'
            '.reg-section {\n'
            '  background: #f5eef8; border: 1px solid #d5c4e0; border-radius: var(--radius);\n'
            '  padding: 10px 12px; margin-bottom: 8px; font-size: 12px;\n'
            '}\n'
            '.reg-section h4 { margin: 0 0 6px; font-size: 13px; color: var(--regulatory); }\n'
            '\n'
            '/* Summary section */\n'
            '.summary-grid {\n'
            '  display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));\n'
            '  gap: 12px; margin-top: 12px;\n'
            '}\n'
            '\n'
            '/* Hidden utility */\n'
            '.hidden { display: none !important; }\n'
            '\n'
            '/* Print styles */\n'
            '@media print {\n'
            '  body { font-size: 11px; }\n'
            '  .controls, .legend { page-break-inside: avoid; }\n'
            '  .step-card { page-break-inside: avoid; }\n'
            '  .no-print { display: none !important; }\n'
            '}\n'
            '\n'
            '/* Responsive */\n'
            '@media (max-width: 768px) {\n'
            '  .container { padding: 8px; }\n'
            '  .stat-row { flex-direction: column; }\n'
            '  .controls { flex-direction: column; align-items: stretch; }\n'
            '  .controls input[type="text"] { min-width: unset; width: 100%; }\n'
            '  .summary-grid { grid-template-columns: 1fr; }\n'
            '}\n'
            '</style>\n'
            '</head>'
        )

    def _header(self, report: ProcessCoverageReport, generated: str) -> str:
        rp = self._readiness_pct(report.overall_readiness)
        depth = max(
            (
                s.scope_depth
                for s in (
                    sr.step_requirements
                    for sr in report.step_reports
                    if sr.step_requirements
                )
            ),
            default=0,
        )
        ki_count = report.total_matched + report.total_partial + report.total_journey_satisfied
        fw_count = len(report.compliance_summary.frameworks_evaluated)

        return (
            '<header class="report-header">\n'
            f'  <h1>{self._esc(report.process_name)} &mdash; Knowledge Spec</h1>\n'
            f'  <div class="subtitle">Generated {generated}</div>\n'
            '  <div class="stat-row">\n'
            f'    <div class="stat-box"><div class="val">{report.total_steps_analyzed}</div><div class="lbl">Steps</div></div>\n'
            f'    <div class="stat-box"><div class="val">{depth}</div><div class="lbl">Max Depth</div></div>\n'
            f'    <div class="stat-box"><div class="val">{ki_count}</div><div class="lbl">Knowledge Items</div></div>\n'
            f'    <div class="stat-box"><div class="val">{fw_count}</div><div class="lbl">Frameworks</div></div>\n'
            f'    <div class="stat-box"><div class="val">{rp}%</div><div class="lbl">Readiness</div></div>\n'
            '  </div>\n'
            '</header>'
        )

    def _legend(self) -> str:
        items = [
            ("var(--matched)", "Matched"),
            ("var(--partial)", "Partial"),
            ("var(--gap)", "Gap"),
            ("var(--journey)", "Journey-Satisfied"),
            ("var(--regulatory)", "Regulatory"),
        ]
        swatches = "\n".join(
            f'  <div class="legend-item">'
            f'<span class="legend-swatch" style="background:{c}"></span>{label}</div>'
            for c, label in items
        )
        return f'<div class="legend">\n{swatches}\n</div>'

    def _controls(self) -> str:
        return (
            '<div class="controls no-print">\n'
            '  <button id="btn-toggle" title="Expand or collapse all step details">Expand All</button>\n'
            '  <button class="filter-btn active" data-filter="all">All</button>\n'
            '  <button class="filter-btn" data-filter="gaps">Gaps Only</button>\n'
            '  <button class="filter-btn" data-filter="regulatory">Regulatory Only</button>\n'
            '  <input type="text" id="search-input" placeholder="Search steps..." />\n'
            '  <button id="btn-print" title="Print-friendly view">Print</button>\n'
            '</div>'
        )

    # ------------------------------------------------------------------
    # Process map
    # ------------------------------------------------------------------

    def _process_map(self, report: ProcessCoverageReport) -> str:
        scopes: dict[str, list[StepCoverageReport]] = {}
        for sr in report.step_reports:
            req = sr.step_requirements
            scope_key = " > ".join(req.scope_path) if req and req.scope_path else "Root"
            scopes.setdefault(scope_key, []).append(sr)

        rows: list[str] = []
        for scope_key, steps in scopes.items():
            depth = scope_key.count(">")
            color = self._depth_color(depth)
            total = sum(s.total_requirements for s in steps)
            gaps = sum(s.gap_count for s in steps)
            rows.append(
                f'<details class="scope-block">'
                f'<summary class="scope-label" style="border-left:3px solid {color};padding-left:8px">'
                f"{self._esc(scope_key)} ({len(steps)} steps, {total} reqs, {gaps} gaps)</summary>"
                f'<div class="scope-block-inner" style="border-left-color:{color}">'
            )
            for s in steps:
                req = s.step_requirements
                name = self._esc(req.node_name) if req else "?"
                badge_cls = "gap" if s.gap_count else "matched"
                rows.append(
                    f'<div style="padding:2px 0;font-size:12px">'
                    f'<span class="badge badge-{badge_cls}" '
                    f'style="font-size:10px">{s.gap_count}G</span> '
                    f"Step {s.step_number}: {name}</div>"
                )
            rows.append("</div></details>")

        return (
            '<div class="card"><div class="card-header">Process Map</div>'
            '<div style="padding:12px">' + "\n".join(rows) + "</div></div>"
        )

    # ------------------------------------------------------------------
    # Step cards
    # ------------------------------------------------------------------

    def _step_cards(
        self,
        report: ProcessCoverageReport,
        journey_summary: JourneySummary | None,
    ) -> str:
        parts: list[str] = ['<div id="step-cards">']
        # Build a lookup of journey entries by node_id
        je_by_node: dict[str, object] = {}
        if journey_summary:
            for je in journey_summary.journey_entries:
                je_by_node[je.node_id] = je

        for sr in report.step_reports:
            parts.append(self._one_step_card(sr, je_by_node))
        parts.append("</div>")
        return "\n".join(parts)

    def _one_step_card(
        self, sr: StepCoverageReport, je_by_node: dict
    ) -> str:
        req = sr.step_requirements
        node_name = self._esc(req.node_name) if req else "Unknown"
        node_type = req.node_type.value if req else ""
        scope_path = " &gt; ".join(req.scope_path) if req and req.scope_path else "Root"
        step_num = sr.step_number
        pct = self._readiness_pct(sr.readiness)
        has_gap = "true" if sr.gap_count > 0 else "false"
        has_reg = "true" if sr.control_evaluations else "false"

        lines: list[str] = []
        lines.append(
            f'<div class="step-card" data-has-gap="{has_gap}" '
            f'data-has-regulatory="{has_reg}" '
            f'data-step="{step_num}" data-name="{self._esc(node_name.lower())}">'
        )
        # Header (click toggles body)
        lines.append(
            f'<div class="step-header" '
            f"onclick=\"this.parentElement.querySelector('.step-body').classList.toggle('hidden')\">"
            f'<div><div class="step-title">Step {step_num}: {node_name}</div>'
            f'<div class="step-meta">{node_type} &middot; Scope: {scope_path}</div></div>'
            f'<div style="text-align:right">'
        )
        if sr.matched_count:
            lines.append(
                f'<span class="badge badge-matched">{sr.matched_count} matched</span> '
            )
        if sr.partial_count:
            lines.append(
                f'<span class="badge badge-partial">{sr.partial_count} partial</span> '
            )
        if sr.gap_count:
            lines.append(
                f'<span class="badge badge-gap">{sr.gap_count} gap</span> '
            )
        if sr.journey_satisfied_count:
            lines.append(
                f'<span class="badge badge-journey">{sr.journey_satisfied_count} journey</span> '
            )
        lines.append("</div></div>")

        # Body (initially hidden)
        lines.append('<div class="step-body hidden">')

        # Readiness bar
        bc = self._bar_color(pct)
        lines.append(
            f'<div class="score-bar-wrap">'
            f'<span style="font-size:12px;font-weight:600">Readiness</span>'
            f'<div class="score-bar">'
            f'<div class="score-bar-fill" style="width:{pct}%;background:{bc}"></div>'
            f'</div>'
            f'<span class="score-bar-label" style="color:{bc}">{pct}%</span></div>'
        )

        # Journey context panel
        je = je_by_node.get(req.node_id if req else "")
        if je:
            lines.append(self._journey_panel(je))

        # Coverage by category
        cats = [
            ("Procedures", sr.procedure_coverage),
            ("Data Inputs", sr.data_coverage),
            ("Contextual", sr.context_coverage),
            ("Decision Criteria", sr.decision_coverage),
            ("Regulatory", sr.regulatory_requirements),
        ]
        for cat_name, cov_list in cats:
            if cov_list:
                lines.append(self._coverage_table(cat_name, cov_list))

        # Expansion cascades
        if sr.expansions:
            lines.append("<details><summary>Expansion Cascades</summary>")
            for exp in sr.expansions:
                lines.append(self._expansion_block(exp))
            lines.append("</details>")

        # Regulatory controls
        if sr.control_evaluations:
            lines.append(self._regulatory_block(sr.control_evaluations))

        lines.append("</div>")  # end step-body
        lines.append("</div>")  # end step-card
        return "\n".join(lines)

    def _journey_panel(self, je: object) -> str:
        lines = [
            '<details><summary style="color:var(--journey)">Journey Context</summary>',
            '<div class="journey-panel">',
            f"<h4>Journey at Step {getattr(je, 'step_number', '?')}</h4>",
        ]
        outputs = getattr(je, "outputs", [])
        if outputs:
            lines.append("<strong>Outputs produced:</strong><ul>")
            for o in outputs:
                lines.append(
                    f"<li>{self._esc(o.description)} <em>({o.data_type})</em></li>"
                )
            lines.append("</ul>")
        decisions = getattr(je, "decisions", [])
        if decisions:
            lines.append("<strong>Decisions:</strong><ul>")
            for d in decisions:
                lines.append(
                    f"<li>{self._esc(d.description)} &rarr; {self._esc(d.outcome)}</li>"
                )
            lines.append("</ul>")
        state_changes = getattr(je, "state_changes", [])
        if state_changes:
            lines.append("<strong>State changes:</strong><ul>")
            for sc in state_changes:
                lines.append(
                    f"<li><code>{self._esc(sc.attribute)}</code>: "
                    f"{self._esc(str(sc.old_value))} &rarr; {self._esc(sc.new_value)}</li>"
                )
            lines.append("</ul>")
        lines.append("</div></details>")
        return "\n".join(lines)

    def _coverage_table(self, title: str, items: list[RequirementCoverage]) -> str:
        rows: list[str] = [
            f"<details><summary>{self._esc(title)} ({len(items)})</summary>",
            '<table class="req-table"><tr><th>Requirement</th><th>Priority</th>'
            "<th>Coverage</th><th>Notes</th></tr>",
        ]
        for c in items:
            badge = (
                f'<span class="badge {self._coverage_class(c.coverage_level)}">'
                f"{self._coverage_label(c.coverage_level)}</span>"
            )
            pri = c.requirement.priority.value if c.requirement else ""
            desc = self._esc(c.requirement.description) if c.requirement else ""
            notes = self._esc(c.coverage_notes or "")
            if c.gap_description:
                notes += (
                    f' <em style="color:var(--gap)">'
                    f"{self._esc(c.gap_description)}</em>"
                )
            rows.append(
                f"<tr><td>{desc}</td><td>{pri}</td><td>{badge}</td><td>{notes}</td></tr>"
            )
        rows.append("</table></details>")
        return "\n".join(rows)

    def _expansion_block(self, exp: ExpansionResult, depth: int = 0) -> str:
        indent = depth * 12
        src = exp.source_item
        title = self._esc(src.title) if src else "Unknown"
        lines = [
            f'<details style="margin-left:{indent}px">'
            f"<summary>Expansion L{exp.expansion_depth}: {title} "
            f"({exp.total_expanded_count} reqs)</summary>"
        ]
        if exp.expanded_coverage:
            lines.append(
                self._coverage_table("Expanded Requirements", exp.expanded_coverage)
            )
        for sub in exp.sub_expansions:
            lines.append(self._expansion_block(sub, depth + 1))
        lines.append("</details>")
        return "\n".join(lines)

    def _regulatory_block(self, evals: list[ControlEvaluation]) -> str:
        lines = ['<div class="reg-section">', "<h4>Regulatory Controls</h4>"]
        for ev in evals:
            status = ev.compliance_status.value
            sev = ev.control.severity.value
            lines.append(
                f"<div style='margin-bottom:6px'>"
                f'<span class="badge badge-regulatory">'
                f"{self._esc(ev.control.control_id)}</span> "
                f"<strong>{self._esc(ev.control.title)}</strong> "
                f"<em>({self._esc(ev.framework.name)})</em> &mdash; "
                f"{sev} / {status}"
            )
            if ev.evidence_needed:
                lines.append(
                    f"<div style='font-size:11px;color:var(--text-muted);margin-left:12px'>"
                    f"Evidence: {', '.join(self._esc(e) for e in ev.evidence_needed)}"
                    f"</div>"
                )
            lines.append("</div>")
        lines.append("</div>")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Summary section
    # ------------------------------------------------------------------

    def _summary_section(
        self,
        report: ProcessCoverageReport,
        journey_summary: JourneySummary | None,
    ) -> str:
        parts: list[str] = [
            '<div class="card" id="summary">'
            '<div class="card-header">Summary</div>',
            '<div style="padding:14px"><div class="summary-grid">',
        ]

        # Category breakdown
        parts.append(
            '<div class="card"><div class="card-header">Coverage Breakdown</div>'
            '<div style="padding:10px">'
        )
        total = report.total_requirements or 1
        breakdown = [
            ("Matched", report.total_matched, "badge-matched", "--matched"),
            ("Partial", report.total_partial, "badge-partial", "--partial"),
            ("Gap", report.total_gaps, "badge-gap", "--gap"),
            ("Journey", report.total_journey_satisfied, "badge-journey", "--journey"),
        ]
        for label, val, cls, var in breakdown:
            pct = round(val / total * 100, 1)
            parts.append(
                f'<div class="score-bar-wrap">'
                f'<span class="badge {cls}" style="min-width:70px">{label} ({val})</span>'
                f'<div class="score-bar">'
                f'<div class="score-bar-fill" style="width:{pct}%;background:var({var})"></div>'
                f'</div>'
                f'<span class="score-bar-label">{pct}%</span></div>'
            )
        parts.append("</div></div>")

        # Scope readiness
        parts.append(
            '<div class="card"><div class="card-header">Scope Readiness</div>'
            '<div style="padding:10px">'
        )
        for ss in report.scope_summaries:
            pct = self._readiness_pct(ss.readiness)
            bc = self._bar_color(pct)
            parts.append(
                f'<div class="score-bar-wrap">'
                f'<span style="font-size:12px;min-width:120px">{self._esc(ss.scope_name)}</span>'
                f'<div class="score-bar">'
                f'<div class="score-bar-fill" style="width:{pct}%;background:{bc}"></div>'
                f'</div>'
                f'<span class="score-bar-label" style="color:{bc}">{pct}%</span></div>'
            )
        parts.append("</div></div>")

        # Compliance summary
        cs = report.compliance_summary
        parts.append(
            '<div class="card"><div class="card-header">Compliance</div>'
            '<div style="padding:10px;font-size:12px">'
        )
        parts.append(
            f"<p>Frameworks: {len(cs.frameworks_evaluated)} &middot; "
            f"Controls: {cs.total_controls_triggered} &middot; "
            f"Compliant: {cs.total_compliant} &middot; "
            f"Partial: {cs.total_partially_compliant} &middot; "
            f"Non-compliant: {cs.total_non_compliant}</p>"
        )
        if cs.critical_violations:
            parts.append("<strong>Critical Violations:</strong><ul>")
            for ev in cs.critical_violations:
                parts.append(
                    f"<li>{self._esc(ev.control.control_id)}: "
                    f"{self._esc(ev.control.title)}</li>"
                )
            parts.append("</ul>")
        parts.append("</div></div>")

        # Critical gaps
        if report.critical_gaps:
            parts.append(
                '<div class="card">'
                '<div class="card-header" style="color:var(--gap)">Critical Gaps</div>'
                '<div style="padding:10px">'
            )
            parts.append(
                '<table class="req-table"><tr><th>Requirement</th><th>Gap</th></tr>'
            )
            for cg in report.critical_gaps:
                parts.append(
                    f"<tr><td>{self._esc(cg.requirement.description)}</td>"
                    f"<td>{self._esc(cg.gap_description or '')}</td></tr>"
                )
            parts.append("</table></div></div>")

        # Journey stats
        if journey_summary:
            parts.append(
                '<div class="card">'
                '<div class="card-header" style="color:var(--journey)">Journey Stats</div>'
                '<div style="padding:10px;font-size:12px">'
            )
            parts.append(
                f"<p>Steps: {journey_summary.total_steps} &middot; "
                f"Scopes: {len(journey_summary.scopes_visited)} &middot; "
                f"Decisions: {journey_summary.decisions_made} &middot; "
                f"Outputs: {journey_summary.outputs_produced} &middot; "
                f"State attrs: {journey_summary.state_attributes_tracked}</p>"
            )
            parts.append("</div></div>")

        parts.append("</div></div></div>")  # grid, padding, card
        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Embedded JSON
    # ------------------------------------------------------------------

    @staticmethod
    def _embedded_json(json_str: str) -> str:
        safe = json_str.replace("</", "<\\/")
        return f'<script type="application/json" id="spec-data">\n{safe}\n</script>'

    # ------------------------------------------------------------------
    # JS
    # ------------------------------------------------------------------

    @staticmethod
    def _script() -> str:
        return (
            "<script>\n"
            "(function() {\n"
            "  // Expand / Collapse all\n"
            "  var toggleBtn = document.getElementById('btn-toggle');\n"
            "  if (toggleBtn) {\n"
            "    toggleBtn.addEventListener('click', function() {\n"
            "      var bodies = document.querySelectorAll('.step-body');\n"
            "      var allVisible = true;\n"
            "      bodies.forEach(function(b) { if (b.classList.contains('hidden')) allVisible = false; });\n"
            "      bodies.forEach(function(b) {\n"
            "        if (allVisible) b.classList.add('hidden');\n"
            "        else b.classList.remove('hidden');\n"
            "      });\n"
            "      toggleBtn.textContent = allVisible ? 'Expand All' : 'Collapse All';\n"
            "    });\n"
            "  }\n"
            "\n"
            "  // Filter buttons\n"
            "  var filterBtns = document.querySelectorAll('.filter-btn');\n"
            "  filterBtns.forEach(function(btn) {\n"
            "    btn.addEventListener('click', function() {\n"
            "      filterBtns.forEach(function(b) { b.classList.remove('active'); });\n"
            "      btn.classList.add('active');\n"
            "      var f = btn.getAttribute('data-filter');\n"
            "      var cards = document.querySelectorAll('.step-card');\n"
            "      cards.forEach(function(c) {\n"
            "        if (f === 'all') { c.style.display = ''; }\n"
            "        else if (f === 'gaps') {\n"
            "          c.style.display = c.getAttribute('data-has-gap') === 'true' ? '' : 'none';\n"
            "        }\n"
            "        else if (f === 'regulatory') {\n"
            "          c.style.display = c.getAttribute('data-has-regulatory') === 'true' ? '' : 'none';\n"
            "        }\n"
            "      });\n"
            "    });\n"
            "  });\n"
            "\n"
            "  // Text search\n"
            "  var searchInput = document.getElementById('search-input');\n"
            "  if (searchInput) {\n"
            "    searchInput.addEventListener('input', function() {\n"
            "      var q = searchInput.value.toLowerCase();\n"
            "      var cards = document.querySelectorAll('.step-card');\n"
            "      cards.forEach(function(c) {\n"
            "        if (!q) { c.style.display = ''; return; }\n"
            "        var name = c.getAttribute('data-name') || '';\n"
            "        var text = c.textContent.toLowerCase();\n"
            "        c.style.display = (name.indexOf(q) !== -1 || text.indexOf(q) !== -1) ? '' : 'none';\n"
            "      });\n"
            "    });\n"
            "  }\n"
            "\n"
            "  // Print mode\n"
            "  var printBtn = document.getElementById('btn-print');\n"
            "  if (printBtn) {\n"
            "    printBtn.addEventListener('click', function() {\n"
            "      document.querySelectorAll('.step-body').forEach(function(b) {\n"
            "        b.classList.remove('hidden');\n"
            "      });\n"
            "      window.print();\n"
            "    });\n"
            "  }\n"
            "})();\n"
            "</script>"
        )
