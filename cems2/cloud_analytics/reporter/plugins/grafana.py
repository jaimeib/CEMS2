"""Grafana Metric Reporter Plugin."""

from cems2 import log
from cems2.cloud_analytics.reporter.base import MetricReporterBase

# Get the logger
LOG = log.get_logger(__name__)


class Grafana(MetricReporterBase):
    """Allows to report the metrics to Grafana Dashboard."""

    def __init__(self):
        """Initialize the connection to Grafana Dashboard."""

    async def report_metric(self, metric_list):
        """Report the metric to Grafana Dashboard.

        :param metric_list: The list of metrics to report
        :type metric_list: list[Metric]
        """
        LOG.info("Reporting metrics to Grafana Dashboard")
        rich.print("GRAFANA", metric_list)
        # Report the metric to Grafana Dashboard
