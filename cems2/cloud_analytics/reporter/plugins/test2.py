"""Metric reporter test2 plug-in."""

import random

import trio

from cems2 import log
from cems2.cloud_analytics.reporter.base import MetricReporterBase

# Get the logger
LOG = log.get_logger(__name__)


class Test2(MetricReporterBase):
    """Allows to test the report the metrics."""

    def __init__(self):
        """Initialize the test reporter."""

    async def report_metric(self, metric_list):
        """Report the metric."""

        # Simulate a delay in the reporting of the metric
        await trio.sleep(random.randint(5, 15))

        print("Test-Reporter:", metric_list)
