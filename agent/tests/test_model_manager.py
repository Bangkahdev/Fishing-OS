import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from fishing_agent.model_manager import (
    FAILED,
    LOADED,
    MISSING,
    UNLOADED,
    ModelError,
    ModelManager,
    ModelManifest,
    ModelNotFound,
    ModelVerificationFailed,
    load_manifests_from_file,
)


class ModelManifestTest(unittest.TestCase):
    def test_dari_dict(self):
        manifest = ModelManifest.from_dict(
            {
                "id": "qwen2.5-vl-3b",
                "version": "1.0",
                "checksum": "deadbeef",
                "source": "official",
            }
        )
        self.assertEqual(manifest.id, "qwen2.5-vl-3b")
        self.assertEqual(manifest.checksum_algorithm, "sha256")

    def test_field_wajib(self):
        with self.assertRaises(Exception):
            ModelManifest.from_dict({"id": "x", "version": "1"})


class ModelManagerTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name) / "models"
        self.dir.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def _write_file(self, name: str, content: bytes = b"data") -> Path:
        path = self.dir / name
        path.write_bytes(content)
        return path

    def test_register_dan_list(self):
        manager = ModelManager(self.dir)
        manager.register(ModelManifest(id="m1", version="1", checksum="abc"))
        manager.register(ModelManifest.from_dict({"id": "m2", "version": "2", "checksum": "def"}))
        self.assertEqual(manager.list_models(), ["m1", "m2"])

    def test_get_model_tidak_ditemukan(self):
        manager = ModelManager(self.dir)
        self.assertIsNone(manager.get_model("tidak-ada"))

    def test_verify_file_hilang(self):
        manager = ModelManager(self.dir)
        manager.register(ModelManifest(id="m1", version="1", checksum="abc"))
        self.assertFalse(manager.verify("m1"))

    def test_verify_checksum_cocok(self):
        content = b"isi model palsu"
        digest = hashlib.sha256(content).hexdigest()
        self._write_file("m1-1", content)
        manager = ModelManager(self.dir)
        manager.register(ModelManifest(id="m1", version="1", checksum=digest))
        self.assertTrue(manager.verify("m1"))

    def test_load_file_hilang(self):
        manager = ModelManager(self.dir)
        manager.register(ModelManifest(id="m1", version="1", checksum="abc"))
        with self.assertRaises(ModelError):
            manager.load("m1")
        self.assertEqual(manager.status("m1"), MISSING)

    def test_load_checksum_salah(self):
        self._write_file("m1-1", b"salah")
        manager = ModelManager(self.dir)
        manager.register(ModelManifest(id="m1", version="1", checksum="abc"))
        with self.assertRaises(ModelVerificationFailed):
            manager.load("m1")
        self.assertEqual(manager.status("m1"), FAILED)

    def test_load_berhasil(self):
        content = b"model benar"
        digest = hashlib.sha256(content).hexdigest()
        self._write_file("m1-1", content)
        manager = ModelManager(self.dir)
        manager.register(
            ModelManifest(id="m1", version="1", checksum=digest, size=len(content))
        )
        self.assertEqual(manager.load("m1"), LOADED)
        self.assertEqual(manager.status("m1"), LOADED)
        self.assertEqual(manager.unload("m1"), UNLOADED)

    def test_oom_membatalkan_muat(self):
        manager = ModelManager(self.dir)
        manager.register(ModelManifest(id="m1", version="1", checksum="abc"))
        manager.set_oom(True)
        with self.assertRaises(ModelError):
            manager.load("m1")
        self.assertTrue(manager.oom)

    def test_load_model_tidak_terdaftar(self):
        manager = ModelManager(self.dir)
        with self.assertRaises(ModelNotFound):
            manager.load("tidak-ada")


class LoadManifestsFileTest(unittest.TestCase):
    def test_dari_berkas_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifests.json"
            path.write_text(
                json.dumps(
                    {"models": [{"id": "a", "version": "1", "checksum": "x"}]}
                ),
                encoding="utf-8",
            )
            manifests = load_manifests_from_file(path)
        self.assertEqual(len(manifests), 1)
        self.assertEqual(manifests[0].id, "a")


if __name__ == "__main__":
    unittest.main()
