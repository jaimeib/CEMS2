"""Base class for Virtual Machine Optimization plug-ins."""

from abc import ABCMeta, abstractmethod


class VMOptimizationBase(metaclass=ABCMeta):
    """Allows to optimize the virtual machines."""

    @abstractmethod
    def __init__(self):
        """."""
