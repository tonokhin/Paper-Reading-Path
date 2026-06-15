from pathlib import Path
import unittest

from paper_reading_path.models import CitationEdge, LocalPaper, PrerequisiteEdge
from paper_reading_path.ordering import order_papers, order_papers_by_dag


class OrderingTests(unittest.TestCase):
    def test_cited_local_paper_comes_first(self):
        older = LocalPaper(path=Path("a.pdf"), title="A", openalex_id="A", publication_year=2020)
        newer = LocalPaper(path=Path("b.pdf"), title="B", openalex_id="B", publication_year=2021)
        edges = [CitationEdge(citing_id="B", cited_id="A")]

        ordered = order_papers([newer, older], edges)

        self.assertEqual([paper.openalex_id for paper in ordered], ["A", "B"])

    def test_topological_order_respects_prerequisite_chain(self):
        foundation = LocalPaper(path=Path("a.pdf"), title="Foundation", openalex_id="A", publication_year=2020)
        middle = LocalPaper(path=Path("b.pdf"), title="Middle", openalex_id="B", publication_year=2019)
        later = LocalPaper(path=Path("c.pdf"), title="Later", openalex_id="C", publication_year=2018)
        edges = [
            PrerequisiteEdge(from_id="A", to_id="B"),
            PrerequisiteEdge(from_id="B", to_id="C"),
        ]

        ordered = order_papers_by_dag([later, middle, foundation], edges)

        self.assertEqual([paper.openalex_id for paper in ordered], ["A", "B", "C"])

    def test_topological_order_handles_cycles(self):
        first = LocalPaper(path=Path("a.pdf"), title="A", openalex_id="A", publication_year=2020)
        second = LocalPaper(path=Path("b.pdf"), title="B", openalex_id="B", publication_year=2021)
        edges = [
            PrerequisiteEdge(from_id="A", to_id="B"),
            PrerequisiteEdge(from_id="B", to_id="A"),
        ]

        ordered = order_papers_by_dag([second, first], edges)

        self.assertEqual({paper.openalex_id for paper in ordered}, {"A", "B"})


if __name__ == "__main__":
    unittest.main()
