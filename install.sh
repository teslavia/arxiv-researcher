#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$HOME/.claude/skills"
SOURCE_SKILL_DIR="$SCRIPT_DIR/skills/arxiv-cli"
TARGET_SKILL_DIR="$SKILLS_DIR/arxiv-cli"

echo "Installing arxiv-cli skill and arxiv command..."

mkdir -p "$SKILLS_DIR"

if [ -d "$SOURCE_SKILL_DIR" ]; then
    rm -rf "$TARGET_SKILL_DIR"
    cp -R "$SOURCE_SKILL_DIR" "$TARGET_SKILL_DIR"
    echo "Installed skill: $TARGET_SKILL_DIR"
else
    echo "Warning: $SOURCE_SKILL_DIR not found."
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is required." >&2
    exit 1
fi

echo "Running: python3 -m pip install -e ."
if ! python3 -m pip install -e "$SCRIPT_DIR"; then
    echo "Editable install failed." >&2
    echo "Tip: use a virtual environment, then retry:" >&2
    echo "  python3 -m venv .venv" >&2
    echo "  source .venv/bin/activate" >&2
    echo "  python3 -m pip install -e ." >&2
    exit 1
fi

echo "Done. You can now run: arxiv --help"
