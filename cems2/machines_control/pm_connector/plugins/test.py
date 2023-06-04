"""Test Connector plug-in."""

import random

import trio

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

    async def power_on(self, m_ip, m_username, m_password, brand_name):
        """Power on the machine."""
        await trio.sleep(random.randint(1, 5))
        LOG.critical("Powering on %s", m_ip)

    async def power_off(self, m_ip, m_username, m_password, brand_name):
        """Power off the machine."""
        await trio.sleep(random.randint(1, 5))
        LOG.critical("Powering off %s", m_ip)

    async def get_power_state(self, m_ip, m_username, m_password, brand_name):
        """Get the power state of the machine."""
        await trio.sleep(random.randint(1, 5))
        return random.choice([ON, OFF])
