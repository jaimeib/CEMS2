"""cloud_analytics manager module."""

import time

import trio

import cems2.cloud_analytics.collector.manager as collector_manager
import cems2.cloud_analytics.reporter.manager as reporter_manager
from cems2 import config_loader, log
from cems2.API.routes.monitoring import monitoring_controller
from cems2.schemas.plugin import Plugin

# Get the logger
LOG = log.get_logger(__name__)

# Get the configuration
CONFIG = config_loader.get_config()


class Manager(object):
    """Cloud Analytics Manager class.

    This class is responsible for:
    - Obtaining the metrics from the collector manager
    - Forwarding the metrics to the reporter manager
    """

    def __init__(self):
        """Initialize the manager."""
        # API Controller
        self.api_controller = monitoring_controller

        # Submanagers
        self.collector = None
        self.reporter = None

        # List of machines to monitor
        self._machines_monitoring = []

        # Dictionary to store the last metrics of each machine
        # (key: hostname, value: list of metrics)
        self.metrics = {}

        # Monitoring interval
        self.monitoring_interval = None

        # On/off switch
        self._running = None

    @property
    def machines_monitoring(self):
        """Get the machines to monitor."""
        return self._machines_monitoring

    @machines_monitoring.setter
    def machines_monitoring(self, machines_list):
        """Update the machines to monitor.

        :param machines_list: list of machines to monitor
        :type machines_list: list[Machine]
        """
        self._machines_monitoring = machines_list
        LOG.info(
            "PMs to monitor: %s",
            [machine.hostname for machine in self.machines_monitoring],
        )

    @property
    def running(self):
        """Get the running status of the manager."""
        return self._running

    @running.setter
    def running(self, value: bool):
        """Update the running status of the manager.

        :param value: value to set (on/off)
        :type value: bool
        """
        self._running = value

        if value is True:
            LOG.warning("Cloud Analytics Manager started")
        else:
            LOG.warning("Cloud Analytics Manager stopped")

    def _load_managers(self):
        """Load the collector and reporter managers."""
        self.collector = collector_manager.Manager()
        self.reporter = reporter_manager.Manager()

    def _set_monitoring_interval(self):
        """Set the monitoring interval of the manager."""
        self.monitoring_interval = CONFIG.getint("cloud_analytics", "interval")
        LOG.info("Monitoring interval set to %s seconds", self.monitoring_interval)

    def run(self):
        """Run the cloud_analytics manager.
        - Load the collector and reporter managers
        - Set the monitoring interval
        - Run periodically as the monitoring interval
            - Get the metrics from the collector manager
            - Send the metrics to the reporter manager
        """
        # Load the managers
        self._load_managers()

        # Set the monitoring interval
        self._set_monitoring_interval()

        # Set the running status to True
        self.running = True

        # Run periodically as the monitoring interval
        while True:
            if self.machines_monitoring and self.running:
                # Run the monitoring async function
                trio.run(self._monitoring)

                # Notify the monitoring API controller of the new metrics obtained
                self.api_controller.notify_new_metrics(self.metrics)

                # Set the running status to False
                self.running = False

                # Wait for the monitoring interval
                trio.run(self._wait_moniring_interval)

            else:
                # Sleep until the manager is started again
                time.sleep(1)

    async def _monitoring(self):
        # Create an async task for each machine
        async with trio.open_nursery() as nursery:
            for machine in self.machines_monitoring:
                nursery.start_soon(self._monitor_machine, machine)

    async def _monitor_machine(self, machine):
        metrics = await self.collector.get_metrics(machine.hostname)
        self.metrics[machine.hostname] = metrics
        await self.reporter.send_metrics(metrics)

    async def _wait_moniring_interval(self):
        # With a timeout of the monitoring interval
        with trio.move_on_after(self.monitoring_interval) as cancel_scope:
            # Create an async coroutine to wait for the manager to be started again
            async with trio.open_nursery() as nursery:
                nursery.start_soon(self._wait_for_monitoring)

        # If the manager is not started again
        if cancel_scope.cancelled_caught:
            LOG.debug("Monitoring interval finished")
            # Set the running status to True to start the manager again
            self.running = True

    async def _wait_for_monitoring(self):
        LOG.debug(
            "Waiting for the monitoring interval (%s) to finish",
            self.monitoring_interval,
        )
        while not self.running:
            await trio.sleep(1)

    # Communication with de API monitoring controller
    def obtain_last_metrics(self):
        """Obtain the last metrics of each machine.

        :return: dictionary with the last metrics of each machine
        :rtype: dict{key: hostname, value: list[Metric]}
        """
        return self.metrics

    def get_plugins(self):
        """Obtain the installed plugins.

        :param plugin_type: type of plugin to obtain
        :type plugin_type: str

        :return: list of installed plugins
        :rtype: list[Plugin]
        """
        plugins = []

        # Get the collector plugins
        collectors = []
        collectors.extend(
            Plugin(name=plugin, type="collector", status="installed")
            for plugin in self.collector.get_installed_plugins()
        )

        # Add the Loaded status if there are in the config file
        for plugin in collectors:
            if plugin.name in CONFIG.getlist("cloud_analytics.plugins", "collectors"):
                plugin.status = "loaded"

        plugins.extend(collectors)

        # Get the reporter plugins
        reporters = []
        reporters.extend(
            Plugin(name=plugin, type="reporter", status="installed")
            for plugin in self.reporter.get_installed_plugins()
        )

        # Add the Loaded status if there are in the config file
        for plugin in reporters:
            if plugin.name in CONFIG.getlist("cloud_analytics.plugins", "reporters"):
                plugin.status = "loaded"

        plugins.extend(reporters)

        return plugins
