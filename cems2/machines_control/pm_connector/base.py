"""Base class for PMs Connector plug-ins."""

from abc import ABCMeta, abstractmethod


class PMConnectorBase(metaclass=ABCMeta):
    """Allows to connect to the PMs."""

    @abstractmethod
    def __init__(self):
        """Initialize the connection to the PMs."""

    @abstractmethod
    async def power_on(self, m_ip, m_username, m_password, brand_name):
        """Power on the machine."""

    @abstractmethod
    async def power_off(self, m_ip, m_username, m_password, brand_name):
        """Power off the machine."""

    @abstractmethod
    async def get_power_state(self, m_ip, m_username, m_password, brand_name):
        """Get the power state of the machine."""
