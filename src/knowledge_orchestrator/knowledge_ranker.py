"""
Knowledge Orchestrator — Knowledge Ranker.

Multi-signal relevance scoring engine. Ranks knowledge items against requirements
using 5 weighted signals: tag overlap, category match, keyword relevance,
scope proximity, and type fit.
"""

from __future__ import annotations

import re

from .models import (
    KnowledgeItem,
    KnowledgeScore,
    KnowledgeType,
    NodeType,
    RequirementCategory,
    RequirementItem,
)

STOP_WORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "for", "of", "to", "in", "and", "or", "on", "at", "by", "with",
    "from", "as", "into", "through", "during", "before", "after",
    "this", "that", "these", "those", "it", "its",
})

# Knowledge-type ↔ requirement-category fit matrix
# Rows = KnowledgeType, Cols = RequirementCategory
TYPE_FIT_MATRIX: dict[KnowledgeType, dict[RequirementCategory, float]] = {
    KnowledgeType.PROCEDURE:  {RequirementCategory.PROCEDURE: 1.0, RequirementCategory.DATA: 0.3, RequirementCategory.CONTEXT: 0.3, RequirementCategory.DECISION: 0.5, RequirementCategory.REGULATORY: 0.6},
    KnowledgeType.RUNBOOK:    {RequirementCategory.PROCEDURE: 0.9, RequirementCategory.DATA: 0.4, RequirementCategory.CONTEXT: 0.3, RequirementCategory.DECISION: 0.3, RequirementCategory.REGULATORY: 0.4},
    KnowledgeType.CHECKLIST:  {RequirementCategory.PROCEDURE: 0.8, RequirementCategory.DATA: 0.2, RequirementCategory.CONTEXT: 0.2, RequirementCategory.DECISION: 0.6, RequirementCategory.REGULATORY: 0.5},
    KnowledgeType.POLICY:     {RequirementCategory.PROCEDURE: 0.5, RequirementCategory.DATA: 0.2, RequirementCategory.CONTEXT: 0.5, RequirementCategory.DECISION: 0.8, RequirementCategory.REGULATORY: 0.9},
    KnowledgeType.REFERENCE:  {RequirementCategory.PROCEDURE: 0.3, RequirementCategory.DATA: 0.7, RequirementCategory.CONTEXT: 0.6, RequirementCategory.DECISION: 0.4, RequirementCategory.REGULATORY: 0.5},
    KnowledgeType.FAQ:        {RequirementCategory.PROCEDURE: 0.4, RequirementCategory.DATA: 0.3, RequirementCategory.CONTEXT: 0.7, RequirementCategory.DECISION: 0.3, RequirementCategory.REGULATORY: 0.2},
}

DEFAULT_WEIGHTS = {
    "tag_overlap": 0.30,
    "category_match": 0.25,
    "keyword_relevance": 0.20,
    "scope_proximity": 0.15,
    "type_fit": 0.10,
}


