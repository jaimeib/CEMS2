"""Physical Machines Connector Manager module."""

from cems2 import config_loader, log
from cems2.machines_control import plugin_loader
from cems2.schemas.machine import Machine

# Get the logger
LOG = log.get_logger(__name__)

# Get the configuration
CONFIG = config_loader.get_config()


class Manager(object):
    """Manager for the Physical Machines Connectors."""

    def __init__(self):
        """Initialize the Physical Machines connector manager."""
        # Obtain the list of Physical Machines connectors configured in the config file
        pm_connectors_list = CONFIG.getlist("machines_control.plugins", "pm_connector")

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

    def get_pm_state(self, pm: Machine):
        """Get the state of a Physical Machine.

        :param pm: Physical Machine to get the state of
        :type pm: Machine
        :return: The state of the Physical Machine
        :rtype: str
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

        # Get the power state of the machine
        LOG.debug("Getting power state of %s", pm.hostname)
        status = pm_connector_plugin().get_power_state(
            pm.management_ip,
            pm.management_username,
            pm.management_password,
            pm.brand_model,
        )

        # Return the state
        return status

    def get_installed_plugins(self):
        """Get the list of installed Physical Machines connectors.

        :return: The list of installed Physical Machines connectors
        :rtype: list[str]
        """
        return plugin_loader.get_pm_connectors_names()
