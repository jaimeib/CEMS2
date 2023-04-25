"""
Collector Manager module
"""

from cems2.cloud_analytics import plugin_loader


class Manager(object):
    """
    Manager for the Cloud Analytics Collectors
    """

    def __init__(self):
        """
        Initialize the collector manager
        """

        # Get all the collectors available
        collectors = plugin_loader.get_collectors()
        self.collectors = collectors

    def get_metrics(self, machine_id):
        """
        Get the metrics from the collectors
        """

        metric_list = []

        # For each collector
        for collector in self.collectors:
            # Get the metrics from the collector
            metric_list.append(collector.collect_metric(machine_id))
