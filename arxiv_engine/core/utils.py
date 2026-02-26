"""Shared utilities for arxiv-engine pipelines."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

# ── Package-level paths ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets" / "templates"

# ── User-level config ────────────────────────────────────────────────
CONFIG_FILE = Path.home() / ".arxiv_researcher_config.json"
DEFAULT_ROOT = Path.home() / "knowledge" / "arxiv"


def get_arxiv_root() -> Path:
    """Get arXiv root directory from config or default."""
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
            if "arxiv_root" in config:
                return Path(config["arxiv_root"]).expanduser()
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_ROOT


ARXIV_ROOT = get_arxiv_root()
CONTEXT_FILE = ARXIV_ROOT / ".context"


# ── Context helpers ──────────────────────────────────────────────────

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
    if arxiv_id:
        clean_id = re.sub(r"v\d+$", "", arxiv_id)
        if not ARXIV_ROOT.exists():
            return None
        for category_dir in ARXIV_ROOT.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith("."):
                for project_dir in category_dir.iterdir():
                    if project_dir.name.startswith(clean_id):
                        return project_dir
        return None

    ctx = get_current_context()
    if ctx and "path" in ctx:
        path = Path(ctx["path"])
        if path.exists():
            return path
    return None


def load_info(project_dir: Path) -> dict[str, Any]:
    """Load info.yaml metadata via regex parsing."""
    info_file = project_dir / "info.yaml"
    if not info_file.exists():
        return {}

    content = info_file.read_text()
    info: dict[str, Any] = {}
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
        if re.search(r'status:\s*"?\w+"?', content):
            content = re.sub(r'status:\s*"?\w+"?', f'status: "{status}"', content)
        else:
            content += f'\nstatus: "{status}"'
        info_file.write_text(content)


def read_text_safe(path: Path) -> str:
    """Read text file, returning empty string on failure."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def update_global_readme() -> None:
    """Regenerate the global README.md index under ARXIV_ROOT."""
    from datetime import datetime

    readme_path = ARXIV_ROOT / "README.md"
    if not ARXIV_ROOT.exists():
        return

    projects: list[dict[str, Any]] = []
    for category_dir in sorted(ARXIV_ROOT.iterdir()):
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue
        for project_dir in sorted(category_dir.iterdir()):
            info_file = project_dir / "info.yaml"
            if not info_file.exists():
                continue
            content = info_file.read_text()
            status_match = re.search(r'status:\s*"?(\w+)"?', content)
            status = status_match.group(1) if status_match else "unknown"
            title_match = re.search(r'title:\s*"([^"]+)"', content)
            title = title_match.group(1)[:60] if title_match else project_dir.name
            projects.append({
                "category": category_dir.name,
                "name": project_dir.name,
                "path": project_dir.relative_to(ARXIV_ROOT),
                "status": status,
                "title": title,
            })

    status_emoji = {
        "downloaded": "\U0001f4e5",
        "learned": "\U0001f4d6",
        "reproduced": "\U0001f52c",
        "optimized": "\U0001f680",
    }

    lines = [
        "# arXiv Research Lab",
        "",
        f"> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Progress",
        "",
        "| Status | Count |",
        "|--------|-------|",
    ]

    status_counts: dict[str, int] = {}
    for p in projects:
        status_counts[p["status"]] = status_counts.get(p["status"], 0) + 1
    for s, count in sorted(status_counts.items()):
        emoji = status_emoji.get(s, "\u2753")
        lines.append(f"| {emoji} {s.title()} | {count} |")

    lines.append(f"\n**Total**: {len(projects)} papers\n\n## Papers\n")

    current_cat = None
    for p in projects:
        if p["category"] != current_cat:
            current_cat = p["category"]
            lines.append(f"\n### {current_cat}\n")
        emoji = status_emoji.get(p["status"], "\u2753")
        lines.append(f"- {emoji} [{p['name']}]({p['path']}) - {p['title']}")

    readme_path.write_text("\n".join(lines) + "\n")
    print(f"Updated global index: {readme_path}")
