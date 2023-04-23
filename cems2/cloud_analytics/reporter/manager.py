class Manager(object):
    """
    Manager for the Cloud Analytics Reporters
    """

    def __init__(self):
        """
        Initialize the reporter manager
        """

        # Get all the reporters available
        reporters = cloud_analytics.reporter.get_reporters()
        self.reporters = reporters

    def report(self, metric_list):
        """
        Report the metrics to the reporters
        """

        # Report the metrics to the reporters
