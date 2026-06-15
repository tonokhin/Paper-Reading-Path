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


if __name__ == "__main__":
    unittest.main()
