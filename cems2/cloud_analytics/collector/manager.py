from cloud_analytics import plugin_loader


class Manager(object):
    """
    Manager for the Cloud Analytics Collectors
    """

    def __init__(self):
        """
        Initialize the collector manager
        """

        # Get all the collectors available
        collectors = cloud_analytics.collector.get_collectors()
        self.collectors = collectors

    def get_metrics(self):
        """
        Get the metrics from the collectors
        """

        # Get the metrics from the collectors
        metric_list = []

        return metric_list
