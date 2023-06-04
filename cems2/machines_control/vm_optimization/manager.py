"""Virtual Machines Optimization Manager module."""

from cems2 import config_loader, log
from cems2.machines_control import plugin_loader

# Get the logger
LOG = log.get_logger(__name__)

# Get the configuration
CONFIG = config_loader.get_config()


class Manager(object):
    """Manager for the Virtual Machines Optimizations."""

    def __init__(self):
        """Initialize the Virtual Machines optimization manager."""
        # Obtain the default Virtual Machines optimization configured in the config file
        default_vm_optimization_name = CONFIG.get(
            "machines_control.plugins", "default_vm_optimization"
        )

        # Check if the default Virtual Machines optimization is installed
        if (
            default_vm_optimization_name
            not in plugin_loader.get_vm_optimizations_names()
        ):
            LOG.error(
                "Virtual Machines Optimization plugin '%s' is not installed.",
                default_vm_optimization_name,
            )
            raise Exception(
                f"Virtual Machines Optimization plugin '{default_vm_optimization_name}' is not installed."
            )

        # Get the default Virtual Machines optimization from the plugin loader
        default_vm_optimization = plugin_loader.get_vm_optimizations()[
            default_vm_optimization_name
        ]
        self.default_vm_optimization = default_vm_optimization
        LOG.debug(
            "Default Virtual Machines Optimizations loaded: %s",
            default_vm_optimization_name,
        )

        # Get all the Virtual Machines optimizations from the plugin loader
        self.vm_optimizations = plugin_loader.get_vm_optimizations()
        LOG.debug(
            "Virtual Machines Optimizations loaded: %s",
            list(plugin_loader.get_vm_optimizations_names()),
        )

    def new_metrics(self, new_metrics):
        """Pass the new metrics to the optimization plugins running.

        :param new_metrics: new metrics
        :type new_metrics: dict
        """

        # Pass the new metrics to the default Virtual Machines optimization

    async def get_default_optimization(self):
        """Get the default Virtual Machines optimization.

        :return: A dict with the result of the optimization
        :rtype: dict
        """

        result = {}

        return result

    def get_installed_plugins(self):
        """Get the list of installed Virtual Machines optimizations.

        :return: The list of installed Virtual Machines optimizations
        :rtype: list[str]
        """
        return plugin_loader.get_vm_optimizations_names()
