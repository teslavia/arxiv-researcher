#!/usr/bin/env python3
"""Lab script generator for arxiv papers - creates playground scripts."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from arxiv_engine.core.utils import ASSETS_DIR, find_project, read_text_safe

TEMPLATES = {
    "demo": "inference_demo_template.py",
    "train": "train_demo_template.py",
    "viz": "viz_attention_template.py",
    "api": "api_template.py",
    "onnx": "onnx_export_template.py",
    "benchmark": "benchmark_template.py",
    "scale": "scale_fsdp_template.py",
    "profile": "profiler_template.py",
    "kernel": "kernel_triton_template.py",
}

OUTPUT_NAMES = {
    "demo": "inference_demo.py",
    "train": "train_demo.py",
    "viz": "viz_attention.py",
    "api": "api.py",
    "onnx": "export_onnx.py",
    "benchmark": "benchmark.py",
    "scale": "scale_fsdp.py",
    "profile": "profiler.py",
    "kernel": "kernel_triton.py",
}


def create_script(project_dir: Path, script_type: str) -> Path | None:
    """Create a script from template."""
    playground_dir = project_dir / "playground"
    playground_dir.mkdir(exist_ok=True)

    template_name = TEMPLATES.get(script_type)
    if not template_name:
        print(f"Unknown script type: {script_type}")
        print(f"   Available: {', '.join(TEMPLATES)}")
        return None

    template_path = ASSETS_DIR / template_name
    output_path = playground_dir / OUTPUT_NAMES[script_type]

    if template_path.exists():
        shutil.copy(template_path, output_path)
        print(f"Created: {output_path}")
        return output_path
    else:
        print(f"Template not found: {template_path}")
        return None


def build_prompt(project_dir: Path, created_scripts: list[Path]) -> str:
    info_text = read_text_safe(project_dir / "info.yaml").strip()
    summary_text = read_text_safe(project_dir / "SUMMARY.md").strip()
    script_list = ", ".join(s.name for s in created_scripts) if created_scripts else "the generated scripts"

    return "\n".join([
        "Please use the paper context below to fill TODOs in the generated scripts.",
        f"Focus on forward pass and core logic for: {script_list}.",
        "",
        "=== info.yaml ===",
        info_text or "(info.yaml not found)",
        "",
        "=== SUMMARY.md ===",
        summary_text or "(SUMMARY.md not found)",
        "",
        "Instruction:",
        "Fill TODO sections in the generated scripts based on the paper context.",
    ])


def write_prompt_file(project_dir: Path, created_scripts: list[Path]) -> Path | None:
    playground_dir = project_dir / "playground"
    prompt_path = playground_dir / "PROMPT_TO_CLAUDE.txt"
    try:
        prompt_path.write_text(build_prompt(project_dir, created_scripts), encoding="utf-8")
        return prompt_path
    except OSError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Create playground scripts")
    parser.add_argument(
        "type", nargs="?",
        choices=list(TEMPLATES) + ["all", "list"],
        default="list",
        help="Script type to create",
    )
    parser.add_argument("--id", help="arXiv ID (uses context if omitted)")
    args = parser.parse_args()

    if args.type == "list":
        print("Available script types:\n")
        for name, template in TEMPLATES.items():
            print(f"   {name:10} - {template}")
        print("\nUsage: arxiv lab <type> [--id <arxiv_id>]")
        return

    project_dir = find_project(args.id)
    if project_dir is None:
        print("No project found. Specify --id or set context first.")
        sys.exit(1)

    print(f"Project: {project_dir.name}")

    created_scripts: list[Path] = []
    if args.type == "all":
        for script_type in TEMPLATES:
            created = create_script(project_dir, script_type)
            if created:
                created_scripts.append(created)
    else:
        created = create_script(project_dir, args.type)
        if created:
            created_scripts.append(created)

    prompt_path = write_prompt_file(project_dir, created_scripts)
    if prompt_path:
        print(f"Created: {prompt_path}")

    print(f"\nScripts created in: {project_dir / 'playground'}")


if __name__ == "__main__":
    main()
