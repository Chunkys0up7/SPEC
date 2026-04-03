# Knowledge Orchestrator

A Python application that takes a BPMN 2.0 process definition as input and generates a **Knowledge Requirements Specification** — a structured analysis mapping every process step to the knowledge, data, procedures, and regulatory controls required to execute it.

## What It Does

Feed it any BPMN XML (no matter how deeply nested) and it produces:

- **Per-step requirements** — what procedures, data, context, and decisions each step needs
- **Regulatory controls** — what frameworks (ITIL, ISO 27001, MISMO, GDPR, SOX, etc.) mandate at each step
- **Gap analysis** — what you have vs. what's missing, with actionable recommendations
- **Cross-step dependencies** — how knowledge flows between steps across subprocess boundaries
- **Procedure expansion** — when a matched procedure itself has requirements (regulatory, compliance, sub-procedures), those cascade into the step
- **Two-dimensional readiness** — knowledge readiness + compliance readiness per step and process-wide

## Quick Start

```bash
# No dependencies required — Python 3.10+ stdlib only
python main.py
```

This runs the sample IT Incident Response process (47 nodes, 4 levels deep) against 10 sample procedures and 2 regulatory frameworks (ITIL v4, ISO 27001).

### Output Formats

```bash
python main.py                              # Console output
python main.py --export-json spec.json      # Structured JSON
python main.py --export-html spec.html      # Interactive HTML visual map
python main.py --verbose                    # Detailed scoring breakdown
```

### Custom Inputs

```bash
python main.py --bpmn your_process.bpmn
python main.py --knowledge your_procedures/
python main.py --regulations your_frameworks/
python main.py --no-expand                  # Skip procedure expansion
python main.py --expand-depth 2             # Limit expansion recursion
```

## Architecture

```
BPMN XML ──────────┐
                    │
Regulatory ─────────├──> Orchestrator ──> Knowledge Requirements Spec
Frameworks          │         │
                    │    ┌────┴────────────────────────┐
Knowledge ──────────┘    │  Per step:                   │
Store                    │  - Infer requirements        │
                         │  - Evaluate regulatory       │
                         │  - Check journey context     │
                         │  - Match knowledge store     │
                         │  - Expand procedures         │
                         │  - Assess gaps               │
                         │  - Record in journey         │
                         └─────────────────────────────┘
```

### Core Components

| Component | Purpose |
|-----------|---------|
| **BPMN Parser** | Parses BPMN 2.0 XML into a process tree with arbitrary nesting depth |
| **Requirements Analyzer** | 4-layer inference: explicit (BPMN docs), journey-aware, type-based, contextual |
| **Knowledge Ranker** | 5-signal scoring: tag overlap, category match, keyword relevance, scope proximity, type fit |
| **Gap Analyzer** | Coverage assessment: MATCHED, PARTIAL, GAP, JOURNEY_SATISFIED |
| **Knowledge Context** | Vertical flow — subprocess scope stack with inheritance and propagation |
| **Journey Context** | Horizontal flow — cross-scope process ledger tracking all step outputs and decisions |
| **Regulatory Analyzer** | Loads framework definitions, fires controls based on domain/tag/type triggers |
| **Procedure Expander** | Recursively expands matched procedures' own requirements (regulatory, sub-procedures) |
| **HTML Renderer** | Self-contained interactive HTML map (zero external dependencies) |

### Two Axes of Knowledge Flow

```
              VERTICAL (scope stack)
              Parent <-> Child subprocess inheritance

===========================================================
HORIZONTAL (journey context)
Step 1 -> Step 2 -> ... -> Step N
Crosses ALL subprocess boundaries, persists entire process
===========================================================
```

**Why both?** A procedure in "Triage" isn't relevant in "Post-Incident Review" (vertical scoping hides it). But the *output* of a triage step (severity = S2) is absolutely relevant to Post-Incident Review (horizontal journey makes it available).

## Adding Your Own Data

### Regulatory Frameworks

Create a JSON file in the regulations directory:

```json
{
  "id": "MISMO",
  "name": "Mortgage Industry Standards Maintenance Organization",
  "version": "3.6",
  "jurisdiction": "US",
  "controls": [
    {
      "control_id": "MISMO-LO-001",
      "title": "Borrower Identity Verification",
      "severity": "mandatory",
      "applies_to": [
        {"trigger_type": "tag_match", "trigger_values": ["borrower-data", "identity"], "match_mode": "any"}
      ],
      "requirements": [
        {"description": "SSN verification through approved source", "category": "PROCEDURE", "tags": ["ssn-verification"], "mandatory": true}
      ],
      "evidence_requirements": ["Verification timestamp", "Source system ID"],
      "failure_consequence": "Loan cannot proceed to underwriting"
    }
  ]
}
```

### Knowledge Items (Procedures)

Create a JSON file in the procedures directory:

```json
{
  "id": "proc_example",
  "title": "Example Procedure",
  "content_summary": "What this procedure covers...",
  "category": "investigation",
  "tags": ["relevant", "tags"],
  "knowledge_type": "procedure",
  "source": "Source Document v1.0",
  "metadata": {"last_updated": "2026-01-15", "owner": "Team Name"},
  "applicable_scopes": ["triage", "investigation"],
  "scope_level": "process",
  "own_requirements": []
}
```

### BPMN Documentation Tags

Annotate BPMN task nodes with structured documentation:

```xml
<bpmn:userTask id="task_example" name="Verify Identity">
  <bpmn:documentation>
    knowledge:identity-verification,kyc,compliance
    data:borrower-ssn,government-id,verification-source
    context:application-status,risk-score
    decision:verification-method,escalation-needed
    output:verification-result,identity-confirmed
  </bpmn:documentation>
</bpmn:userTask>
```

## Project Structure

```
SPEC/
├── docs/product-document.md          # Detailed product document
├── spec/knowledge-orchestrator-spec.md  # Engineering spec (3,930 lines)
├── src/knowledge_orchestrator/       # 16 Python modules
├── samples/
│   ├── incident_response.bpmn       # Sample BPMN (47 nodes, 4 levels)
│   ├── procedures/                   # 10 sample procedures
│   └── regulations/                  # ITIL v4 + ISO 27001
├── main.py                           # CLI entry point
└── requirements.txt                  # No external dependencies
```

## Phase 2 Roadmap

This is Phase 1 — knowledge readiness analysis. Phase 2 transforms the orchestrator into an **agentic execution engine**. Full spec: [`spec/phase2-agentic-execution-spec.md`](spec/phase2-agentic-execution-spec.md)

| Capability | Phase 1 (Current) | Phase 2 (Future) |
|-----------|-------------------|-------------------|
| Requirements | Inferred and displayed | Used to drive actions |
| Knowledge gaps | Reported | Resolved (agent searches external systems) |
| Gateway decisions | All paths explored | Paths selected (LLM + state evaluation) |
| Regulatory controls | Evaluated and reported | Enforced (block non-compliant steps) |
| Step execution | Walked and analyzed | Executed (APIs, scripts, human tasks) |
| Knowledge matching | Tag-based scoring | Semantic search (vector embeddings + LLM) |
| Process learning | Stateless between runs | Adaptive (learns from execution history) |

**Six capability layers:** Knowledge Acquisition Agent, Gateway Decision Engine, Regulatory Compliance Gates, Step Execution Orchestration, LLM-Enhanced Inference, Adaptive Process Learning.

**Eight implementation phases** (2.1 through 2.8) ordered by dependency and risk.

## Requirements

- Python 3.10+
- No external dependencies (stdlib only)
