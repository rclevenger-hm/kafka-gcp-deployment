# Security model

All Kafka network listeners require TLS client certificates. `StandardAuthorizer` rejects unmatched ACLs. Node certificate principals and the explicitly configured admin principals are superusers because inter-node operations must remain authorized; application certificates are not superusers. Distinct node keys limit accidental credential sharing, but a compromised Kafka node remains a serious cluster trust compromise.

