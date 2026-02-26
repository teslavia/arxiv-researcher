#!/usr/bin/env python3
"""Deployment scaffold generator for arxiv papers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from arxiv_engine.core.utils import ASSETS_DIR, find_project

TARGET_TEMPLATES: dict[str, str] = {
    "coreml": "deploy_coreml_template.py",
    "tensorrt": "deploy_tensorrt_template.py",
    "rknn": "deploy_rknn_template.py",
}

TARGET_OUTPUTS: dict[str, str] = {
    "coreml": "deploy_coreml.py",
    "tensorrt": "deploy_tensorrt.py",
    "rknn": "deploy_rknn.py",
}

SUPPORTED_TARGETS = tuple(TARGET_TEMPLATES)
SUPPORTED_QUANTIZE = ("fp16", "int8")


def read_text_safe(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def write_text_safe(path: Path, content: str) -> bool:
    try:
        path.write_text(content, encoding="utf-8")
        return True
    except OSError:
        return False


def render_template(template_path: Path, quantize: str | None) -> str | None:
    content = read_text_safe(template_path)
    if content is None:
        return None
    quantize_literal = f'"{quantize}"' if quantize else "None"
    return content.replace("{{QUANTIZE}}", quantize_literal)


def create_deploy_script(project_dir: Path, target: str, quantize: str | None) -> Path | None:
    playground_dir = project_dir / "playground"
    try:
        playground_dir.mkdir(exist_ok=True)
    except OSError:
        print("Failed to create playground directory.")
        return None

    template_name = TARGET_TEMPLATES.get(target)
    output_name = TARGET_OUTPUTS.get(target)
    if not template_name or not output_name:
        print(f"Unknown target: {target}")
        return None

    template_path = ASSETS_DIR / template_name
    if not template_path.exists():
        print(f"Template not found: {template_path}")
        return None

    rendered = render_template(template_path, quantize)
    if rendered is None:
        print("Failed to read template.")
        return None

    output_path = playground_dir / output_name
    if not write_text_safe(output_path, rendered):
        print("Failed to write deploy script.")
        return None

    print(f"Created: {output_path}")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create deployment scaffold")
    parser.add_argument("--target", choices=SUPPORTED_TARGETS, default="coreml")
    parser.add_argument("--quantize", choices=SUPPORTED_QUANTIZE)
    parser.add_argument("--id", help="arXiv ID (uses context if omitted)")
    args = parser.parse_args()

    project_dir = find_project(args.id)
    if project_dir is None:
        print("No project found. Specify --id or set context first.")
        sys.exit(1)

    print(f"Project: {project_dir.name}")
    create_deploy_script(project_dir, args.target, args.quantize)


if __name__ == "__main__":
    main()
