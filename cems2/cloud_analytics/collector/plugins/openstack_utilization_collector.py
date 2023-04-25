"""
OpenStack utilization collector plug-in
"""

from cems2.cloud_analytics.collector.base import MetricCollectorBase


class OpenStackUtilizationCollector(MetricCollectorBase):
    """
    Allows to collect the utilization metrics from the OpenStack cloud platform
    """

    def __init__(self):
        """
        Initialize the connection to the OpenStack cloud platform
        """

        # TODO: Open a session to the OpenStack cloud platform

    def collect_metric(self, machine_id):
        """
        Collect the utilization metric from the OpenStack cloud platform
        """

        # Get the server object

        # Get the server utilization
