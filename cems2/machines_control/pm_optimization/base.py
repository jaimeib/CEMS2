"""Base class for Physical Machines Optimization plug-ins."""

from abc import ABCMeta, abstractmethod


class PMOptimizationBase(metaclass=ABCMeta):
    """Allows to optimize the physical machines."""

    @abstractmethod
    def __init__(self):
        """."""

    @abstractmethod
    async def run(self):
        """Run the Physical Machines Optimization."""
