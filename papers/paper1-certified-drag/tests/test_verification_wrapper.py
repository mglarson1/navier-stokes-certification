"""Failure-path tests for packaging; these are not mathematical proof tests."""
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("verify_bundle", ROOT / "tools/verify_bundle.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class WrapperTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def archive(self, entries):
        p = self.root / "test.tar.gz"
        with tarfile.open(p, "w:gz") as archive:
            for name, payload, kind in entries:
                member = tarfile.TarInfo(name)
                member.type = kind
                member.size = len(payload) if kind == tarfile.REGTYPE else 0
                if kind in (tarfile.SYMTYPE, tarfile.LNKTYPE):
                    member.linkname = "../../outside"
                archive.addfile(member, io.BytesIO(payload) if kind == tarfile.REGTYPE else None)
        target = self.root / "extract"
        target.mkdir(exist_ok=True)
        expected = dict(root="root", extracted_regular_files=1, extracted_bytes=2)
        return p, target, expected

    def test_same_size_tamper_is_rejected(self):
        p = self.root / "input"
        p.write_bytes(b"ab")
        record = dict(bytes=2, sha256=v.digest(p))
        v.check_file(p, record)
        p.write_bytes(b"ac")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            v.check_file(p, record)

    def test_missing_file_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "regular file"):
            v.check_file(self.root / "missing", dict(bytes=0, sha256="0" * 64))

    def test_valid_extraction(self):
        p, target, record = self.archive([("root/a", b"ab", tarfile.REGTYPE)])
        self.assertTrue(v.extract_archive(p, target, record)["passed"])
        self.assertEqual((target / "root/a").read_bytes(), b"ab")

    def test_path_traversal_is_rejected(self):
        for name in ("../outside", "root/../outside", "/root/a", "other/a", "root\\a"):
            with self.subTest(name=name):
                p, target, record = self.archive([(name, b"ab", tarfile.REGTYPE)])
                with self.assertRaises(ValueError):
                    v.extract_archive(p, target, record)
        self.assertFalse((self.root / "outside").exists())

    def test_links_and_devices_are_rejected(self):
        for kind in (tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.CHRTYPE, tarfile.FIFOTYPE):
            with self.subTest(kind=kind):
                p, target, record = self.archive([("root/a", b"", kind)])
                with self.assertRaisesRegex(ValueError, "Unsupported"):
                    v.extract_archive(p, target, record)

    def test_duplicate_member_is_rejected(self):
        p, target, record = self.archive([("root/a", b"ab", tarfile.REGTYPE)] * 2)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            v.extract_archive(p, target, record)

    def test_wrong_extracted_size_is_rejected(self):
        p, target, record = self.archive([("root/a", b"a", tarfile.REGTYPE)])
        with self.assertRaisesRegex(ValueError, "total size"):
            v.extract_archive(p, target, record)

    def test_reusing_work_directory_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Work directory exists"):
            v.main(["--source-dir", str(self.root), "--work-dir", str(self.root), "--mode", "records"])

    def test_nonlocal_http_or_embedded_secrets_are_rejected(self):
        for url in ("http://example.com/files", "https://user:password@example.com/files", "https://example.com/files?token=abc"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                v.validate_base_url(url)
        self.assertEqual(v.validate_base_url("https://zenodo.org/records/123/files/"), "https://zenodo.org/records/123/files")

    def test_download_is_promoted_only_after_hash_check(self):
        original = self.root / "original"
        original.write_bytes(b"ab")
        expected = dict(bytes=2, sha256=v.digest(original))
        for data, success in ((b"ab", True), (b"ac", False), (b"abc", False), (b"a", False)):
            with self.subTest(data=data):
                response = io.BytesIO(data)
                response.geturl = lambda: "https://example.com/file"
                dest = self.root / "download"
                with patch.object(v, "urlopen", return_value=response):
                    if success:
                        v.fetch("https://example.com/file", dest, expected)
                        self.assertEqual(dest.read_bytes(), b"ab")
                        dest.unlink()
                    else:
                        with self.assertRaises(ValueError):
                            v.fetch("https://example.com/file", dest, expected)
                        self.assertFalse(dest.exists())
                self.assertFalse(dest.with_name("download.part").exists())

    def test_disabled_assertions_are_rejected(self):
        import subprocess
        import sys
        result = subprocess.run([sys.executable, "-O", "-B", str(ROOT / "tools/verify_bundle.py"),
                                 "--source-dir", str(self.root), "--work-dir", str(self.root / "new"),
                                 "--mode", "records"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Do not use Python -O", result.stderr)
        self.assertFalse((self.root / "new").exists())

    def test_false_report_is_rejected_even_when_process_succeeds(self):
        script = self.root / "false.py"
        script.write_text("import json\nfrom pathlib import Path\nPath('result.json').write_text(json.dumps({'passed':False}))\n")
        with self.assertRaisesRegex(ValueError, "passed=true"):
            v.run_stage("false", [str(script)], self.root / "result.json", self.root, self.root, {})

    def test_curated_copies_match_provenance(self):
        records = json.loads((ROOT / "data/PROVENANCE.json").read_text())["files"]
        for rec in records:
            with self.subTest(file=rec["path"]):
                self.assertEqual(v.digest(ROOT / rec["path"]), rec["sha256"])


if __name__ == "__main__":
    unittest.main()
