"""machines_control manager module."""

import time

import trio

import cems2.machines_control.pm_connector.manager as pm_connector_manager
import cems2.machines_control.pm_optimization.manager as pm_optimization_manager
import cems2.machines_control.vm_connector.manager as vm_connector_manager
import cems2.machines_control.vm_optimization.manager as vm_optimization_manager
from cems2 import config_loader, log
from cems2.API.routes.actions import actions_controller
from cems2.schemas.machine import Machine
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

        # API controller
        self.api_controller = actions_controller

        # Submanagers
        self.vm_optimization = None
        self.pm_optimization = None
        self.vm_connector = None
        self.pm_connector = None

        # List of physical machines to control
        self._pm_monitoring = None

        # On/off switch
        self._running = None

        # Async tasks
        self._vm_running_task = None
        self._pm_running_task = None

        # New metrics event triggers
        # self.new_metrics_event_vm = trio.Event()
        self.new_metrics_event_pm = False  # FIXME: Using a trio.Event() here

    @property
    def running(self):
        """Get the running status of the manager."""
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
    def pm_monitoring(self):
        """Get the list of physical machines to control."""
        return self._pm_monitoring

    @pm_monitoring.setter
    def pm_monitoring(self, machines_list: list):
        """Update the list of physical machines.

        :param machines_list: list of physical machines
        :type machines_list: list
        """

        self._pm_monitoring = machines_list
        LOG.info(
            "Physical machines to control: %s",
            [machine.hostname for machine in self.pm_monitoring],
        )

    def _load_managers(self):
        self.vm_optimization = vm_optimization_manager.Manager()
        self.pm_optimization = pm_optimization_manager.Manager()
        self.vm_connector = vm_connector_manager.Manager()
        self.pm_connector = pm_connector_manager.Manager()

    def _set_baseline(self):
        """Set the baseline for the physical machines.

        The baseline is the minimum number of physical machines
        that must be on to supply the future demand.
        """
        LOG.debug("Setting the baseline for the physical machines")

        # Get the configured baseline in % from the configuration file
        percent_baseline = int(CONFIG["machines_control"]["baseline"])

        # Calculate the baseline in number of physical machines
        # (round up to the nearest integer)
        numeric_baseline = round(len(self.pm_monitoring) * percent_baseline / 100)

        # Set the baseline to the pm_optimization manager
        self.pm_optimization.pm_baseline = numeric_baseline

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

        # Set the current state of the physical machines
        self._get_pms_energy_status()

        # Set the baseline for the physical machines
        self._set_baseline()

        # Set the running status to True
        self.running = True

        # Run the tasks concurrently
        trio.run(self.control_tasks)

        while True:
            if not self.running:
                # Boot all the physical machines
                self._boot_all()
                # Cancel the async tasks
                # self._vm_control_task.cancel()
                self._pm_running_task.cancel()
                LOG.debug("Manager control tasks canceled")

                # Wait until the running status is set to True
                while not self.running:
                    time.sleep(1)

    async def control_tasks(self):
        async with trio.open_nursery() as nursery:
            # nursery.start_soon(self._vm_control_task
            nursery.start_soon(self._pm_control_task)

    async def _vm_control_task(self):
        """Control the Virtual Machines concurrently.

        - Get the Virtual Machines optimization
        - Apply the Virtual Machines optimization
        """
        # Run the task indefinitely
        while True:
            # Await the event to be true
            await self.new_metrics_event_vm.wait()

            # Get the best Virtual Machines optimization
            vm_optimization = self.vm_optimization.get_best_optimization()

            # Apply the best Virtual Machines optimization
            self.vm_connector.apply_optimization(vm_optimization)

            # Notify the API controller to analyze the current state of the physical machines
            self.api_controller.notify_new_vm_optimization()

            # Reset the event
            self.new_metrics_event_vm.clear()

    async def _pm_control_task(self):
        """Control the Physical Machines concurrently.

        - Get the Physical Machines optimization
        - Apply the Physical Machines optimization
        """
        # Run the task indefinitely
        while True:
            # Wait until the event is true FIXME: Using a trio.Event() here
            while not self.new_metrics_event_pm:
                await trio.sleep(1)

            # Get the best Physical Machines optimization
            pm_optimization_hostnames = self.pm_optimization.get_best_optimization()

            # Convert the dict of hostnames to a dict of Machine objects
            pm_optimization_machines = self._convert_pm_optimization(
                pm_optimization_hostnames
            )

            # Apply the best Physical Machines optimization
            self.pm_connector.apply_optimization(pm_optimization_machines)

            # Update the current state of the physical machines on the API controller
            self._get_pms_energy_status()

            # Reset the event
            self.new_metrics_event_pm = False

    def _convert_pm_optimization(self, pm_optimization: dict):
        """Convert the Physical Machines optimization from hostnames to Machine objects.

        :param pm_optimization: Physical Machines optimization
        :type pm_optimization: dict

        :return: Physical Machines optimization with Machine objects
        :rtype: dict
        """
        pm_optimization_machines = {"on": [], "off": []}

        for hostname in pm_optimization["on"]:
            for machine in self.pm_monitoring:
                if machine.hostname == hostname:
                    pm_optimization_machines["on"].append(machine)
                    break

        for hostname in pm_optimization["off"]:
            for machine in self.pm_monitoring:
                if machine.hostname == hostname:
                    pm_optimization_machines["off"].append(machine)
                    break

        return pm_optimization_machines

    def new_metrics(self, metrics: dict):
        """Get the last metrics from the monitoring controller.

        :param metrics: last metrics
        :type metrics: dict
        """
        LOG.debug("New metrics received on the Machines Control Manager")

        # Update the metrics on the optimization managers
        # self.vm_optimization.metrics = metrics
        self.pm_optimization.pm_metrics = metrics

        # Activate the events to start the optimization process
        # self.new_metrics_event_vm.set()
        self.new_metrics_event_pm = True  # FIXME: Using a trio.Event() here

        LOG.critical("New metrics event activated")

    def _boot_all(self):
        """Boot all the physical machines."""
        LOG.critical("Booting all the physical machines")

        # Get the list of physical machines available from the API controller
        available_pms = self.api_controller.machines_available()

        for machine in available_pms:
            self.pm_connector.turn_on(machine)

        # Notify the API controller of the current state of the physical machines
        self.api_controller.notify_machine_status(available_pms)

    def _get_pms_energy_status(self):
        """Get the energy status of the physical machines."""
        LOG.debug("Setting the current state of the physical machines available")

        # Get the list of physical machines available from the API controller
        available_pms = self.api_controller.machines_available()

        for machine in available_pms:
            machine.energy_status = self._get_current_state(machine)

        # Notify the API controller of the current state of the physical machines
        self.api_controller.notify_machine_status(available_pms)

    def _get_current_state(self, machine: Machine):
        """Get the current state of the physical machine.

        :param machine: physical machine
        :type machine: Machine

        :return: current state of the physical machine (on/off)
        :rtype: bool
        """
        # Get the state from the pm_connector
        return self.pm_connector.get_pm_state(machine)

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
