from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .graph import build_edges, build_prerequisite_edges
from .graph_io import apply_cached_metadata, has_cached_metadata, load_cached_papers, write_graph_json
from .metadata import enrich_papers
from .ordering import order_papers
from .pdf_scanner import scan_pdfs
from .reporting import write_reading_order


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        papers = scan_pdfs(Path(args.pdf_dir))
        for paper in papers:
            print(f"{paper.path}\t{paper.arxiv_id or '-'}")
        print(f"Found {len(papers)} PDFs")
        return 0

    if args.command in (None, "order"):
        pdf_dir = Path(args.pdf_dir)
        output_path = Path(args.output)
        papers = scan_pdfs(pdf_dir)
        if args.max_papers:
            papers = papers[: args.max_papers]
        cache_count = 0
        if not args.no_cache:
            cache_count = apply_cached_metadata(papers, load_cached_papers(Path(args.graph_output)))
        if not args.no_metadata:
            for index, paper in enumerate(papers, start=1):
                if not args.refresh_metadata and has_cached_metadata(paper):
                    continue
                print(f"Resolving metadata {index}/{len(papers)}: {paper.path.name}", file=sys.stderr, flush=True)
                enrich_papers([paper], timeout=args.metadata_timeout)
        edges = build_edges(papers)
        prerequisite_edges = build_prerequisite_edges(edges)
        ordered = order_papers(papers, edges)
        write_graph_json(ordered, prerequisite_edges, Path(args.graph_output))
        write_reading_order(ordered, edges, output_path)
        print(f"Scanned {len(papers)} PDFs")
        if cache_count:
            print(f"Loaded cached metadata for {cache_count} PDFs")
        print(f"Found {len(edges)} local citation edges")
        print(f"Saved citation graph to {args.graph_output}")
        print(f"Saved reading order to {output_path}")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paper-reading-path",
        description="Generate a reading sequence from a folder of paper PDFs.",
    )
    parser.add_argument("command", nargs="?", choices=["scan", "order"], help="Command to run.")
    parser.add_argument("pdf_dir", help="Folder containing PDF papers.")
    parser.add_argument("--output", default="reading_order.md", help="Markdown output path.")
    parser.add_argument("--graph-output", default="citation_graph.json", help="JSON output path for the prerequisite DAG.")
    parser.add_argument("--metadata-timeout", type=float, default=8.0, help="Seconds to wait for each metadata request.")
    parser.add_argument("--max-papers", type=int, help="Limit the number of PDFs processed, useful for smoke tests.")
    parser.add_argument("--no-cache", action="store_true", help="Do not reuse metadata from an existing graph output file.")
    parser.add_argument("--refresh-metadata", action="store_true", help="Refresh metadata even when graph cache exists.")
    parser.add_argument("--no-metadata", action="store_true", help="Skip arXiv/OpenAlex metadata enrichment.")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
