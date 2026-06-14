from __future__ import annotations

from pathlib import Path

from .models import CitationEdge, LocalPaper


def write_reading_order(papers: list[LocalPaper], edges: list[CitationEdge], output_path: Path) -> None:
    output_path.write_text(render_reading_order(papers, edges), encoding="utf-8")


def render_reading_order(papers: list[LocalPaper], edges: list[CitationEdge]) -> str:
    local_citation_counts = _local_citation_counts(edges)
    lines = [
        "# Reading Order",
        "",
        f"Total papers: {len(papers)}",
        f"Local citation edges: {len(edges)}",
        "",
    ]

    for index, paper in enumerate(papers, start=1):
        lines.extend(
            [
                f"## {index}. {paper.display_title}",
                "",
                f"- File: {paper.path}",
                f"- arXiv ID: {_value_or_dash(paper.arxiv_id)}",
                f"- OpenAlex: {_value_or_dash(paper.openalex_id)}",
                f"- Year: {_value_or_dash(str(paper.publication_year) if paper.publication_year else '')}",
                f"- Citation count: {paper.citation_count}",
                f"- Cited by local papers: {local_citation_counts.get(paper.openalex_id, 0)}",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def _local_citation_counts(edges: list[CitationEdge]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for edge in edges:
        counts[edge.cited_id] = counts.get(edge.cited_id, 0) + 1
    return counts


def _value_or_dash(value: str) -> str:
    return value if value else "-"
