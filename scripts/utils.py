#!/usr/bin/env python3
"""Shared utilities for arxiv-researcher scripts."""

import json
import re
import sys
from pathlib import Path
from typing import Any

# Configuration
# TODO: Make this configurable via env var or config file
ARXIV_ROOT = Path("/Volumes/TMAC/Satoshi/DEV/mac/knowledge/arxiv")
CONTEXT_FILE = ARXIV_ROOT / ".context"

def get_current_context() -> dict[str, Any] | None:
    """Get current paper context safely."""
    if CONTEXT_FILE.exists():
        try:
            return json.loads(CONTEXT_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            pass
    return None

def find_project(arxiv_id: str | None = None) -> Path | None:
    """Find project directory by ID or current context."""
    # 1. Try to use explicit ID
    if arxiv_id:
        # Normalize ID (remove v1, v2 suffix if present)
        clean_id = re.sub(r"v\d+$", "", arxiv_id)

        if not ARXIV_ROOT.exists():
            return None

        for category_dir in ARXIV_ROOT.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith("."):
                for project_dir in category_dir.iterdir():
                    if project_dir.name.startswith(clean_id):
                        return project_dir
        return None

    # 2. Fallback to context
    ctx = get_current_context()
    if ctx and "path" in ctx:
        path = Path(ctx["path"])
        if path.exists():
            return path

    return None

def load_info(project_dir: Path) -> dict[str, Any]:
    """Load info.yaml metadata."""
    info_file = project_dir / "info.yaml"
    if not info_file.exists():
        return {}

    content = info_file.read_text()
    info = {}

    # Robust regex parsing
    patterns = {
        "id": r'id:\s*["\']?([^"\'\n]+)',
        "title": r'title:\s*["\']?([^"\'\n]+)',
        "github_repo": r'github_repo:\s*["\']?([^"\'\n]+)',
        "abs_url": r'abs_url:\s*["\']?([^"\'\n]+)',
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            info[key] = match.group(1).strip()

    return info

def update_status(project_dir: Path, status: str) -> None:
    """Update project status in info.yaml."""
    info_file = project_dir / "info.yaml"
    if info_file.exists():
        content = info_file.read_text()
        # Regex to find status line and replace it
        if re.search(r'status:\s*"?\w+"?', content):
            content = re.sub(r'status:\s*"?\w+"?', f'status: "{status}"', content)
        else:
            # Append if not found
            content += f'\nstatus: "{status}"'
        info_file.write_text(content)
