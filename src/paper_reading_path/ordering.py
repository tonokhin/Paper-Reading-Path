from __future__ import annotations

from .models import CitationEdge, LocalPaper, PrerequisiteEdge


def order_papers(papers: list[LocalPaper], edges: list[CitationEdge]) -> list[LocalPaper]:
    prerequisite_edges = [
        PrerequisiteEdge(from_id=edge.cited_id, to_id=edge.citing_id)
        for edge in edges
    ]
    return order_papers_by_dag(papers, prerequisite_edges, edges)


def order_papers_by_dag(
    papers: list[LocalPaper],
    prerequisite_edges: list[PrerequisiteEdge],
    citation_edges: list[CitationEdge] | None = None,
) -> list[LocalPaper]:
    citation_edges = citation_edges or []
    by_id = {
        paper.openalex_id: paper
        for paper in papers
        if paper.openalex_id
    }
    without_ids = [paper for paper in papers if not paper.openalex_id]
    incoming: dict[str, set[str]] = {paper_id: set() for paper_id in by_id}
    outgoing: dict[str, set[str]] = {paper_id: set() for paper_id in by_id}

    for edge in prerequisite_edges:
        if edge.from_id not in by_id or edge.to_id not in by_id:
            continue
        outgoing[edge.from_id].add(edge.to_id)
        incoming[edge.to_id].add(edge.from_id)

    ordered: list[LocalPaper] = []
    remaining = set(by_id)

    while remaining:
        available = [
            by_id[paper_id]
            for paper_id in remaining
            if not incoming[paper_id] & remaining
        ]
        if available:
            chosen = min(available, key=lambda paper: _sort_key(paper, citation_edges))
        else:
            # Metadata can contain cycles. Break them deterministically while
            # preserving the best available prerequisite-style ordering.
            chosen = min((by_id[paper_id] for paper_id in remaining), key=lambda paper: _sort_key(paper, citation_edges))

        ordered.append(chosen)
        remaining.remove(chosen.openalex_id)

    return ordered + sorted(without_ids, key=lambda paper: _sort_key(paper, citation_edges))


def _sort_key(paper: LocalPaper, edges: list[CitationEdge]) -> tuple[int, int, int, str]:
    cited_by_local_count = _local_citation_counts(edges)
    return (
        -cited_by_local_count.get(paper.openalex_id, 0),
        paper.publication_year or 9999,
        -paper.citation_count,
        paper.display_title.lower(),
    )


def _local_citation_counts(edges: list[CitationEdge]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for edge in edges:
        counts[edge.cited_id] = counts.get(edge.cited_id, 0) + 1
    return counts
