#!/usr/bin/env python3
"""Dataset scaffold generator for arxiv papers."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from arxiv_engine.core.utils import find_project, load_info, read_text_safe

ABSTRACT_HEADING_RE = re.compile(r"^#{1,3}\s*abstract\s*$", re.IGNORECASE)
NEXT_SECTION_RE = re.compile(r"^#{1,3}\s+", re.IGNORECASE)
PDF_ABSTRACT_RE = re.compile(
    r"\babstract\b\s*[:\-]?\s*(.+?)(\n\s*\n|\n\s*\d+\.?\s+introduction|\n\s*1\s+introduction)",
    re.IGNORECASE | re.DOTALL,
)


def extract_abstract_from_summary(summary_text: str) -> str:
    lines = summary_text.splitlines()
    abstract_lines: list[str] = []
    in_section = False
    for line in lines:
        if not in_section and ABSTRACT_HEADING_RE.match(line.strip()):
            in_section = True
            continue
        if in_section:
            if NEXT_SECTION_RE.match(line.strip()):
                break
            abstract_lines.append(line)
    abstract = "\n".join(abstract_lines).strip()
    if abstract:
        return abstract

    match = re.search(r"\babstract\b\s*[:\-]?\s*(.+)", summary_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


def extract_abstract_from_pdf(pdf_path: Path) -> str:
    if not pdf_path.exists():
        return ""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "paper.txt"
            subprocess.run(
                ["pdftotext", "-f", "1", "-l", "2", str(pdf_path), str(output_path)],
                check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30,
            )
            text = read_text_safe(output_path)
    except FileNotFoundError:
        print("pdftotext not found; install poppler to extract abstracts.")
        return ""
    except (OSError, subprocess.SubprocessError):
        return ""

    match = PDF_ABSTRACT_RE.search(text)
    if not match:
        return ""
    return " ".join(match.group(1).strip().split())


def build_sft_items(summary: str, abstract: str, info: dict[str, Any]) -> list[dict[str, Any]]:
    title = str(info.get("title", ""))
    paper_id = str(info.get("id", ""))
    context = "\n\n".join(part for part in [abstract, summary] if part).strip()
    if not context:
        context = "(no summary or abstract available)"

    return [
        {
            "instruction": "Summarize the paper in 5 bullet points.",
            "input": context, "output": "TODO",
            "meta": {"paper_id": paper_id, "title": title},
        },
        {
            "instruction": "Explain the core method and training pipeline.",
            "input": context, "output": "TODO",
            "meta": {"paper_id": paper_id, "title": title},
        },
        {
            "instruction": "Write pseudocode for the model forward pass.",
            "input": context, "output": "TODO",
            "meta": {"paper_id": paper_id, "title": title},
        },
    ]


def write_jsonl(path: Path, items: list[dict[str, Any]]) -> bool:
    try:
        with path.open("w", encoding="utf-8") as handle:
            for item in items:
                handle.write(json.dumps(item, ensure_ascii=False) + "\n")
        return True
    except OSError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SFT dataset scaffold")
    parser.add_argument("--id", help="arXiv ID (uses context if omitted)")
    parser.add_argument("--output", type=Path, help="Output JSONL path")
    args = parser.parse_args()

    project_dir = find_project(args.id)
    if project_dir is None:
        print("No project found. Specify --id or set context first.")
        sys.exit(1)

    summary_path = project_dir / "SUMMARY.md"
    pdf_path = project_dir / "paper.pdf"
    playground_dir = project_dir / "playground"
    try:
        playground_dir.mkdir(exist_ok=True)
    except OSError:
        print("Failed to create playground directory.")
        sys.exit(1)

    summary_text = read_text_safe(summary_path)
    summary_abstract = extract_abstract_from_summary(summary_text)
    pdf_abstract = extract_abstract_from_pdf(pdf_path)

    abstract = summary_abstract or pdf_abstract
    info = load_info(project_dir)

    items = build_sft_items(summary_text, abstract, info)
    output_path = args.output or (playground_dir / "dataset_sft.jsonl")
    if write_jsonl(output_path, items):
        print(f"Created dataset scaffold: {output_path}")
    else:
        print("Failed to write dataset scaffold.")


if __name__ == "__main__":
    main()
