from pathlib import Path
import unittest

from paper_reading_path.models import CitationEdge, LocalPaper
from paper_reading_path.ordering import order_papers


class OrderingTests(unittest.TestCase):
    def test_cited_local_paper_comes_first(self):
        older = LocalPaper(path=Path("a.pdf"), title="A", openalex_id="A", publication_year=2020)
        newer = LocalPaper(path=Path("b.pdf"), title="B", openalex_id="B", publication_year=2021)
        edges = [CitationEdge(citing_id="B", cited_id="A")]

        ordered = order_papers([newer, older], edges)

        self.assertEqual([paper.openalex_id for paper in ordered], ["A", "B"])


if __name__ == "__main__":
    unittest.main()
