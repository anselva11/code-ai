"""LLM Abstraction Layer for AXIOM.
Provides model-agnostic interfaces for planner, agents, and summarizers.
"""
from typing import Protocol, Any, Dict, List
import os

class LLMProvider(Protocol):
    """Protocol for pluggable LLM backends."""
    def complete(self, prompt: str, system: str = "", temperature: float = 0.2) -> str:
        ...

class MockLLM:
    """Mock LLM implementation for testing and development without API keys."""
    def __init__(self, model_name: str = "mock-gpt"):
        self.model_name = model_name

    def complete(self, prompt: str, system: str = "", temperature: float = 0.2) -> str:
        if "rencana" in prompt.lower() or "plan" in prompt.lower():
            return (
                "1. Data Agent: Ingestion & data quality check\n"
                "2. Quant Agent: Factor calculation & statistical significance\n"
                "3. Backtest Agent: Walk-forward simulation\n"
                "4. Critic Agent: Bias detection & verification\n"
                "5. Report Agent: Executive synthesis & risk notes"
            )
        return "Hasil analisis terstruktur AXIOM."

def get_llm() -> LLMProvider:
    """Factory to retrieve configured LLM provider."""
    return MockLLM()
