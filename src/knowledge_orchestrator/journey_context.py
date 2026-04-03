"""
Knowledge Orchestrator — Journey Context.

Append-only process ledger for horizontal knowledge flow. Records every step's
outputs, decisions, and state changes. Enables cross-scope queries — step 26 can
find step 1's outputs even across subprocess boundaries.
"""

from __future__ import annotations

from datetime import datetime, timezone

from .models import (
    JourneyDecision,
    JourneyEntry,
    JourneyEntryType,
    JourneyOutput,
    JourneyStateChange,
    JourneySummary,
)


class JourneyContext:

    def __init__(self) -> None:
        self._entries: list[JourneyEntry] = []
        self._step_counter: int = 0
        self._outputs_by_tag: dict[str, list[JourneyOutput]] = {}
        self._outputs_by_node: dict[str, list[JourneyOutput]] = {}
        self._outputs_by_scope: dict[str, list[JourneyOutput]] = {}
        self._decisions: list[JourneyDecision] = []
        self._state: dict[str, str] = {}
        self._state_history: list[tuple[int, JourneyStateChange]] = []

    def record_step(
        self,
        node_id: str,
        node_name: str,
        scope_path: list[str],
        scope_depth: int,
        entry_type: JourneyEntryType = JourneyEntryType.TASK_COMPLETED,
        outputs: list[JourneyOutput] | None = None,
        decisions: list[JourneyDecision] | None = None,
        state_changes: list[JourneyStateChange] | None = None,
        gateway_condition: str | None = None,
    ) -> JourneyEntry:
        self._step_counter += 1
        outputs = outputs or []
        decisions = decisions or []
        state_changes = state_changes or []

        # Stamp outputs with step number and node
        for output in outputs:
            output.produced_at_step = self._step_counter
            output.produced_by_node = node_id

        entry = JourneyEntry(
            step_number=self._step_counter,
            node_id=node_id,
            node_name=node_name,
            scope_path=list(scope_path),
            scope_depth=scope_depth,
            entry_type=entry_type,
            outputs=outputs,
            decisions=decisions,
            state_changes=state_changes,
            timestamp=datetime.now(timezone.utc).isoformat(),
            gateway_condition=gateway_condition,
        )

        self._entries.append(entry)

        # Index outputs
        for output in outputs:
            for tag in output.tags:
                self._outputs_by_tag.setdefault(tag, []).append(output)
            self._outputs_by_node.setdefault(node_id, []).append(output)
            if scope_path:
                for scope_name in scope_path:
                    key = scope_name.lower().replace(" ", "-").replace("&", "and")
                    self._outputs_by_scope.setdefault(key, []).append(output)

        # Record decisions
        for decision in decisions:
            self._decisions.append(decision)

        # Apply state changes
        for change in state_changes:
            change_old = self._state.get(change.attribute)
            if change_old is not None:
                change.old_value = change_old
            self._state[change.attribute] = change.new_value
            self._state_history.append((self._step_counter, change))

        return entry

    def query_prior_outputs(self, tags: list[str]) -> list[JourneyOutput]:
        seen_ids: set[str] = set()
        results: list[JourneyOutput] = []

        for tag in tags:
            for output in self._outputs_by_tag.get(tag, []):
                if output.output_id not in seen_ids:
                    seen_ids.add(output.output_id)
                    results.append(output)

        results.sort(key=lambda o: o.produced_at_step, reverse=True)
        return results

    def query_outputs_from_node(self, node_id: str) -> list[JourneyOutput]:
        return list(self._outputs_by_node.get(node_id, []))

    def query_outputs_from_scope(self, scope_name: str) -> list[JourneyOutput]:
        key = scope_name.lower().replace(" ", "-").replace("&", "and")
        return list(self._outputs_by_scope.get(key, []))

    def get_decision_trail(self) -> list[JourneyDecision]:
        return list(self._decisions)

    def get_current_state(self) -> dict[str, str]:
        return dict(self._state)

    def get_state_at_step(self, step_number: int) -> dict[str, str]:
        state: dict[str, str] = {}
        for sn, change in self._state_history:
            if sn <= step_number:
                state[change.attribute] = change.new_value
        return state

    def get_step_count(self) -> int:
        return self._step_counter

    def get_journey_so_far(self) -> list[JourneyEntry]:
        return list(self._entries)

    def get_journey_summary(self) -> JourneySummary:
        scopes_visited: list[str] = []
        seen_scopes: set[str] = set()
        for entry in self._entries:
            for scope in entry.scope_path:
                if scope not in seen_scopes:
                    seen_scopes.add(scope)
                    scopes_visited.append(scope)

        total_outputs = sum(len(e.outputs) for e in self._entries)

        return JourneySummary(
            total_steps=self._step_counter,
            scopes_visited=scopes_visited,
            decisions_made=len(self._decisions),
            outputs_produced=total_outputs,
            state_attributes_tracked=len(self._state),
            journey_entries=list(self._entries),
        )

    def get_outputs_available_at_step(self, step_number: int) -> list[JourneyOutput]:
        results: list[JourneyOutput] = []
        for entry in self._entries:
            if entry.step_number < step_number:
                results.extend(entry.outputs)
        return results
