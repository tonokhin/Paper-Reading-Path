from pathlib import Path
import tempfile
import unittest

from paper_reading_path.pdf_scanner import infer_arxiv_id, scan_pdfs


class PdfScannerTests(unittest.TestCase):
    def test_infer_arxiv_id(self):
        self.assertEqual(infer_arxiv_id("1706.03762_Attention_Is_All_You_Need.pdf"), "1706.03762")
        self.assertEqual(infer_arxiv_id("paper.pdf"), "")

    def test_scan_pdfs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "1706.03762_test.pdf").write_text("pdf", encoding="utf-8")
            (root / "notes.txt").write_text("notes", encoding="utf-8")

            papers = scan_pdfs(root)

        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].arxiv_id, "1706.03762")


if __name__ == "__main__":
    unittest.main()
