#!/usr/bin/env python3
"""Run the real Kafka 4.1 runtime with TLS, ACLs and six isolated local processes."""
import argparse
import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import uuid
from helpers import config, load, pki, provision

health = load("tools/health.py", "health")
smoke = load("tools/smoke.py", "smoke")


def kafka_uuid():
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode().rstrip("=")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kafka-home", type=Path, required=True)
    p.add_argument("--jmx-jar", type=Path)
    args = p.parse_args()
    kafka = args.kafka_home.resolve()
    processes, streams = {}, []
    with tempfile.TemporaryDirectory(prefix="kafka-integration-") as temp:
        root = Path(temp)
        pki.create_ca(root / "pki")
        pki.issue(root / "pki", "kafka-admin")
        pki.issue(root / "pki", "unprivileged-client")
        cluster = kafka_uuid()
        controllers = ",".join(f"{100+i}@localhost:{19093+i}:{kafka_uuid()}" for i in range(3))
        quorum = ",".join(f"localhost:{19093+i}" for i in range(3))
        names = [f"kafka-controller-{i+1}" for i in range(3)] + [f"kafka-broker-{i+1}" for i in range(3)]
        super_users = ";".join("User:CN=" + name for name in [*names, "kafka-admin"])
        commands = {}
        environment = {**os.environ, "KAFKA_HEAP_OPTS": "-Xms128m -Xmx256m", "KAFKA_JVM_PERFORMANCE_OPTS": "-server -XX:+UseG1GC -XX:ActiveProcessorCount=2"}
        bootstrap = ",".join(f"localhost:{29092+i}" for i in range(3))
        client = root / "client.properties"
        client.write_text(f"security.protocol=SSL\nssl.keystore.type=PEM\nssl.keystore.location={root}/pki/kafka-admin-client.pem\nssl.truststore.type=PEM\nssl.truststore.location={root}/pki/ca.pem\nssl.endpoint.identification.algorithm=https\n")
        try:
            for index, name in enumerate(names):
                role = "controller" if index < 3 else "broker"
                i = index % 3
                node = root / name; node.mkdir()
                bundle = json.loads(pki.issue(root / "pki", name, "localhost").read_text())
                c = config(role); c.update(node_id=100+i if role == "controller" else i+1, node_name=name, fqdn="localhost", cluster_id=cluster, quorum=quorum, initial_controllers=controllers, super_users=super_users)
                provision.install_tls(bundle, c, node / "tls")
                properties = provision.render_properties(c, str(node / "storage"), str(node / "tls"))
                if role == "controller":
                    properties = properties.replace("CONTROLLER://0.0.0.0:9093", f"CONTROLLER://127.0.0.1:{19093+i}").replace("CONTROLLER://localhost:9093", f"CONTROLLER://localhost:{19093+i}")
                else:
                    properties = properties.replace(":9092", f":{29092+i}").replace(":9094", f":{39094+i}")
                conf = node / "server.properties"; conf.write_text(properties)
                format_cmd = [str(kafka / "bin/kafka-storage.sh"), "format", "--cluster-id", cluster, "--config", str(conf)]
                format_cmd += ["--initial-controllers", controllers] if role == "controller" else ["--no-initial-controllers"]
                subprocess.run(format_cmd, check=True, env=environment, timeout=45, capture_output=True)
                if not provision.verify_identity(node / "storage", cluster, c["node_id"]):
                    raise RuntimeError("Kafka storage identity validation failed")
                log = (node / "server.log").open("w"); streams.append(log)
                env = {**environment, "LOG_DIR": str(node / "logs")}
                if args.jmx_jar:
                    env["KAFKA_OPTS"] = f"-javaagent:{args.jmx_jar.resolve()}={19404+index}:{Path(__file__).resolve().parents[1]}/bootstrap/jmx.yml"
                command = [str(kafka / "bin/kafka-server-start.sh"), str(conf)]
                commands[name] = (command, env, log)
                processes[name] = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT)
            deadline = time.monotonic() + 150
            while True:
                if any(proc.poll() is not None for proc in processes.values()):
                    raise RuntimeError("Kafka process exited during bootstrap")
                try:
                    health.health(kafka, bootstrap, client)
                    smoke.smoke(kafka, bootstrap, client)
                    break
                except (subprocess.SubprocessError, ValueError):
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(5)
            # A trusted certificate alone must not grant Kafka access.
            denied = root / "denied.properties"
            denied.write_text(client.read_text().replace("kafka-admin-client.pem", "unprivileged-client-client.pem"))
            unauthorized = subprocess.run([str(kafka / "bin/kafka-topics.sh"), "--bootstrap-server", bootstrap, "--command-config", str(denied), "--create", "--topic", "unauthorized", "--replication-factor", "3", "--partitions", "1"], capture_output=True, text=True, timeout=45)
            if unauthorized.returncode == 0 or "Authorization" not in unauthorized.stdout + unauthorized.stderr:
                raise RuntimeError("Expected a Kafka authorization denial for an unprivileged certificate")
            # Verify that a broker restart preserves cluster identity and data availability.
            node = "kafka-broker-1"
            processes[node].terminate(); processes[node].wait(timeout=45)
            command, env, log = commands[node]
            processes[node] = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT)
            deadline = time.monotonic() + 90
            while True:
                try:
                    health.health(kafka, bootstrap, client)
                    print(json.dumps(smoke.smoke(kafka, bootstrap, client)))
                    break
                except (subprocess.SubprocessError, ValueError):
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(5)
            print("PASS: six-node TLS quorum, RF3 roundtrip, ACL denial, persisted storage, broker restart")
        except Exception:
            for stream in streams: stream.flush()
            for logfile in root.glob("*/server.log"):
                print(f"--- {logfile.parent.name}: last 60 log lines ---", file=sys.stderr)
                print("\n".join(logfile.read_text().splitlines()[-60:]), file=sys.stderr)
            raise
        finally:
            for proc in processes.values():
                if proc.poll() is None: proc.terminate()
            for proc in processes.values():
                try: proc.wait(timeout=30)
                except subprocess.TimeoutExpired: proc.kill(); proc.wait()
            for stream in streams: stream.close()


if __name__ == "__main__":
    main()
