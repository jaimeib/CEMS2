"""Metric reporter test plug-in."""

from cems2 import log
from cems2.cloud_analytics.reporter.base import MetricReporterBase

# Get the logger
LOG = log.get_logger(__name__)


class Test(MetricReporterBase):
    """Allows to test the report the metrics."""

    def __init__(self):
        """Initialize the test reporter."""

    def report_metric(self, metric_list):
        """Report the metric."""
        LOG.info("Reporting metrics to Test reporter")
        print("Test-Reporter:", metric_list)
