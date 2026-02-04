#!/usr/bin/env python3
"""Read paper and generate SUMMARY.md for arxiv papers."""

import argparse
import json
import re
import sys
from pathlib import Path

ARXIV_ROOT = Path("/Volumes/TMAC/Satoshi/DEV/mac/knowledge/arxiv")
CONTEXT_FILE = ARXIV_ROOT / ".context"


def get_current_context() -> dict | None:
    """Get current paper context."""
    if CONTEXT_FILE.exists():
        try:
            return json.loads(CONTEXT_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            pass
    return None


def find_project(arxiv_id: str | None) -> Path | None:
    """Find project directory."""
    if arxiv_id is None:
        ctx = get_current_context()
        if ctx:
            return Path(ctx["path"])
        return None

    for category_dir in ARXIV_ROOT.iterdir():
        if category_dir.is_dir() and not category_dir.name.startswith("."):
            for project_dir in category_dir.iterdir():
                if project_dir.name.startswith(arxiv_id):
                    return project_dir
    return None


def update_status(project_dir: Path, status: str) -> None:
    """Update project status in info.yaml."""
    info_file = project_dir / "info.yaml"
    if info_file.exists():
        content = info_file.read_text()
        content = re.sub(r'status:\s*"?\w+"?', f'status: "{status}"', content)
        info_file.write_text(content)


def get_paper_info(project_dir: Path) -> dict:
    """Extract paper info from info.yaml."""
    info_file = project_dir / "info.yaml"
    info = {"title": "", "id": "", "authors": []}

    if info_file.exists():
        content = info_file.read_text()

        title_match = re.search(r'title:\s*"([^"]+)"', content)
        if title_match:
            info["title"] = title_match.group(1)

        id_match = re.search(r'id:\s*"([^"]+)"', content)
        if id_match:
            info["id"] = id_match.group(1)

    return info


def main():
    parser = argparse.ArgumentParser(description="Read paper and prepare SUMMARY.md")
    parser.add_argument("id", nargs="?", help="arXiv ID (uses context if omitted)")
    parser.add_argument("--status", "-s", action="store_true", help="Show current status")
    parser.add_argument("--mark-learned", "-m", action="store_true", help="Mark as learned")
    args = parser.parse_args()

    project_dir = find_project(args.id)
    if project_dir is None:
        print("❌ No project found. Specify ID or set context first.")
        sys.exit(1)

    print(f"📁 Project: {project_dir.name}")

    paper_info = get_paper_info(project_dir)
    pdf_path = project_dir / "paper.pdf"
    summary_path = project_dir / "SUMMARY.md"

    if args.status:
        print(f"\n📄 Paper: {paper_info.get('title', 'Unknown')[:60]}...")
        print(f"   PDF: {'✅ exists' if pdf_path.exists() else '❌ missing'}")
        print(f"   SUMMARY.md: {'✅ exists' if summary_path.exists() else '❌ missing'}")
        return

    if args.mark_learned:
        update_status(project_dir, "learned")
        print("✅ Status updated to: learned")
        return

    # Main read workflow
    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        sys.exit(1)

    print(f"\n📖 Paper: {paper_info.get('title', 'Unknown')}")
    print(f"   PDF: {pdf_path}")
    print(f"   SUMMARY: {summary_path}")

    print("\n📋 Next steps:")
    print("   1. Read the PDF using Claude's Read tool")
    print("   2. Fill in SUMMARY.md with structured notes")
    print("   3. Run: python3 read.py --mark-learned")

    print(f"\n💡 Tip: Use Claude to read {pdf_path}")


if __name__ == "__main__":
    main()
