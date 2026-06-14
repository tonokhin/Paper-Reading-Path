from pathlib import Path
import unittest

from paper_reading_path.models import CitationEdge, LocalPaper
from paper_reading_path.reporting import render_reading_order


class ReportingTests(unittest.TestCase):
    def test_render_reading_order(self):
        paper = LocalPaper(
            path=Path("1706.03762.pdf"),
            title="Attention Is All You Need",
            arxiv_id="1706.03762",
            openalex_id="A",
            publication_year=2017,
            citation_count=100,
        )

        markdown = render_reading_order([paper], [CitationEdge(citing_id="B", cited_id="A")])

        self.assertIn("# Reading Order", markdown)
        self.assertIn("Attention Is All You Need", markdown)
        self.assertIn("Cited by local papers: 1", markdown)


if __name__ == "__main__":
    unittest.main()
