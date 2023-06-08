"""Metric reporter test plug-in."""

import random

import trio

from cems2 import log
from cems2.cloud_analytics.reporter.base import MetricReporterBase

# Get the logger
LOG = log.get_logger(__name__)


class Test(MetricReporterBase):
    """Allows to test the report the metrics."""

    def __init__(self):
        """Initialize the test reporter."""

    async def report_metric(self, metric_list):
        """Report the metric.

        :param metric_list: The list of metrics to report
        :type metric_list: list[Metric]
        """
        # Simulate a delay in the reporting of the metric
        await trio.sleep(random.randint(1, 5))
        print("Test-Reporter:", metric_list)
