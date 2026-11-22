import unittest
from pathlib import Path

from fishing_agent.perception import (
    Grounder,
    GroundingResult,
    UnavailableDescriber,
    VisualTarget,
)


class _El:
    def __init__(self, role, name):
        self.role = role
        self.name = name


class _StubAtspi:
    def __init__(self, available, elements=None):
        self.available = available
        self._elements = elements or []

    def find_elements(self, role, name, app_id):
        return self._elements


class _StubScreenshot:
    available = True

    def capture(self, path):
        Path(path).write_bytes(b"\x89PNG")


class _StubDescriber:
    name = "stub-vlm"

    def __init__(self, targets):
        self._targets = targets
        self.seen = None

    def describe(self, image_path):
        self.seen = str(image_path)
        return self._targets


class GrounderTest(unittest.TestCase):
    def test_atspi_dipakai_utama(self):
        grounder = Grounder(atspi=_StubAtspi(True, [_El("push button", "Simpan")]))
        result = grounder.ground(role="push button", name="Simpan")
        self.assertEqual(result.source, "atspi")
        self.assertTrue(result.available)

    def test_fallback_visual_saat_atspi_tidak_tersedia(self):
        describer = _StubDescriber([VisualTarget("Simpan", 10, 10, 20, 20, confidence=0.9)])
        grounder = Grounder(atspi=_StubAtspi(False), screenshot=_StubScreenshot(), describer=describer)
        result = grounder.ground(role="push button", name="Simpan")
        self.assertEqual(result.source, "visual")
        self.assertEqual(result.element.label, "Simpan")
        self.assertIsNotNone(describer.seen)

    def test_visual_target_terbaik_dipilih(self):
        targets = [
            VisualTarget("Batal", 0, 0, 10, 10, confidence=0.4),
            VisualTarget("Simpan berkas", 5, 5, 10, 10, confidence=0.95),
        ]
        grounder = Grounder(atspi=_StubAtspi(False), screenshot=_StubScreenshot(), describer=_StubDescriber(targets))
        result = grounder.ground(name="Simpan")
        self.assertEqual(result.element.label, "Simpan berkas")

    def test_tidak_ada_sumber_none(self):
        grounder = Grounder(atspi=_StubAtspi(False), screenshot=type("S", (), {"available": False})(), describer=UnavailableDescriber())
        result = grounder.ground(role="x", name="y")
        self.assertEqual(result.source, "none")
        self.assertFalse(result.available)

    def test_describer_unavailable_melaporkan_gagal(self):
        grounder = Grounder(atspi=_StubAtspi(False), screenshot=_StubScreenshot(), describer=UnavailableDescriber())
        self.assertFalse(grounder.visual_available)
        result = grounder.ground(name="x")
        self.assertEqual(result.source, "none")

    def test_ground_wajib_role_atau_name(self):
        grounder = Grounder(atspi=_StubAtspi(True, [_El("a", "b")]))
        self.assertEqual(grounder.ground().source, "none")

    def test_visual_cleanup_temp_file(self):
        describer = _StubDescriber([VisualTarget("Simpan", 0, 0, 5, 5, confidence=1.0)])
        grounder = Grounder(atspi=_StubAtspi(False), screenshot=_StubScreenshot(), describer=describer)
        grounder.ground(name="Simpan")
        self.assertFalse(Path(describer.seen).exists())


if __name__ == "__main__":
    unittest.main()