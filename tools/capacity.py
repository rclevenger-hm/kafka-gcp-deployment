#!/usr/bin/env python3
"""Estimate per-broker storage after a broker loss; this is not a price quote."""
import argparse
import json
import math


def estimate(ingress_mib_s, retention_hours, brokers=3, replication=3, utilization=0.65, lost_brokers=1, overhead=1.2, recovery_mib_s=50):
    values = (ingress_mib_s, retention_hours, utilization, overhead, recovery_mib_s)
    if not all(math.isfinite(x) and x > 0 for x in values):
        raise ValueError("Inputs must be finite and positive")
    if not 0 < utilization < 1 or overhead < 1:
        raise ValueError("Utilization must be below one and overhead at least one")
    if any(type(x) is not int for x in (brokers, replication, lost_brokers)) or not 1 <= replication <= brokers or not 0 <= lost_brokers < brokers:
        raise ValueError("Invalid broker, replication or failure count")
    total = ingress_mib_s * retention_hours * 3600 * replication / 1024 * overhead
    surviving = brokers - lost_brokers
    return {
        "replicated_gib_with_overhead": round(total, 2),
        "normal_gib_per_broker": math.ceil(total / brokers / utilization),
        "failure_headroom_gib_per_survivor": math.ceil(total / surviving / utilization),
        "estimated_rebuild_seconds_per_lost_broker": math.ceil(total / brokers * 1024 / recovery_mib_s),
        "can_restore_full_replication_without_replacement": surviving >= replication,
        "note": "Failure headroom assumes redistribution; RF3 with two survivors needs a replacement broker. Recovery bandwidth must be spare capacity.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ingress-mib-s", type=float, required=True)
    p.add_argument("--retention-hours", type=float, default=168)
    p.add_argument("--brokers", type=int, default=3)
    p.add_argument("--replication", type=int, default=3)
    p.add_argument("--utilization", type=float, default=0.65)
    p.add_argument("--lost-brokers", type=int, default=1)
    p.add_argument("--overhead", type=float, default=1.2)
    p.add_argument("--recovery-mib-s", type=float, default=50)
    args = p.parse_args()
    try:
        print(json.dumps(estimate(**vars(args)), indent=2))
    except ValueError as error:
        p.error(str(error))


if __name__ == "__main__":
    main()
