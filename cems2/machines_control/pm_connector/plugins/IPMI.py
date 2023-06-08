"""IPMI Connector plug-in."""

import pyipmi

from cems2 import log
from cems2.machines_control.pm_connector.base import PMConnectorBase

# Get the logger
LOG = log.get_logger(__name__)

# Power states
ON = True
OFF = False


class IPMI(PMConnectorBase):
    """Allows to connect to the IPMI interface of the PMs."""

    def __init__(self):
        """Initialize the connection to the IPMI interface of the PMs."""

    def power_on(self, m_ip, m_username, m_password, brand_name):
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
        LOG.critical("Powering on: %s", m_ip)

    def power_off(self, m_ip, m_username, m_password, brand_name):
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
        LOG.critical("Powering off: %s", m_ip)

    def get_power_state(self, m_ip, m_username, m_password, brand_name):
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
        LOG.info("Getting power state of %s", m_ip)
        return ON
