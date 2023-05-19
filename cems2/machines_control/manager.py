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
        self.vm_optimization = None
        self.pm_optimization = None
        self.vm_connector = None
        self.pm_connector = None

    def _load_managers(self):
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

        # Load the managers
        self._load_managers()

        while True:
            print("Machines Control Manager running...")
            time.sleep(1)

    def get_plugins(self):
        """Obtain the installed plugins.

        :return: list of installed plugins
        :rtype: list[Plugin]
        """

        plugins = []

        # Get the pm_connector plugins
        plugins.extend(
            Plugin(name=plugin, type="pm_connector")
            for plugin in self.pm_connector.get_installed_plugins()
        )

        # Get the pm_optimization plugins
        plugins.extend(
            Plugin(name=plugin, type="pm_optimization")
            for plugin in self.pm_optimization.get_installed_plugins()
        )

        # Get the vm_connector plugins
        plugins.extend(
            Plugin(name=plugin, type="vm_connector")
            for plugin in self.vm_connector.get_installed_plugins()
        )

        # Get the vm_optimization plugins
        plugins.extend(
            Plugin(name=plugin, type="vm_optimization")
            for plugin in self.vm_optimization.get_installed_plugins()
        )

        return plugins
