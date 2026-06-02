# Testing

## Offline checks

Run `python3 -m unittest discover -s tests -v`, `python3 tools/check_repo.py`, and `bash -n bootstrap/startup.sh`. Python uses the standard library; PKI tests require OpenSSL. Terraform tests use mock Google/random providers, so no GCP credentials or cloud API apply are required. Run `terraform -chdir=terraform init -backend=false`, `terraform -chdir=terraform validate`, then `terraform -chdir=terraform test`.

Mock plans assert private addressing, failure-domain placement, access controls, deletion protection, optional NAT/IAP, input validation and complete node secret references. They cannot verify GCP IAM propagation, API quotas or network reachability.

## Real Kafka integration

On a Linux host with Java 17, OpenSSL, Python 3.11+, outbound HTTPS and approximately 4 GiB free RAM:

```bash
python3 tools/fetch_test_runtime.py
python3 tests/integration.py --kafka-home .local/kafka_2.13-4.1.2 --jmx-jar .local/jmx.jar
```

This fetches checksummed artifacts, creates a temporary CA and node/client certificates, formats and starts three controllers and three brokers on separate local ports, verifies TLS quorum, performs an RF3 roundtrip, rejects an unauthorized client and restarts a broker. The harness terminates its own processes and removes temporary secrets on exit. It does not emulate GCE disks, DNS, IAP or zones.

