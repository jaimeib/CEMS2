"""VM Optimization Manager module."""

from cems2 import config_loader, log
from cems2.machines_control import plugin_loader

# Get the logger
LOG = log.get_logger(__name__)

# Get the configuration
CONFIG = config_loader.get_config()


class Manager(object):
    """Manager for the VM Optimizations."""

    def __init__(self):
        """Initialize the VM optimization manager."""
        # Obtain the default VM optimization configured in the config file
        default_vm_optimization_name = CONFIG.get(
            "machines_control.plugins", "default_vm_optimization"
        )

        # Check if the default VM optimization is installed
        if (
            default_vm_optimization_name
            not in plugin_loader.get_vm_optimizations_names()
        ):
            LOG.error(
                "VM Optimization plugin '%s' is not installed.",
                default_vm_optimization_name,
            )
            raise Exception(
                f"VM Optimization plugin '{default_vm_optimization_name}' is not installed."
            )

        # Get the default VM optimization from the plugin loader
        default_vm_optimization = plugin_loader.get_vm_optimizations()[
            default_vm_optimization_name
        ]
        self.default_vm_optimization = default_vm_optimization()
        LOG.debug(
            "Default VM Optimizations loaded: %s",
            default_vm_optimization_name,
        )

        # Get all the VM optimizations from the plugin loader
        self.vm_optimizations = plugin_loader.get_vm_optimizations()
        LOG.debug(
            "VM Optimizations loaded: %s",
            list(plugin_loader.get_vm_optimizations_names()),
        )

    def new_metrics(self, new_metrics):
        """Pass the new metrics to the default optimization.

        :param new_metrics: new metrics
        :type new_metrics: dict
        """
        self.default_vm_optimization.recieve_metrics(new_metrics)

    async def get_default_optimization(self):
        """Get the default VM optimization.

        :return: A dict with the result of the optimization
        :rtype: dict
        """
        return await self.default_vm_optimization.get_optimization()

    async def get_current_distribution(self):
        """Get the current distribution of VMs.

        :return: A dict with the current distribution of VMs
        :rtype: dict
        """
        return await self.default_vm_optimization.get_current_distribution()

    def get_installed_plugins(self):
        """Get the list of installed VM optimizations.

        :return: The list of installed VM optimizations
        :rtype: list[str]
        """
        return plugin_loader.get_vm_optimizations_names()
