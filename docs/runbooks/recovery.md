# Recovery and disaster recovery

## One node

Preserve its original data disk, node ID, cluster UUID and DNS identity. Diagnose host failure separately from disk loss. Reattach the intact disk to a replacement in its zone with the same node identity; inspect a Terraform plan carefully because automatic VM replacement is guarded. The bootstrap rejects foreign or partial metadata. Never copy another node's disk and simply change its ID.

A lost broker disk requires a controlled replacement and replica recovery from surviving ISR members. A lost controller disk requires Apache's dynamic quorum replacement procedure with correct directory IDs and membership changes; do not repeatedly run initial cluster bootstrap against an existing quorum. Take another controller out of service only after the replacement is caught up and membership is verified.

