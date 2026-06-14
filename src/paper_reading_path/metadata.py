from __future__ import annotations

import json
from difflib import SequenceMatcher
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from .models import LocalPaper
from .network import ssl_context


ARXIV_API_URL = "https://export.arxiv.org/api/query"
OPENALEX_WORKS_URL = "https://api.openalex.org/works"
ATOM = "{http://www.w3.org/2005/Atom}"


def enrich_papers(papers: list[LocalPaper]) -> None:
    for paper in papers:
        if paper.arxiv_id:
            try:
                enrich_from_arxiv(paper)
            except (HTTPError, URLError, ET.ParseError):
                pass
        try:
            enrich_from_openalex(paper)
        except (HTTPError, URLError, json.JSONDecodeError):
            pass


def enrich_from_arxiv(paper: LocalPaper) -> None:
    params = urlencode({"id_list": paper.arxiv_id})
    request = Request(f"{ARXIV_API_URL}?{params}", headers={"User-Agent": "paper-reading-path/0.1"})
    with urlopen(request, timeout=30, context=ssl_context()) as response:
        root = ET.fromstring(response.read())

    entry = root.find(f"{ATOM}entry")
    if entry is None:
        return

    title = _text(entry, f"{ATOM}title")
    published = _text(entry, f"{ATOM}published")
    paper.title = " ".join(title.split()) or paper.title
    paper.publication_year = _year(published) or paper.publication_year


def enrich_from_openalex(paper: LocalPaper) -> None:
    work = None
    if paper.title:
        work = _openalex_by_title(paper.title)
    if work is None:
        return

    paper.openalex_id = work.get("id", "") or paper.openalex_id
    paper.title = work.get("title", "") or paper.title
    paper.publication_year = paper.publication_year or int(work.get("publication_year") or 0)
    paper.citation_count = int(work.get("cited_by_count") or 0)
    paper.referenced_openalex_ids = set(work.get("referenced_works") or [])


def _openalex_by_title(title: str) -> dict | None:
    params = urlencode(
        {
            "search": title,
            "per-page": 5,
            "select": "id,title,publication_year,cited_by_count,referenced_works",
        }
    )
    payload = _get_json(f"{OPENALEX_WORKS_URL}?{params}")
    results = payload.get("results", [])
    return _best_title_match(title, results)


def _best_title_match(title: str, results: list[dict]) -> dict | None:
    scored = [
        (_title_similarity(title, result.get("title", "")), result)
        for result in results
    ]
    scored = [item for item in scored if item[0] >= 0.90]
    if not scored:
        return None
    return max(scored, key=lambda item: item[0])[1]


def _title_similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, _normalize_title(left), _normalize_title(right)).ratio()


def _normalize_title(value: str) -> str:
    return " ".join(value.lower().split())


def _get_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "paper-reading-path/0.1"})
    with urlopen(request, timeout=30, context=ssl_context()) as response:
        return json.loads(response.read().decode("utf-8"))


def _text(element: ET.Element, path: str) -> str:
    found = element.find(path)
    return found.text.strip() if found is not None and found.text else ""


def _year(value: str) -> int:
    try:
        return int(value[:4])
    except (TypeError, ValueError):
        return 0
