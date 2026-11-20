import tempfile
import unittest
from pathlib import Path

from fishing_agent.files import FileOperationError, FileTool, PathOutsideWorkspace, resolve_within, search


class SearchTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self._tmp.name) / "workspace"
        (self.workspace / "src").mkdir(parents=True)
        (self.workspace / "catatan.md").write_text("a", encoding="utf-8")
        (self.workspace / "src" / "slide.md").write_text("b", encoding="utf-8")
        (self.workspace / "src" / "gambar.png").write_text("c", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_pola_dan_batas_hasil(self):
        hits = search(self.workspace, "*.md")
        self.assertEqual(hits, [Path("catatan.md"), Path("src/slide.md")])
        self.assertEqual(search(self.workspace, "*.md", limit=1), [Path("catatan.md")])

    def test_pola_traversal_tidak_keluar_workspace(self):
        self.assertEqual(search(self.workspace, "../*"), [])
        self.assertEqual(search(self.workspace, "*"), [Path("catatan.md"), Path("src/gambar.png"), Path("src/slide.md")])

    def test_resolve_within_menolak_keluar(self):
        inside = resolve_within(self.workspace, "src/slide.md")
        self.assertTrue(str(inside).startswith(str(self.workspace.resolve())))
        with self.assertRaises(PathOutsideWorkspace):
            resolve_within(self.workspace, "../rahasia.txt")

    def test_workspace_hilang(self):
        with self.assertRaises(FileNotFoundError):
            search(Path(self._tmp.name) / "tidak-ada", "*")


class FileToolTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.tool = FileTool(max_read_bytes=20, max_write_bytes=20)

    def tearDown(self):
        self._tmp.cleanup()

    def test_read_write_copy_move_metadata(self):
        source = self.tool.write(self.root / "a.txt", "halo")
        self.assertEqual(self.tool.read(source), "halo")
        copied = self.tool.copy(source, self.root / "b.txt")
        moved = self.tool.move(copied, self.root / "c.txt")
        self.assertEqual(self.tool.metadata(moved)["type"], "file")

    def test_overwrite_dan_delete_memerlukan_approval(self):
        target = self.tool.write(self.root / "a.txt", "awal")
        with self.assertRaises(FileOperationError):
            self.tool.write(target, "baru")
        with self.assertRaises(FileOperationError):
            self.tool.delete(target)
        self.tool.delete(target, approved=True)
        self.assertFalse(target.exists())

    def test_symlink_tidak_diikuti(self):
        target = self.root / "target.txt"
        target.write_text("rahasia", encoding="utf-8")
        link = self.root / "link.txt"
        link.symlink_to(target)
        with self.assertRaises(FileOperationError):
            self.tool.read(link)
        self.assertEqual(self.tool.search(self.root, "*.txt"), [target])


if __name__ == "__main__":
    unittest.main()
