#!/usr/bin/env python3
"""arXiv search with GitHub enrichment."""

from __future__ import annotations

import argparse
import json
import subprocess
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ARXIV_API = "http://export.arxiv.org/api/query"


def search_arxiv(query: str, max_results: int = 10) -> list[dict]:
    """Search arXiv API and return parsed results."""
    params = urllib.parse.urlencode({
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    })
    url = f"{ARXIV_API}?{params}"

    with urllib.request.urlopen(url, timeout=30) as resp:
        xml_data = resp.read().decode("utf-8")

    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(xml_data)

    results = []
    for entry in root.findall("atom:entry", ns):
        id_element = entry.find("atom:id", ns)
        title_element = entry.find("atom:title", ns)
        summary_element = entry.find("atom:summary", ns)
        published_element = entry.find("atom:published", ns)

        arxiv_id = id_element.text.split("/abs/")[-1] if id_element is not None and id_element.text else "unknown"
        title = title_element.text.strip().replace("\n", " ") if title_element is not None and title_element.text else "No Title"
        summary = summary_element.text.strip()[:300] if summary_element is not None and summary_element.text else ""
        published = published_element.text[:10] if published_element is not None and published_element.text else ""

        categories = [c.get("term") for c in entry.findall("atom:category", ns)]
        primary_cat = categories[0] if categories and categories[0] else "unknown"

        results.append({
            "id": arxiv_id,
            "title": title,
            "summary": summary,
            "published": published,
            "category": primary_cat,
            "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
            "abs_url": f"https://arxiv.org/abs/{arxiv_id}",
        })

    return results


def search_github_for_paper(arxiv_id: str, title: str) -> dict | None:
    """Search GitHub for paper implementation."""
    try:
        result = subprocess.run(
            ["gh", "search", "repos", arxiv_id, "--json", "fullName,stargazersCount", "--limit", "3"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            repos = json.loads(result.stdout)
            if repos:
                top = max(repos, key=lambda x: x.get("stargazersCount", 0))
                return {"repo": top["fullName"], "stars": top["stargazersCount"]}
    except Exception:
        pass
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Search arXiv papers")
    parser.add_argument("--search", "-s", required=True, help="Search query")
    parser.add_argument("--max", "-m", type=int, default=10, help="Max results")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    args = parser.parse_args()

    results = search_arxiv(args.search, args.max)

    for r in results:
        gh = search_github_for_paper(r["id"], r["title"])
        if gh:
            r["github"] = gh["repo"]
            r["stars"] = gh["stars"]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for i, r in enumerate(results, 1):
            stars = f"⭐{r['stars']}" if "stars" in r else "No code"
            print(f"\n{i}. [{r['id']}] {r['title'][:70]}...")
            print(f"   📅 {r['published']} | 📁 {r['category']} | {stars}")
            print(f"   🔗 {r['abs_url']}")
            if "github" in r:
                print(f"   💻 https://github.com/{r['github']}")


if __name__ == "__main__":
    main()
