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
citation_graph.json
```

Visualize the prerequisite graph:

```bash
.venv/bin/paper-reading-path visualize citation_graph.json --output citation_graph.md
```

Open `citation_graph.md` in a Markdown viewer that supports Mermaid, such as GitHub or VS Code Markdown Preview.

## Test With AI Paper Fetcher PDFs

If you already downloaded papers with AI Paper Fetcher, run:

```bash
cd /Users/nokhin/Documents/paper-reading-path
.venv/bin/paper-reading-path order /Users/nokhin/Documents/ai-paper-fetcher/papers --output reading_order.md
```

If metadata lookups are slow, lower the per-request timeout:

```bash
.venv/bin/paper-reading-path order /Users/nokhin/Documents/ai-paper-fetcher/papers --metadata-timeout 5 --output reading_order.md
```

For a smaller metadata-backed smoke test:

```bash
.venv/bin/paper-reading-path order /Users/nokhin/Documents/ai-paper-fetcher/papers --max-papers 10 --metadata-timeout 3 --output reading_order.md
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
- Inverts citation edges into prerequisite edges
- Uses DAG-style topological ordering so prerequisites appear earlier
- Generates a Markdown reading order
- Saves the prerequisite graph as `citation_graph.json`

## Commands

```bash
.venv/bin/paper-reading-path scan ./papers
.venv/bin/paper-reading-path order ./papers
.venv/bin/paper-reading-path order ./papers --graph-output citation_graph.json
.venv/bin/paper-reading-path visualize citation_graph.json --output citation_graph.md
```

By default, an existing `citation_graph.json` is reused as a metadata cache on later runs. Use `--refresh-metadata` to force new arXiv/OpenAlex lookups, or `--no-cache` to ignore the existing graph file.

## Notes

PDF text parsing is intentionally not part of the first MVP. Filename and metadata-based matching is more reliable to start with, especially for folders of arXiv PDFs.
