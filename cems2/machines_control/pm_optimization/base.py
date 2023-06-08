"""Base class for PMs Optimization plug-ins."""

from abc import ABCMeta, abstractmethod


class PMOptimizationBase(metaclass=ABCMeta):
    """Allows to optimize the PMs."""

    @abstractmethod
    def __init__(self):
        """Initialize the PMs Optimization."""

    @abstractmethod
    async def run(self):
        """Run the PMs Optimization."""

    @abstractmethod
    async def get_optimization(self):
        """Get the optimization result.

        :return: A dict with the result of the optimization
        :rtype: dict
        """

    @abstractmethod
    def recieve_metrics(self, metrics):
        """Recieve the metrics from the manager.

        :param metrics: metrics
        :type metrics: dict
        """

    @abstractmethod
    def recieve_baseline(self, baseline):
        """Recieve the baseline from the manager.

        :param baseline: baseline
        :type baseline: int
        """
