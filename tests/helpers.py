import importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
provision = load("bootstrap/provision.py", "provision")
pki = load("tools/lab_pki.py", "pki")
def config(role="broker"):
    return dict(node_name="kafka-broker-1" if role == "broker" else "kafka-controller-1",
                node_id=1 if role == "broker" else 100, role=role,
                fqdn="kafka-broker-1.kafka.internal" if role == "broker" else "kafka-controller-1.kafka.internal",
                zone="us-central1-a", cluster_id="AAAAAAAAAAAAAAAAAAAAAA",
                kafka_version="4.1.2", kafka_sha512="a" * 128, retention_hours=168,
                quorum="kafka-controller-1.kafka.internal:9093,kafka-controller-2.kafka.internal:9093,kafka-controller-3.kafka.internal:9093",
                initial_controllers="100@kafka-controller-1.kafka.internal:9093:BBBBBBBBBBBBBBBBBBBBBB",
                super_users="User:CN=kafka-admin;User:CN=kafka-broker-1",
                tls_secret_version="projects/test-project/secrets/node/versions/1")
