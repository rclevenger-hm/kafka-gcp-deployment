# Security model

All Kafka network listeners require TLS client certificates. `StandardAuthorizer` rejects unmatched ACLs. Node certificate principals and the explicitly configured admin principals are superusers because inter-node operations must remain authorized; application certificates are not superusers. Distinct node keys limit accidental credential sharing, but a compromised Kafka node remains a serious cluster trust compromise.

## Application access

Issue a separate client certificate. Create topic and consumer group ACLs using the admin identity from a private client host. Example for a producer:

```bash
/opt/kafka/bin/kafka-acls.sh --bootstrap-server BROKER_ENDPOINTS \
  --command-config /secure/admin.properties --add \
  --allow-principal User:CN=orders-producer --producer --topic orders.events
```

For consumers use `--consumer --topic orders.events --group orders-service`. Review wildcard use explicitly. Test denied access with an unrelated trusted certificate. Certificate authentication identifies the caller; it does not automatically grant data access.

## Cloud identity

Each VM uses a distinct service account with access to exactly its own TLS secret. No JSON keys are generated. The OAuth `cloud-platform` scope is constrained by IAM. Humans use IAP and OS Login; the project SSH metadata key path and serial console access are disabled. Do not add Editor or Owner to node accounts.

## Supply chain and host controls

Kafka and the Java exporter use pinned release URLs and expected digests. Archive extraction rejects traversal, symlinks and special files. Debian packages are installed through signed package repositories; the Debian image family and security package versions are intentionally not bit-for-bit frozen. Patch and rehearse changes in a staging project. For immutable-image deployments, build a reviewed image and replace the image family reference with its exact resource ID.

systemd runs Kafka as an unprivileged user with filesystem protections and file descriptor limits. Private TLS keys are mode 0600. Provisioning never enables shell tracing or prints secret responses. Administrators with root or metadata write access can change runtime code and must be treated as privileged.

## Remaining security gates

Metrics are plaintext HTTP on a private allowlisted port. Use a private collector and a secured remote-write path; add a proxy or exporter TLS configuration if required by policy. The runtime does not install a host log/metrics agent. Attach your approved agent and IAM roles separately. Certificate expiry, host disk pressure, secret access auditing and organization policy checks must be monitored before production. See [rotation](runbooks/certificate-rotation.md).
