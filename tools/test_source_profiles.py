"""Run with: python -m unittest tools.test_source_profiles"""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import inspect_source_schema as source


class SourceProfilesTest(unittest.TestCase):
    def test_profile_selection_is_independent_of_legacy_environment(self):
        before = dict(os.environ)
        with patch.dict(os.environ, {"ERP_SOURCE_DB_NAME": "wrong_database"}):
            local = source.connection_string("coerp_xgyzx")
            self.assertIn("DATABASE={coerp_xgyzx};", local)
            self.assertIn("Trusted_Connection={yes};", local)
            self.assertNotIn("PWD=", local)
            with patch.object(source, "read_dotenv", return_value={
                "ERP_SOURCE_DB_USER": "reader", "ERP_SOURCE_DB_PASSWORD": "semi;brace}"
            }):
                remote = source.connection_string("coerp_dgyzx1")
            self.assertIn("SERVER={192.168.8.100,14331};", remote)
            self.assertIn("DATABASE={coerp_dgyzx1};", remote)
            self.assertIn("PWD={semi;brace}}};", remote)
            self.assertEqual(local, source.connection_string("coerp_xgyzx"))
            with self.assertRaises(ValueError):
                source.connection_string("missing")
        self.assertEqual(before, dict(os.environ))

    def test_legacy_dotenv_preserves_process_overrides(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env"
            path.write_text('# comment\nERP_SOURCE_DB_NAME="file_db"\n', encoding="utf-8")
            with patch.dict(os.environ, {"ERP_SOURCE_DB_NAME": "process_db"}):
                source.load_dotenv(path)
                self.assertEqual(os.environ["ERP_SOURCE_DB_NAME"], "process_db")


if __name__ == "__main__":
    unittest.main()
