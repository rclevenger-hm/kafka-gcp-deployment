#!/usr/bin/env python3
"""Issue short-lived lab certificates offline. Use your organizational CA in production."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess


def run(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=60)


def issue(directory, name, fqdn=None, days=30):
    directory = Path(directory)
    if not re.fullmatch(r"[a-z][a-z0-9-]{2,60}", name):
        raise ValueError("Invalid certificate name")
    if fqdn and not re.fullmatch(r"[a-z][a-z0-9.-]+", fqdn):
        raise ValueError("Invalid DNS name")
    key, cert, csr = [directory / (name + ext) for ext in (".key", ".pem", ".csr")]
    if any(p.exists() for p in (key, cert, csr)):
        raise FileExistsError("Refusing to overwrite a certificate identity")
    run("openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-out", str(key))
    run("openssl", "req", "-new", "-key", str(key), "-subj", "/CN=" + name, "-out", str(csr))
    ext = directory / (name + ".ext")
    ext.write_text("basicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth,clientAuth\n" + ("subjectAltName=DNS:" + fqdn + "\n" if fqdn else ""))
    run("openssl", "x509", "-req", "-in", str(csr), "-CA", str(directory / "ca.pem"), "-CAkey", str(directory / "ca.key"), "-CAcreateserial", "-days", str(days), "-sha256", "-extfile", str(ext), "-out", str(cert))
    bundle = {"certificate": cert.read_text(), "private_key": key.read_text(), "ca": (directory / "ca.pem").read_text()}
    path = directory / (name + ".json")
    path.write_text(json.dumps(bundle) + "\n")
    combined = directory / (name + "-client.pem")
    combined.write_text(key.read_text() + cert.read_text())
    for p in (key, path, combined):
        p.chmod(0o600)
    return path


def create_ca(directory, days=30):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False, mode=0o700)
    run("openssl", "req", "-x509", "-newkey", "rsa:3072", "-nodes", "-sha256", "-days", str(days), "-subj", "/CN=kafka-lab-ca", "-addext", "basicConstraints=critical,CA:TRUE", "-addext", "keyUsage=critical,keyCertSign,cRLSign", "-keyout", str(directory / "ca.key"), "-out", str(directory / "ca.pem"))
    (directory / "ca.key").chmod(0o600)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, default=Path("pki"))
    p.add_argument("--prefix", default="kafka")
    p.add_argument("--domain", default="kafka.internal")
    p.add_argument("--brokers", type=int, choices=range(3, 19), default=3)
    args = p.parse_args()
    os.umask(0o077)
    create_ca(args.out)
    for role, count in (("controller", 3), ("broker", args.brokers)):
        for i in range(1, count + 1):
            name = f"{args.prefix}-{role}-{i}"
            issue(args.out, name, f"{name}.{args.domain}")
    issue(args.out, "kafka-admin")
    print(f"Created 30-day lab PKI in {args.out}; protect the CA key and upload only each node JSON to its own secret.")


if __name__ == "__main__":
    main()
