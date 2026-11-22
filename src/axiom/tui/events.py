"""Event definitions for AXIOM TUI.
All asynchronous messages from the backend to the UI are strongly typed dataclasses.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class StageStarted:
    stage: str  # "Rencana", "Analisa", "Critic", "Laporan"

@dataclass
class StageFinished:
    stage: str
    duration: float

@dataclass
class PlanReady:
    plan: List[Dict[str, str]]
    summary: str

@dataclass
class ToolCall:
    code: str
    step: int
    agent: str

@dataclass
class ToolResult:
    output: str
    step: int
    error: bool = False

@dataclass
class VerdictReady:
    verdict: str  # "LULUS", "LULUS DENGAN CATATAN", "GAGAL"
    findings: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ReportReady:
    markdown: str

@dataclass
class RunFinished:
    run_id: str
    success: bool = True

@dataclass
class ErrorEvent:
    message: str
    hint: str
