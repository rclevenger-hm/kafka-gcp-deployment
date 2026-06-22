import json
from pathlib import Path
import tempfile
import unittest
from helpers import config, pki, provision
class PkiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(); cls.root=Path(cls.temp.name)/"pki"
        pki.create_ca(cls.root)
        cls.bundle=json.loads(pki.issue(cls.root,"kafka-broker-1","kafka-broker-1.kafka.internal").read_text())
    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()
    def test_valid_identity_is_installed(self):
        target=Path(self.temp.name)/"valid"
        provision.install_tls(self.bundle,config(),target)
        self.assertEqual((target/"node.pem").stat().st_mode & 0o777,0o600)
        self.assertIn("BEGIN PRIVATE KEY",(target/"node.pem").read_text())
    def test_wrong_hostname_fails(self):
        c=config(); c["fqdn"]="wrong.kafka.internal"
        with self.assertRaises(Exception): provision.install_tls(self.bundle,c,Path(self.temp.name)/"wrong")
    def test_wrong_principal_fails(self):
        c=config(); c["node_name"]="kafka-broker-2"
        with self.assertRaises(ValueError): provision.install_tls(self.bundle,c,Path(self.temp.name)/"principal")
    def test_overwrite_prohibited(self):
        with self.assertRaises(FileExistsError): pki.issue(self.root,"kafka-broker-1","kafka-broker-1.kafka.internal")
    def test_missing_material_rejected(self):
        bundle=dict(self.bundle); del bundle["private_key"]
        with self.assertRaises(ValueError): provision.install_tls(bundle,config(),Path(self.temp.name)/"missing")
    def test_subject_injection_rejected(self):
        with self.assertRaises(ValueError): pki.issue(self.root,"bad/OU=admin")
