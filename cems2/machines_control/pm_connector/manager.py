"""PM Connector Manager module."""

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
    """Manager for the PM Connectors."""

    def __init__(self):
        """Initialize the PM connector manager."""

        # Control Manager
        self.machines_control_manager = None

        # Obtain the list of PM connectors configured in the config file
        pm_connectors_list = CONFIG.getlist("machines_control.plugins", "pm_connectors")

        # Check if the PM connectors are installed
        for pm_connector in pm_connectors_list:
            if pm_connector not in plugin_loader.get_pm_connectors_names():
                LOG.error(
                    "PM Connector plugin '%s' is not installed",
                    pm_connector,
                )
                raise Exception(
                    f"PM Connector plugin '{pm_connector}' is not installed."
                )

        # Get the PM connectors from the plugin loader
        pm_connectors = [
            (i, plugin_loader.get_pm_connectors()[i]) for i in pm_connectors_list
        ]

        # Create an instance of each PM connector (Only one object for each connector)
        pm_connectors = [(i, j()) for i, j in pm_connectors]

        self.pm_connectors = pm_connectors
        LOG.debug("PM Connectors loaded: %s", pm_connectors_list)

        # Set the PM connector plugin timeout
        self.timeout = CONFIG.getint("machines_control", "pm_connector_timeout")

    async def apply_optimization(self, optimization: dict):
        """Apply the PM optimization.

        :param optimization: The PM optimization to apply
        :type optimization: dict
        """
        # Create an async task for each PM to turn on/off
        # Use a timeout for each task
        with trio.move_on_after(self.timeout) as cancel_scope:
            async with trio.open_nursery() as nursery:
                for pm in optimization["on"]:
                    nursery.start_soon(self.turn_on, pm)
                for pm in optimization["off"]:
                    nursery.start_soon(self.turn_off, pm)

        if cancel_scope.cancelled_caught:
            LOG.error(
                "PM connector timeout for machine %s using connector %s.",
                pm.hostname,
                pm.connector,
            )

    async def turn_on(self, pm: Machine):
        """Turn on a PM.

        :param pm: PM to turn on
        :type pm: Machine
        """
        # Get the connector of the PM
        pm_connector_plugin = self._get_pm_connector(pm)

        # Check if the machine is already on
        if pm.energy_status == ON:
            LOG.debug("%s is already on", pm.hostname)
            return

        # Turn on the machine
        LOG.warning("Turning on %s", pm.hostname)
        await pm_connector_plugin.power_on(
            pm.management_ip,
            pm.management_username,
            pm.management_password,
            pm.brand_model,
        )

        # Get the state of the machine to check if it is on
        status = await self.get_pm_state(pm)

        # Notify the controller that the machine is on
        if status == ON:
            LOG.debug("Checking that %s is now on", pm.hostname)
            # Update the machine status
            pm.energy_status = ON
            self.machines_control_manager.notify_machine_status(pm)
        else:
            LOG.error(
                "Failed to turn on %s using connector %s",
                pm.hostname,
                pm.connector,
            )

    async def turn_off(self, pm: Machine):
        """Turn off a PM.

        :param pm: PM to turn off
        :type pm: Machine
        """
        # Get the connector of the PM
        pm_connector_plugin = self._get_pm_connector(pm)

        # Check if the machine is already off
        if pm.energy_status == OFF:
            LOG.debug("%s is already off", pm.hostname)
            return

        # Turn off the machine
        LOG.warning("Turning off %s", pm.hostname)
        await pm_connector_plugin.power_off(
            pm.management_ip,
            pm.management_username,
            pm.management_password,
            pm.brand_model,
        )

        # Get the state of the machine to check if it is off
        status = await self.get_pm_state(pm)

        # Notify the controller that the machine is off
        if status == OFF:
            LOG.debug("Checking that %s is now off", pm.hostname)
            # Update the machine status
            pm.energy_status = OFF
            self.machines_control_manager.notify_machine_status(pm)
        else:
            LOG.error(
                "Failed to turn off %s using connector %s",
                pm.hostname,
                pm.connector,
            )

    async def get_pm_state(self, pm: Machine):
        """Get the state of a PM.

        :param pm: PM to get the state of
        :type pm: Machine
        :return: The state of the PM
        :rtype: bool
        """

        # Get the connector of the PM
        pm_connector_plugin = self._get_pm_connector(pm)

        # Get the power state of the machine
        status = await pm_connector_plugin.get_power_state(
            pm.management_ip,
            pm.management_username,
            pm.management_password,
            pm.brand_model,
        )

        # Return the state
        return status

    def _get_pm_connector(self, pm: Machine):
        """Get the connector of a PM.

        :param pm: PM to get the connector of
        :type pm: Machine

        :return: The connector plugin of the PM
        :rtype: object
        """
        # Find the connector for the PM
        for pm_connector_name, pm_connector_plugin in self.pm_connectors:
            if pm_connector_name == pm.connector:
                break

        # If the connector is not found, raise an exception
        if pm_connector_plugin is None:
            LOG.error(
                "PM Connector plugin '%s' is not installed",
                pm.connector,
            )
            raise Exception(f"PM Connector plugin '{pm.connector}' is not installed.")

        # Return the connector
        return pm_connector_plugin

    def get_installed_plugins(self):
        """Get the list of installed PM connectors.

        :return: The list of installed PM connectors
        :rtype: list[str]
        """
        return plugin_loader.get_pm_connectors_names()
