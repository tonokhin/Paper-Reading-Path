from __future__ import annotations

import json
from pathlib import Path

from .models import LocalPaper, PrerequisiteEdge


def write_graph_json(papers: list[LocalPaper], edges: list[PrerequisiteEdge], output_path: Path) -> None:
    output_path.write_text(json.dumps(graph_payload(papers, edges), indent=2) + "\n", encoding="utf-8")


def graph_payload(papers: list[LocalPaper], edges: list[PrerequisiteEdge]) -> dict:
    return {
        "nodes": [
            {
                "id": paper_id(paper),
                "title": paper.display_title,
                "path": str(paper.path),
                "arxiv_id": paper.arxiv_id,
                "doi": paper.doi,
                "openalex_id": paper.openalex_id,
                "year": paper.publication_year,
                "citation_count": paper.citation_count,
                "referenced_openalex_ids": sorted(paper.referenced_openalex_ids),
            }
            for paper in papers
        ],
        "edges": [
            {
                "from": edge.from_id,
                "to": edge.to_id,
                "type": edge.relation,
            }
            for edge in edges
        ],
    }


def paper_id(paper: LocalPaper) -> str:
    return paper.openalex_id or str(paper.path)


def load_cached_papers(graph_path: Path) -> dict[str, LocalPaper]:
    if not graph_path.exists():
        return {}

    payload = json.loads(graph_path.read_text(encoding="utf-8"))
    cached: dict[str, LocalPaper] = {}
    for node in payload.get("nodes", []):
        paper = LocalPaper(
            path=Path(node.get("path", "")),
            title=node.get("title", ""),
            arxiv_id=node.get("arxiv_id", ""),
            doi=node.get("doi", ""),
            openalex_id=node.get("openalex_id", ""),
            publication_year=int(node.get("year") or 0),
            citation_count=int(node.get("citation_count") or 0),
            referenced_openalex_ids=set(node.get("referenced_openalex_ids") or []),
        )
        for key in _cache_keys(paper):
            cached[key] = paper
    return cached


def apply_cached_metadata(papers: list[LocalPaper], cached: dict[str, LocalPaper]) -> int:
    applied = 0
    for paper in papers:
        cached_paper = cached.get(str(paper.path)) or cached.get(paper.arxiv_id)
        if cached_paper is None:
            continue
        paper.title = cached_paper.title
        paper.doi = cached_paper.doi
        paper.openalex_id = cached_paper.openalex_id
        paper.publication_year = cached_paper.publication_year
        paper.citation_count = cached_paper.citation_count
        paper.referenced_openalex_ids = set(cached_paper.referenced_openalex_ids)
        applied += 1
    return applied


def has_cached_metadata(paper: LocalPaper) -> bool:
    return bool(paper.title and (paper.openalex_id or paper.publication_year or paper.referenced_openalex_ids))


def _cache_keys(paper: LocalPaper) -> list[str]:
    keys = [str(paper.path)]
    if paper.arxiv_id:
        keys.append(paper.arxiv_id)
    return keys
