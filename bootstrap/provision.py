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


