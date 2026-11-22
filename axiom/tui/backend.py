"""Backend Protocol and Data Models for AXIOM TUI.
Separates UI completely from the execution engine.
"""
from dataclasses import dataclass, field
from typing import Protocol, AsyncIterator, List, Dict, Any, Optional, Union
from axiom.tui.events import (
    StageStarted, StageFinished, PlanReady, ToolCall, ToolResult,
    VerdictReady, ReportReady, RunFinished, ErrorEvent
)

Event = Union[
    StageStarted, StageFinished, PlanReady, ToolCall, ToolResult,
    VerdictReady, ReportReady, RunFinished, ErrorEvent
]

@dataclass
class RunSummary:
    id: str
    timestamp: str
    verdict: str
    question: str
    mode: str = "quant"
    audience: str = "analis"

@dataclass
class RunDetail:
    id: str
    question: str
    mode: str
    audience: str
    verdict: str
    plan: List[Dict[str, str]] = field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    critic_findings: List[Dict[str, Any]] = field(default_factory=list)
    report_markdown: str = ""
    chart_files: List[str] = field(default_factory=list)

class AxiomBackend(Protocol):
    """Protocol defining backend operations required by the TUI."""
    async def run(self, question: str, mode: str, audience: str) -> AsyncIterator[Event]:
        """Stream execution events asynchronously."""
        ...

    def approve_plan(self, approved: bool, edited_question: Optional[str] = None) -> None:
        """User feedback for the presented execution plan."""
        ...

    def cancel(self) -> None:
        """Cancel ongoing run execution."""
        ...

    def list_runs(self) -> List[RunSummary]:
        """Retrieve list of historical runs."""
        ...

    def load_run(self, run_id: str) -> RunDetail:
        """Load complete details of a specific past run."""
        ...
