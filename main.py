"""Knowledge Orchestrator — Entry Point."""

from __future__ import annotations

import argparse
import sys

from src.knowledge_orchestrator import __version__
from src.knowledge_orchestrator.bpmn_parser import BPMNParser
from src.knowledge_orchestrator.display import ConsoleDisplay
from src.knowledge_orchestrator.gap_analyzer import GapAnalyzer
from src.knowledge_orchestrator.journey_context import JourneyContext
from src.knowledge_orchestrator.knowledge_context import KnowledgeContextManager
from src.knowledge_orchestrator.knowledge_ranker import KnowledgeRanker
from src.knowledge_orchestrator.knowledge_store import InMemoryKnowledgeStore
from src.knowledge_orchestrator.orchestrator import KnowledgeOrchestrator
from src.knowledge_orchestrator.procedure_expander import ProcedureExpander
from src.knowledge_orchestrator.regulatory_analyzer import RegulatoryAnalyzer
from src.knowledge_orchestrator.requirements_analyzer import RequirementsAnalyzer
from src.knowledge_orchestrator.spec_generator import SpecGenerator


def main() -> None:
    parser = argparse.ArgumentParser(
        description=f"Knowledge Orchestrator v{__version__}"
    )
    parser.add_argument(
        "--bpmn", default="samples/incident_response.bpmn",
        help="Path to BPMN XML file",
    )
    parser.add_argument(
        "--knowledge", default="samples/procedures",
        help="Path to knowledge/procedures directory",
    )
    parser.add_argument(
        "--regulations", default="samples/regulations",
        help="Path to regulatory framework definitions directory",
    )
    parser.add_argument(
        "--export-json", default=None,
        help="Path to export JSON requirements spec",
    )
    parser.add_argument(
        "--export-html", default=None,
        help="Path to export interactive HTML visual spec",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Show detailed scoring breakdown",
    )
    parser.add_argument(
        "--no-expand", action="store_true",
        help="Disable recursive procedure expansion",
    )
    parser.add_argument(
        "--expand-depth", type=int, default=3,
        help="Max recursion depth for procedure expansion (default: 3)",
    )
    args = parser.parse_args()

    print(f"Knowledge Orchestrator v{__version__}")
    print()

    # 1. Load knowledge store
    store = InMemoryKnowledgeStore()
    count = store.load_from_directory(args.knowledge)
    print(f"Loaded {count} knowledge items")

    # 2. Parse BPMN
    bpmn_parser = BPMNParser()
    process = bpmn_parser.parse(args.bpmn)
    print(f"Parsed process: {process.name} ({len(process.nodes)} top-level nodes)")

    # 3. Load regulatory frameworks
    reg_analyzer = RegulatoryAnalyzer()
    reg_count = reg_analyzer.load_frameworks(args.regulations)
    print(f"Loaded {reg_count} regulatory frameworks")

    # 4. Initialize components
    analyzer = RequirementsAnalyzer()
    ranker = KnowledgeRanker()
    gap = GapAnalyzer()
    expander = (
        ProcedureExpander(max_depth=args.expand_depth)
        if not args.no_expand
        else None
    )
    context = KnowledgeContextManager()
    journey = JourneyContext()
    display = ConsoleDisplay(verbose=args.verbose)

    # 5. Create orchestrator, register display
    orchestrator = KnowledgeOrchestrator(
        knowledge_store=store,
        requirements_analyzer=analyzer,
        knowledge_ranker=ranker,
        gap_analyzer=gap,
        context_manager=context,
        journey_context=journey,
        procedure_expander=expander,
        regulatory_analyzer=reg_analyzer,
    )
    orchestrator.register_display(display.on_event)

    # 6. Run
    report = orchestrator.run(process)

    # 7. Display summary
    display.display_summary(report)

    # 8. Optional JSON export
    if args.export_json:
        spec_gen = SpecGenerator()
        spec_gen.export_json(report, args.export_json)
        print(f"JSON spec exported to: {args.export_json}")

    # 9. Optional HTML export
    if args.export_html:
        from src.knowledge_orchestrator.html_renderer import HTMLRenderer
        renderer = HTMLRenderer()
        renderer.export_html(report, journey.get_journey_summary(), args.export_html)
        print(f"HTML spec exported to: {args.export_html}")


if __name__ == "__main__":
    main()
