"""This module contains the implementation of the Grafana Matric Reporter class."""

from cems2 import log
from cems2.cloud_analytics.reporter.base import MetricReporterBase

# Get the logger
LOG = log.get_logger(__name__)


class Grafana(MetricReporterBase):
    """Allows to report the metrics to Grafana Dashboard."""

    def __init__(self):
        """Initialize the connection to Grafana Dashboard."""

    def report_metric(self, metric_list):
        """Report the metric to Grafana Dashboard."""
        LOG.info("Reporting metrics to Grafana Dashboard")
        print("Report:", metric_list)
        # Report the metric to Grafana Dashboard
