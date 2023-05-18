"""Virtual Machines Optimization Manager module."""

from cems2 import config_loader, log
from cems2.machines_control import plugin_loader

# Get the logger
LOG = log.get_logger(__name__)

# Get the configuration
CONFIG = config_loader.get_config()


class Manager(object):
    """Manager for the Virtual Machines Optimizations."""

    def __init__(self):
        """Initialize the Virtual Machines optimization manager."""
        # Obtain the list of Virtual Machines optimizations configured in the config file
        vm_optimizations_list = CONFIG.getlist(
            "machines_control.plugins", "vm_optimization"
        )

        # Check if the Virtual Machines optimizations are installed
        for vm_optimization in vm_optimizations_list:
            if vm_optimization not in plugin_loader.get_vm_optimizations_names():
                LOG.error(
                    "Virtual Machines Optimization plugin '%s' is not installed.",
                    vm_optimization,
                )
                raise Exception(
                    f"Virtual Machines Optimization plugin '{vm_optimization}' is not installed."
                )
        # Get the Virtual Machines optimizations from the plugin loader
        vm_optimizations = [
            (i, plugin_loader.get_vm_optimizations()[i]) for i in vm_optimizations_list
        ]
        self.vm_optimizations = vm_optimizations
        LOG.debug("Virtual Machines Optimizations loaded: %s", vm_optimizations_list)

    def get_installed_plugins(self):
        """Get the list of installed Virtual Machines optimizations.

        :return: The list of installed Virtual Machines optimizations
        :rtype: list[str]
        """
        return plugin_loader.get_vm_optimizations_names()
