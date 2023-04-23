class Manager(object):
    """
    cloud_analytics manager class to orchestrate the collection of metrics from
    the cloud infrastructure and their forwarding to other systems
    """

    def __init__(self):
        """
        Initialize the manager
        """

    def load_managers(self):
        # Load the managers
        self.collector = cloud_analytics.collector.Manager()
        self.reporter = cloud_analytics.reporter.Manager()

    def run(self):
        """
        Run the cloud_analytics manager

        - Load the managers
        - Get the metrics from the collector manager
        - Send the metrics to the reporter manager
        """

        # Load the managers
        self.load_managers()

        # Get the metrics from the collector manager
        metrics = self.collector.get_metrics()

        # Send the metrics to the reporter manager
        self.reporter.send_metrics(metrics)

        # Comunicate with the API to send the metrics if required

        # TODO: Communication with the API??
