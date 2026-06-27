#!/usr/bin/env python3
"""Read-only Kafka health gates for smoke tests and rolling maintenance."""
import argparse
import json
from pathlib import Path
import re
import subprocess


def parse_quorum(text, expected_voters=3):
    fields = dict(line.split(":", 1) for line in text.splitlines() if ":" in line)
    leader = int(fields.get("LeaderId", "-1").strip())
    lag = int(fields.get("MaxFollowerLag", "-1").strip())
    voters = json.loads(fields.get("CurrentVoters", "[]").strip())
    if leader < 0 or lag != 0 or len(voters) != expected_voters:
        raise ValueError("Quorum is not healthy: require a leader, zero follower lag and all expected voters")
    return {"leader": leader, "max_follower_lag": lag, "voters": len(voters)}


def health(home, bootstrap, config):
    def call(tool, *args):
        return subprocess.run([str(Path(home) / "bin" / tool), "--bootstrap-server", bootstrap, "--command-config", str(config), *args], capture_output=True, text=True, timeout=60, check=True).stdout
    quorum = parse_quorum(call("kafka-metadata-quorum.sh", "describe", "--status"))
    for flag in ("--under-replicated-partitions", "--unavailable-partitions", "--under-min-isr-partitions"):
        output = call("kafka-topics.sh", "--describe", flag)
        if re.search(r"\bTopic:", output):
            raise ValueError("Unsafe maintenance state: " + flag)
    return {"ok": True, "quorum": quorum}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kafka-home", default="/opt/kafka")
    p.add_argument("--bootstrap", required=True)
    p.add_argument("--config", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(health(args.kafka_home, args.bootstrap, args.config), indent=2))


if __name__ == "__main__":
    main()
