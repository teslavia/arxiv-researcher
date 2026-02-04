#!/usr/bin/env python3
"""Context management for arxiv-researcher.

Manages the .context file to track the currently active paper.
Supports implicit operations when paper ID is omitted.
"""

import argparse
import json
import sys
from pathlib import Path

ARXIV_ROOT = Path("/Volumes/TMAC/Satoshi/DEV/mac/knowledge/arxiv")
CONTEXT_FILE = ARXIV_ROOT / ".context"


def get_context() -> dict | None:
    """Read current context."""
    if not CONTEXT_FILE.exists():
        return None
    try:
        return json.loads(CONTEXT_FILE.read_text())
    except (json.JSONDecodeError, IOError):
        return None


def set_context(arxiv_id: str, project_path: str) -> None:
    """Set current context."""
    ARXIV_ROOT.mkdir(parents=True, exist_ok=True)
    context = {
        "id": arxiv_id,
        "path": project_path,
    }
    CONTEXT_FILE.write_text(json.dumps(context, indent=2))


def clear_context() -> None:
    """Clear current context."""
    if CONTEXT_FILE.exists():
        CONTEXT_FILE.unlink()


def find_project_by_id(arxiv_id: str) -> Path | None:
    """Find project directory by arXiv ID."""
    for category_dir in ARXIV_ROOT.iterdir():
        if category_dir.is_dir() and not category_dir.name.startswith("."):
            for project_dir in category_dir.iterdir():
                if project_dir.name.startswith(arxiv_id):
                    return project_dir
    return None


def main():
    parser = argparse.ArgumentParser(description="Manage arxiv context")
    parser.add_argument("id", nargs="?", help="arXiv ID to set as context")
    parser.add_argument("--get", "-g", action="store_true", help="Get current context")
    parser.add_argument("--clear", "-c", action="store_true", help="Clear context")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    args = parser.parse_args()

    if args.clear:
        clear_context()
        print("✅ Context cleared")
        return

    if args.get or args.id is None:
        ctx = get_context()
        if ctx is None:
            print("❌ No active context. Use: context.py <arxiv_id>")
            sys.exit(1)
        if args.json:
            print(json.dumps(ctx, indent=2))
        else:
            print(f"📍 Current context: {ctx['id']}")
            print(f"   Path: {ctx['path']}")
        return

    # Set new context
    project_path = find_project_by_id(args.id)
    if project_path is None:
        print(f"❌ Project not found for: {args.id}")
        print("   Run: init_project.py <arxiv_id> first")
        sys.exit(1)

    set_context(args.id, str(project_path))
    print(f"✅ Context set to: {args.id}")
    print(f"   Path: {project_path}")


if __name__ == "__main__":
    main()
