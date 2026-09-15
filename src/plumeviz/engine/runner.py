from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass(frozen=True)
class RunResult:
    status: str
    returncode: int | None
    input_path: Path
    output_path: Path
    stdout: str = ""
    stderr: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "success"


def _append_debug_footer(
    output_path: Path,
    reason: str,
    stdout: str,
    stderr: str,
    input_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    mode = "a" if output_path.exists() else "w"

    with output_path.open(mode, encoding="utf-8", errors="ignore") as f:
        f.write("\n" + "*" * 110 + "\n")
        f.write(f"RUN ENDED EARLY: {reason}\n")
        f.write(f"Input file: {input_path}\n")

        if stdout:
            f.write("\n-- Captured stdout --\n")
            f.write(stdout)

        if stderr:
            f.write("\n-- Captured stderr --\n")
            f.write(stderr)

        f.write("\n")


def run_plumeria(
    executable: str | Path,
    input_path: str | Path,
    output_path: str | Path,
    *,
    timeout: float = 1.0,
    terminate_grace: float = 0.2,
) -> RunResult:
    """
    Run a Plumeria executable against one input file.

    The expected Plumeria output path is supplied explicitly so the caller
    can verify that the Fortran program actually produced output.

    On timeout or failure, a diagnostic footer is appended to the output
    file, preserving the behavior of the existing PlumeViz batch runner.
    """
    executable = Path(executable).expanduser()
    input_path = Path(input_path).expanduser()
    output_path = Path(output_path).expanduser()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        process = subprocess.Popen(
            [str(executable), str(input_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            stdout, stderr = process.communicate(timeout=timeout)

        except subprocess.TimeoutExpired:
            try:
                process.terminate()
                stdout, stderr = process.communicate(timeout=terminate_grace)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()

            _append_debug_footer(
                output_path,
                "timeout",
                stdout,
                stderr,
                input_path,
            )

            return RunResult(
                status="timeout",
                returncode=process.returncode,
                input_path=input_path,
                output_path=output_path,
                stdout=stdout,
                stderr=stderr,
            )

        if process.returncode != 0:
            reason = f"nonzero_exit({process.returncode})"

            _append_debug_footer(
                output_path,
                reason,
                stdout,
                stderr,
                input_path,
            )

            return RunResult(
                status="nonzero_exit",
                returncode=process.returncode,
                input_path=input_path,
                output_path=output_path,
                stdout=stdout,
                stderr=stderr,
            )

        if not output_path.is_file() or output_path.stat().st_size == 0:
            _append_debug_footer(
                output_path,
                "no_output_from_binary",
                stdout,
                stderr,
                input_path,
            )

            return RunResult(
                status="no_output",
                returncode=process.returncode,
                input_path=input_path,
                output_path=output_path,
                stdout=stdout,
                stderr=stderr,
            )

        return RunResult(
            status="success",
            returncode=process.returncode,
            input_path=input_path,
            output_path=output_path,
            stdout=stdout,
            stderr=stderr,
        )

    except Exception as exc:
        stderr = str(exc)

        _append_debug_footer(
            output_path,
            f"exception:{type(exc).__name__}",
            "",
            stderr,
            input_path,
        )

        return RunResult(
            status="exception",
            returncode=None,
            input_path=input_path,
            output_path=output_path,
            stderr=stderr,
        )
