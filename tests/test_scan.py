import json
import tempfile
import unittest
from pathlib import Path

from adapterbill.cli import scan_adapter


class ScanAdapterTests(unittest.TestCase):
    def test_inventory_and_metadata_findings(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "adapter_config.json").write_text(
                json.dumps(
                    {
                        "peft_type": "LORA",
                        "base_model_name_or_path": "example/base",
                        "r": 8,
                        "target_modules": ["q_proj"],
                    }
                ),
                encoding="utf-8",
            )
            report = scan_adapter(root)

        self.assertEqual(report["adapter"]["format"], "LORA")
        self.assertEqual(report["adapter"]["rank"], 8)
        self.assertEqual(len(report["files"]), 1)
        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("base_revision_missing", codes)
        self.assertIn("license_missing", codes)

    def test_pickle_weight_is_high_risk(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "adapter_config.json").write_text(
                json.dumps(
                    {
                        "peft_type": "LORA",
                        "base_model_name_or_path": "example/base",
                        "base_model_revision": "abc123",
                        "license": "mit",
                        "training_data": "example/dataset",
                    }
                ),
                encoding="utf-8",
            )
            (root / "adapter_model.bin").write_bytes(b"not-a-real-model")
            report = scan_adapter(root)

        unsafe = [
            finding
            for finding in report["findings"]
            if finding["code"] == "unsafe_serialization"
        ]
        self.assertEqual(len(unsafe), 1)
        self.assertEqual(unsafe[0]["severity"], "high")


if __name__ == "__main__":
    unittest.main()
