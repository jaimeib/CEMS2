"""Physical Machines Optimization Manager module."""

from cems2 import config_loader, log
from cems2.machines_control import plugin_loader

# Get the logger
LOG = log.get_logger(__name__)

# Get the configuration
CONFIG = config_loader.get_config()


class Manager(object):
    """Manager for the Physical Machines Optimizations."""

    def __init__(self):
        """Initialize the Physical Machines optimization manager."""
        # Physical Machines baseline
        self.pm_baseline = None

        # Physical Machines last metrics
        self.pm_metrics = None

        # Obtain the list of Physical Machines optimizations configured in the config file
        pm_optimizations_list = CONFIG.getlist(
            "machines_control.plugins", "pm_optimization"
        )

        # Check if the Physical Machines optimizations are installed
        for pm_optimization in pm_optimizations_list:
            if pm_optimization not in plugin_loader.get_pm_optimizations_names():
                LOG.error(
                    "Physical Machines Optimization plugin '%s' is not installed.",
                    pm_optimization,
                )
                raise Exception(
                    f"Physical Machines Optimization plugin '{pm_optimization}' is not installed."
                )

        # Get the Physical Machines optimizations from the plugin loader
        pm_optimizations = [
            (i, plugin_loader.get_pm_optimizations()[i]) for i in pm_optimizations_list
        ]
        self.pm_optimizations = pm_optimizations
        LOG.debug("Physical Machines Optimizations loaded: %s", pm_optimizations_list)

    def get_best_optimization(self):
        """Get the best Physical Machines optimization.

        The optimization is represented by a dict with 2 lists:
        - key = "on" -> list of Physical Machines to turn on
        - key = "off" -> list of Physical Machines to turn off

        :return: The best Physical Machines optimization
        :rtype: dict
        """

        # Initialize the best optimization
        best_optimization = {"on": [], "off": []}

        # Put all the hostnames in the metrics on on list
        for hostname in self.pm_metrics.keys():
            best_optimization["on"].append(hostname)

        return best_optimization

    def get_installed_plugins(self):
        """Get the list of installed Physical Machines optimizations.

        :return: The list of installed Physical Machines optimizations
        :rtype: list[str]
        """
        return plugin_loader.get_pm_optimizations_names()
