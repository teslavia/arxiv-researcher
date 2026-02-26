#!/usr/bin/env python3
"""Context management for arxiv-researcher."""

from __future__ import annotations

import argparse
import json
import sys

from arxiv_engine.core.utils import ARXIV_ROOT, CONTEXT_FILE


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
    context = {"id": arxiv_id, "path": project_path}
    CONTEXT_FILE.write_text(json.dumps(context, indent=2))


def clear_context() -> None:
    """Clear current context."""
    if CONTEXT_FILE.exists():
        CONTEXT_FILE.unlink()


def find_project_by_id(arxiv_id: str) -> "Path | None":
    from pathlib import Path

    for category_dir in ARXIV_ROOT.iterdir():
        if category_dir.is_dir() and not category_dir.name.startswith("."):
            for project_dir in category_dir.iterdir():
                if project_dir.name.startswith(arxiv_id):
                    return project_dir
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage arxiv context")
    parser.add_argument("id", nargs="?", help="arXiv ID to set as context")
    parser.add_argument("--get", "-g", action="store_true", help="Get current context")
    parser.add_argument("--clear", "-c", action="store_true", help="Clear context")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    args = parser.parse_args()

    if args.clear:
        clear_context()
        print("Context cleared")
        return

    if args.get or args.id is None:
        ctx = get_context()
        if ctx is None:
            print("No active context. Use: arxiv context <arxiv_id>")
            sys.exit(1)
        if args.json:
            print(json.dumps(ctx, indent=2))
        else:
            print(f"Current context: {ctx['id']}")
            print(f"   Path: {ctx['path']}")
        return

    project_path = find_project_by_id(args.id)
    if project_path is None:
        print(f"Project not found for: {args.id}")
        print("   Run: arxiv init <arxiv_id> first")
        sys.exit(1)

    set_context(args.id, str(project_path))
    print(f"Context set to: {args.id}")
    print(f"   Path: {project_path}")


if __name__ == "__main__":
    main()
