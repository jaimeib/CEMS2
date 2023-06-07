"""IPMI Connector plug-in."""

import pyipmi

from cems2 import log
from cems2.machines_control.pm_connector.base import PMConnectorBase

# Get the logger
LOG = log.get_logger(__name__)

# Power states
ON = 1
OFF = 0


class IPMI(PMConnectorBase):
    """Allows to connect to the IPMI interface of the PMs."""

    def __init__(self):
        """Initialize the connection to the IPMI interface of the PMs."""

    def power_on(self, m_ip, m_username, m_password, brand_name):
        """Power on the machine."""
        LOG.critical("Powering on: %s", m_ip)

    def power_off(self, m_ip, m_username, m_password, brand_name):
        """Power off the machine."""
        LOG.critical("Powering off: %s", m_ip)

    def get_power_state(self, m_ip, m_username, m_password, brand_name):
        """Get the power state of the machine."""
        LOG.info("Getting power state of %s", m_ip)
        return OFF
