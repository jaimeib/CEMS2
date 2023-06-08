"""Reporter Manager module."""

import trio

from cems2 import config_loader, log
from cems2.cloud_analytics import plugin_loader

# Get the logger
LOG = log.get_logger(__name__)

# Get the configurtion
CONFIG = config_loader.get_config()


class Manager(object):
    """Manager for the Cloud Analytics Reporters."""

    def __init__(self):
        """Initialize the reporter manager."""
        # Obtain the list of reporters configured in the config file
        reporters_list = CONFIG.getlist("cloud_analytics.plugins", "reporters")

        # Check if the reporters are installed
        for reporter in reporters_list:
            if reporter not in plugin_loader.get_reporters_names():
                LOG.error(
                    "Reporter plugin '%s' is not installed.",
                    reporter,
                )
                raise Exception(f"Reporter plugin '{reporter}' is not installed.")

        # Get the reporters from the plugin loader
        reporters = [(i, plugin_loader.get_reporters()[i]) for i in reporters_list]
        self.reporters = reporters
        LOG.debug("Reporters loaded: %s", reporters_list)

        # Set the reporter plugin timeout
        self.timeout = CONFIG.getint("cloud_analytics", "reporter_timeout")

    async def send_metrics(self, metric_list):
        """Send the metrics to the reporters.

        :param metric_list: The list of metrics to send
        :type metric_list: list[Metric]
        """
        # If the metric list is empty, do nothing
        if not metric_list:
            return

        for reporter_name, reporter_cls in self.reporters:
            # Create an async task for each reporter and set a timeout
            with trio.move_on_after(self.timeout) as cancel_scope:
                async with trio.open_nursery() as nursery:
                    nursery.start_soon(self._forward_metrics, reporter_cls, metric_list)

            if cancel_scope.cancelled_caught:
                LOG.error(
                    "Timeout reached for the reporter '%s' for the machine %s",
                    reporter_name,
                    metric_list[0].hostname,
                )

    async def _forward_metrics(self, reporter, metric_list):
        LOG.info(
            "Reporting metrics to '%s', from the machine %s",
            reporter.__name__,
            metric_list[0].hostname,
        )
        await reporter().report_metric(metric_list)

    def get_installed_plugins(self):
        """Get the list of installed reporters.

        :return: The list of installed reporters
        :rtype: list[str]
        """
        return plugin_loader.get_reporters_names()
