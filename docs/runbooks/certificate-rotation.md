# Certificate and CA rotation

For a same-CA node rotation, issue a new certificate with the same exact CN and DNS SAN, valid beyond the response window. Verify the key matches and both serverAuth/clientAuth usages exist. Add a new Secret Manager version, pin its numeric path in Terraform and perform the [rolling runtime procedure](rolling-upgrade.md) one node at a time. Confirm peers and clients authenticate before continuing. Disable the previous secret version only after rollback is no longer required.

For CA rotation, first distribute a trust bundle containing both old and new CAs to all nodes and clients. Roll trust alone and verify. Then rotate leaf certificates to the new CA, one node/client at a time. Finally remove the old CA only after all active identities use the new chain. A single-step CA replacement can partition the cluster.

Private keys remain in protected local files and per-node secrets. Do not place secret payloads in tfvars, workflow artifacts, logs or issue reports. Monitor certificate expiration separately; a 30-day lab certificate is not a production lifecycle solution.
