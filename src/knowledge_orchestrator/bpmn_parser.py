"""
Knowledge Orchestrator — BPMN 2.0 XML Parser.

Transforms a BPMN 2.0 XML file into a ProcessDefinition tree of ProcessNode
and SubProcess objects, extracting structured documentation tags (knowledge,
data, context, decision, output) from each element's <bpmn:documentation>.
"""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET

from .models import (
    NodeType,
    ProcessDefinition,
    ProcessNode,
    SequenceFlow,
    SubProcess,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class BPMNParseError(Exception):
    """Raised when the BPMN XML is structurally invalid or missing required attributes."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BPMN_NS = "http://www.omg.org/spec/BPMN/20100524/MODEL"
NS_MAP = {"bpmn": BPMN_NS}

ELEMENT_TYPE_MAP: dict[str, NodeType] = {
    "startEvent": NodeType.START_EVENT,
    "endEvent": NodeType.END_EVENT,
    "task": NodeType.TASK,
    "userTask": NodeType.USER_TASK,
    "serviceTask": NodeType.SERVICE_TASK,
    "scriptTask": NodeType.SCRIPT_TASK,
    "manualTask": NodeType.MANUAL_TASK,
    "exclusiveGateway": NodeType.EXCLUSIVE_GATEWAY,
    "parallelGateway": NodeType.PARALLEL_GATEWAY,
    "inclusiveGateway": NodeType.INCLUSIVE_GATEWAY,
    "subProcess": NodeType.SUB_PROCESS,
}


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class BPMNParser:
    """Parses a BPMN 2.0 XML file into a :class:`ProcessDefinition`."""

    # ---- public -----------------------------------------------------------

    def parse(self, xml_path: str) -> ProcessDefinition:
        """Parse a BPMN 2.0 XML file and return a :class:`ProcessDefinition`.

        Parameters
        ----------
        xml_path:
            Filesystem path to the BPMN XML file.

        Returns
        -------
        ProcessDefinition
            Fully populated process tree with nodes, flows, and nested
            sub-processes.

        Raises
        ------
        BPMNParseError
            If the XML is missing a ``<bpmn:process>`` element or a node is
            missing its ``id`` attribute.
        """
        tree = ET.parse(xml_path)  # noqa: S314 — trusted local files only
        root = tree.getroot()

        process_el = root.find(f"{{{BPMN_NS}}}process")
        if process_el is None:
            raise BPMNParseError(
                "No <bpmn:process> element found in the BPMN XML."
            )

        process_id = process_el.get("id", "")
        process_name = process_el.get("name", "Unnamed Process")

        nodes, flows = self._parse_level(process_el)

        description = ""
        doc_el = process_el.find(f"{{{BPMN_NS}}}documentation")
        if doc_el is not None and doc_el.text:
            description = doc_el.text.strip()

        return ProcessDefinition(
            id=process_id,
            name=process_name,
            nodes=nodes,
            flows=flows,
            description=description,
        )

    # ---- level parsing ----------------------------------------------------

    def _parse_level(
        self,
        parent_element: ET.Element,
        parent_subprocess_id: str | None = None,
    ) -> tuple[dict[str, ProcessNode], dict[str, SequenceFlow]]:
        """Recursively parse all child elements of *parent_element*.

        Returns a ``(nodes, flows)`` tuple for this level.  Sub-process
        elements are parsed recursively so their ``child_nodes`` and
        ``child_flows`` are fully populated.
        """
        nodes: dict[str, ProcessNode] = {}
        flows: dict[str, SequenceFlow] = {}

        for child in parent_element:
            # Strip namespace to get the local tag name
            tag = _strip_ns(child.tag)

            if tag == "sequenceFlow":
                flow = self._parse_sequence_flow(child)
                flows[flow.id] = flow
            elif tag in ELEMENT_TYPE_MAP:
                node_type = ELEMENT_TYPE_MAP[tag]
                node = self._parse_node(child, node_type, parent_subprocess_id)
                nodes[node.id] = node
            else:
                # Skip non-element children (documentation, extensionElements, …)
                if tag not in (
                    "documentation",
                    "extensionElements",
                    "incoming",
                    "outgoing",
                    "conditionExpression",
                    "ioSpecification",
                    "dataInputAssociation",
                    "dataOutputAssociation",
                    "laneSet",
                    "dataObject",
                    "dataObjectReference",
                    "dataStoreReference",
                ):
                    logger.warning(
                        "Skipping unrecognized BPMN element <%s> (id=%s)",
                        tag,
                        child.get("id", "?"),
                    )

        # Wire incoming / outgoing flow references onto each node
        for flow in flows.values():
            src = nodes.get(flow.source_ref)
            if src is not None:
                src.outgoing_flows.append(flow.id)
            tgt = nodes.get(flow.target_ref)
            if tgt is not None:
                tgt.incoming_flows.append(flow.id)

        return nodes, flows

    # ---- node parsing -----------------------------------------------------

    def _parse_node(
        self,
        element: ET.Element,
        node_type: NodeType,
        parent_subprocess_id: str | None = None,
    ) -> ProcessNode:
        """Create a :class:`ProcessNode` (or :class:`SubProcess`) from an XML element.

        Raises :class:`BPMNParseError` if the element has no ``id`` attribute.
        """
        node_id = element.get("id")
        if node_id is None:
            raise BPMNParseError(
                f"BPMN element <{_strip_ns(element.tag)}> is missing a "
                f"required 'id' attribute."
            )

        node_name = element.get("name") or f"Unnamed {node_type.value}"

        # Documentation
        doc_el = element.find(f"{{{BPMN_NS}}}documentation")
        documentation: str | None = None
        if doc_el is not None and doc_el.text:
            documentation = doc_el.text.strip()

        # Extract structured tags from documentation
        knowledge_tags = self._extract_knowledge_tags(documentation)
        data_tags = self._extract_data_tags(documentation)
        context_tags = self._extract_context_tags(documentation)
        decision_tags = self._extract_decision_tags(documentation)
        output_tags = self._extract_output_tags(documentation)

        if node_type == NodeType.SUB_PROCESS:
            child_nodes, child_flows = self._parse_level(element, parent_subprocess_id=node_id)

            # Attempt to extract a scope domain from documentation
            scope_domain = ""
            if documentation:
                for line in documentation.splitlines():
                    stripped = line.strip().lower()
                    if stripped.startswith("domain:"):
                        scope_domain = stripped[len("domain:"):].strip()
                        break

            node = SubProcess(
                id=node_id,
                name=node_name,
                node_type=node_type,
                documentation=documentation,
                knowledge_tags=knowledge_tags,
                data_tags=data_tags,
                context_tags=context_tags,
                decision_tags=decision_tags,
                output_tags=output_tags,
                parent_subprocess=parent_subprocess_id,
                child_nodes=child_nodes,
                child_flows=child_flows,
                scope_domain=scope_domain,
            )
        else:
            node = ProcessNode(
                id=node_id,
                name=node_name,
                node_type=node_type,
                documentation=documentation,
                knowledge_tags=knowledge_tags,
                data_tags=data_tags,
                context_tags=context_tags,
                decision_tags=decision_tags,
                output_tags=output_tags,
                parent_subprocess=parent_subprocess_id,
            )

        return node

    # ---- sequence flow parsing --------------------------------------------

    def _parse_sequence_flow(self, element: ET.Element) -> SequenceFlow:
        """Create a :class:`SequenceFlow` from a ``<bpmn:sequenceFlow>`` element."""
        flow_id = element.get("id")
        if flow_id is None:
            raise BPMNParseError(
                "A <sequenceFlow> element is missing a required 'id' attribute."
            )

        name = element.get("name") or None
        source_ref = element.get("sourceRef", "")
        target_ref = element.get("targetRef", "")

        condition_expr: str | None = None
        cond_el = element.find(f"{{{BPMN_NS}}}conditionExpression")
        if cond_el is not None and cond_el.text:
            condition_expr = cond_el.text.strip()

        return SequenceFlow(
            id=flow_id,
            name=name,
            source_ref=source_ref,
            target_ref=target_ref,
            condition_expression=condition_expr,
        )

    # ---- tag extraction helpers -------------------------------------------

    @staticmethod
    def _extract_knowledge_tags(doc_text: str | None) -> list[str]:
        """Extract tags from lines starting with ``knowledge:``."""
        return _extract_tagged_line(doc_text, "knowledge:")

    @staticmethod
    def _extract_data_tags(doc_text: str | None) -> list[str]:
        """Extract tags from lines starting with ``data:``."""
        return _extract_tagged_line(doc_text, "data:")

    @staticmethod
    def _extract_context_tags(doc_text: str | None) -> list[str]:
        """Extract tags from lines starting with ``context:``."""
        return _extract_tagged_line(doc_text, "context:")

    @staticmethod
    def _extract_decision_tags(doc_text: str | None) -> list[str]:
        """Extract tags from lines starting with ``decision:``."""
        return _extract_tagged_line(doc_text, "decision:")

    @staticmethod
    def _extract_output_tags(doc_text: str | None) -> list[str]:
        """Extract tags from lines starting with ``output:``."""
        return _extract_tagged_line(doc_text, "output:")


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _strip_ns(tag: str) -> str:
    """Remove the ``{namespace}`` prefix from an ElementTree tag string."""
    if tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def _extract_tagged_line(doc_text: str | None, prefix: str) -> list[str]:
    """Return comma-separated tags from lines matching *prefix* in *doc_text*.

    Example::

        >>> _extract_tagged_line("knowledge:foo,bar\\ndata:baz", "knowledge:")
        ['foo', 'bar']
    """
    if not doc_text:
        return []

    tags: list[str] = []
    for line in doc_text.splitlines():
        stripped = line.strip()
        lower = stripped.lower()
        if lower.startswith(prefix):
            value_part = stripped[len(prefix):]
            for tag in value_part.split(","):
                tag = tag.strip()
                if tag:
                    tags.append(tag)
    return tags
