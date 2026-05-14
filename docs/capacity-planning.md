# Capacity and cost planning

Use measured peak ingress, retention, replication, compression, partition skew, compaction overhead and spare recovery bandwidth. Do not infer throughput from vCPU count alone. E2 defaults are examples, not a performance guarantee.

```bash
python3 tools/capacity.py --ingress-mib-s 5 --retention-hours 72 \
  --brokers 3 --utilization 0.65 --recovery-mib-s 50
```

The calculator returns replicated GiB with overhead, normal per-broker capacity, failure redistribution headroom and a recovery-time estimate. Recovery bandwidth must remain available in addition to normal production traffic. With three brokers and RF3, two survivors cannot restore three distinct replicas: replacement is required even with spare disk space.

## Worksheet

Record peak MiB/s, retention hours, required partitions, broker count, compression factor, topic skew, recovery objective, maximum acceptable lag and growth horizon. Run a representative load test, then record disk latency, client p99, CPU/network saturation and recovery performance under load. Size heap independently from Linux page cache.

