#!/usr/bin/env python3
"""Read paper and generate SUMMARY.md for arxiv papers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from arxiv_engine.core.utils import find_project, load_info, update_status


def main() -> None:
    parser = argparse.ArgumentParser(description="Read paper and prepare SUMMARY.md")
    parser.add_argument("id", nargs="?", help="arXiv ID (uses context if omitted)")
    parser.add_argument("--status", "-s", action="store_true", help="Show current status")
    parser.add_argument("--mark-learned", "-m", action="store_true", help="Mark as learned")
    args = parser.parse_args()

    project_dir = find_project(args.id)
    if project_dir is None:
        print("No project found. Specify ID or set context first.")
        sys.exit(1)

    print(f"Project: {project_dir.name}")

    paper_info = load_info(project_dir)
    pdf_path = project_dir / "paper.pdf"
    summary_path = project_dir / "SUMMARY.md"

    if args.status:
        print(f"\nPaper: {paper_info.get('title', 'Unknown')[:60]}...")
        print(f"   PDF: {'exists' if pdf_path.exists() else 'missing'}")
        print(f"   SUMMARY.md: {'exists' if summary_path.exists() else 'missing'}")
        return

    if args.mark_learned:
        update_status(project_dir, "learned")
        print("Status updated to: learned")
        return

    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        sys.exit(1)

    print(f"\nPaper: {paper_info.get('title', 'Unknown')}")
    print(f"   PDF: {pdf_path}")
    print(f"   SUMMARY: {summary_path}")
    print("\nNext steps:")
    print("   1. Read the PDF")
    print("   2. Fill in SUMMARY.md with structured notes")
    print("   3. Run: arxiv read --mark-learned")


if __name__ == "__main__":
    main()
