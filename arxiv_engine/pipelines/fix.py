#!/usr/bin/env python3
"""Error capture wrapper that generates a debug prompt."""

from __future__ import annotations

import argparse
import json
import platform
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from arxiv_engine.core.utils import find_project, read_text_safe

FILE_RE = re.compile(r'File "([^"]+)"')


def trim_text(text: str, limit: int = 8000) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def extract_paths_from_command(command: str) -> list[Path]:
    try:
        tokens = shlex.split(command)
    except ValueError:
        return []
    return [Path(t) for t in tokens if t.endswith(".py")]


def extract_paths_from_stderr(stderr: str) -> list[Path]:
    return [Path(m) for m in FILE_RE.findall(stderr)]


def resolve_existing_path(paths: list[Path], base: Path | None) -> Path | None:
    for path in paths:
        candidate = path if path.is_absolute() else (base / path if base else path)
        if candidate.exists():
            return candidate
    return None


def collect_env_info() -> dict[str, Any]:
    info: dict[str, Any] = {
        "python": sys.version.replace("\n", " "),
        "executable": sys.executable,
        "platform": platform.platform(),
    }
    try:
        import torch
        info["torch"] = torch.__version__
        info["cuda_available"] = torch.cuda.is_available()
        info["cuda_device"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    except Exception:
        info["torch"] = None
        info["cuda_available"] = False
        info["cuda_device"] = None
    return info


def build_prompt(
    command: str,
    cwd: Path | None,
    result: subprocess.CompletedProcess[str],
    code_path: Path | None,
    code_text: str,
) -> str:
    env_info = collect_env_info()
    lines = [
        "Task: Diagnose and fix the error produced by the command below.",
        "",
        "Command:", command, "",
        "Working directory:", str(cwd) if cwd else "(unknown)", "",
        f"Return code: {result.returncode}", "",
        "STDERR:", trim_text(result.stderr or "(empty)"), "",
        "STDOUT:", trim_text(result.stdout or "(empty)"), "",
        "Environment:", json.dumps(env_info, indent=2),
    ]

    if code_path and code_text:
        lines += ["", "File context:", str(code_path), "```python", trim_text(code_text), "```"]

    return "\n".join(lines)


def run_command(command: str, cwd: Path | None) -> subprocess.CompletedProcess[str] | None:
    try:
        tokens = shlex.split(command)
    except ValueError as exc:
        print(f"Failed to parse command: {exc}")
        return None
    if not tokens:
        print("Command is empty.")
        return None
    try:
        return subprocess.run(
            tokens, cwd=str(cwd) if cwd else None,
            text=True, capture_output=True, check=False,
        )
    except OSError as exc:
        print(f"Failed to execute command: {exc}")
        return None


def write_prompt_file(project_dir: Path, content: str) -> Path | None:
    playground_dir = project_dir / "playground"
    try:
        playground_dir.mkdir(exist_ok=True)
    except OSError:
        return None
    prompt_path = playground_dir / "DEBUG_PROMPT.txt"
    try:
        prompt_path.write_text(content, encoding="utf-8")
        return prompt_path
    except OSError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Run command and generate debug prompt")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("--id", help="arXiv ID (uses context if omitted)")
    args = parser.parse_args()

    project_dir = find_project(args.id)
    if project_dir is None:
        print("No project found. Specify --id or set context first.")
        sys.exit(1)

    result = run_command(args.command, project_dir)
    if result is None:
        sys.exit(1)

    if result.returncode == 0 and not result.stderr:
        print("Command succeeded; no DEBUG_PROMPT.txt generated.")
        return

    stderr_paths = extract_paths_from_stderr(result.stderr or "")
    cmd_paths = extract_paths_from_command(args.command)
    code_path = resolve_existing_path(stderr_paths, project_dir) or resolve_existing_path(cmd_paths, project_dir)
    code_text = read_text_safe(code_path) if code_path else ""

    prompt = build_prompt(args.command, project_dir, result, code_path, code_text)
    prompt_path = write_prompt_file(project_dir, prompt)
    if prompt_path:
        print(f"Created: {prompt_path}")
    else:
        print("Failed to write DEBUG_PROMPT.txt")


if __name__ == "__main__":
    main()
