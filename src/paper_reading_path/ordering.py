from __future__ import annotations

from .models import CitationEdge, LocalPaper


def order_papers(papers: list[LocalPaper], edges: list[CitationEdge]) -> list[LocalPaper]:
    cited_by_local_count = _local_citation_counts(edges)

    return sorted(
        papers,
        key=lambda paper: (
            -cited_by_local_count.get(paper.openalex_id, 0),
            paper.publication_year or 9999,
            -paper.citation_count,
            paper.display_title.lower(),
        ),
    )


def _local_citation_counts(edges: list[CitationEdge]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for edge in edges:
        counts[edge.cited_id] = counts.get(edge.cited_id, 0) + 1
    return counts
