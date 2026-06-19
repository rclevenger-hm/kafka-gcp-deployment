import hashlib
import io
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch
from helpers import provision
class ArtifactTests(unittest.TestCase):
    def test_checksum_success_and_cached_reuse(self):
        payload=b"verified artifact"; digest=hashlib.sha256(payload).hexdigest()
        with tempfile.TemporaryDirectory() as temp, patch.object(provision.urllib.request, "urlopen", return_value=io.BytesIO(payload)) as fetch:
            path=Path(temp)/"artifact"
            provision.download_verified("https://example.test/a", path, digest, "sha256")
            provision.download_verified("https://example.test/a", path, digest, "sha256")
            self.assertEqual(fetch.call_count, 1)
            self.assertEqual(path.read_bytes(), payload)
    def test_checksum_failure_does_not_install(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(provision.urllib.request, "urlopen", return_value=io.BytesIO(b"tampered")):
            path=Path(temp)/"artifact"
            with self.assertRaises(ValueError): provision.download_verified("https://example.test/a", path, "0"*64, "sha256")
            self.assertFalse(path.exists()); self.assertFalse(Path(str(path)+".partial").exists())
    def test_http_rejected(self):
        with self.assertRaises(ValueError): provision.download_verified("http://example.test/a", "/tmp/unused", "0"*64)
    def test_archive_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            archive=Path(temp)/"bad.tgz"
            with tarfile.open(archive, "w:gz") as tar:
                info=tarfile.TarInfo("../escape"); info.size=1; tar.addfile(info, io.BytesIO(b"x"))
            with self.assertRaises(ValueError): provision.extract_verified(archive, Path(temp)/"dest")
    def test_archive_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            archive=Path(temp)/"bad.tgz"
            with tarfile.open(archive, "w:gz") as tar:
                info=tarfile.TarInfo("link"); info.type=tarfile.SYMTYPE; info.linkname="/etc/passwd"; tar.addfile(info)
            with self.assertRaises(ValueError): provision.extract_verified(archive, Path(temp)/"dest")
    def test_numeric_secret_version_required(self):
        with self.assertRaises(ValueError): provision.secret_payload("projects/test/secrets/tls/versions/latest")
