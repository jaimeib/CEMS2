"""Base class for Virtual Machine Connector plug-ins."""

from abc import ABCMeta, abstractmethod


class VMConnectorBase(metaclass=ABCMeta):
    """Allows to connect to the cloud management system to manage VMs."""

    @abstractmethod
    def __init__(self):
        """."""
