"""Physical Machines Connector Manager module."""

import trio

from cems2 import config_loader, log
from cems2.machines_control import plugin_loader
from cems2.schemas.machine import Machine

# Get the logger
LOG = log.get_logger(__name__)

# Get the configuration
CONFIG = config_loader.get_config()

ON = True
OFF = False


class Manager(object):
    """Manager for the Physical Machines Connectors."""

    def __init__(self):
        """Initialize the Physical Machines connector manager."""
        # Obtain the list of Physical Machines connectors configured in the config file
        pm_connectors_list = CONFIG.getlist("machines_control.plugins", "pm_connectors")

        # Check if the Physical Machines connectors are installed
        for pm_connector in pm_connectors_list:
            if pm_connector not in plugin_loader.get_pm_connectors_names():
                LOG.error(
                    "Physical Machines Connector plugin '%s' is not installed",
                    pm_connector,
                )
                raise Exception(
                    f"Physical Machines Connector plugin '{pm_connector}' is not installed."
                )

        # Get the Physical Machines connectors from the plugin loader
        pm_connectors = [
            (i, plugin_loader.get_pm_connectors()[i]) for i in pm_connectors_list
        ]
        self.pm_connectors = pm_connectors
        LOG.debug("Physical Machines Connectors loaded: %s", pm_connectors_list)

        # Set the Physical Machines connector plugin timeout
        self.timeout = CONFIG.getint("machines_control", "pm_connector_timeout")

    async def apply_optimization(self, optimization: dict):
        """Apply the Physical Machines optimization.

        :param optimization: The Physical Machines optimization to apply
        :type optimization: dict
        """
        # Create an async task for each Physical Machine to turn on/off
        # Use a timeout for each task
        with trio.move_on_after(self.timeout) as cancel_scope:
            async with trio.open_nursery() as nursery:
                for pm in optimization["on"]:
                    nursery.start_soon(self.turn_on, pm)
                for pm in optimization["off"]:
                    nursery.start_soon(self.turn_off, pm)

        if cancel_scope.cancelled_caught:
            LOG.error(
                "Physical Machines optimization timeout for machine %s using connector %s",
                pm.hostname,
                pm.connector,
            )

    async def turn_on(self, pm: Machine):
        """Turn on a Physical Machine.

        :param pm: Physical Machine to turn on
        :type pm: Machine
        """
        # Get the connector of the physical machine
        pm_connector_plugin = self._get_machine_connector(pm)

        # Check if the machine is already on
        if pm.energy_status == ON:
            LOG.debug("%s is already on", pm.hostname)
            return

        # Turn on the machine
        LOG.debug("Turning on %s", pm.hostname)
        await pm_connector_plugin().power_on(
            pm.management_ip,
            pm.management_username,
            pm.management_password,
            pm.brand_model,
        )

    async def turn_off(self, pm: Machine):
        """Turn off a Physical Machine.

        :param pm: Physical Machine to turn off
        :type pm: Machine
        """
        # Get the connector of the physical machine
        pm_connector_plugin = self._get_machine_connector(pm)

        # Check if the machine is already off
        if pm.energy_status == OFF:
            LOG.debug("%s is already off", pm.hostname)
            return

        # Turn off the machine
        LOG.debug("Turning off %s", pm.hostname)
        await pm_connector_plugin().power_off(
            pm.management_ip,
            pm.management_username,
            pm.management_password,
            pm.brand_model,
        )

    async def get_pm_state(self, pm: Machine):
        """Get the state of a Physical Machine.

        :param pm: Physical Machine to get the state of
        :type pm: Machine
        :return: The state of the Physical Machine
        :rtype: bool
        """

        # Get the connector of the physical machine
        pm_connector_plugin = self._get_machine_connector(pm)

        # Get the power state of the machine
        status = await pm_connector_plugin().get_power_state(
            pm.management_ip,
            pm.management_username,
            pm.management_password,
            pm.brand_model,
        )

        # Return the state
        return status

    def _get_machine_connector(self, pm: Machine):
        """Get the connector of a Physical Machine.

        :param pm: Physical Machine to get the connector of
        :type pm: Machine

        :return: The connector plugin of the Physical Machine
        :rtype: object
        """
        # Find the connector for the physical machine
        for pm_connector_name, pm_connector_plugin in self.pm_connectors:
            if pm_connector_name == pm.connector:
                break

        # If the connector is not found, raise an exception
        if pm_connector_plugin is None:
            LOG.error(
                "Physical Machines Connector plugin '%s' is not installed",
                pm.connector,
            )
            raise Exception(
                f"Physical Machines Connector plugin '{pm.connector}' is not installed."
            )

        # Return the connector
        return pm_connector_plugin

    def get_installed_plugins(self):
        """Get the list of installed Physical Machines connectors.

        :return: The list of installed Physical Machines connectors
        :rtype: list[str]
        """
        return plugin_loader.get_pm_connectors_names()
