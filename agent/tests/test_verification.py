import unittest

from fishing_agent.verification import (
    VerificationFailed,
    VerificationResult,
    require_verified,
    verify_elements,
)


class VerifyElementsTest(unittest.TestCase):
    def test_state_sama(self):
        before = {"role": "button", "name": "Simpan", "state": ("enabled",)}
        after = dict(before)
        result = verify_elements(before, after)
        self.assertTrue(result.passed)
        self.assertIn("diverifikasi", result.note)

    def test_state_berubah_tidak_terduga(self):
        before = {"role": "button", "name": "Simpan", "state": ("enabled",)}
        after = {"role": "button", "name": "Simpan", "state": ("disabled",)}
        result = verify_elements(before, after)
        self.assertFalse(result.passed)
        self.assertIn("state", result.note)

    def test_perubahan_diharapkan(self):
        before = {"role": "toggle", "name": "Mode", "state": ("off",)}
        after = {"role": "toggle", "name": "Mode", "state": ("on",)}
        result = verify_elements(
            before, after, expected_change={"state": "on"}
        )
        self.assertTrue(result.passed)

    def test_perubahan_diharapkan_tetapi_tidak_berubah(self):
        before = {"role": "toggle", "name": "Mode", "state": ("off",)}
        after = dict(before)
        result = verify_elements(
            before, after, expected_change={"state": "on"}
        )
        self.assertFalse(result.passed)


class RequireVerifiedTest(unittest.TestCase):
    def test_gagal_menimbulkan_eksepsi(self):
        result = VerificationResult(
            passed=False,
            before={"a": 1},
            after={"a": 2},
            note="a berubah",
        )
        with self.assertRaises(VerificationFailed):
            require_verified(result)

    def test_lolos(self):
        result = VerificationResult(passed=True, before={}, after={})
        require_verified(result)  # tidak raise


if __name__ == "__main__":
    unittest.main()
