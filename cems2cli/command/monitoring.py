"""Monitoring commands for the cems2cli command line interface."""

import json
from typing import Optional

import requests
import rich
import typer
from fastapi import status as HTTPstatus
from typer import Option

from cems2cli import config_loader
from cems2cli.command.actions import _parse_vm, process_plugins

# Get the configuration
CONFIG = config_loader.get_config()

# From the configuration, get the base URL for the API
API_BASE_URL = CONFIG["API"]["URL"]

# Table title
TITLE = "CEMS2 Cloud Analytics System"

# Create a typer app
monitoring_app = typer.Typer()


@monitoring_app.command(
    "plugins", help="Get plugins installed on cems2 cloud analytics system."
)
def get_plugins(
    type: Optional[str] = Option(
        None,
        "-t",
        "--type",
        help="Type of the plugin.",
        case_sensitive=False,
        show_default=False,
    ),
    status: Optional[str] = Option(
        None,
        "-s",
        "--status",
        help="Status of the plugin.",
        case_sensitive=False,
        show_default=False,
    ),
):
    """Get plugins on cems2 cloud analytics system.

    :param type: Type of the plugin.
    :type type: str

    :param status: Status of the plugin.
    :type status: str
    """

    # Create the URL for the API call
    url = f"{API_BASE_URL}/monitoring/plugins"

    # Call the common method to process the plugins
    process_plugins(url, "CEMS2 Cloud Analytics System Plugins", type, status)


@monitoring_app.command(
    "status", help="Get the running status of the cems2 cloud analytics system."
)
def get_status():
    """Get the running status of the cems2 cloud analytics system."""
    # Create the URL for the API call
    url = f"{API_BASE_URL}/monitoring/cloud-analytics"

    # Make the API call
    response = requests.get(url)

    # Check if the API call was successful
    if response.status_code == HTTPstatus.HTTP_200_OK:
        # Print the response as a table
        table = rich.table.Table(title=TITLE)

        table.add_column("Status", justify="center", style="bold", min_width=30)

        running_status = response.json()

        if running_status:
            table.add_row("[green]Running[/green]")
        else:
            table.add_row("[red]Not Running[/red]")

        rich.print(table)
    # If the API call was not successful
    else:
        # Print an error message
        rich.print(f"[red]Error: {response.json()['detail']}[/red]")


@monitoring_app.command("start", help="Start cems2 cloud analytics system.")
def start():
    """Start cems2 cloud analytics system."""

    # Create the URL for the API call
    url = f"{API_BASE_URL}/monitoring/cloud-analytics=True"

    # Make the API call
    response = requests.put(url)

    # Check if the API call was successful
    if response.status_code == HTTPstatus.HTTP_200_OK:
        # Print the response as a table
        table = rich.table.Table(title=TITLE)

        table.add_column("Status", justify="center", style="bold", min_width=30)

        # Get the message from the response
        message = response.json()["message"]

        table.add_row(f"[green]{message}[/green]")

        rich.print(table)
    # If the API call was not successful
    else:
        # Print an error message
        rich.print(f"[red]Error: {response.json()['detail']}[/red]")


@monitoring_app.command("stop", help="Stop cems2 cloud analytics system.")
def stop():
    """Stop cems2 cloud analytics system."""

    # Create the URL for the API call
    url = f"{API_BASE_URL}/monitoring/cloud-analytics=False"

    # Make the API call
    response = requests.put(url)

    # Check if the API call was successful
    if response.status_code == HTTPstatus.HTTP_200_OK:
        # Print the response as a table
        table = rich.table.Table(title=TITLE)

        table.add_column("Status", justify="center", style="bold", min_width=30)

        # Get the message from the response
        message = response.json()["message"]

        table.add_row(f"[red]{message}[/red]")

        rich.print(table)
    # If the API call was not successful
    else:
        # Print an error message
        rich.print(f"[red]Error: {response.json()['detail']}[/red]")


