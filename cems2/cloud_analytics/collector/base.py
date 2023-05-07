"""Base class for the metric collector plug-ins."""

from abc import ABCMeta, abstractmethod


class MetricCollectorBase(metaclass=ABCMeta):
    """Allows to collect the metrics obtained through the plug-ins."""

    @abstractmethod
    def __init__(self):
        """Initialize the connection to the cloud platform."""

    @abstractmethod
    def collect_metric(self, machine_id):
        """Collect the metric from the cloud platform."""
