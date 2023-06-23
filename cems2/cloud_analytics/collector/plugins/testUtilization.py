"""Metric collector utilization test plug-in."""

import json
import random
from datetime import datetime

import rich
import trio

from cems2 import log
from cems2.cloud_analytics.collector.base import MetricCollectorBase
from cems2.schemas.metric import Metric

# Get the logger
LOG = log.get_logger(__name__)


class TestUtilization(MetricCollectorBase):
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

        # Generate a random float value between 0 and 100 and round it to 3 decimals
        value = round(
            random.choice([random.uniform(0, 100), 3, 0.0])
        )  # To have more chances of having 0.0

        # Generate a payload with a random value and a unit of %
        payload = {"value": value, "unit": "%"}

        # Coverting the payload to json
        payload_json = json.dumps(payload)

        metric = Metric(
            name="utilization",
            payload=payload_json,
            timestamp=datetime.now(),
            hostname=machine_id,
            collected_by="testUtilization",
        )

        rich.print("TEST-COLLECTOR", metric)
        return metric
