"""
Knowledge Orchestrator — Knowledge Store.

Protocol-based interface for knowledge access, plus an in-memory implementation
that loads from JSON files. Designed for future DB/vector-store backends.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol, runtime_checkable

from .models import KnowledgeItem, KnowledgeType, KnowledgeRequirement, RequirementPriority


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------

@runtime_checkable
class KnowledgeStore(Protocol):

    def query(self, tags: list[str], scope: str | None = None,
              category: str | None = None) -> list[KnowledgeItem]: ...

    def get_by_id(self, item_id: str) -> KnowledgeItem | None: ...

    def get_all(self) -> list[KnowledgeItem]: ...

    def get_by_category(self, category: str) -> list[KnowledgeItem]: ...

    def get_by_scope(self, scope: str) -> list[KnowledgeItem]: ...

    def get_by_type(self, knowledge_type: KnowledgeType) -> list[KnowledgeItem]: ...

    def count(self) -> int: ...


# ---------------------------------------------------------------------------
# In-Memory Implementation
# ---------------------------------------------------------------------------

class InMemoryKnowledgeStore:

    def __init__(self) -> None:
        self._items: list[KnowledgeItem] = []
        self._by_id: dict[str, KnowledgeItem] = {}
        self._by_tag: dict[str, list[KnowledgeItem]] = {}
        self._by_category: dict[str, list[KnowledgeItem]] = {}
        self._by_scope: dict[str, list[KnowledgeItem]] = {}
        self._by_type: dict[KnowledgeType, list[KnowledgeItem]] = {}

    def load_from_directory(self, dir_path: str) -> int:
        directory = Path(dir_path)
        if not directory.is_dir():
            raise FileNotFoundError(f"Knowledge directory not found: {dir_path}")

        loaded = 0
        for json_file in sorted(directory.glob("*.json")):
            item = self._load_item(json_file)
            if item:
                self._items.append(item)
                loaded += 1

        self._build_indices()
        return loaded

    def _load_item(self, file_path: Path) -> KnowledgeItem | None:
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Could not load {file_path}: {e}")
            return None

        kt_str = data.get("knowledge_type", "procedure")
        try:
            knowledge_type = KnowledgeType(kt_str)
        except ValueError:
            knowledge_type = KnowledgeType.PROCEDURE

        own_reqs = []
        for req_data in data.get("own_requirements", []):
            priority_str = req_data.get("priority", "important")
            try:
                priority = RequirementPriority(priority_str)
            except ValueError:
                priority = RequirementPriority.IMPORTANT

            own_reqs.append(KnowledgeRequirement(
                requirement_type=req_data.get("requirement_type", "procedure"),
                description=req_data.get("description", ""),
                tags=req_data.get("tags", []),
                priority=priority,
                regulatory_framework=req_data.get("regulatory_framework"),
                mandatory=req_data.get("mandatory", False),
            ))

        return KnowledgeItem(
            id=data["id"],
            title=data["title"],
            content_summary=data.get("content_summary", ""),
            category=data.get("category", ""),
            tags=data.get("tags", []),
            knowledge_type=knowledge_type,
            source=data.get("source", ""),
            metadata=data.get("metadata", {}),
            applicable_scopes=data.get("applicable_scopes", []),
            scope_level=data.get("scope_level", "process"),
            own_requirements=own_reqs,
        )

    def _build_indices(self) -> None:
        self._by_id.clear()
        self._by_tag.clear()
        self._by_category.clear()
        self._by_scope.clear()
        self._by_type.clear()

        for item in self._items:
            self._by_id[item.id] = item

            for tag in item.tags:
                self._by_tag.setdefault(tag, []).append(item)

            if item.category:
                self._by_category.setdefault(item.category, []).append(item)

            for scope in item.applicable_scopes:
                self._by_scope.setdefault(scope, []).append(item)

            self._by_type.setdefault(item.knowledge_type, []).append(item)

    # --- Query methods ---

    def query(self, tags: list[str], scope: str | None = None,
              category: str | None = None) -> list[KnowledgeItem]:
        if not tags:
            return []

        seen_ids: set[str] = set()
        candidates: list[KnowledgeItem] = []

        for tag in tags:
            for item in self._by_tag.get(tag, []):
                if item.id not in seen_ids:
                    seen_ids.add(item.id)
                    candidates.append(item)

        if scope:
            scope_lower = scope.lower()
            candidates = [
                item for item in candidates
                if scope_lower in [s.lower() for s in item.applicable_scopes]
                or item.scope_level == "global"
            ]

        if category:
            cat_lower = category.lower()
            candidates = [
                item for item in candidates
                if item.category.lower() == cat_lower
            ]

        candidates.sort(
            key=lambda item: sum(1 for t in tags if t in item.tags),
            reverse=True,
        )

        return candidates

    def get_by_id(self, item_id: str) -> KnowledgeItem | None:
        return self._by_id.get(item_id)

    def get_all(self) -> list[KnowledgeItem]:
        return list(self._items)

    def get_by_category(self, category: str) -> list[KnowledgeItem]:
        return list(self._by_category.get(category, []))

    def get_by_scope(self, scope: str) -> list[KnowledgeItem]:
        scope_lower = scope.lower()
        results: list[KnowledgeItem] = []
        seen: set[str] = set()

        for item in self._by_scope.get(scope, []):
            if item.id not in seen:
                seen.add(item.id)
                results.append(item)

        for item in self._items:
            if item.scope_level == "global" and item.id not in seen:
                seen.add(item.id)
                results.append(item)

        return results

    def get_by_type(self, knowledge_type: KnowledgeType) -> list[KnowledgeItem]:
        return list(self._by_type.get(knowledge_type, []))

    def count(self) -> int:
        return len(self._items)
