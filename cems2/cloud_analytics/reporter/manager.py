"""
Reporter Manager module
"""

from cems2.cloud_analytics import plugin_loader


class Manager(object):
    """
    Manager for the Cloud Analytics Reporters
    """

    def __init__(self):
        """
        Initialize the reporter manager
        """

        # Get all the reporters available
        reporters = plugin_loader.get_reporters()
        self.reporters = reporters

    def send_metrics(self, metric_list):
        """
        Send the metrics to the reporters
        """

        # For each reporter
