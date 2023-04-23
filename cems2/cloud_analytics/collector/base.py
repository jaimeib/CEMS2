from abc import ABCMeta, abstractmethod


class MetricCollectorBase(metaclass=abc.ABCMeta):
    """
    Allows to collect the metrics obtained through the plug-ins (Extensions in Stevedore)
    """

    @abstractmethod
    def __init__(self) -> None:
        """
        Initialize the connection to the cloud platform
        """

    @abstractmethod
    def collect_metric(self, instance_id) -> None:
        """
        Collect the metric from the cloud platform
        """
