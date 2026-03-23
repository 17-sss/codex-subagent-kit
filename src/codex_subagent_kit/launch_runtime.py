from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

from .generator import resolve_scaffold_dir
from .launchers import default_backend_title
from .models import LaunchPlan


class LaunchError(RuntimeError):
    """Raised when launch CLI resolution or execution fails."""


def resolve_launchers_dir(project_root: Path) -> Path:
    return resolve_scaffold_dir(project_root) / "launchers"


def resolve_launcher_script(project_root: Path, backend: str) -> Path:
    if backend not in {"tmux", "cmux"}:
        raise LaunchError(f"unsupported backend: {backend}")

    launchers_dir = resolve_launchers_dir(project_root)
    if not launchers_dir.exists():
        raise LaunchError(
            f"launcher scaffold not found under {launchers_dir}; run project install first"
        )

    script_path = launchers_dir / f"launch-{backend}.sh"
    if not script_path.exists():
        raise LaunchError(
            f"launcher script not found: {script_path}; rerun project install to backfill launchers"
        )
    if not script_path.is_file():
        raise LaunchError(f"expected launcher file but found non-file path: {script_path}")
    return script_path


def build_launch_plan(
    *,
    project_root: Path,
    backend: str,
    name: str | None = None,
    attach: bool = True,
) -> LaunchPlan:
    if backend == "cmux" and not attach:
        raise LaunchError("--no-attach is only supported for the tmux backend")

    script_path = resolve_launcher_script(project_root, backend)
    argv = [str(script_path)]
    cleaned_name = name.strip() if name is not None else ""

    if backend == "tmux":
        if cleaned_name:
            argv.append(cleaned_name)
        elif not attach:
            argv.append(default_backend_title(project_root))
        if not attach:
            argv.append("--no-attach")
    elif cleaned_name:
        argv.append(cleaned_name)

    return LaunchPlan(
        backend=backend,
        script_path=script_path,
        argv=argv,
    )


def render_launch_preview(plan: LaunchPlan) -> str:
    return "\n".join(
        [
            f"backend: {plan.backend}",
            f"launcher: {plan.script_path}",
            f"command: {shlex.join(plan.argv)}",
        ]
    )


def execute_launch_plan(plan: LaunchPlan, *, project_root: Path) -> int:
    try:
        completed = subprocess.run(plan.argv, cwd=project_root, check=False)
    except OSError as exc:
        raise LaunchError(f"failed to execute launcher: {exc}") from exc
    return completed.returncode
