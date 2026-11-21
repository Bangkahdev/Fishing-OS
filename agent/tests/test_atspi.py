import unittest
from types import SimpleNamespace
from unittest import mock

from fishing_agent.atspi import (
    _STATE_NAMES,
    ATSPiActionFailed,
    ATSPiReader,
    ATSPiUnavailable,
    UIElement,
)


class FakeStates:
    def __init__(self, names):
        self.names = tuple(names)

    def contains(self, state):
        return state in self.names


class FakeAction:
    def __init__(self, names=("click",), on_action=None):
        self.names = list(names)
        self.pressed = None
        self.on_action = on_action

    @property
    def nActions(self):
        return len(self.names)

    def getName(self, index):
        return self.names[index]

    def doAction(self, index):
        self.pressed = index
        if self.on_action:
            self.on_action(self)


class FakeAccessible:
    def __init__(self, name, role, states=(), extents=(0, 0, 10, 10), children=(), action=None):
        self.name = name
        self.role = role
        self.states = states
        self.extents = extents
        self.children = list(children)
        self.action = action
        self.broken = False

    def __iter__(self):
        return iter(self.children)

    def getRole(self):
        if self.broken:
            raise RuntimeError("elemen sudah tidak ada")
        return SimpleNamespace(name=self.role)

    def getState(self):
        if self.broken:
            raise RuntimeError("elemen sudah tidak ada")
        return FakeStates(self.states)

    def getExtents(self, *_args):
        if self.broken:
            raise RuntimeError("elemen sudah tidak ada")
        return self.extents

    def queryAction(self):
        if self.action is None:
            raise RuntimeError("tidak ada Action")
        return self.action


class FakeRegistry:
    def __init__(self, desktop):
        self.desktop = desktop

    def getDesktop(self, _index):
        return self.desktop


def fake_module(desktop):
    return SimpleNamespace(
        DESKTOP_COORDS=0,
        StateType=SimpleNamespace(**{name.upper(): name for name in _STATE_NAMES}),
        Registry=FakeRegistry(desktop),
    )


def sample_tree(active=True):
    button = FakeAccessible("Insert Table", "push button", ("enabled", "showing"), (10, 10, 80, 20))
    entry = FakeAccessible("Body", "text", ("enabled", "editable"), (10, 40, 200, 100))
    frame = FakeAccessible(
        "Dokumen",
        "frame",
        ("active", "showing") if active else ("showing",),
        (0, 0, 800, 600),
        [button, entry],
    )
    app = FakeAccessible("Doc", "application", (), (0, 0, 800, 600), [frame])
    return FakeAccessible("desktop", "desktop", (), (0, 0, 1920, 1080), [app])


