"""Base class for PMs Connector plug-ins."""

from abc import ABCMeta, abstractmethod


class PMConnectorBase(metaclass=ABCMeta):
    """Allows to connect to the PMs."""

    @abstractmethod
    def __init__(self):
        """Initialize the connection to the PMs."""

    @abstractmethod
    async def power_on(self, m_ip, m_username, m_password, brand_name):
        """Power on the machine.

        :param m_ip: The IP address of the machine
        :type m_ip: str

        :param m_username: The username to connect to the machine
        :type m_username: str

        :param m_password: The password to connect to the machine
        :type m_password: str

        :param brand_name: The brand name of the machine
        :type brand_name: str
        """

    @abstractmethod
    async def power_off(self, m_ip, m_username, m_password, brand_name):
        """Power off the machine.

        :param m_ip: The IP address of the machine
        :type m_ip: str

        :param m_username: The username to connect to the machine
        :type m_username: str

        :param m_password: The password to connect to the machine
        :type m_password: str

        :param brand_name: The brand name of the machine
        :type brand_name: str
        """

    @abstractmethod
    async def get_power_state(self, m_ip, m_username, m_password, brand_name):
        """Get the power state of the machine.

         :param m_ip: The IP address of the machine
        :type m_ip: str

        :param m_username: The username to connect to the machine
        :type m_username: str

        :param m_password: The password to connect to the machine
        :type m_password: str

        :param brand_name: The brand name of the machine
        :type brand_name: str

        :return: The power state of the machine
        :rtype: bool
        """
