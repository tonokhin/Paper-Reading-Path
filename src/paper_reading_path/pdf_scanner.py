from __future__ import annotations

import re
from pathlib import Path

from .models import LocalPaper


ARXIV_ID_PATTERN = re.compile(r"(?<!\d)(\d{4}\.\d{4,5})(?:v\d+)?(?!\d)")


def scan_pdfs(root: Path) -> list[LocalPaper]:
    return [
        LocalPaper(path=path, arxiv_id=infer_arxiv_id(path.name))
        for path in sorted(root.rglob("*.pdf"))
    ]


def infer_arxiv_id(filename: str) -> str:
    match = ARXIV_ID_PATTERN.search(filename)
    return match.group(1) if match else ""
