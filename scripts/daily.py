#!/usr/bin/env python3
"""Fetch daily arXiv papers for a topic.

Provides a daily digest of new papers with GitHub code availability.
"""

import argparse
import json
import subprocess
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

ARXIV_API = "http://export.arxiv.org/api/query"


def fetch_recent_papers(topic: str, days: int = 7, max_results: int = 20) -> list[dict]:
    """Fetch recent papers from arXiv."""
    # arXiv API doesn't support date filtering directly, so we fetch more and filter
    params = urllib.parse.urlencode({
        "search_query": f"all:{topic}",
        "start": 0,
        "max_results": max_results * 2,  # Fetch extra to filter
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    })
    url = f"{ARXIV_API}?{params}"

    with urllib.request.urlopen(url, timeout=30) as resp:
        xml_data = resp.read().decode("utf-8")

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml_data)

    cutoff = datetime.now() - timedelta(days=days)
    results = []

    for entry in root.findall("atom:entry", ns):
        published_str = entry.find("atom:published", ns).text[:10]
        published = datetime.strptime(published_str, "%Y-%m-%d")

        if published < cutoff:
            continue

        arxiv_id = entry.find("atom:id", ns).text.split("/abs/")[-1]
        title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
        summary = entry.find("atom:summary", ns).text.strip()[:200]
        categories = [c.get("term") for c in entry.findall("atom:category", ns)]

        results.append({
            "id": arxiv_id,
            "title": title,
            "summary": summary,
            "published": published_str,
            "category": categories[0] if categories else "unknown",
            "abs_url": f"https://arxiv.org/abs/{arxiv_id}",
        })

        if len(results) >= max_results:
            break

    return results


def check_github(arxiv_id: str) -> dict | None:
    """Check if paper has GitHub code."""
    try:
        result = subprocess.run(
            ["gh", "search", "repos", arxiv_id, "--json", "fullName,stargazersCount", "--limit", "1"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            repos = json.loads(result.stdout)
            if repos:
                return {"repo": repos[0]["fullName"], "stars": repos[0]["stargazersCount"]}
    except Exception:
        pass
    return None


def main():
    parser = argparse.ArgumentParser(description="Daily arXiv digest")
    parser.add_argument("topic", help="Topic to search (e.g., 'LLM inference')")
    parser.add_argument("--days", "-d", type=int, default=7, help="Days to look back")
    parser.add_argument("--max", "-m", type=int, default=15, help="Max results")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    parser.add_argument("--code-only", "-c", action="store_true", help="Only show papers with code")
    args = parser.parse_args()

    print(f"📅 arXiv Daily: '{args.topic}' (last {args.days} days)\n")

    papers = fetch_recent_papers(args.topic, args.days, args.max)

    # Enrich with GitHub info
    for p in papers:
        gh = check_github(p["id"])
        if gh:
            p["github"] = gh["repo"]
            p["stars"] = gh["stars"]

    # Filter if needed
    if args.code_only:
        papers = [p for p in papers if "github" in p]

    if args.json:
        print(json.dumps(papers, indent=2))
        return

    if not papers:
        print("No papers found matching criteria.")
        return

    # Group by date
    by_date = {}
    for p in papers:
        date = p["published"]
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(p)

    for date in sorted(by_date.keys(), reverse=True):
        print(f"### {date}")
        for p in by_date[date]:
            code = f"⭐{p['stars']} {p['github']}" if "github" in p else "❌ No code"
            print(f"\n  [{p['id']}] {p['title'][:65]}...")
            print(f"  {p['category']} | {code}")
            print(f"  {p['abs_url']}")
        print()

    print(f"📊 Total: {len(papers)} papers ({sum(1 for p in papers if 'github' in p)} with code)")


if __name__ == "__main__":
    main()
