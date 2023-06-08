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
        """Collect a utilization metric.

        :param machine_id: The id of the machine (hostname)
        :type machine_id: str

        :return: The metric
        :rtype: Metric
        """
        # Simulate a delay in the collection of the metric
        await trio.sleep(random.randint(1, 5))

        # Generate a random int value in range 0-5 VMs
        num_vms = random.randint(0, 5)

        vms_list = []

        for _ in range(num_vms):
            vms_list.append(
                {
                    "vcpus": random.randint(1, 8),
                    "memory": {"amount": random.randint(1024, 8192), "unit": "MB"},
                    "disk": {"amount": random.randint(10, 50), "unit": "GB"},
                    "managed_by": "test",  # The VM connector that manages the VM
                }
            )

        # Create a dict with the VMs
        vms_dict = {str(uuid.uuid4()): vm for vm in vms_list}

        # Convert the dict to a json
        vms_json = json.dumps(vms_dict)

        # Create a multiple metric
        metric = Metric(
            name="vms",
            payload=vms_json,
            timestamp=datetime.now(),
            hostname=machine_id,
            collected_from="test_VMs",
        )

        print("TEST-Collector:", metric)
        return metric
