"""
This module contains the implementation of the GrafanaReporter class
"""

from cems2.cloud_analytics.reporter.base import MetricReporterBase


class GrafanaReporter(MetricReporterBase):
    """
    Allows to report the metrics to Grafana Dashboard
    """

    def __init__(self):
        """
        Initialize the connection to Grafana Dashboard
        """

    def report_metric(self):
        """
        Report the metric to Grafana Dashboard
        """

        # Report the metric to Grafana Dashboard
