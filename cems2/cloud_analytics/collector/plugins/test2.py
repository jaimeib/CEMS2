"""Metric collector test2 plug-in."""

import random
from datetime import datetime

import trio

from cems2 import log
from cems2.cloud_analytics.collector.base import MetricCollectorBase
from cems2.schemas.metric import Metric

# Get the logger
LOG = log.get_logger(__name__)


class Test2(MetricCollectorBase):
    """Allows to test the collect the metrics."""

    def __init__(self):
        """Initialize the test collector."""

    async def collect_metric(self, machine_id):
        """Collect a metric."""

        # Simulate a delay in the collection of the metric
        await trio.sleep(random.randint(5, 15))

        # Generate a random float value between 0 and 100 and round it to 3 decimals
        value = round(random.uniform(1000, 2000), 3)

        metric = Metric(
            name="test2",
            value=value,
            unit="MB/s",
            timestamp=datetime.now(),
            hostname=machine_id,
            collected_from="test2",
        )

        print("TEST-Collector:", metric)
        return metric
