"""Subprocess-based Python function executor with timeout.

WARNING: This module uses subprocess for prototyping and testing only.
It does NOT provide security isolation.  Production use requires
Docker, nsjail, or E2B sandboxing to prevent arbitrary code execution
from compromising the host.

The sandbox:
1. Writes the candidate function to a temporary file.
2. Executes it in a subprocess with a timeout.
3. Captures stdout or exception information.
4. Returns a SandboxResult.
"""

from __future__ import annotations

import dataclasses
import subprocess
import sys
import tempfile
import textwrap
import time
from typing import Any, Callable, Optional


@dataclasses.dataclass(frozen=True)
class SandboxResult:
    """Result of executing a candidate function in the sandbox.

    Attributes:
        success: whether execution completed without error.
        output: the function's return value (as a string repr) if success.
        error: error message if not success.
        timed_out: whether execution exceeded the timeout.
        elapsed_ms: wall-clock time in milliseconds.
        stdout: captured standard output.
    """

    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    timed_out: bool = False
    elapsed_ms: float = 0.0
    stdout: str = ""


# ---------------------------------------------------------------------------
# Minimal subprocess executor
# ---------------------------------------------------------------------------

_DEFAULT_TIMEOUT_SEC = 5.0
_MAX_OUTPUT_BYTES = 10_000


def _build_runner_script(
    candidate_code: str, call_str: str
) -> str:
    """Wrap candidate code and a call into a self-contained script."""
    return textwrap.dedent(f"""\
import sys
import traceback

{candidate_code}

try:
    result = {call_str}
    print(repr(result))
except Exception:
    traceback.print_exc()
    sys.exit(1)
""")


def execute_candidate(
    candidate_code: str,
    args: tuple,
    kwargs: dict | None = None,
    timeout_sec: float = _DEFAULT_TIMEOUT_SEC,
) -> SandboxResult:
    """Execute a candidate function with given arguments in a subprocess.

    The candidate_code must define a callable named ``solve`` or the name given.
    By convention the code block should define ``def solve(...)``.

    Args:
        candidate_code: Python source code defining the candidate function.
        args: positional arguments to pass.
        kwargs: keyword arguments to pass.
        timeout_sec: maximum wall-clock time.

    Returns:
        SandboxResult with execution outcome.
    """
    kwargs = kwargs or {}
    kwargs_repr = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    args_repr = ", ".join(repr(a) for a in args)
    if args_repr and kwargs_repr:
        call_str = f"solve({args_repr}, {kwargs_repr})"
    elif args_repr:
        call_str = f"solve({args_repr})"
    elif kwargs_repr:
        call_str = f"solve({kwargs_repr})"
    else:
        call_str = "solve()"

    script = _build_runner_script(candidate_code, call_str)

    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            timeout=timeout_sec,
            text=True,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
    except subprocess.TimeoutExpired:
        elapsed_ms = timeout_sec * 1000.0
        return SandboxResult(
            success=False,
            timed_out=True,
            elapsed_ms=elapsed_ms,
            error="TimeoutExpired",
        )

    stdout = (proc.stdout or "")[: _MAX_OUTPUT_BYTES]
    stderr = (proc.stderr or "")[: _MAX_OUTPUT_BYTES]

    if proc.returncode == 0:
        output = stdout.strip()
        return SandboxResult(
            success=True,
            output=output,
            elapsed_ms=elapsed_ms,
            stdout=stdout,
        )
    else:
        return SandboxResult(
            success=False,
            error=stderr or f"Return code: {proc.returncode}",
            elapsed_ms=elapsed_ms,
            stdout=stdout,
        )


def execute_candidate_on_example(
    candidate_code: str,
    example: Any,  # frontier_delta.tasks.Example (avoid circular import)
    timeout_sec: float = _DEFAULT_TIMEOUT_SEC,
) -> SandboxResult:
    """Execute a candidate function on a single Example.

    The Example is expected to have ``.args`` (tuple), ``.kwargs`` (tuple of
    (str, object) pairs), and ``.output`` (expected value).

    Returns:
        SandboxResult.  The caller must compare result.output to the expected
        example.output.
    """
    kwargs = dict(example.kwargs) if example.kwargs else {}
    return execute_candidate(
        candidate_code,
        args=example.args,
        kwargs=kwargs,
        timeout_sec=timeout_sec,
    )
