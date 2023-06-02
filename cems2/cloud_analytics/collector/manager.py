"""Collector Manager module."""

import trio

from cems2 import config_loader, log
from cems2.cloud_analytics import plugin_loader

# Get the logger
LOG = log.get_logger(__name__)

# Get the configuration
CONFIG = config_loader.get_config()


class Manager(object):
    """Manager for the Cloud Analytics Collectors."""

    def __init__(self):
        """Initialize the collector manager."""
        # Obtain the list of collectors configured in the config file
        collectors_list = CONFIG.getlist("cloud_analytics.plugins", "collectors")

        # Check if the collectors are installed
        for collector in collectors_list:
            if collector not in plugin_loader.get_collectors_names():
                LOG.error(
                    "Collector plugin '%s' is not installed.",
                    collector,
                )
                raise Exception(f"Collector plugin '{collector}' is not installed.")

        # Get the collectors from the plugin loader
        collectors = [(i, plugin_loader.get_collectors()[i]) for i in collectors_list]
        self.collectors = collectors
        LOG.debug("Collectors loaded: %s", collectors_list)

        # Set the collector plugin timeout
        self.timeout = CONFIG.getint("cloud_analytics", "collector_timeout")

    async def get_metrics(self, machine_id):
        """Get the metric list from the collectors for the instance.

        :param machine_id: The ID of the machine
        :type machine_id: str

        :return: The metric list
        :rtype: list[Metric]
        """
        metric_list = []

        for collector_name, collector_cls in self.collectors:
            # Create an async task for each collector and set a timeout
            with trio.move_on_after(self.timeout) as cancel_scope:
                async with trio.open_nursery() as nursery:
                    nursery.start_soon(
                        self._obtain_metrics, collector_cls, machine_id, metric_list
                    )

            if cancel_scope.cancelled_caught:
                LOG.error(
                    "Timeout reached for the collector '%s' from the machine %s",
                    collector_name,
                    machine_id,
                )

        return metric_list

    async def _obtain_metrics(self, collector, machine_id, metric_list):
        LOG.info(
            "Collecting metrics from '%s', from the machine %s",
            collector.__name__,
            machine_id,
        )
        metric = await collector().collect_metric(machine_id)
        metric_list.append(metric)

    def get_installed_plugins(self):
        """Get the list of installed collectors.

        :return: The list of installed collectors
        :rtype: list[str]
        """
        return plugin_loader.get_collectors_names()
