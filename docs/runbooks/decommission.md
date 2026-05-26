# Decommissioning

Export required data/configuration and confirm retention obligations, ownership and a recovery copy before removal. Drain producers/consumers, verify no remaining dependencies and remove private client routing/DNS references deliberately.

VM API deletion protection and Terraform disk `prevent_destroy` intentionally block a casual destroy. Disabling VM protection alone does not unlock disks. To retire the cluster, review a dedicated change that disables API protection and explicitly removes the disk lifecycle guard after recovery and deletion approval. Inspect a saved destroy plan, including state prefix/project, before executing. Do not use broad force deletion or state removal to bypass the review.

Deleting this module leaves enabled project APIs unchanged and does not delete pre-existing Secret Manager secrets, state buckets, monitoring collectors or client credentials. Handle those systems according to their own retention policies. Destroying a VM must never be mistaken for safely deleting Kafka data.
