#!/usr/bin/env python3
"""Create a unique RF3 topic, verify exact roundtrip, and delete only that topic."""
import argparse
import json
from pathlib import Path
import subprocess
import time
import uuid


def smoke(kafka_home, bootstrap, config, timeout=90):
    topic = "deployment-smoke-" + uuid.uuid4().hex
    payload = "kafka-gcp-" + uuid.uuid4().hex
    home = Path(kafka_home) / "bin"
    common = ["--bootstrap-server", bootstrap]
    def call(tool, *args, **kwargs):
        return subprocess.run([str(home / tool), *common, *args], text=True, capture_output=True, check=True, timeout=timeout, **kwargs)
    created = False
    started = time.monotonic()
    try:
        call("kafka-topics.sh", "--command-config", str(config), "--create", "--topic", topic, "--partitions", "3", "--replication-factor", "3", "--config", "min.insync.replicas=2")
        created = True
        call("kafka-console-producer.sh", "--producer.config", str(config), "--topic", topic, "--producer-property", "acks=all", "--producer-property", "enable.idempotence=true", input=payload + "\n")
        result = call("kafka-console-consumer.sh", "--consumer.config", str(config), "--topic", topic, "--from-beginning", "--max-messages", "1", "--timeout-ms", str((timeout - 5) * 1000), "--group", topic)
        if result.stdout.strip() != payload:
            raise RuntimeError("Roundtrip payload mismatch")
        return {"ok": True, "topic": topic, "elapsed_seconds": round(time.monotonic() - started, 2)}
    finally:
        if created:
            call("kafka-topics.sh", "--command-config", str(config), "--delete", "--topic", topic)


