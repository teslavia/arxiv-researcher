#!/usr/bin/env python3
"""Extension system for arxiv-researcher.

Allows users to define custom commands via natural language.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add local directory to path to import utils
sys.path.append(str(Path(__file__).parent))
from utils import ARXIV_ROOT

EXTENSIONS_DIR = ARXIV_ROOT / ".extensions"


def list_extensions() -> list[dict]:
    """List all registered extensions."""
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    extensions = []
    for ext_file in EXTENSIONS_DIR.glob("*.json"):
        try:
            ext = json.loads(ext_file.read_text())
            extensions.append(ext)
        except (json.JSONDecodeError, IOError):
            continue

    return sorted(extensions, key=lambda x: x.get("name", ""))


def create_extension(name: str, instruction: str) -> Path:
    """Create a new extension."""
    EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    ext_file = EXTENSIONS_DIR / f"{name}.json"
    ext_data = {
        "name": name,
        "command": f"/arxiv-{name}",
        "instruction": instruction,
        "created_at": datetime.now().isoformat(),
    }

    ext_file.write_text(json.dumps(ext_data, indent=2, ensure_ascii=False))
    return ext_file


def get_extension(name: str) -> dict | None:
    """Get extension by name."""
    ext_file = EXTENSIONS_DIR / f"{name}.json"
    if ext_file.exists():
        try:
            return json.loads(ext_file.read_text())
        except (json.JSONDecodeError, IOError):
            pass
    return None


def delete_extension(name: str) -> bool:
    """Delete an extension."""
    ext_file = EXTENSIONS_DIR / f"{name}.json"
    if ext_file.exists():
        ext_file.unlink()
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Extension manager")
    parser.add_argument("action", choices=["list", "create", "get", "delete"], help="Action")
    parser.add_argument("name", nargs="?", help="Extension name")
    parser.add_argument("--instruction", "-i", help="Extension instruction")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    args = parser.parse_args()

    if args.action == "list":
        extensions = list_extensions()
        if args.json:
            print(json.dumps(extensions, indent=2, ensure_ascii=False))
        else:
            if not extensions:
                print("No extensions registered.")
                print("Create one: extend.py create <name> -i '<instruction>'")
            else:
                print("📦 Registered Extensions:\n")
                for ext in extensions:
                    print(f"  /arxiv-{ext['name']}")
                    print(f"    {ext['instruction'][:60]}...")
                    print()

    elif args.action == "create":
        if not args.name or not args.instruction:
            print("❌ Usage: extend.py create <name> -i '<instruction>'")
            sys.exit(1)

        ext_file = create_extension(args.name, args.instruction)
        print(f"✅ Created extension: /arxiv-{args.name}")
        print(f"   Instruction: {args.instruction}")
        print(f"   File: {ext_file}")

    elif args.action == "get":
        if not args.name:
            print("❌ Usage: extend.py get <name>")
            sys.exit(1)

        ext = get_extension(args.name)
        if ext:
            if args.json:
                print(json.dumps(ext, indent=2, ensure_ascii=False))
            else:
                print(f"Command: /arxiv-{ext['name']}")
                print(f"Instruction: {ext['instruction']}")
        else:
            print(f"❌ Extension not found: {args.name}")
            sys.exit(1)

    elif args.action == "delete":
        if not args.name:
            print("❌ Usage: extend.py delete <name>")
            sys.exit(1)

        if delete_extension(args.name):
            print(f"✅ Deleted extension: /arxiv-{args.name}")
        else:
            print(f"❌ Extension not found: {args.name}")
            sys.exit(1)


if __name__ == "__main__":
    main()
