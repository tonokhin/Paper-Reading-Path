from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class LocalPaper:
    path: Path
    title: str = ""
    arxiv_id: str = ""
    doi: str = ""
    openalex_id: str = ""
    publication_year: int = 0
    citation_count: int = 0
    referenced_openalex_ids: set[str] = field(default_factory=set)

    @property
    def display_title(self) -> str:
        return self.title or self.path.stem


@dataclass
class CitationEdge:
    citing_id: str
    cited_id: str


@dataclass
class PrerequisiteEdge:
    from_id: str
    to_id: str
    relation: str = "prerequisite"
