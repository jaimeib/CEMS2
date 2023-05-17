"""Physical Machines Connector Manager module."""

from cems2 import config_loader, log
from cems2.machines_control import plugin_loader

# Get the logger
LOG = log.get_logger(__name__)

# Get the configuration
CONFIG = config_loader.get_config()


class Manager(object):
    """Manager for the Physical Machines Connectors."""

    def __init__(self):
        """Initialize the Physical Machines connector manager."""
        # Obtain the list of Physical Machines connectors configured in the config file
        pm_connectors_list = CONFIG.getlist("machines_control.plugins", "pm_connector")

        for pm_connector in pm_connectors_list:
            if pm_connector not in plugin_loader.get_pm_connectors_names():
                LOG.error(
                    "Physical Machines Connector plugin '%s' is not installed",
                    pm_connector,
                )
                raise Exception(
                    f"Physical Machines Connector plugin '{pm_connector}' is not installed."
                )
        # Get the Physical Machines connectors from the plugin loader
        pm_connectors = [
            (i, plugin_loader.get_pm_connectors()[i]) for i in pm_connectors_list
        ]
        self.pm_connectors = pm_connectors
        LOG.debug("Physical Machines Connectors loaded: %s", pm_connectors_list)

    # TODO: Apagados y encendidos de máquinas dinamicos -> Como se decide que conectores se usan?
