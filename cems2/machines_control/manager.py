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

        if self.pm_monitoring:
            self._set_baseline()
            self.running = True

    def _load_managers(self):
        self.vm_optimization = vm_optimization_manager.Manager()
        self.pm_optimization = pm_optimization_manager.Manager()
        self.vm_connector = vm_connector_manager.Manager()
        self.pm_connector = pm_connector_manager.Manager()

        # Set this manager on the necesary submanagers
        self.pm_optimization.machines_control_manager = self

    def _set_baseline(self):
        """Set the baseline for the physical machines.

        The baseline is the minimum number of physical machines
        that must be on to supply the future demand.
        """
        # Get the configured baseline in % from the configuration file
        percent_baseline = float(CONFIG["machines_control"]["baseline"])

        # Calculate the baseline in number of physical machines
        # (round up to the nearest integer)
        numeric_baseline = round(len(self.pm_monitoring) * percent_baseline / 100)

        # Set the baseline
        self.baseline = numeric_baseline

        # Log the baseline
        LOG.info("Baseline set to %s machines", self.baseline)

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
        trio.run(self._get_pms_energy_status)

        # Get the machines to control from the API controller
        self.pm_monitoring = self.api_controller.machines_monitoring()

        # Run the manager asynchronously
        trio.run(self._run_async)

    async def _run_async(self):
        """Run the machines_control manager asynchronously"""
        # Create 2 tasks to run in parallel: Running control and Control tasks
        async with trio.open_nursery() as nursery:
            # Start the running control task
            nursery.start_soon(self._running_control_task)
            # Start the control tasks
            nursery.start_soon(self._control_tasks)

    async def _running_control_task(self):
        """Control the running status of the manager."""
        # Run the task indefinitely
        while True:
            # If the running status is set to False
            if not self.running:
                # Boot all the physical machines
                trio.run(self._boot_all)
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
        - Get the Virtual Machines optimizations
        - Apply the Virtual Machines optimizations
        - Notify the API controller to monitor the system again
        - Wait for new metrics event trigger
        - Get the Physical Machines optimizations
        - Apply the Physical Machines optimizations
        - Notify the API controller to monitor the system again
        """
        while True:
            # # Wait for new metrics event trigger
            # while not self.new_metrics_event:
            #     await trio.sleep(1)

            # # Get the Virtual Machines default optimization
            # vm_optimization = await self.vm_optimization.get_optimization()

            # # Apply the Virtual Machines default optimization
            # await self.vm_connector.apply_optimization(vm_optimization)

            # # Notify the API controller to monitor the system again
            # self.api_controller.monitor_again()

            # # Set the new metrics event trigger to False
            # self.new_metrics_event = False

            # Wait for new metrics event trigger
            while not self.new_metrics_event:
                await trio.sleep(1)

            # Get the Physical Machines optimizations
            pm_optimization = await self.pm_optimization.get_default_optimization()

            # Convert the Physical Machines optimization from hostnames to Machine objects
            pm_optimization = self._convert_pm_optimization(pm_optimization)

            # Apply the Physical Machines optimizations
            await self.pm_connector.apply_optimization(pm_optimization)

            # Notify the API controller to monitor the system again
            self.api_controller.monitor_again()

            # Set the new metrics event trigger to False
            self.new_metrics_event = False

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
        if not self.running:
            return

        # Update the metrics on the optimization managers
        self.vm_optimization.new_metrics(metrics)
        self.pm_optimization.new_metrics(metrics)

        # What to do if the optimization is already running?
        if self.new_metrics_event is True:
            # FIXME: Cancel the current optimization
            pass

        # Activate the event trigger to start the optimization sprint
        self.new_metrics_event = True

        LOG.critical("New metrics event activated - Resuming control tasks")

    async def _boot_all(self):
        """Boot all the physical machines."""
        LOG.critical("Booting all the physical machines")

        # Get the list of physical machines available from the API controller
        available_pms = self.api_controller.machines_available()

        for machine in available_pms:
            # Create an async task for each machine and set a timeout
            with trio.move_on_after(self.pm_connector.timeout) as cancel_scope:
                async with trio.open_nursery() as nursery:
                    # Create an async task an obtain the return value
                    nursery.start_soon(self._boot_machine, machine)

            if cancel_scope.cancelled_caught:
                LOG.error(
                    "Physical Machines Connector plugin '%s' timed out for machine: %s",
                    self.pm_connector.name,
                    machine.hostname,
                )

        # Notify the API controller of the current state of the physical machines
        self.api_controller.notify_machine_status(available_pms)

    async def _boot_machine(self, machine: Machine):
        """Boot a physical machine.

        :param machine: physical machine
        :type machine: Machine
        """
        LOG.critical("Booting the physical machine: %s", machine.hostname)
        # Boot the machine with the pm_connector
        await self.pm_connector.turn_on(machine)

    async def _get_pms_energy_status(self):
        """Get the energy status of the physical machines."""
        LOG.debug("Setting the current state of the physical machines available")

        # Get the list of physical machines available from the API controller
        available_pms = self.api_controller.machines_available()

        for machine in available_pms:
            # Create an async task for each machine and set a timeout
            with trio.move_on_after(self.pm_connector.timeout) as cancel_scope:
                async with trio.open_nursery() as nursery:
                    # Create an async task an obtain the return value
                    nursery.start_soon(self._get_current_state, machine)

            if cancel_scope.cancelled_caught:
                LOG.error(
                    "Physical Machines Connector plugin '%s' timed out for machine: %s",
                    self.pm_connector.name,
                    machine.hostname,
                )

        # Notify the API controller of the current state of the physical machines
        self.api_controller.notify_machine_status(available_pms)

    async def _get_current_state(self, machine: Machine):
        """Get the current state of the physical machine.

        :param machine: physical machine
        :type machine: Machine

        :return: current state of the physical machine (on/off)
        :rtype: bool
        """
        LOG.debug(
            "Getting the current state of the physical machine: %s", machine.hostname
        )
        # Get the state from the pm_connector
        machine.energy_status = await self.pm_connector.get_pm_state(machine)

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
