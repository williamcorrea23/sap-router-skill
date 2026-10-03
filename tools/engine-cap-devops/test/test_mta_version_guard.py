import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile


SPEC = importlib.util.spec_from_file_location(
    "mta_version_guard", Path(__file__).parents[1] / "assets" / "mta_version_guard.py"
)
GUARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)


class MtaVersionGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.mtar = root / "app.mtar"
        with zipfile.ZipFile(self.mtar, "w") as archive:
            archive.writestr("META-INF/mtad.yaml", "ID: demo\nversion: 1.0.1\n")
        self.extension = root / "dev.mtaext"
        self.extension.write_text("extends: demo\nversion: 1.0.1\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_blocks_downgrade_with_common_mta_header(self):
        with self.assertRaisesRegex(ValueError, "DOWNGRADE_BLOCKED"):
            GUARD.check(self.mtar, self.extension, "mta id version created\ndemo 1.0.2 today\n")

    def test_rejects_unknown_inventory_format(self):
        with self.assertRaisesRegex(ValueError, "Unrecognized"):
            GUARD.check(self.mtar, self.extension, "unexpected output\n")

    def test_allows_first_deploy_only_with_recognized_empty_inventory(self):
        result = GUARD.check(self.mtar, self.extension, "No multi-target apps found\n")
        self.assertEqual(result["result"], "passed")
        self.assertIsNone(result["deployedVersion"])


if __name__ == "__main__":
    unittest.main()
