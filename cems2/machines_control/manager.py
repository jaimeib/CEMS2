"""machines_control manager module."""

import time

import cems2.machines_control.pm_connector.manager as pm_connector_manager
import cems2.machines_control.pm_optimization.manager as pm_optimization_manager
import cems2.machines_control.vm_connector.manager as vm_connector_manager
import cems2.machines_control.vm_optimization.manager as vm_optimization_manager
from cems2 import config_loader, log
from cems2.schemas.plugin import Plugin

# Get the logger
LOG = log.get_logger(__name__)

# Get the configuration
CONFIG = config_loader.get_config()


class Manager(object):
    """Machines Control Manager class.

    This class is responsible for:
    - Obtaining the Virtual Machines optimizations from the vm_optimization manager
    - Obtaining the Physical Machines optimizations from the pm_optimization manager
    - Applying the optimizations with the vm_connector to the VMs
    - Applying the optimizations with the pm_connector to the PMs
    """

    def __init__(self):
        """Initialize the manager."""
        self.vm_optimization = vm_optimization_manager.Manager()
        self.pm_optimization = pm_optimization_manager.Manager()
        self.vm_connector = vm_connector_manager.Manager()
        self.pm_connector = pm_connector_manager.Manager()

    def run(self):
        """Run the machines_control manager.

        - Load the managers
        - Get the Virtual Machines optimizations
        - Apply the Virtual Machines optimizations
        - Get the Physical Machines optimizations
        - Apply the Physical Machines optimizations
        """

        while True:
            print("Machines Control Manager running...")
            time.sleep(1)

    def get_plugins(self, plugin_type: str):
        """Obtain the installed plugins.

        :param plugin_type: type of plugin to obtain
        :type plugin_type: str

        :return: list of installed plugins
        :rtype: list[Plugin]
        """

        plugins = []
        if plugin_type == "vm_optimization":
            # Create a list of plugins with the name and type of each plugin
            plugins = [
                Plugin(name=plugin, type=plugin_type)
                for plugin in self.vm_optimization.get_installed_plugins()
            ]
        elif plugin_type == "pm_optimization":
            plugins = [
                Plugin(name=plugin, type=plugin_type)
                for plugin in self.pm_optimization.get_installed_plugins()
            ]
        elif plugin_type == "vm_connector":
            plugins = [
                Plugin(name=plugin, type=plugin_type)
                for plugin in self.vm_connector.get_installed_plugins()
            ]
        elif plugin_type == "pm_connector":
            plugins = [
                Plugin(name=plugin, type=plugin_type)
                for plugin in self.pm_connector.get_installed_plugins()
            ]
        else:
            plugins = None

        return plugins
