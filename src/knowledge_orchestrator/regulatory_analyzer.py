"""
Knowledge Orchestrator — Regulatory Analyzer.

Loads regulatory frameworks from JSON files and evaluates each BPMN step against
all loaded controls. Fires controls based on domain, tags, node type, data
categories, step name patterns, scope depth, or unconditionally. Converts fired
controls into RequirementItem objects with category=REGULATORY.
"""

from __future__ import annotations

import json
import re
import uuid
from pathlib import Path

from .models import (
    ComplianceStatus,
    ControlEvaluation,
    ControlRequirement,
    ControlSeverity,
    ControlTrigger,
    ControlTriggerType,
    ProcessNode,
    RegulatoryControl,
    RegulatoryFramework,
    RequirementCategory,
    RequirementItem,
    RequirementPriority,
)


def _make_id() -> str:
    return f"reg_{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Severity → priority mapping
# ---------------------------------------------------------------------------

_SEVERITY_TO_PRIORITY: dict[ControlSeverity, RequirementPriority] = {
    ControlSeverity.MANDATORY: RequirementPriority.CRITICAL,
    ControlSeverity.RECOMMENDED: RequirementPriority.IMPORTANT,
    ControlSeverity.ADVISORY: RequirementPriority.HELPFUL,
}


class RegulatoryAnalyzer:

    def __init__(self) -> None:
        self._frameworks: list[RegulatoryFramework] = []
        self._control_index: dict[ControlTriggerType, dict[str, list[RegulatoryControl]]] = {}
        # Map control_id → framework for lookup
        self._control_framework: dict[str, RegulatoryFramework] = {}

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load_frameworks(self, directory: str) -> int:
        dir_path = Path(directory)
        if not dir_path.is_dir():
            return 0

        loaded = 0
        for json_file in sorted(dir_path.glob("*.json")):
            try:
                fw = self._parse_framework(json_file)
                if fw:
                    self._frameworks.append(fw)
                    for control in fw.controls:
                        self._control_framework[control.control_id] = fw
                    self._build_index(fw)
                    loaded += 1
            except (json.JSONDecodeError, OSError, KeyError) as e:
                print(f"Warning: Could not load framework {json_file}: {e}")

        return loaded

    def load_framework(self, file_path: str) -> RegulatoryFramework | None:
        path = Path(file_path)
        fw = self._parse_framework(path)
        if fw:
            self._frameworks.append(fw)
            for control in fw.controls:
                self._control_framework[control.control_id] = fw
            self._build_index(fw)
        return fw

    def _parse_framework(self, file_path: Path) -> RegulatoryFramework | None:
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

        controls: list[RegulatoryControl] = []
        for ctrl_data in data.get("controls", []):
            triggers: list[ControlTrigger] = []
            for trig_data in ctrl_data.get("applies_to", []):
                tt_str = trig_data.get("trigger_type", "any")
                try:
                    tt = ControlTriggerType(tt_str)
                except ValueError:
                    continue
                triggers.append(ControlTrigger(
                    trigger_type=tt,
                    trigger_values=trig_data.get("trigger_values", []),
                    match_mode=trig_data.get("match_mode", "any"),
                ))

            requirements: list[ControlRequirement] = []
            for req_data in ctrl_data.get("requirements", []):
                requirements.append(ControlRequirement(
                    description=req_data.get("description", ""),
                    category=req_data.get("category", "REGULATORY"),
                    tags=req_data.get("tags", []),
                    mandatory=req_data.get("mandatory", True),
                ))

            sev_str = ctrl_data.get("severity", "mandatory")
            try:
                severity = ControlSeverity(sev_str)
            except ValueError:
                severity = ControlSeverity.MANDATORY

            controls.append(RegulatoryControl(
                control_id=ctrl_data.get("control_id", ""),
                title=ctrl_data.get("title", ""),
                description=ctrl_data.get("description", ""),
                framework_id=data.get("id", ""),
                section_reference=ctrl_data.get("section_reference", ""),
                severity=severity,
                applies_to=triggers,
                requirements=requirements,
                evidence_requirements=ctrl_data.get("evidence_requirements", []),
                failure_consequence=ctrl_data.get("failure_consequence", ""),
            ))

        return RegulatoryFramework(
            id=data.get("id", ""),
            name=data.get("name", ""),
            version=data.get("version", ""),
            description=data.get("description", ""),
            jurisdiction=data.get("jurisdiction", "global"),
            controls=controls,
        )

    def _build_index(self, framework: RegulatoryFramework) -> None:
        for control in framework.controls:
            for trigger in control.applies_to:
                tt = trigger.trigger_type
                if tt not in self._control_index:
                    self._control_index[tt] = {}

                if tt == ControlTriggerType.ANY_STEP:
                    self._control_index[tt].setdefault("*", []).append(control)
                else:
                    for val in trigger.trigger_values:
                        key = val.lower().strip()
                        self._control_index[tt].setdefault(key, []).append(control)

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate_step(
        self,
        node: ProcessNode,
        scope_path: list[str],
        scope_depth: int,
        step_tags: list[str],
        step_data_tags: list[str],
    ) -> list[ControlEvaluation]:
        if not self._frameworks:
            return []

        # Build step match context
        domains = [s.lower().replace(" ", "-").replace("&", "and") for s in scope_path]
        domains.append(node.name.lower().replace(" ", "-").replace("&", "and"))

        all_tags = set(
            t.lower() for t in (
                step_tags + step_data_tags + node.knowledge_tags + node.data_tags
            )
        )
        node_type = node.node_type.value

        # Track fired controls with their triggers (dedup by control_id)
        fired: dict[str, tuple[RegulatoryControl, list[ControlTrigger]]] = {}

        for framework in self._frameworks:
            for control in framework.controls:
                if control.control_id in fired:
                    continue

                matched_triggers: list[ControlTrigger] = []
                for trigger in control.applies_to:
                    if self._trigger_matches(
                        trigger, domains, all_tags, node_type,
                        step_data_tags, node.name, scope_depth,
                    ):
                        matched_triggers.append(trigger)

                if matched_triggers:
                    fired[control.control_id] = (control, matched_triggers)

        # Convert to evaluations
        evaluations: list[ControlEvaluation] = []
        for control, triggers in fired.values():
            fw = self._control_framework.get(control.control_id)
            if not fw:
                continue

            req_items = self._control_to_requirements(control, fw)

            evaluations.append(ControlEvaluation(
                control=control,
                framework=fw,
                triggered_by=triggers,
                requirements=req_items,
                evidence_needed=list(control.evidence_requirements),
                compliance_status=ComplianceStatus.NOT_ASSESSED,
            ))

        return evaluations

    def _trigger_matches(
        self,
        trigger: ControlTrigger,
        domains: list[str],
        tags: set[str],
        node_type: str,
        data_tags: list[str],
        node_name: str,
        scope_depth: int,
    ) -> bool:
        values = [v.lower().strip() for v in trigger.trigger_values]
        mode = trigger.match_mode

        match trigger.trigger_type:
            case ControlTriggerType.DOMAIN_MATCH:
                matches = [v in domains for v in values]
            case ControlTriggerType.TAG_MATCH:
                matches = [v in tags for v in values]
            case ControlTriggerType.NODE_TYPE_MATCH:
                matches = [v == node_type for v in values]
            case ControlTriggerType.DATA_CATEGORY:
                data_lower = {t.lower() for t in data_tags}
                matches = [v in data_lower for v in values]
            case ControlTriggerType.STEP_NAME_PATTERN:
                name_lower = node_name.lower()
                matches = [bool(re.search(v, name_lower)) for v in values]
            case ControlTriggerType.SCOPE_DEPTH:
                matches = []
                for v in values:
                    try:
                        matches.append(scope_depth >= int(v))
                    except ValueError:
                        matches.append(False)
            case ControlTriggerType.ANY_STEP:
                return True
            case _:
                return False

        if not matches:
            return False

        if mode == "all":
            return all(matches)
        else:  # "any" or default
            return any(matches)

    def _control_to_requirements(
        self,
        control: RegulatoryControl,
        framework: RegulatoryFramework,
    ) -> list[RequirementItem]:
        items: list[RequirementItem] = []

        for ctrl_req in control.requirements:
            cat_str = ctrl_req.category.upper()
            try:
                category = RequirementCategory(cat_str.lower())
            except ValueError:
                category = RequirementCategory.REGULATORY

            priority = _SEVERITY_TO_PRIORITY.get(
                control.severity, RequirementPriority.IMPORTANT
            )
            if ctrl_req.mandatory:
                priority = RequirementPriority.CRITICAL

            items.append(RequirementItem(
                requirement_id=_make_id(),
                description=ctrl_req.description,
                category=category,
                tags=list(ctrl_req.tags),
                priority=priority,
                source=f"regulatory:{framework.id}:{control.control_id}",
                rationale=(
                    f"{control.title} ({framework.name}"
                    + (f" {control.section_reference}" if control.section_reference else "")
                    + ")"
                ),
            ))

        return items

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def get_frameworks_summary(self) -> dict:
        return {
            "frameworks": [
                {
                    "id": fw.id,
                    "name": fw.name,
                    "version": fw.version,
                    "controls_count": len(fw.controls),
                }
                for fw in self._frameworks
            ],
            "total_controls": sum(len(fw.controls) for fw in self._frameworks),
        }

    def get_controls_for_domain(self, domain: str) -> list[RegulatoryControl]:
        key = domain.lower().strip()
        idx = self._control_index.get(ControlTriggerType.DOMAIN_MATCH, {})
        return list(idx.get(key, []))
