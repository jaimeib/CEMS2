"""PM Optimization Manager module."""

import trio

from cems2 import config_loader, log
from cems2.machines_control import plugin_loader

# Get the logger
LOG = log.get_logger(__name__)

# Get the configuration
CONFIG = config_loader.get_config()


class Manager(object):
    """Manager for the PM Optimizations."""

    def __init__(self):
        """Initialize the PM optimization manager."""
        # Obtain the list of PM optimizations configured in the config file
        default_pm_optimization_name = CONFIG.get(
            "machines_control.plugins", "default_pm_optimization"
        )

        # Check if the default PM optimization is installed
        if (
            default_pm_optimization_name
            not in plugin_loader.get_pm_optimizations_names()
        ):
            LOG.error(
                "PM Optimization plugin '%s' is not installed.",
                default_pm_optimization_name,
            )
            raise Exception(
                f"PM Optimization plugin '{default_pm_optimization_name}' is not installed."
            )

        # Get the default PM optimization from the plugin loader
        default_pm_optimization = plugin_loader.get_pm_optimizations()[
            default_pm_optimization_name
        ]

        # Initialize the default PM optimization
        self.default_pm_optimization = default_pm_optimization()
        LOG.debug(
            "Default PM Optimizations loaded: %s",
            default_pm_optimization_name,
        )

        # Get all the PM optimizations from the plugin loader
        self.pm_optimizations = plugin_loader.get_pm_optimizations()
        LOG.debug(
            "PM Optimizations loaded: %s",
            list(plugin_loader.get_pm_optimizations_names()),
        )

    def new_metrics(self, new_metrics):
        """Pass the new metrics to the default optimization.

        :param new_metrics: new metrics
        :type new_metrics: dict
        """
        self.default_pm_optimization.recieve_metrics(new_metrics)

    def new_baseline(self, new_baseline):
        """Pass the new baseline to the default optimization.

        :param new_baseline: new baseline
        :type new_baseline: dict
        """
        self.default_pm_optimization.recieve_baseline(new_baseline)

    async def get_default_optimization(self):
        """Get the default PM optimization.

        :return: A dict with the result of the optimization
        :rtype: dict
        """
        return await self.default_pm_optimization.get_optimization()

    def get_installed_plugins(self):
        """Get the list of installed PM optimizations.

        :return: The list of installed PM optimizations
        :rtype: list[str]
        """
        return plugin_loader.get_pm_optimizations_names()
