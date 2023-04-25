"""
Base class for the metric reporter plug-ins
"""

from abc import ABCMeta, abstractmethod


class MetricReporterBase(metaclass=ABCMeta):
    """
    Allows to report the metrics forwarding it through the plug-ins (Extensions in Stevedore)
    """

    @abstractmethod
    def __init__(self):
        """
        Initialize the connection to report platform
        """

    @abstractmethod
    def report_metric(self):
        """
        Report the metric to report platform
        """