from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from paper_reading_path.metadata import enrich_papers
from paper_reading_path.models import LocalPaper


class MetadataTests(unittest.TestCase):
    def test_enrich_papers_continues_after_http_error(self):
        papers = [LocalPaper(path=Path("1706.03762.pdf"), arxiv_id="1706.03762")]
        error = HTTPError("https://example.com", 400, "Bad Request", hdrs=None, fp=None)

        with (
            patch("paper_reading_path.metadata.enrich_from_arxiv", side_effect=error),
            patch("paper_reading_path.metadata.enrich_from_openalex", side_effect=error),
        ):
            enrich_papers(papers)

        self.assertEqual(papers[0].arxiv_id, "1706.03762")

    def test_enrich_papers_continues_after_timeout(self):
        papers = [LocalPaper(path=Path("1706.03762.pdf"), arxiv_id="1706.03762")]

        with (
            patch("paper_reading_path.metadata.enrich_from_arxiv", side_effect=TimeoutError("timed out")),
            patch("paper_reading_path.metadata.enrich_from_openalex", side_effect=TimeoutError("timed out")),
        ):
            enrich_papers(papers)

        self.assertEqual(papers[0].arxiv_id, "1706.03762")


if __name__ == "__main__":
    unittest.main()