class ATSPiReaderTest(unittest.TestCase):
    def test_default_mengikuti_deteksi(self):
        with mock.patch.object(ATSPiReader, "_load_pyatspi", return_value=None):
            reader = ATSPiReader()
            self.assertFalse(reader.available)

    def test_tersedia_dapat_dipaksa(self):
        reader = ATSPiReader(available=True)
        self.assertTrue(reader.available)

    def test_require_available_menghasilkan_galat(self):
        reader = ATSPiReader(available=False)
        with self.assertRaises(ATSPiUnavailable):
            reader.require_available()

    def test_find_elements_tanpa_availability(self):
        reader = ATSPiReader(available=False)
        with self.assertRaises(ATSPiUnavailable):
            reader.find_elements(role="button")

    def test_element_deskriptor(self):
        element = UIElement("button", "Simpan", ("enabled",), 10, 20, 100, 30, "app1")
        reader = ATSPiReader(available=True)
        data = reader.describe(element)
        self.assertEqual(data["role"], "button")
        self.assertEqual(data["name"], "Simpan")
        self.assertEqual(data["source"], "atspi")

    def test_get_active_window(self):
        reader = ATSPiReader(module=fake_module(sample_tree()))
        window = reader.get_active_window()
        self.assertIsNotNone(window)
        self.assertEqual(window.role, "frame")
        self.assertEqual(window.name, "Dokumen")
        self.assertEqual(window.app_id, "Doc")
        self.assertIn("active", window.state)

    def test_get_active_window_tanpa_frame_aktif(self):
        reader = ATSPiReader(module=fake_module(sample_tree(active=False)))
        self.assertIsNone(reader.get_active_window())

    def test_find_elements_filter_role_dan_nama(self):
        reader = ATSPiReader(module=fake_module(sample_tree()))
        buttons = reader.find_elements(role="push button")
        self.assertEqual([item.name for item in buttons], ["Insert Table"])
        matches = reader.find_elements(name="insert")
        self.assertEqual([item.role for item in matches], ["push button"])
        self.assertEqual(reader.find_elements(role="slider"), [])

    def test_find_elements_filter_aplikasi(self):
        reader = ATSPiReader(module=fake_module(sample_tree()))
        self.assertEqual(len(reader.find_elements(app_id="Doc")), 3)
        self.assertEqual(reader.find_elements(app_id="Lain"), [])

    def test_element_at_memilih_area_terkecil(self):
        reader = ATSPiReader(module=fake_module(sample_tree()))
        element = reader.element_at(20, 20)
        self.assertIsNotNone(element)
        self.assertEqual(element.name, "Insert Table")
        self.assertIsNone(reader.element_at(900, 700))

    def test_element_at_tanpa_frame_aktif(self):
        reader = ATSPiReader(module=fake_module(sample_tree(active=False)))
        self.assertIsNone(reader.element_at(20, 20))
        self.assertEqual(reader.find_elements(), [])

    def _action_tree(self, names=("grab focus", "click"), on_action=None):
        action = FakeAction(names, on_action)
        button = FakeAccessible(
            "Insert Table",
            "push button",
            ("enabled", "showing"),
            (10, 10, 80, 20),
            action=action,
        )
        frame = FakeAccessible("Dokumen", "frame", ("active",), (0, 0, 800, 600), [button])
        app = FakeAccessible("Doc", "application", (), (0, 0, 800, 600), [frame])
        desktop = FakeAccessible("desktop", "desktop", (), (0, 0, 1920, 1080), [app])
        return button, action, fake_module(desktop)

    def test_perform_action_memilih_aksi_umum(self):
        button, action, module = self._action_tree()
        reader = ATSPiReader(module=module)
        result = reader.perform_action(role="push button", name="insert")
        self.assertTrue(result["ok"])
        self.assertEqual(result["grounding"], "atspi")
        self.assertEqual(result["action"], "click")
        self.assertEqual(action.pressed, 1)
        self.assertTrue(result["verified"])

    def test_perform_action_nama_aksi_eksplisit(self):
        _button, action, module = self._action_tree(names=("Grab Focus", "Activate"))
        reader = ATSPiReader(module=module)
        result = reader.perform_action(role="push button", name="Insert", action="activate")
        self.assertEqual(result["action"], "Activate")
        self.assertEqual(action.pressed, 1)

    def test_perform_action_aksi_tidak_dikenal(self):
        _button, _action, module = self._action_tree()
        reader = ATSPiReader(module=module)
        with self.assertRaises(ATSPiActionFailed) as context:
            reader.perform_action(role="push button", name="Insert", action="double click")
        self.assertIn("pilihan:", str(context.exception))

    def test_perform_action_target_tidak_ditemukan(self):
        _button, _action, module = self._action_tree()
        reader = ATSPiReader(module=module)
        with self.assertRaises(ATSPiActionFailed):
            reader.perform_action(role="push button", name="Hapus")

    def test_perform_action_tanpa_antarmuka_action(self):
        reader = ATSPiReader(module=fake_module(sample_tree()))
        with self.assertRaises(ATSPiActionFailed):
            reader.perform_action(role="push button", name="Insert")

    def test_perform_action_state_berubah_sesuai_harapan(self):
        def press(_action):
            button = _action.owner
            button.states = ("enabled", "showing", "pressed")

        button, action, module = self._action_tree()
        action.owner = button
        action.on_action = press
        reader = ATSPiReader(module=module)
        result = reader.perform_action(
            role="push button",
            name="Insert",
            expected_change=("state",),
        )
        self.assertTrue(result["verified"])
        self.assertIn("pressed", result["after"]["state"])

    def test_perform_action_target_hilang_setelah_aksi(self):
        def close(_action):
            _action.owner.broken = True

        button, action, module = self._action_tree()
        action.owner = button
        action.on_action = close
        reader = ATSPiReader(module=module)
        result = reader.perform_action(role="push button", name="Insert")
        self.assertTrue(result["ok"])
        self.assertIsNone(result["after"])
        self.assertFalse(result["verified"])
        self.assertIn("hilang", result["note"])


if __name__ == "__main__":
    unittest.main()
