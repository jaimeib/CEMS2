"""Metric collector test plug-in."""

import random
from datetime import datetime

import trio

from cems2 import log
from cems2.cloud_analytics.collector.base import MetricCollectorBase
from cems2.schemas.metric import Metric

# Get the logger
LOG = log.get_logger(__name__)


class Test(MetricCollectorBase):
    """Allows to test the collect the metrics."""

    def __init__(self):
        """Initialize the test collector."""

    async def collect_metric(self, machine_id):
        """Collect a metric."""
        LOG.info("Collecting test metric from the machine %s", machine_id)

        # Simulate a delay in the collection of the metric
        await trio.sleep(random.randint(1, 5))

        # Generate a random float value between 0 and 100 and round it to 3 decimals
        value = round(random.uniform(0, 100), 3)

        metric = Metric(
            name="test",
            value=value,
            unit="%",
            timestamp=datetime.now(),
            hostname=machine_id,
        )

        print("TEST-Collector:", metric)
        return metric
