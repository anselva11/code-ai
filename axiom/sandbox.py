"""Sandbox Execution Environment for AXIOM.
Executes Python code deterministically, capturing outputs, execution time, and metrics.
Adheres to Rule 1: No calculations inside LLM, all calculations must run in sandbox.
"""
import io
import sys
import time
import traceback
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class ExecutionResult:
    success: bool
    stdout: str
    stderr: str
    duration_sec: float
    output_data: Optional[Dict[str, Any]] = None

class PythonSandbox:
    """Safe execution sandbox for quantitative scripts."""
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        start_time = time.time()
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        exec_globals = {
            "__builtins__": __builtins__,
            "context": context or {}
        }
        
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        success = True
        
        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            exec(code, exec_globals)
        except Exception:
            success = False
            traceback.print_exc(file=stderr_capture)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        duration = time.time() - start_time
        return ExecutionResult(
            success=success,
            stdout=stdout_capture.getvalue(),
            stderr=stderr_capture.getvalue(),
            duration_sec=duration,
            output_data=exec_globals.get("results")
        )
