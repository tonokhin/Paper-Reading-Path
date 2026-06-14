from __future__ import annotations

import argparse
from pathlib import Path

from .graph import build_edges
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
        if not args.no_metadata:
            enrich_papers(papers)
        edges = build_edges(papers)
        ordered = order_papers(papers, edges)
        write_reading_order(ordered, edges, output_path)
        print(f"Scanned {len(papers)} PDFs")
        print(f"Found {len(edges)} local citation edges")
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
    parser.add_argument("--no-metadata", action="store_true", help="Skip arXiv/OpenAlex metadata enrichment.")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
