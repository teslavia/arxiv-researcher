#!/usr/bin/env python3
"""Initialize arXiv paper project space."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from arxiv_engine.core.utils import ARXIV_ROOT, CONTEXT_FILE, update_global_readme


def fetch_paper_info(arxiv_id: str) -> dict:
    """Fetch paper metadata from arXiv API."""
    arxiv_id = re.sub(r"v\d+$", "", arxiv_id)

    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        xml_data = resp.read().decode("utf-8")

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml_data)
    entry = root.find("atom:entry", ns)

    if entry is None:
        raise ValueError(f"Paper not found: {arxiv_id}")

    title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
    summary = entry.find("atom:summary", ns).text.strip()
    published = entry.find("atom:published", ns).text[:10]
    authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
    categories = [c.get("term") for c in entry.findall("atom:category", ns)]

    return {
        "id": arxiv_id,
        "title": title,
        "summary": summary,
        "published": published,
        "authors": authors,
        "categories": categories,
        "primary_category": categories[0] if categories else "unknown",
        "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
        "abs_url": f"https://arxiv.org/abs/{arxiv_id}",
    }


def to_snake_case(text: str) -> str:
    """Convert title to snake_case directory name."""
    clean = re.sub(r"[^\w\s]", "", text)
    words = clean.split()[:6]
    return "_".join(words)


def create_project(info: dict) -> Path:
    """Create project directory structure."""
    year_month = info["published"][:7].replace("-", "")
    year_short = year_month[2:6]
    category = info["primary_category"].split(".")[0].upper()

    parent_dir = ARXIV_ROOT / f"{year_short}.{category}"
    project_name = f"{info['id']}_{to_snake_case(info['title'])}"
    project_dir = parent_dir / project_name

    project_dir.mkdir(parents=True, exist_ok=True)
    for sub in ("src", "models", "data", "playground", "contribution"):
        (project_dir / sub).mkdir(exist_ok=True)

    (project_dir / ".gitignore").write_text(
        "# Large files - do not commit\n"
        "models/\ndata/\n*.ckpt\n*.bin\n*.safetensors\n*.pt\n*.pth\n"
        "__pycache__/\n.ipynb_checkpoints/\n"
    )

    first_author = info["authors"][0].split()[-1] if info["authors"] else "Unknown"
    year = info["published"][:4]
    bibtex = (
        f"@article{{{first_author.lower()}{year}{info['id'].replace('.', '')},\n"
        f"  title={{{info['title']}}},\n"
        f"  author={{{' and '.join(info['authors'][:5])}}},\n"
        f"  journal={{arXiv preprint arXiv:{info['id']}}},\n"
        f"  year={{{year}}}\n"
        f"}}"
    )

    info_yaml = (
        f"# Paper Metadata\n"
        f'id: "{info["id"]}"\n'
        f'title: "{info["title"]}"\n'
        f"authors: {info['authors'][:5]}\n"
        f'published: "{info["published"]}"\n'
        f"categories: {info['categories']}\n"
        f'status: "downloaded"\n\n'
        f"tags: []\n\n"
        f'pdf_url: "{info["pdf_url"]}"\n'
        f'abs_url: "{info["abs_url"]}"\n'
        f'github_repo: ""\n'
        f'huggingface_model: ""\n\n'
        f"metrics:\n"
        f"  inference_latency_ms: null\n"
        f"  gpu_memory_mb: null\n"
        f"  accuracy: null\n\n"
        f'created_at: "{datetime.now().isoformat()}"\n\n'
        f"bibtex: |\n"
    )
    for line in bibtex.split("\n"):
        info_yaml += f"  {line}\n"

    (project_dir / "info.yaml").write_text(info_yaml)

    summary_template = (
        f"# {info['title']}\n\n"
        f"**arXiv**: [{info['id']}]({info['abs_url']})\n"
        f"**Authors**: {', '.join(info['authors'][:3])}{'...' if len(info['authors']) > 3 else ''}\n"
        f"**Status**: Downloaded\n\n"
        f"## Context\n\n## Key Insight\n\n## Method\n\n"
        f"### Architecture\n\n### Key Equations\n\n"
        f"```python\n# Pseudo-code implementation\n```\n\n"
        f"## Results\n\n| Method | Metric1 | Metric2 |\n|--------|---------|---------|"
        f"\n| Baseline | - | - |\n| This Paper | - | - |\n\n"
        f"## Takeaways\n\n## Open Questions\n\n## Related Papers\n"
    )
    (project_dir / "SUMMARY.md").write_text(summary_template)

    repro_template = (
        f"# Reproduction Log: {info['title']}\n\n"
        f"**arXiv**: [{info['id']}]({info['abs_url']})\n"
        f"**Status**: Reproducing\n\n"
        f"## Environment\n- **OS**:\n- **Python**:\n- **CUDA**:\n- **GPU**:\n\n"
        f"## Setup Steps\n```bash\ngit clone <repo_url> src/\ncd src && pip install -r requirements.txt\n```\n\n"
        f"## Performance Metrics\n| Metric | Paper | Reproduced | Notes |\n"
        f"|--------|-------|------------|-------|\n\n"
        f"## Run Log\n| Date | Command | Result | Notes |\n|------|---------|--------|-------|\n\n"
        f"## Issues Encountered\n\n## Sanity Check\n"
        f"- [ ] Environment setup successful\n- [ ] Model weights downloaded\n"
        f"- [ ] inference_demo.py runs without error\n- [ ] Output matches expected format\n"
    )
    (project_dir / "REPRODUCTION.md").write_text(repro_template)

    return project_dir


def download_pdf(url: str, dest: Path) -> bool:
    """Download PDF file."""
    try:
        print("Downloading PDF...")
        subprocess.run(["curl", "-L", "-o", str(dest), url], check=True, timeout=120)
        return dest.exists() and dest.stat().st_size > 1000
    except Exception as e:
        print(f"PDF download failed: {e}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize arXiv paper project")
    parser.add_argument("arxiv_id", help="arXiv ID (e.g., 2401.12345) or URL")
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF download")
    parser.add_argument("--update-index", action="store_true", help="Only update global README")
    args = parser.parse_args()

    if args.update_index:
        update_global_readme()
        return

    arxiv_id = args.arxiv_id
    if "arxiv.org" in arxiv_id:
        match = re.search(r"(\d{4}\.\d{4,5})", arxiv_id)
        if match:
            arxiv_id = match.group(1)

    print(f"Fetching metadata for {arxiv_id}...")
    info = fetch_paper_info(arxiv_id)
    print(f"{info['title'][:70]}...")

    project_dir = create_project(info)
    print(f"Created: {project_dir}")

    if not args.no_pdf:
        pdf_path = project_dir / "paper.pdf"
        if download_pdf(info["pdf_url"], pdf_path):
            print(f"PDF saved: {pdf_path}")

    context_file = ARXIV_ROOT / ".context"
    context_file.write_text(json.dumps({"id": info["id"], "path": str(project_dir)}, indent=2))

    (ARXIV_ROOT / ".extensions").mkdir(exist_ok=True)

    update_global_readme()
    print(f"\nProject ready: {project_dir}")
    print(f"Context set to: {info['id']}")


if __name__ == "__main__":
    main()
