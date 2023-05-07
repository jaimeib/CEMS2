"""Base class for Physical Machines Connector plug-ins."""

from abc import ABCMeta, abstractmethod


class PMConnectorBase(metaclass=ABCMeta):
    """Allows to connect to the physical machines."""

    @abstractmethod
    def __init__(self):
        """."""
