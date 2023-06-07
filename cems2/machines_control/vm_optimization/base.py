"""Base class for VMs Optimization plug-ins."""

from abc import ABCMeta, abstractmethod


class VMOptimizationBase(metaclass=ABCMeta):
    """Allows to optimize the VMs."""

    @abstractmethod
    def __init__(self):
        """."""
