# Decision 002: deliberate runtime changes

Terraform updates nonsecret metadata without replacing all Kafka VMs. Bootstrap compares a fingerprint of node settings and runtime source with the last applied configuration. A changed runtime requires the operator to follow a one-node rolling procedure and explicitly pass `--apply-change`. Machine-type updates do not get automatic stop permission.

Persistent disks have independent Terraform resources and deletion guards. Formatting is allowed only for empty directories on the dedicated ext4 disk, and existing metadata must match the node and cluster. The bootstrap never uses `--ignore-formatted` to bypass an identity mismatch. This favors explicit recovery over automatically bringing up a potentially different cluster.
