# Paper Reading Path

Paper Reading Path builds a suggested reading sequence from a local folder of research paper PDFs.

The tool is designed for the situation where you already have a folder of papers and want help deciding what to read first based on citation relationships and metadata.

## Quick Start

```bash
cd /Users/nokhin/Documents/paper-reading-path
python -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/paper-reading-path order ./papers
```

This writes:

```text
reading_order.md
```

## Test With AI Paper Fetcher PDFs

If you already downloaded papers with AI Paper Fetcher, run:

```bash
cd /Users/nokhin/Documents/paper-reading-path
.venv/bin/paper-reading-path order /Users/nokhin/Documents/ai-paper-fetcher/papers --output reading_order.md
```

Preview the result:

```bash
cat reading_order.md
```

For a fast smoke test without arXiv/OpenAlex metadata calls:

```bash
.venv/bin/paper-reading-path order /Users/nokhin/Documents/ai-paper-fetcher/papers --no-metadata --output reading_order.md
```

## MVP Behavior

The current MVP:

- Scans a folder recursively for `.pdf` files
- Infers arXiv IDs from filenames when possible
- Resolves metadata from arXiv or OpenAlex
- Uses OpenAlex references to detect citation relationships among the local PDFs
- Scores papers so prerequisite/foundational papers appear earlier
- Generates a Markdown reading order

## Commands

```bash
.venv/bin/paper-reading-path scan ./papers
.venv/bin/paper-reading-path order ./papers
```

## Notes

PDF text parsing is intentionally not part of the first MVP. Filename and metadata-based matching is more reliable to start with, especially for folders of arXiv PDFs.
