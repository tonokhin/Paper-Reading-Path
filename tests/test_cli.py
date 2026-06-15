from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

from paper_reading_path.cli import main


class CliTests(unittest.TestCase):
    def test_order_reuses_graph_cache(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pdf_path = root / "1234.5678_cached.pdf"
            pdf_path.write_text("pdf", encoding="utf-8")
            graph_path = root / "citation_graph.json"
            graph_path.write_text(
                json.dumps(
                    {
                        "nodes": [
                            {
                                "path": str(pdf_path),
                                "title": "Cached Paper",
                                "arxiv_id": "1234.5678",
                                "openalex_id": "A",
                                "year": 2020,
                                "citation_count": 10,
                                "referenced_openalex_ids": [],
                            }
                        ],
                        "edges": [],
                    }
                ),
                encoding="utf-8",
            )

            with patch("paper_reading_path.cli.enrich_papers") as enrich:
                exit_code = main(
                    [
                        "order",
                        str(root),
                        "--output",
                        str(root / "reading_order.md"),
                        "--graph-output",
                        str(graph_path),
                    ]
                )

        self.assertEqual(exit_code, 0)
        enrich.assert_not_called()

    def test_order_refresh_metadata_ignores_cache_for_lookup(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pdf_path = root / "1234.5678_cached.pdf"
            pdf_path.write_text("pdf", encoding="utf-8")
            graph_path = root / "citation_graph.json"
            graph_path.write_text(
                json.dumps(
                    {
                        "nodes": [
                            {
                                "path": str(pdf_path),
                                "title": "Cached Paper",
                                "arxiv_id": "1234.5678",
                                "openalex_id": "A",
                                "year": 2020,
                                "citation_count": 10,
                                "referenced_openalex_ids": [],
                            }
                        ],
                        "edges": [],
                    }
                ),
                encoding="utf-8",
            )

            with patch("paper_reading_path.cli.enrich_papers") as enrich:
                exit_code = main(
                    [
                        "order",
                        str(root),
                        "--refresh-metadata",
                        "--output",
                        str(root / "reading_order.md"),
                        "--graph-output",
                        str(graph_path),
                    ]
                )

        self.assertEqual(exit_code, 0)
        enrich.assert_called_once()

    def test_visualize_writes_mermaid_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            graph_path = root / "citation_graph.json"
            output_path = root / "citation_graph.md"
            graph_path.write_text(
                json.dumps(
                    {
                        "nodes": [
                            {"id": "A", "title": "Foundation", "year": 2017, "citation_count": 100},
                            {"id": "B", "title": "Follow Up", "year": 2018, "citation_count": 50},
                        ],
                        "edges": [{"from": "A", "to": "B", "type": "prerequisite"}],
                    }
                ),
                encoding="utf-8",
            )

            exit_code = main(["visualize", str(graph_path), "--output", str(output_path)])

            self.assertEqual(exit_code, 0)
            self.assertIn("```mermaid", output_path.read_text(encoding="utf-8"))
            self.assertIn("N1 --> N2", output_path.read_text(encoding="utf-8"))

    def test_visualize_writes_graphviz_dot(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            graph_path = root / "citation_graph.json"
            output_path = root / "citation_graph.dot"
            graph_path.write_text(
                json.dumps(
                    {
                        "nodes": [
                            {"id": "A", "title": "Foundation", "year": 2017, "citation_count": 100},
                            {"id": "B", "title": "Follow Up", "year": 2018, "citation_count": 50},
                        ],
                        "edges": [{"from": "A", "to": "B", "type": "prerequisite"}],
                    }
                ),
                encoding="utf-8",
            )

            exit_code = main(["visualize", str(graph_path), "--format", "dot", "--output", str(output_path)])

            self.assertEqual(exit_code, 0)
            self.assertIn("digraph CitationGraph", output_path.read_text(encoding="utf-8"))
            self.assertIn("n1 -> n2;", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
