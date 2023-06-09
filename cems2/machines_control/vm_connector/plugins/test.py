"""VM connector test plug-in."""

import random

import rich
import trio

from cems2 import log
from cems2.machines_control.vm_connector.base import VMConnectorBase

# Get the logger
LOG = log.get_logger(__name__)


class Test(VMConnectorBase):
    def __init__(self):
        """Initialize the test connection."""

    async def migrate_vm(self, vm_id, pm_hostname):
        """Migrate the VM to the PM.

        :param vm_id: The ID of the VM to migrate
        :type vm_id: str

        :param pm_hostname: The hostname of the dest PM
        :type pm_hostname: str
        """
        LOG.critical("Migrating VM %s to PM %s", vm_id, pm_hostname)
        await trio.sleep(random.randint(1, 5))
        rich.print("TEST-VM_CONNECTOR: Migrating VM %s to PM %s" % (vm_id, pm_hostname))
