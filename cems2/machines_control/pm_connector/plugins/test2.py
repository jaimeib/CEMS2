"""Test 2 Connector plug-in."""

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


class Test2(PMConnectorBase):
    """Allows to test the connector to the PMs."""

    def __init__(self):
        """Initialize the test connection."""
        self.machines_status = create_data()

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
        await trio.sleep(random.randint(5, 15))
        LOG.critical("Powering on: %s", m_ip)

        # Move the machine from the off list to the on list
        self.machines_status["off"].remove(m_ip)
        self.machines_status["on"].append(m_ip)

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
        await trio.sleep(random.randint(5, 15))
        LOG.critical("Powering off: %s", m_ip)

        # Move the machine from the on list to the off list
        self.machines_status["on"].remove(m_ip)
        self.machines_status["off"].append(m_ip)

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
        await trio.sleep(random.randint(5, 15))

        # Search the machine in the list
        if m_ip in self.machines_status["on"]:
            return ON
        elif m_ip in self.machines_status["off"]:
            return OFF


# Plugin utils:
def create_data():
    """Create the data for the test plugin.

    :return: The data for the test plugin
    :rtype: dict
    """
    # Make a request to the API to get the list of machines available
    api_url = "http://localhost:8000"

    # Get the list of machines available
    machines = requests.get(f"{api_url}/machines?avaliable=True").json()

    # Get only the IP addresses
    machines_ips = [m["management_ip"] for m in machines]

    machines_status = {"on": [], "off": []}

    for m_ip in machines_ips:
        # Randomly choose if the machine is on or off
        if random.choice([ON, OFF, ON, OFF]):
            machines_status["on"].append(m_ip)
        else:
            machines_status["off"].append(m_ip)

    return machines_status
