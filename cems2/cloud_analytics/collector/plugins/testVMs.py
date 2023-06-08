"""Metric collector utilization test plug-in."""

import json
import random
import uuid
from datetime import datetime

import trio

from cems2 import log
from cems2.cloud_analytics.collector.base import MetricCollectorBase
from cems2.schemas.metric import Metric

# Get the logger
LOG = log.get_logger(__name__)


class TestVMs(MetricCollectorBase):
    """Allows to test the collect of the utilization metrics."""

    def __init__(self):
        """Initialize the utilization test collector."""

    async def collect_metric(self, machine_id):
        """Collect a utilization metric."""

        # Simulate a delay in the collection of the metric
        await trio.sleep(random.randint(1, 5))

        # Generate a random int value in range 0-10 VMs
        num_vms = random.randint(0, 10)

        vms_list = []

        for _ in range(num_vms):
            vms_list.append(
                {
                    "uuid": str(uuid.uuid4()),
                    "vcpus": random.randint(0, 16),
                    "memory": {
                        "amount": random.randint(0, 16384),
                        "unit": "MB",
                    },
                    "disk": {"amount": random.randint(0, 100), "unit": "GB"},
                    "managed_by": "OpenStack",
                }
            )

        # Convert the list to a dict the key is the vmsX where X is the number of the VM
        vms_dict = {"vms{}".format(i): vms_list[i] for i in range(len(vms_list))}

        # Convert the dict to a json
        vms_json = json.dumps(vms_dict)

        # Create a multiple metric
        metric = Metric(
            name="vms",
            payload=vms_json,
            timestamp=datetime.now(),
            hostname=machine_id,
            collected_from="testVMs",
        )

        print("TEST-Collector:", metric)
        return metric
