"""
Knowledge Orchestrator — Process Tree Walker.

Depth-first traversal of the BPMN process tree following sequence flows.
Handles subprocess entry/exit, gateway path exploration (all paths — we're
mapping knowledge needs, not simulating execution), and cycle detection.
"""

from __future__ import annotations

from collections.abc import Callable

from .models import (
    NodeType,
    ProcessDefinition,
    ProcessNode,
    SequenceFlow,
    SubProcess,
    WalkerEvent,
    WalkerEventType,
)


class WalkerError(Exception):
    pass


class ProcessWalker:

    def walk(
        self,
        process: ProcessDefinition,
        callback: Callable[[WalkerEvent], None],
    ) -> None:
        callback(WalkerEvent(
            event_type=WalkerEventType.ENTER_PROCESS,
            depth=0,
            scope_path=[process.name],
            metadata={"process_id": process.id, "process_name": process.name},
        ))

        self._walk_level(
            nodes=process.nodes,
            flows=process.flows,
            depth=0,
            scope_path=[process.name],
            callback=callback,
        )

        callback(WalkerEvent(
            event_type=WalkerEventType.EXIT_PROCESS,
            depth=0,
            scope_path=[process.name],
        ))

    def _walk_level(
        self,
        nodes: dict[str, ProcessNode],
        flows: dict[str, SequenceFlow],
        depth: int,
        scope_path: list[str],
        callback: Callable[[WalkerEvent], None],
    ) -> None:
        start_node = self._find_start_event(nodes)
        if not start_node:
            return

        visited: set[str] = set()
        self._walk_from(start_node, nodes, flows, depth, scope_path, visited, callback)

    def _walk_from(
        self,
        node: ProcessNode,
        nodes: dict[str, ProcessNode],
        flows: dict[str, SequenceFlow],
        depth: int,
        scope_path: list[str],
        visited: set[str],
        callback: Callable[[WalkerEvent], None],
    ) -> None:
        if node.id in visited:
            callback(WalkerEvent(
                event_type=WalkerEventType.CYCLE_DETECTED,
                node=node,
                depth=depth,
                scope_path=list(scope_path),
                metadata={"cycle_node": node.id},
            ))
            return

        visited.add(node.id)

        is_subprocess = isinstance(node, SubProcess) and node.node_type == NodeType.SUB_PROCESS
        is_gateway = node.node_type in (
            NodeType.EXCLUSIVE_GATEWAY,
            NodeType.PARALLEL_GATEWAY,
            NodeType.INCLUSIVE_GATEWAY,
        )

        if is_subprocess:
            sub = node
            child_scope = list(scope_path) + [sub.name]

            callback(WalkerEvent(
                event_type=WalkerEventType.ENTER_SCOPE,
                node=sub,
                depth=depth,
                scope_path=child_scope,
            ))

            callback(WalkerEvent(
                event_type=WalkerEventType.ENTER_NODE,
                node=sub,
                depth=depth,
                scope_path=child_scope,
            ))

            # Recurse into subprocess
            self._walk_level(
                nodes=sub.child_nodes,
                flows=sub.child_flows,
                depth=depth + 1,
                scope_path=child_scope,
                callback=callback,
            )

            callback(WalkerEvent(
                event_type=WalkerEventType.EXIT_NODE,
                node=sub,
                depth=depth,
                scope_path=child_scope,
            ))

            callback(WalkerEvent(
                event_type=WalkerEventType.EXIT_SCOPE,
                node=sub,
                depth=depth,
                scope_path=child_scope,
            ))

            # Continue to next nodes after subprocess
            targets = self._get_outgoing_targets(sub, flows, nodes)
            for _flow, target_node in targets:
                self._walk_from(target_node, nodes, flows, depth, scope_path, visited, callback)

        elif is_gateway:
            callback(WalkerEvent(
                event_type=WalkerEventType.ENTER_GATEWAY,
                node=node,
                depth=depth,
                scope_path=list(scope_path),
            ))

            callback(WalkerEvent(
                event_type=WalkerEventType.ENTER_NODE,
                node=node,
                depth=depth,
                scope_path=list(scope_path),
            ))

            callback(WalkerEvent(
                event_type=WalkerEventType.EXIT_NODE,
                node=node,
                depth=depth,
                scope_path=list(scope_path),
            ))

            # Walk ALL outgoing paths (we're mapping knowledge, not executing)
            targets = self._get_outgoing_targets(node, flows, nodes)
            for flow, target_node in targets:
                condition = flow.condition_expression or flow.name or ""

                callback(WalkerEvent(
                    event_type=WalkerEventType.GATEWAY_PATH,
                    node=node,
                    depth=depth,
                    scope_path=list(scope_path),
                    metadata={"condition": condition, "target": target_node.id},
                ))

                self._walk_from(target_node, nodes, flows, depth, scope_path, visited, callback)

        else:
            # Regular node (task, event)
            callback(WalkerEvent(
                event_type=WalkerEventType.ENTER_NODE,
                node=node,
                depth=depth,
                scope_path=list(scope_path),
            ))

            callback(WalkerEvent(
                event_type=WalkerEventType.EXIT_NODE,
                node=node,
                depth=depth,
                scope_path=list(scope_path),
            ))

            # Follow outgoing sequence flows
            targets = self._get_outgoing_targets(node, flows, nodes)
            for _flow, target_node in targets:
                self._walk_from(target_node, nodes, flows, depth, scope_path, visited, callback)

    def _find_start_event(self, nodes: dict[str, ProcessNode]) -> ProcessNode | None:
        for node in nodes.values():
            if node.node_type == NodeType.START_EVENT:
                return node
        return None

    def _get_outgoing_targets(
        self,
        node: ProcessNode,
        flows: dict[str, SequenceFlow],
        nodes: dict[str, ProcessNode],
    ) -> list[tuple[SequenceFlow, ProcessNode]]:
        results: list[tuple[SequenceFlow, ProcessNode]] = []

        for flow in flows.values():
            if flow.source_ref == node.id:
                target = nodes.get(flow.target_ref)
                if target:
                    results.append((flow, target))

        return results
