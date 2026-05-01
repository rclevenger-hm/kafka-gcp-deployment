#!/usr/bin/env python3
"""Provision one private Kafka node. No cloud credentials or TLS payloads in state."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import pwd
import re
import shutil
import subprocess
import tarfile
import tempfile
import time
import urllib.request

META = "http://metadata.google.internal/computeMetadata/v1/"
JMX_URL = "https://github.com/prometheus/jmx_exporter/releases/download/1.1.0/jmx_prometheus_javaagent-1.1.0.jar"
JMX_SHA256 = "2d158db7a4cd2999f40ca30a2532bc8456ca3ecf37498cbe60a02a588bf3c9f1"


def run(*args, **kwargs):
    return subprocess.run(args, check=True, text=True, timeout=300, **kwargs)


def atomic_write(path, value, mode=0o640):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, mode)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def request(url, headers=None):
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read()
        except OSError:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)


def secret_payload(version):
    if not re.fullmatch(r"projects/[a-z0-9-]+/secrets/[A-Za-z0-9_-]+/versions/[1-9][0-9]*", version):
        raise ValueError("Expected a pinned numeric secret version")
    token = json.loads(request(META + "instance/service-accounts/default/token", {"Metadata-Flavor": "Google"}))["access_token"]
    data = json.loads(request("https://secretmanager.googleapis.com/v1/" + version + ":access", {"Authorization": "Bearer " + token}))
    return json.loads(base64.b64decode(data["payload"]["data"], validate=True))


def validate_config(c):
    patterns = {
        "node_name": r"[a-z][a-z0-9-]{2,50}", "fqdn": r"[a-z][a-z0-9.-]+",
        "zone": r"[a-z]+-[a-z]+[0-9]+-[a-z]", "cluster_id": r"[A-Za-z0-9_-]{22}",
        "kafka_version": r"4\.1\.[0-9]+", "kafka_sha512": r"[a-f0-9]{128}",
        "quorum": r"[a-z0-9.,:-]+", "initial_controllers": r"[A-Za-z0-9_.,:@-]+",
        "super_users": r"User:CN=[a-zA-Z0-9._-]+(?:;User:CN=[a-zA-Z0-9._-]+)*",
    }
    for field, pattern in patterns.items():
        if not isinstance(c.get(field), str) or not re.fullmatch(pattern, c[field]):
            raise ValueError("Invalid configuration field: " + field)
    if c.get("role") not in {"broker", "controller"}:
        raise ValueError("Dedicated broker or controller role required")
    for field in ("node_id", "retention_hours"):
        if type(c.get(field)) is not int or c[field] < 1:
            raise ValueError("Invalid positive integer: " + field)


def render_properties(c, root="/var/lib/kafka", tls="/etc/kafka/tls"):
    validate_config(c)
    config = {
        "process.roles": c["role"], "node.id": c["node_id"],
        "controller.quorum.bootstrap.servers": c["quorum"],
        "controller.listener.names": "CONTROLLER",
        "listener.security.protocol.map": "CLIENT:SSL,BROKER:SSL,CONTROLLER:SSL",
        "inter.broker.listener.name": "BROKER",
        "listeners": "CONTROLLER://0.0.0.0:9093" if c["role"] == "controller" else "CLIENT://0.0.0.0:9092,BROKER://0.0.0.0:9094",
        "log.dirs": root + "/data", "metadata.log.dir": root + "/metadata",
        "ssl.keystore.type": "PEM", "ssl.keystore.location": tls + "/node.pem",
        "ssl.truststore.type": "PEM", "ssl.truststore.location": tls + "/ca.pem",
        "ssl.client.auth": "required", "ssl.endpoint.identification.algorithm": "https",
        "ssl.enabled.protocols": "TLSv1.3,TLSv1.2",
        "authorizer.class.name": "org.apache.kafka.metadata.authorizer.StandardAuthorizer",
        "allow.everyone.if.no.acl.found": "false", "super.users": c["super_users"],
        "auto.create.topics.enable": "false", "unclean.leader.election.enable": "false",
        "default.replication.factor": 3, "min.insync.replicas": 2,
        "offsets.topic.replication.factor": 3, "transaction.state.log.replication.factor": 3,
        "transaction.state.log.min.isr": 2, "log.retention.hours": c["retention_hours"],
        "num.partitions": 3,
    }
    if c["role"] == "broker":
        config["advertised.listeners"] = f"CLIENT://{c['fqdn']}:9092,BROKER://{c['fqdn']}:9094"
        config["broker.rack"] = c["zone"]
    return "".join(f"{key}={value}\n" for key, value in config.items())


def verify_identity(root, cluster_id, node_id):
    """Never overwrite foreign, incomplete or nonempty unformatted storage."""
    paths = [Path(root) / "data", Path(root) / "metadata"]
    found = []
    for path in paths:
        meta = path / "meta.properties"
        if meta.exists():
            values = dict(line.split("=", 1) for line in meta.read_text().splitlines() if "=" in line and not line.startswith("#"))
            if values.get("cluster.id") != cluster_id or values.get("node.id") != str(node_id):
                raise ValueError("Disk cluster/node identity does not match configuration")
            found.append(True)
        else:
            if path.exists() and any(path.iterdir()):
                raise ValueError("Refusing to format a nonempty directory without identity")
            found.append(False)
    if any(found) and not all(found):
        raise ValueError("Partial storage identity; operator recovery required")
    return all(found)


