"""VM Connector Manager module."""

from cems2 import config_loader, log
from cems2.machines_control import plugin_loader

# Get the logger
LOG = log.get_logger(__name__)

# Get the configuration
CONFIG = config_loader.get_config()


class Manager(object):
    """ "Manager for the VM Connectors."""

    def __init__(self):
        """Initialize the VM connector manager."""
        # Obtain the list of VM connectors configured in the config file
        vm_connectors_list = CONFIG.getlist("machines_control.plugins", "vm_connectors")

        # Check if the VM connectors are installed
        for vm_connector in vm_connectors_list:
            if vm_connector not in plugin_loader.get_vm_connectors_names():
                LOG.error(
                    "VM Connector plugin '%s' is not installed.",
                    vm_connector,
                )
                raise Exception(
                    f"VM Connector plugin '{vm_connector}' is not installed."
                )
        # Get the VM connectors from the plugin loader
        vm_connectors = [
            (i, plugin_loader.get_vm_connectors()[i]) for i in vm_connectors_list
        ]
        self.vm_connectors = vm_connectors
        LOG.debug("VM Connectors loaded: %s", vm_connectors_list)

    def get_installed_plugins(self):
        """Get the list of installed VM connectors.

        :return: The list of installed VM connectors
        :rtype: list[str]
        """
        return plugin_loader.get_vm_connectors_names()
