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

