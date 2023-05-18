"""cloud_analytics manager module."""

import time

import cems2.cloud_analytics.collector.manager as collector_manager
import cems2.cloud_analytics.reporter.manager as reporter_manager
from cems2 import config_loader, log
from cems2.schemas.machine import Machine  # TODO: To test
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
        self.collector = collector_manager.Manager()
        self.reporter = reporter_manager.Manager()

        # List of machines to monitor
        self.machines_monitoring = []

        # Dictionary to store the last metrics of each machine
        # (key: hostname, value: list of metrics)
        self.metrics = {}

        # Monitoring interval
        self.monitoring_interval = CONFIG.getint("cloud_analytics", "interval")
        LOG.info("Monitoring interval set to %s", self.monitoring_interval)

    def set_machines(self, machines_list):
        """Update the machines to monitor.

        :param machines_list: list of machines to monitor
        :type machines_list: list[Machine]
        """

        print(self)
        self.machines_monitoring = machines_list.copy()
        LOG.info(
            "Machines to monitor: %s", [machine.hostname for machine in machines_list]
        )

    def run(self):
        """Run the cloud_analytics manager.

        - Get the metrics from the collector manager
        - Send the metrics to the reporter manager
        """

        # Run periodically as the monitoring interval
        while True:
            # Wait the monitoring interval
            LOG.debug("Waiting %s seconds", self.monitoring_interval)
            time.sleep(self.monitoring_interval)

            # For each machine to monitor
            for machine in self.machines_monitoring:
                # Get the metrics from the collector manager
                self.metrics[machine.hostname] = self.collector.get_metrics(
                    machine.hostname
                )
                # Send the metrics to the reporter manager
                self.reporter.send_metrics(self.metrics[machine.hostname])

    # Communication with de API monitoring controller
    def obtain_last_metrics(self):
        """Obtain the last metrics of each machine.

        :return: dictionary with the last metrics of each machine
        :rtype: dict{key: hostname, value: list[Metric]}
        """
        return self.metrics

    def get_plugins(self, plugin_type: str):
        """Obtain the installed plugins.

        :param plugin_type: type of plugin to obtain
        :type plugin_type: str

        :return: list of installed plugins
        :rtype: list[Plugin]
        """
        plugins = []
        if plugin_type == "collector":
            # Create a list of plugins with the name and type of each plugin
            plugins = [
                Plugin(name=plugin, type=plugin_type)
                for plugin in self.collector.get_installed_plugins()
            ]
        elif plugin_type == "reporter":
            # Create a list of plugins with the name and type of each plugin
            plugins = [
                Plugin(name=plugin, type=plugin_type)
                for plugin in self.reporter.get_installed_plugins()
            ]
        else:
            plugins = None

        return plugins
