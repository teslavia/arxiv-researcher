#!/usr/bin/env python3
"""Read paper and generate SUMMARY.md for arxiv papers."""

import argparse
import sys
from pathlib import Path

# Add local directory to path to import utils
sys.path.append(str(Path(__file__).parent))
from utils import find_project, load_info, update_status

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

    paper_info = load_info(project_dir)
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
