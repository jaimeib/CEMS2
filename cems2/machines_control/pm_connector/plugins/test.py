"""Test Connector plug-in."""

import random

import requests
import trio

from cems2 import config_loader, log
from cems2.machines_control.pm_connector.base import PMConnectorBase

# Get the logger
LOG = log.get_logger(__name__)

# Get the config
CONFIG = config_loader.get_config()

ON = True
OFF = False


class Test(PMConnectorBase):
    """Allows to test the connector to the PMs."""

    def __init__(self):
        """Initialize the test connection."""
        self.machines_status = create_data()

    async def power_on(self, m_ip, m_username, m_password, brand_name):
        """Power on the machine."""
        await trio.sleep(random.randint(1, 5))
        LOG.critical("Powering on: %s", m_ip)

        # Move the machine from the off list to the on list
        self.machines_status["off"].remove(m_ip)
        self.machines_status["on"].append(m_ip)

    async def power_off(self, m_ip, m_username, m_password, brand_name):
        """Power off the machine."""
        await trio.sleep(random.randint(1, 5))
        LOG.critical("Powering off: %s", m_ip)

        # Move the machine from the on list to the off list
        self.machines_status["on"].remove(m_ip)
        self.machines_status["off"].append(m_ip)

    async def get_power_state(self, m_ip, m_username, m_password, brand_name):
        """Get the power state of the machine."""
        await trio.sleep(random.randint(1, 5))

        # Search the machine in the list
        if m_ip in self.machines_status["on"]:
            return ON
        elif m_ip in self.machines_status["off"]:
            return OFF


# Plugin utils:
def create_data():
    # Make a request to the API to get the list of machines available
    API_URL = "http://localhost:8000"

    # Get the list of machines available
    machines = requests.get(f"{API_URL}/machines?avaliable=True").json()

    # Get only the IP addresses
    machines_ips = [m["management_ip"] for m in machines]

    machines_status = {"on": [], "off": []}

    for m_ip in machines_ips:
        # Randomly choose if the machine is on or off
        if random.choice([ON, OFF, ON, ON]):
            machines_status["on"].append(m_ip)
        else:
            machines_status["off"].append(m_ip)

    return machines_status
