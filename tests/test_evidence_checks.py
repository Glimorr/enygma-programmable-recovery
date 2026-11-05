"""Mutation checks for the released, offline local-evidence verifier."""
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

PROJECT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("released_evidence_check",PROJECT/"scripts/check_evidence.py")
checker=importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

class EvidenceSensitivity(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.new=Path(self.temp.name)
        shutil.copytree(PROJECT/"evidence",self.new/"evidence")
        self.saved=checker.ROOT
        checker.ROOT=self.new
        self.addCleanup(lambda: setattr(checker,"ROOT",self.saved))

    def test_original_data_passes(self):
        self.assertEqual(checker.verify()["receipt_header_consistency_checks"],51)

    def test_changed_application_effect_rejected(self):
        file=self.new/"evidence/raw/measured/F2-02/historical-state.json"
        d=json.loads(file.read_text())
        d["destination"][1]["observer_after"]+=1
        file.write_text(json.dumps(d))
        with self.assertRaises(AssertionError):checker.verify()

    def test_changed_receipt_root_rejected(self):
        file=self.new/"evidence/raw/measured/F2-02/receipts/dest-first-roots.json"
        d=json.loads(file.read_text())
        d["calculated_receipt_root"]="0x"+"0"*64
        file.write_text(json.dumps(d))
        with self.assertRaises(AssertionError):checker.verify()

    def test_missing_source_receipt_rejected(self):
        file=self.new/"evidence/raw/measured/F2-02/receipts/source.json"
        file.unlink()
        with self.assertRaises(AssertionError):checker.verify()

if __name__=="__main__":unittest.main()