class KnowledgeRanker:

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self._weights = weights or dict(DEFAULT_WEIGHTS)

    def rank(
        self,
        items: list[KnowledgeItem],
        requirement: RequirementItem,
        scope_path: list[str],
        scope_depth: int,
        node_type: NodeType,
    ) -> list[KnowledgeScore]:
        scores: list[KnowledgeScore] = []

        for item in items:
            signal_scores: dict[str, float] = {}
            signal_contributions: dict[str, float] = {}

            signal_scores["tag_overlap"] = self._score_tag_overlap(item, requirement)
            signal_scores["category_match"] = self._score_category_match(item, scope_path)
            signal_scores["keyword_relevance"] = self._score_keyword_relevance(item, requirement)
            signal_scores["scope_proximity"] = self._score_scope_proximity(item, scope_path, scope_depth)
            signal_scores["type_fit"] = self._score_type_fit(item, requirement.category, node_type)

            total = 0.0
            for signal_name, raw_score in signal_scores.items():
                weight = self._weights.get(signal_name, 0.0)
                contribution = raw_score * weight
                signal_contributions[signal_name] = contribution
                total += contribution

            explanation = self._build_explanation(item, requirement, signal_scores)

            scores.append(KnowledgeScore(
                knowledge_item=item,
                total_score=round(total, 4),
                signal_scores=signal_scores,
                signal_contributions=signal_contributions,
                match_explanation=explanation,
            ))

        scores.sort(key=lambda s: s.total_score, reverse=True)
        return scores

    # --- Scoring Signals ---

    def _score_tag_overlap(self, item: KnowledgeItem, requirement: RequirementItem) -> float:
        item_tags = set(t.lower() for t in item.tags)
        req_tags = set(t.lower() for t in requirement.tags)

        if not item_tags or not req_tags:
            return 0.0

        # Exact Jaccard similarity
        intersection = item_tags & req_tags
        union = item_tags | req_tags
        exact_score = len(intersection) / len(union) if union else 0.0

        # Partial tag matching: word-level overlap within tags
        # e.g., "log-analysis" partially matches "log-collection" via shared "log"
        item_words = set()
        for tag in item_tags:
            item_words.update(re.split(r"[-_\s]", tag))
        req_words = set()
        for tag in req_tags:
            req_words.update(re.split(r"[-_\s]", tag))

        word_intersection = item_words & req_words - STOP_WORDS
        word_union = (item_words | req_words) - STOP_WORDS
        partial_score = len(word_intersection) / len(word_union) if word_union else 0.0

        # Blend: 70% exact, 30% partial
        return exact_score * 0.7 + partial_score * 0.3

    def _score_category_match(self, item: KnowledgeItem, scope_path: list[str]) -> float:
        if not scope_path:
            return 0.0

        item_cat = item.category.lower().replace(" ", "-")
        item_scopes = set(s.lower().replace(" ", "-") for s in item.applicable_scopes)
        normalized_path = [s.lower().replace(" ", "-").replace("&", "and") for s in scope_path]

        # Check against scope path from deepest to shallowest
        for i, scope in enumerate(reversed(normalized_path)):
            distance = i  # 0 = current, 1 = parent, 2 = grandparent...
            if item_cat == scope or scope in item_scopes:
                if distance == 0:
                    return 1.0
                elif distance == 1:
                    return 0.7
                else:
                    return 0.3

        return 0.0

    def _score_keyword_relevance(self, item: KnowledgeItem, requirement: RequirementItem) -> float:
        item_text = f"{item.title} {item.content_summary}".lower()
        req_text = requirement.description.lower()

        item_words = set(re.findall(r"\w+", item_text)) - STOP_WORDS
        req_words = set(re.findall(r"\w+", req_text)) - STOP_WORDS

        if not item_words or not req_words:
            return 0.0

        intersection = item_words & req_words
        max_len = max(len(item_words), len(req_words))
        return len(intersection) / max_len if max_len else 0.0

    def _score_scope_proximity(self, item: KnowledgeItem, scope_path: list[str],
                                scope_depth: int) -> float:
        if item.scope_level == "global":
            return 0.5

        item_scopes = set(s.lower().replace(" ", "-") for s in item.applicable_scopes)
        normalized_path = [s.lower().replace(" ", "-").replace("&", "and") for s in scope_path]

        for i, scope in enumerate(reversed(normalized_path)):
            if scope in item_scopes:
                distance = i
                if distance == 0:
                    return 1.0
                elif distance == 1:
                    return 0.7
                elif distance == 2:
                    return 0.4
                else:
                    return 0.2

        return 0.1

    def _score_type_fit(self, item: KnowledgeItem, requirement_category: RequirementCategory,
                         node_type: NodeType) -> float:
        type_row = TYPE_FIT_MATRIX.get(item.knowledge_type)
        if not type_row:
            return 0.3
        return type_row.get(requirement_category, 0.3)

    # --- Explanation ---

    def _build_explanation(self, item: KnowledgeItem, requirement: RequirementItem,
                           signal_scores: dict[str, float]) -> str:
        # Find matched tags
        item_tags = set(t.lower() for t in item.tags)
        req_tags = set(t.lower() for t in requirement.tags)
        matched_tags = item_tags & req_tags

        # Find strongest signal
        strongest = max(signal_scores.items(), key=lambda x: x[1])

        parts = []
        if matched_tags:
            parts.append(f"Tags matched: {', '.join(sorted(matched_tags))}")
        parts.append(f"Category: {item.category}")
        parts.append(f"Primary signal: {strongest[0]} ({strongest[1]:.2f})")

        return " | ".join(parts)
