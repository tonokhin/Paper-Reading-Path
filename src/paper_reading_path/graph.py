from __future__ import annotations

from .models import CitationEdge, LocalPaper, PrerequisiteEdge


def build_edges(papers: list[LocalPaper]) -> list[CitationEdge]:
    by_openalex_id = {
        paper.openalex_id: paper
        for paper in papers
        if paper.openalex_id
    }
    edges: list[CitationEdge] = []

    for paper in papers:
        if not paper.openalex_id:
            continue
        for referenced_id in paper.referenced_openalex_ids:
            if referenced_id in by_openalex_id:
                edges.append(CitationEdge(citing_id=paper.openalex_id, cited_id=referenced_id))

    return edges


def build_prerequisite_edges(edges: list[CitationEdge]) -> list[PrerequisiteEdge]:
    return [
        PrerequisiteEdge(from_id=edge.cited_id, to_id=edge.citing_id)
        for edge in edges
    ]