@monitoring_app.command("restart", help="Restart cems2 cloud analytics system.")
def restart():
    """Restart cems2 cloud analytics system."""

    # Create the URL for the API call to stop the system
    url = f"{API_BASE_URL}/monitoring/cloud-analytics=False"

    # Make the API call
    response = requests.put(url)

    # Check if the API call was successful
    if response.status_code == HTTPstatus.HTTP_200_OK:
        # Create the URL for the API call to start the system
        url = f"{API_BASE_URL}/monitoring/cloud-analytics=True"

        # Make the API call
        response = requests.put(url)

        if response.status_code == HTTPstatus.HTTP_200_OK:
            # Print the response as a table
            table = rich.table.Table(title=TITLE)

            table.add_column("Status", justify="center", style="bold", min_width=30)

            # Get the message from the response
            message = response.json()["message"]

            table.add_row(f"[green]{message}[/green]")

            rich.print(table)
        # If the API call was not successful
        else:
            # Print an error message
            rich.print(f"[red]Error: {response.json()['detail']}[/red]")
    # If the API call was not successful
    else:
        # Print an error message
        rich.print(f"[red]Error: {response.json()['detail']}[/red]")


@monitoring_app.command(
    "metrics", help="Get metrics from cems2 cloud analytics system."
)
def get_metrics(
    name: Optional[str] = Option(
        None,
        "-n",
        "--name",
        help="Name of the metric.",
        case_sensitive=True,
        show_default=False,
    ),
    id: Optional[str] = Option(
        None,
        "-i",
        "--id",
        help="ID of the machine.",
        case_sensitive=True,
        show_default=False,
    ),
    host: Optional[str] = Option(
        None,
        "-h",
        "--host",
        help="Hostname of the machine.",
        case_sensitive=True,
        show_default=False,
    ),
):
    """Get metrics from cems2 cloud analytics system.

    :param name: Name of the metric.
    :type name: str

    :param id: ID of the machine on cems2database.
    :type id: str

    :param host: Hostname of the machine.
    :type host: str
    """

    # Check that only one identifier was provided
    if host and id:
        rich.print("[red]ERROR: Only one identifier can be provided.[/red]")
        exit(1)

    # Create the URL for the API call
    url = f"{API_BASE_URL}/monitoring/metrics"

    # Create a payload
    payload = {}

    # If the name is not None, add it to the payload
    if name is not None:
        payload["name"] = name

    # If the id is not None, add it to the payload
    if id is not None:
        payload["id"] = id

    # If the hostname is not None, add it to the payload
    if host is not None:
        payload["hostname"] = host

    # Make the API call
    response = requests.get(url, params=payload)

    # Check if the API call was successful
    if response.status_code == HTTPstatus.HTTP_200_OK:
        # Print the response as a table

        table = rich.table.Table(title="CEMS2 Cloud Analytics System Metrics")

        table.add_column("Name")
        table.add_column("Payload")
        table.add_column("Hostname")
        table.add_column("Collected from")
        table.add_column("Timestamp")

        # Parse the response
        metrics = parse_metrics(response.json(), table)

        rich.print(metrics)
    # If the API call was not successful
    else:
        # Print an error message
        rich.print(f"[red]Error: {response.json()['detail']}[/red]")


def parse_metrics(response, table):
    """Parse the metrics response from the API call

    :param response: Response from the API call.
    :type response: dict

    :param table: Table to print the metrics.
    :type table: rich.table.Table

    :return: Table with the metrics.
    :rtype: rich.table.Table
    """
    vms_list = []
    for machine, metrics in response.items():
        for metric in metrics:
            if metric["name"] == "vms":
                for vm_uuid, vm_info in json.loads(metric["payload"]).items():
                    vms_list.append({vm_uuid: vm_info})
                table.add_row(
                    metric["name"],
                    _parse_vm(vms_list),
                    metric["hostname"],
                    metric["collected_from"],
                    metric["timestamp"],
                )
                vms_list = []
            else:
                # Get the payload as a string of a value and a unit from the dictionary
                payload = json.loads(metric["payload"])
                value = str(payload["value"]) + " " + payload["unit"] + "\n"

                table.add_row(
                    "\n" + metric["name"],
                    "\n" + value,
                    "\n" + metric["hostname"],
                    "\n" + metric["collected_from"],
                    "\n" + metric["timestamp"],
                )

    return table
