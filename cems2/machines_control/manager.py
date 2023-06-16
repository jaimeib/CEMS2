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
    - Obtaining the VM optimizations from the vm_optimization manager
    - Applying the optimizations with the vm_connector to the VMs
    - Obtaining the PM optimizations from the pm_optimization manager
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

        # List of PMs to control
        self._pm_monitoring = None

        # Baseline
        self.baseline = None

        # On/off switch
        self._running = None

        # New metrics event trigger
        self.new_metrics_event = False

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
        """Get the list of PMs to control."""
        return self._pm_monitoring

    @pm_monitoring.setter
    def pm_monitoring(self, machines_list: list):
        """Update the list of PMs.

        :param machines_list: list of PMs
        :type machines_list: list
        """
        self._pm_monitoring = machines_list
        LOG.info(
            "PMs to control: %s",
            [machine.hostname for machine in self.pm_monitoring],
        )

        if self.pm_monitoring:
            self._set_baseline()
            self.running = True

    def _load_managers(self):
        """Load the submanagers."""
        self.vm_optimization = vm_optimization_manager.Manager()
        self.pm_optimization = pm_optimization_manager.Manager()
        self.vm_connector = vm_connector_manager.Manager()
        self.pm_connector = pm_connector_manager.Manager()

        # Set this manager on the necesary submanagers
        self.pm_connector.machines_control_manager = self

    def _set_baseline(self):
        """Set the baseline for the PMs.

        The baseline is the minimum number of PMs
        that must be on to supply the future demand.
        """
        # Get the configured baseline in % from the configuration file
        percent_baseline = float(CONFIG["machines_control"]["baseline"])

        # Calculate the baseline in number of PMs
        # (round up to the nearest integer)
        numeric_baseline = round(len(self.pm_monitoring) * percent_baseline / 100)

        # Set the baseline
        self.baseline = numeric_baseline

        # Log the baseline
        LOG.info("Baseline set to %s machines", self.baseline)

        # Notify the pm_optimization manager of the new baseline
        self.pm_optimization.new_baseline(self.baseline)

    def run(self):
        """Run the machines_control manager.

        - Load the managers
        - Get the VM optimizations
        - Apply the VM optimizations
        - Get the PM optimizations
        - Apply the PM optimizations
        """

        # Load the managers
        self._load_managers()

        # Set the current state of the PMs
        trio.run(self._get_pms_energy_status)

        # Get the machines to control from the API controller
        self.pm_monitoring = self.api_controller.machines_monitoring()

        # Run the manager asynchronously (2 subtasks + 2 plugins)
        trio.run(self._run_async)

    async def _run_async(self):
        """Run the machines_control manager asynchronously"""
        # Create 2 tasks to run in parallel: Running control and Control tasks
        async with trio.open_nursery() as nursery:
            # Start the running control task
            nursery.start_soon(self._running_control_task)
            # Start the defaul_vm_optimization
            nursery.start_soon(self.vm_optimization.default_vm_optimization.run, True)
            # Start the defaul_pm_optimization
            nursery.start_soon(self.pm_optimization.default_pm_optimization.run, True)
            # Start the control tasks
            nursery.start_soon(self._control_tasks)

    async def _running_control_task(self):
        """Control the running status of the manager."""
        # Run the task indefinitely
        while True:
            # If the running status is set to False
            if not self.running:
                # Boot all the PMs
                await self._boot_all()
                LOG.debug("Manager control tasks canceled")

                # Wait until the running status is set to True
                while not self.running:
                    await trio.sleep(1)
            else:
                # Wait 1 second
                await trio.sleep(1)

    async def _control_tasks(self):
        """Run the control tasks.

        - Wait for new metrics event trigger
        - Get the VM optimizations
        - Apply the VM optimizations
        - Notify the API controller to monitor the system again
        - Wait for new metrics event trigger
        - Get the PM optimizations
        - Apply the PM optimizations
        - Notify the API controller to monitor the system again
        """
        while True:
            # Wait for new metrics event trigger
            while not self.new_metrics_event:
                await trio.sleep(1)

            # Get the VM current distribution
            current_dist = await self.vm_optimization.get_current_distribution()

            # Get the VM default optimization
            vm_optimization = await self.vm_optimization.get_default_optimization()

            # Apply the VM default optimization
            await self.vm_connector.apply_optimization(current_dist, vm_optimization)

            # Notify the API controller to monitor the system again
            self.api_controller.monitor_again()

            # Set the new metrics event trigger to False
            self.new_metrics_event = False

            # Wait for new metrics event trigger
            while not self.new_metrics_event:
                await trio.sleep(1)

            # Get the PM optimizations
            pm_optimization = await self.pm_optimization.get_default_optimization()

            # Convert the PM optimization from hostnames to Machine objects
            pm_optimization = self._convert_pm_optimization(pm_optimization)

            # Apply the PM optimizations
            await self.pm_connector.apply_optimization(pm_optimization)

            # Notify the API controller to monitor the system again
            self.api_controller.monitor_again()

            # Set the new metrics event trigger to False
            self.new_metrics_event = False

    def _convert_pm_optimization(self, pm_optimization: dict):
        """Convert the PM optimization from hostnames to Machine objects.

        :param pm_optimization: PM optimization
        :type pm_optimization: dict

        :return: PM optimization with Machine objects
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
        if not self.running:
            return

        if metrics is None:
            return

        # Update the metrics on the optimization managers
        self.vm_optimization.new_metrics(metrics)
        self.pm_optimization.new_metrics(metrics)

        # Activate the event trigger to start the optimization sprint
        self.new_metrics_event = True

        LOG.critical("New metrics event activated - Resuming control tasks")

    def new_baseline(self):
        """Update the baseline on the pm optimization plugins."""
        self.pm_optimization.new_baseline(baseline)

    async def _boot_all(self):
        """Boot all the PMs."""
        LOG.critical("Booting all the PMs")

        # Get the list of PMs available from the API controller
        available_pms = self.api_controller.machines_available()

        for machine in available_pms:
            # Create an async task for each machine and set a timeout
            with trio.move_on_after(self.pm_connector.timeout) as cancel_scope:
                async with trio.open_nursery() as nursery:
                    # Create an async task an obtain the return value
                    nursery.start_soon(self._boot_machine, machine)

            if cancel_scope.cancelled_caught:
                LOG.error(
                    "PM Connector plugin '%s' timed out for machine: %s",
                    self.pm_connector.name,
                    machine.hostname,
                )

        # Notify the API controller of the current state of the PMs
        self.api_controller.notify_machine_status(available_pms)

    async def _boot_machine(self, machine: Machine):
        """Boot a PM.

        :param machine: PM
        :type machine: Machine
        """
        LOG.critical("Booting the PM: %s", machine.hostname)
        # Boot the machine with the pm_connector
        await self.pm_connector.turn_on(machine)

    async def _get_pms_energy_status(self):
        """Get the energy status of the PMs."""
        LOG.debug("Setting the current state of the PMs available")

        # Get the list of PMs available from the API controller
        available_pms = self.api_controller.machines_available()

        for machine in available_pms:
            # Create an async task for each machine and set a timeout
            with trio.move_on_after(self.pm_connector.timeout) as cancel_scope:
                async with trio.open_nursery() as nursery:
                    # Create an async task an obtain the return value
                    nursery.start_soon(self._get_current_state, machine)

            if cancel_scope.cancelled_caught:
                LOG.error(
                    "PM Connector plugin '%s' timed out for machine: %s",
                    self.pm_connector.name,
                    machine.hostname,
                )

        # Notify the API controller of the current state of the PMs
        self.api_controller.notify_machine_status(available_pms)

    async def _get_current_state(self, machine: Machine):
        """Get the current state of the PM.

        :param machine: PM
        :type machine: Machine

        :return: current state of the PM (on/off)
        :rtype: bool
        """
        LOG.debug("Getting the current state of the PM: %s", machine.hostname)
        # Get the state from the pm_connector
        machine.energy_status = await self.pm_connector.get_pm_state(machine)

    def notify_machine_status(self, machine: Machine):
        """Notify the API controller of the current state of a PM.

        :param machine: PM
        :type machines: Machine
        """
        self.api_controller.notify_machine_status([machine])

    def get_plugins(self):
        """Obtain the installed plugins.

        :return: list of installed plugins
        :rtype: list[Plugin]
        """
        plugins = []

        # Get the pm_connector plugins
        pm_connectors = []
        pm_connectors.extend(
            Plugin(name=plugin, type="pm_connector", status="installed")
            for plugin in self.pm_connector.get_installed_plugins()
        )

        # Add the Loaded status if there are in the config file
        for plugin in pm_connectors:
            if plugin.name in CONFIG["machines_control.plugins"]["pm_connectors"]:
                plugin.status = "loaded"

        plugins.extend(pm_connectors)

        # Get the pm_optimization plugins
        pm_optimizations = []
        pm_optimizations.extend(
            Plugin(name=plugin, type="pm_optimization", status="loaded")
            for plugin in self.pm_optimization.get_installed_plugins()
        )

        # Add the Default status if there is in the config file
        for plugin in pm_optimizations:
            if (
                plugin.name
                == CONFIG["machines_control.plugins"]["default_pm_optimization"]
            ):
                plugin.status = "default"

        plugins.extend(pm_optimizations)

        # Get the vm_connector plugins
        vm_connectors = []
        vm_connectors.extend(
            Plugin(name=plugin, type="vm_connector", status="installed")
            for plugin in self.vm_connector.get_installed_plugins()
        )

        # Add the Loaded status if there are in the config file
        for plugin in vm_connectors:
            if plugin.name in CONFIG["machines_control.plugins"]["vm_connectors"]:
                plugin.status = "loaded"

        plugins.extend(vm_connectors)

        # Get the vm_optimization plugins
        vm_optimizations = []
        vm_optimizations.extend(
            Plugin(name=plugin, type="vm_optimization", status="loaded")
            for plugin in self.vm_optimization.get_installed_plugins()
        )

        # Add the Default status if there is in the config file
        for plugin in vm_optimizations:
            if (
                plugin.name
                == CONFIG["machines_control.plugins"]["default_vm_optimization"]
            ):
                plugin.status = "default"

        plugins.extend(vm_optimizations)

        return plugins

    def get_vm_optimizations(self, name: str = None):
        """Obtain the VM optimizations.

        :param name: name of the VM optimization
        :type name: str

        :return: list of VM optimizations
        :rtype:  dict[str, dict]
        """
        # Launch the VM optimizations and get the results
        optimizations = trio.run(self.vm_optimization.get_vm_optimizations, name)
        return optimizations

    def get_pm_optimizations(self, name: str = None):
        """Obtain the PM optimizations.

        :param name: name of the PM optimization
        :type name: str

        :return: list of PM optimizations
        :rtype: dict[str, dict]
        """
        # Launch the PM optimizations and get the results
        optimizations = trio.run(self.pm_optimization.get_pm_optimizations, name)
        return optimizations
