from cloud_analytics.collector.base import MetricCollectorBase


class OpenStackUtilizationCollector(MetricCollectorBase):
    """
    Allows to collect the utilization metrics from the OpenStack cloud platform
    """

    def __init__(self) -> None:
        """
        Initialize the connection to the OpenStack cloud platform
        """

    def collect_metric(self, instance_id) -> None:
        """
        Collect the utilization metric from the OpenStack cloud platform
        """

        # Get the server object

        # Get the server utilization
