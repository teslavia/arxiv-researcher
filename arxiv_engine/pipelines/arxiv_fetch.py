#!/usr/bin/env python3
"""Compatibility module for the search pipeline."""

from __future__ import annotations

from arxiv_engine.pipelines.search import main, search_arxiv, search_github_for_paper

__all__ = ["main", "search_arxiv", "search_github_for_paper"]


if __name__ == "__main__":
    main()
