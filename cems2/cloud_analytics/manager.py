"""cloud_analytics manager module."""

import copy
import time

import trio

import cems2.cloud_analytics.collector.manager as collector_manager
import cems2.cloud_analytics.reporter.manager as reporter_manager
from cems2 import config_loader, log
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
        self.collector = None
        self.reporter = None

        # List of machines to monitor
        self._machines_monitoring = []

        # Dictionary to store the last metrics of each machine
        # (key: hostname, value: list of metrics)
        self.metrics = {}

        # Monitoring interval
        self.monitoring_interval = None

    @property
    def machines_monitoring(self):
        return self._machines_monitoring

    @machines_monitoring.setter
    def machines_monitoring(self, machines_list):
        """Update the machines to monitor.

        :param machines_list: list of machines to monitor
        :type machines_list: list[Machine]
        """

        self._machines_monitoring = machines_list
        LOG.info(
            "Machines to monitor: %s",
            [machine.hostname for machine in self.machines_monitoring],
        )

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

        # Run periodically as the monitoring interval
        while True:
            if self.machines_monitoring:
                LOG.warning("Starting monitoring")
                # Run the monitoring async function
                trio.run(self._monitoring)
                # Wait the monitoring interval
                LOG.debug("Waiting %s seconds", self.monitoring_interval)
                time.sleep(self.monitoring_interval)

    async def _monitoring(self):
        # Create an async task for each machine
        async with trio.open_nursery() as nursery:
            for machine in self.machines_monitoring:
                nursery.start_soon(self._monitor_machine, machine)

    async def _monitor_machine(self, machine):
        metrics = await self.collector.get_metrics(machine.hostname)
        self.metrics[machine.hostname] = metrics
        await self.reporter.send_metrics(metrics)

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
        plugins.extend(
            Plugin(name=plugin, type="collector")
            for plugin in self.collector.get_installed_plugins()
        )

        # Get the reporter plugins
        plugins.extend(
            Plugin(name=plugin, type="reporter")
            for plugin in self.reporter.get_installed_plugins()
        )
        return plugins
