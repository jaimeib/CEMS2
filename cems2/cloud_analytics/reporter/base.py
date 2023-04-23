from abc import ABCMeta, abstractmethod


class MetricReporterBase(metaclass=abc.ABCMeta):
    """
    Allows to report the metrics forwarding it through the plug-ins (Extensions in Stevedore)
    """

    @abstractmethod
    def __init__(self) -> None:
        """
        Initialize the connection to report platform
        """

    @abstractmethod
    def report_metric(self) -> None:
        """
        Report the metric to report platform
        """
