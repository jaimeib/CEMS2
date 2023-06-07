"""Metric collector utilization test plug-in."""

import random
from datetime import datetime

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
        """Collect a utilization metric."""

        # Simulate a delay in the collection of the metric
        await trio.sleep(random.randint(1, 5))

        # Generate a random float value between 0 and 100 and round it to 3 decimals
        first_value = round(random.uniform(0, 100), 3)

        value = random.choice([first_value, 0.0])  # To have more chances of having 0.0

        metric = Metric(
            name="utilization",
            value=value,
            unit="%",
            timestamp=datetime.now(),
            hostname=machine_id,
            collected_from="testUtilization",
        )

        print("TEST-Collector:", metric)
        return metric
