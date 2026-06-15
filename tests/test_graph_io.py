from pathlib import Path
import unittest

from paper_reading_path.graph_io import apply_cached_metadata, dot_graph, graph_payload, load_cached_papers, mermaid_graph
from paper_reading_path.models import LocalPaper, PrerequisiteEdge


class GraphIoTests(unittest.TestCase):
    def test_graph_payload_uses_prerequisite_edges(self):
        paper = LocalPaper(
            path=Path("paper.pdf"),
            title="Paper",
            openalex_id="A",
            arxiv_id="1234.5678",
            publication_year=2020,
            citation_count=10,
        )
        payload = graph_payload([paper], [PrerequisiteEdge(from_id="A", to_id="B")])

        self.assertEqual(payload["nodes"][0]["id"], "A")
        self.assertEqual(payload["nodes"][0]["referenced_openalex_ids"], [])
        self.assertEqual(payload["edges"][0], {"from": "A", "to": "B", "type": "prerequisite"})

    def test_load_and_apply_cached_metadata(self):
        with self.subTest("cache by path and arxiv id"):
            payload = {
                "nodes": [
                    {
                        "path": "paper.pdf",
                        "title": "Cached Paper",
                        "arxiv_id": "1234.5678",
                        "doi": "10.1234/example",
                        "openalex_id": "A",
                        "year": 2020,
                        "citation_count": 10,
                        "referenced_openalex_ids": ["B"],
                    }
                ],
                "edges": [],
            }

            import json
            import tempfile

            with tempfile.TemporaryDirectory() as temp_dir:
                graph_path = Path(temp_dir) / "citation_graph.json"
                graph_path.write_text(json.dumps(payload), encoding="utf-8")
                cached = load_cached_papers(graph_path)
                paper = LocalPaper(path=Path("paper.pdf"), arxiv_id="1234.5678")

                applied = apply_cached_metadata([paper], cached)

        self.assertEqual(applied, 1)
        self.assertEqual(paper.title, "Cached Paper")
        self.assertEqual(paper.openalex_id, "A")
        self.assertEqual(paper.referenced_openalex_ids, {"B"})

    def test_mermaid_graph_renders_prerequisite_edges(self):
        payload = {
            "nodes": [
                {"id": "A", "title": "Foundation", "year": 2017, "citation_count": 100},
                {"id": "B", "title": "Follow Up", "year": 2018, "citation_count": 50},
            ],
            "edges": [{"from": "A", "to": "B", "type": "prerequisite"}],
        }

        graph = mermaid_graph(payload)

        self.assertIn("graph TD", graph)
        self.assertIn('N1["Foundation (2017, 100 cites)"]', graph)
        self.assertIn('N2["Follow Up (2018, 50 cites)"]', graph)
        self.assertIn("N1 --> N2", graph)

    def test_dot_graph_renders_prerequisite_edges(self):
        payload = {
            "nodes": [
                {"id": "A", "title": "Foundation", "year": 2017, "citation_count": 100},
                {"id": "B", "title": "Follow Up", "year": 2018, "citation_count": 50},
            ],
            "edges": [{"from": "A", "to": "B", "type": "prerequisite"}],
        }

        graph = dot_graph(payload)

        self.assertIn("digraph CitationGraph", graph)
        self.assertIn("rankdir=LR", graph)
        self.assertIn('n1 [label="Foundation\\n2017 | 100 cites"];', graph)
        self.assertIn('n2 [label="Follow Up\\n2018 | 50 cites"];', graph)
        self.assertIn("n1 -> n2;", graph)


if __name__ == "__main__":
    unittest.main()
