"""Test Connector plug-in."""

import random

from cems2 import log
from cems2.machines_control.pm_connector.base import PMConnectorBase

# Get the logger
LOG = log.get_logger(__name__)

ON = True
OFF = False


class Test(PMConnectorBase):
    """Allows to test ."""

    def __init__(self):
        """Initialize the test connection."""

    def power_on(self, m_ip, m_username, m_password, brand_name):
        """Power on the machine."""
        LOG.critical("Powering on %s", m_ip)

    def power_off(self, m_ip, m_username, m_password, brand_name):
        """Power off the machine."""
        LOG.critical("Powering off %s", m_ip)

    def get_power_state(self, m_ip, m_username, m_password, brand_name):
        """Get the power state of the machine."""
        return random.choice([ON, OFF])
