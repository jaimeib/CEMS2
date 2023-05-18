"""Virtual Machines Connector Manager module."""

from cems2 import config_loader, log
from cems2.machines_control import plugin_loader

# Get the logger
LOG = log.get_logger(__name__)

# Get the configuration
CONFIG = config_loader.get_config()


class Manager(object):
    """ "Manager for the Virtual Machines Connectors."""

    def __init__(self):
        """Initialize the Virtual Machines connector manager."""
        # Obtain the list of Virtual Machines connectors configured in the config file
        vm_connectors_list = CONFIG.getlist("machines_control.plugins", "vm_connector")

        # Check if the Virtual Machines connectors are installed
        for vm_connector in vm_connectors_list:
            if vm_connector not in plugin_loader.get_vm_connectors_names():
                LOG.error(
                    "Virtual Machines Connector plugin '%s' is not installed.",
                    vm_connector,
                )
                raise Exception(
                    f"Virtual Machines Connector plugin '{vm_connector}' is not installed."
                )
        # Get the Virtual Machines connectors from the plugin loader
        vm_connectors = [
            (i, plugin_loader.get_vm_connectors()[i]) for i in vm_connectors_list
        ]
        self.vm_connectors = vm_connectors
        LOG.debug("Virtual Machines Connectors loaded: %s", vm_connectors_list)

    def get_installed_plugins(self):
        """Get the list of installed Virtual Machines connectors.

        :return: The list of installed Virtual Machines connectors
        :rtype: list[str]
        """
        return plugin_loader.get_vm_connectors_names()
