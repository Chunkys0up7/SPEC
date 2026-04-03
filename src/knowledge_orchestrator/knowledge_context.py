"""
Knowledge Orchestrator — Knowledge Context Manager.

Stack-based scoping that mirrors subprocess nesting. Handles vertical knowledge flow:
parent-to-child inheritance, local scoping, and upward propagation on subprocess exit.
"""

from __future__ import annotations

from .models import KnowledgeContext, KnowledgeItem


class KnowledgeContextManager:

    def __init__(self) -> None:
        self._scope_stack: list[KnowledgeContext] = []
        self._global_scope = KnowledgeContext(scope_name="global", scope_level=-1, scope_domain="global")
        self._scope_history: list[KnowledgeContext] = []

    def initialize_global(self, items: list[KnowledgeItem]) -> None:
        self._global_scope.local_items = list(items)

    def push_scope(self, scope_name: str, scope_level: int, scope_domain: str = "") -> KnowledgeContext:
        inherited: list[KnowledgeItem] = []

        if self._scope_stack:
            parent = self._scope_stack[-1]
            seen_ids: set[str] = set()
            for item in parent.local_items + parent.inherited_items + parent.discovered_items:
                if item.id not in seen_ids:
                    seen_ids.add(item.id)
                    inherited.append(item)

        new_scope = KnowledgeContext(
            scope_name=scope_name,
            scope_level=scope_level,
            scope_domain=scope_domain or scope_name.lower().replace(" ", "-").replace("&", "and"),
            inherited_items=inherited,
        )

        self._scope_stack.append(new_scope)
        return new_scope

    def pop_scope(self) -> KnowledgeContext:
        if not self._scope_stack:
            raise RuntimeError("Cannot pop scope — stack is empty")

        popped = self._scope_stack.pop()

        if self._scope_stack and popped.discovered_items:
            parent = self._scope_stack[-1]
            existing_ids = {item.id for item in parent.discovered_items}
            for item in popped.discovered_items:
                if item.id not in existing_ids:
                    parent.discovered_items.append(item)
                    existing_ids.add(item.id)

        self._scope_history.append(popped)
        return popped

    def current_scope(self) -> KnowledgeContext:
        if not self._scope_stack:
            return self._global_scope
        return self._scope_stack[-1]

    def add_to_current_scope(self, item: KnowledgeItem, propagate_up: bool = False) -> None:
        scope = self.current_scope()
        scope.local_items.append(item)
        if propagate_up:
            scope.discovered_items.append(item)

    def get_all_accessible_knowledge(self) -> list[KnowledgeItem]:
        seen_ids: set[str] = set()
        result: list[KnowledgeItem] = []

        # Current scope local items
        if self._scope_stack:
            current = self._scope_stack[-1]
            for item in current.local_items:
                if item.id not in seen_ids:
                    seen_ids.add(item.id)
                    result.append(item)

            # Inherited items (covers all parent scopes)
            for item in current.inherited_items:
                if item.id not in seen_ids:
                    seen_ids.add(item.id)
                    result.append(item)

            # Discovered items in current scope
            for item in current.discovered_items:
                if item.id not in seen_ids:
                    seen_ids.add(item.id)
                    result.append(item)

        # Walk up the stack for any parent local items not already inherited
        for scope in reversed(self._scope_stack[:-1] if self._scope_stack else []):
            for item in scope.local_items:
                if item.id not in seen_ids:
                    seen_ids.add(item.id)
                    result.append(item)

        # Global scope
        for item in self._global_scope.local_items:
            if item.id not in seen_ids:
                seen_ids.add(item.id)
                result.append(item)

        return result

    def get_scope_path(self) -> list[str]:
        return [scope.scope_name for scope in self._scope_stack]

    def get_scope_depth(self) -> int:
        return len(self._scope_stack)

    def get_full_state_snapshot(self) -> dict:
        return {
            "global": {
                "items": len(self._global_scope.local_items),
            },
            "stack": [
                {
                    "name": scope.scope_name,
                    "level": scope.scope_level,
                    "domain": scope.scope_domain,
                    "local": len(scope.local_items),
                    "inherited": len(scope.inherited_items),
                    "discovered": len(scope.discovered_items),
                }
                for scope in self._scope_stack
            ],
            "depth": len(self._scope_stack),
        }
