"""Collector Manager module."""

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
        collectors_list = CONFIG.getlist("cloud_analytics.plugins", "collector")

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

    def get_metrics(self, machine_id):
        """Get the metric list from the collectors for the instance.

        :param machine_id: The ID of the machine
        :type machine_id: str

        :return: The metric list
        :rtype: list[Metric]
        """
        metric_list = []

        # For each collector
        for collector_name, collector_cls in self.collectors:
            # Get the metrics
            metrics = collector_cls().collect_metric(machine_id)

            # Add the metrics to the list
            metric_list.extend(metrics)

        return metric_list
