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

        # Submanagers
        self.vm_optimization = None
        self.pm_optimization = None
        self.vm_connector = None
        self.pm_connector = None

        # List of physical machines to control
        self._physical_machines = None

        # On/off switch
        self._running = None

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, value: bool):
        """Update the running status of the manager.

        :param value: new running status (on/off)
        :type value: bool
        """

        self._running = value
        if value is True:
            LOG.warning("Machines Control Manager started")
        else:
            LOG.warning("Machines Control Manager stopped")

    @property
    def physical_machines(self):
        return self._physical_machines

    @physical_machines.setter
    def physical_machines(self, machines_list: list):
        """Update the list of physical machines.

        :param machines_list: list of physical machines
        :type machines_list: list
        """

        self._physical_machines = machines_list
        LOG.info(
            "Physical machines to control: %s",
            [machine.hostname for machine in self.physical_machines],
        )

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

        # Set the running status to True
        self.running = True

        while True:
            if self.running:
                print("Machines Control Manager running...")
                time.sleep(1)
            else:
                # Boot all the physical machines
                self.boot_all()
                # Wait until the running status is set to True
                while not self.running:
                    time.sleep(1)

    def new_metrics(self, metrics: dict):
        """Get the last metrics from the monitoring controller.

        :param metrics: last metrics
        :type metrics: dict
        """

        print("Machines Control Manager: New metrics received")
        print(metrics)

    def boot_all(self):
        """Boot all the physical machines."""
        LOG.critical("Booting all the physical machines")

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
