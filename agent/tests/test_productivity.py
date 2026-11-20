import csv
import tempfile
import unittest
import zipfile
from pathlib import Path

from fishing_agent.productivity import (
    ProductivityError,
    create_csv,
    create_markdown,
    create_pptx,
    validate_pptx,
)


class ProductivityTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_markdown_and_csv_are_valid(self):
        markdown = create_markdown(
            self.root / "report.md",
            "Laporan",
            [("Hasil", "Isi laporan")],
        )
        self.assertIn("# Laporan", markdown.read_text(encoding="utf-8"))
        csv_path = create_csv(self.root / "data.csv", ["nama", "nilai"], [["A", 10]])
        with csv_path.open(newline="", encoding="utf-8") as handle:
            self.assertEqual(list(csv.reader(handle)), [["nama", "nilai"], ["A", "10"]])

    def test_pptx_valid_and_contains_slides(self):
        path = create_pptx(
            self.root / "presentasi.pptx",
            [{"title": "Pembuka", "body": "Isi"}, {"title": "Penutup", "body": "Selesai"}],
        )
        validate_pptx(path)
        with zipfile.ZipFile(path) as archive:
            self.assertIn("ppt/slides/slide1.xml", archive.namelist())
            self.assertIn("ppt/slides/slide2.xml", archive.namelist())
            self.assertIn("Pembuka", archive.read("ppt/slides/slide1.xml").decode())

    def test_overwrite_requires_approval(self):
        path = self.root / "report.md"
        create_markdown(path, "A", [])
        with self.assertRaises(ProductivityError):
            create_markdown(path, "B", [])
        create_markdown(path, "B", [], overwrite=True)
        self.assertIn("# B", path.read_text(encoding="utf-8"))

    def test_csv_row_width_is_validated(self):
        with self.assertRaises(ProductivityError):
            create_csv(self.root / "bad.csv", ["a", "b"], [["only-one"]])


if __name__ == "__main__":
    unittest.main()
