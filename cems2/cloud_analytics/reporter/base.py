"""Base class for the metric reporter plug-ins."""

from abc import ABCMeta, abstractmethod


class MetricReporterBase(metaclass=ABCMeta):
    """Allows to report the metrics forwarding it through the plug-ins."""

    @abstractmethod
    def __init__(self):
        """Initialize the connection to report platform."""

    @abstractmethod
    async def report_metric(self, metric_list):
        """Report the metric to report platform.

        :param metric_list: The list of metrics to report
        :type metric_list: list[Metric]
        """
