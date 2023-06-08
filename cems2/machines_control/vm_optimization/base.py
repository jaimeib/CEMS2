"""Base class for VMs Optimization plug-ins."""

from abc import ABCMeta, abstractmethod


class VMOptimizationBase(metaclass=ABCMeta):
    """Allows to optimize the VMs."""

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
    async def get_current_distribution(self):
        """Get the current distribution of VMs.

        :return: A dict with the current distribution of VMs
        :rtype: dict
        """

    @abstractmethod
    def recieve_metrics(self, metrics):
        """Recieve the metrics from the manager.

        :param metrics: metrics
        :type metrics: dict
        """
