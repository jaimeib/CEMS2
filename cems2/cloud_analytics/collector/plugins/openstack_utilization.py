"""OpenStack utilization collector plug-in."""

from datetime import datetime

from cems2 import log
from cems2.cloud_analytics.collector.base import MetricCollectorBase
from cems2.schemas.metric import Metric

# Get the logger
LOG = log.get_logger(__name__)


class OpenStackUtilization(MetricCollectorBase):
    """Allows to collect the utilization metrics from the OpenStack cloud platform."""

    def __init__(self):
        """Initialize the connection to the OpenStack cloud platform."""
        # TODO: Open a session to the OpenStack cloud platform

    def collect_metric(self, machine_id):
        """Collect the utilization metric from the OpenStack cloud platform."""
        LOG.info("Collecting utilization metric from OpenStack cloud platform")
        metric = Metric(
            name="utilization",
            value=0.0,
            unit="%",
            timestamp=datetime.now(),
            hostname=machine_id,
        )
        print("Collect:", metric)
        return metric
