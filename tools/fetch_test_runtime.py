#!/usr/bin/env python3
"""Fetch the exact checksummed runtime used by Terraform for integration tests."""
import argparse
import importlib.util
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("provision", ROOT / "bootstrap/provision.py")
provision = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provision)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, default=ROOT/".local")
    args=p.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
    variables=(ROOT/"terraform/variables.tf").read_text()
    def default(name):
        return re.search(r'variable "'+name+r'" \{.*?default\s*=\s*"([^"]+)"',variables,re.S)[1]
    version=default("kafka_version"); digest=default("kafka_sha512")
    archive=args.out/f"kafka_2.13-{version}.tgz"
    provision.download_verified(f"https://archive.apache.org/dist/kafka/{version}/{archive.name}",archive,digest)
    provision.extract_verified(archive,args.out)
    provision.download_verified(provision.JMX_URL,args.out/"jmx.jar",provision.JMX_SHA256,"sha256")
    print(args.out/f"kafka_2.13-{version}")


if __name__ == "__main__": main()
