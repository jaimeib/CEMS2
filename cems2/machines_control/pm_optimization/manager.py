"""Physical Machines Optimization Manager module."""

import trio

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

        # Global manager
        self.machines_control_manager = None

        # List of running optimizations
        self.running_optimizations = []

        # Obtain the list of Physical Machines optimizations configured in the config file
        default_pm_optimization_name = CONFIG.get(
            "machines_control.plugins", "default_pm_optimization"
        )

        # Check if the default Physical Machines optimization is installed
        if (
            default_pm_optimization_name
            not in plugin_loader.get_pm_optimizations_names()
        ):
            LOG.error(
                "Physical Machines Optimization plugin '%s' is not installed.",
                default_pm_optimization_name,
            )
            raise Exception(
                f"Physical Machines Optimization plugin '{default_pm_optimization_name}' is not installed."
            )

        # Get the default Physical Machines optimization from the plugin loader
        default_pm_optimization = plugin_loader.get_pm_optimizations()[
            default_pm_optimization_name
        ]

        self.default_pm_optimization = default_pm_optimization
        LOG.debug(
            "Default Pysical Machines Optimizations loaded: %s",
            default_pm_optimization_name,
        )

        # Get all the Physical Machines optimizations from the plugin loader
        self.pm_optimizations = plugin_loader.get_pm_optimizations()

        LOG.debug(
            "Physical Machines Optimizations loaded: %s",
            list(plugin_loader.get_pm_optimizations_names()),
        )

        # Launch the optimization plugins
        trio.run(self.launch_optimization_plugins)

    async def launch_optimization_plugins(self):
        """Launch the optimization plugins."""

        # For each optimization plugin create an async task
        for optimization_name, optimization_cls in self.pm_optimizations.items():
            async with trio.open_nursery() as nursery:
                nursery.start_soon(self._launch_optimization_plugin, optimization_cls)

    async def _launch_optimization_plugin(self, optimization_cls):
        """Launch the optimization plugin.

        :param optimization_cls: The optimization plugin class
        :type optimization_cls: Optimization
        """

        # Create the optimization plugin
        optimization = optimization_cls()

        # Save the optimization plugin in the list of running optimizations
        self.running_optimizations.append(optimization)

        # Run the optimization plugin
        await optimization.run()

    def new_metrics(self, new_metrics):
        """Pass the new metrics to the optimization plugins running.

        :param new_metrics: new metrics
        :type new_metrics: dict
        """

        # Pass the new metrics to the default Physical Machines optimization

    async def get_default_optimization(self):
        """Get the default Physical Machines optimization.

        :return: A dict with the result of the optimization
        :rtype: dict
        """

        result = {"on": [], "off": []}

        return result

    def get_installed_plugins(self):
        """Get the list of installed Physical Machines optimizations.

        :return: The list of installed Physical Machines optimizations
        :rtype: list[str]
        """
        return plugin_loader.get_pm_optimizations_names()
