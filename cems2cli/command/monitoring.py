"""Monitoring commands for the cems2cli command line interface."""

import requests
import rich
import typer
from fastapi import status
from typer import Argument, Option
from typing_extensions import Annotated

from cems2cli import config_loader

# Get the configuration
CONFIG = config_loader.get_config()

# From the configuration, get the base URL for the API
API_BASE_URL = CONFIG["API"]["URL"]

# Create a typer app
monitoring_app = typer.Typer()


@monitoring_app.command(
    "plugins", help="Get plugins installed on cems2 cloud analytics system."
)
def get_plugins(type: Annotated[str, Option(help="Type of the plugin.")] = None):
    """Get plugins on cems2 cloud analytics system.

    :param type: Type of the plugin.
    :type type: str
    """

    # Create the URL for the API call
    url = f"{API_BASE_URL}/monitoring/plugins"

    # Create a payload
    payload = {}

    # If the type is not None, add it to the payload
    if type is not None:
        payload["type"] = type

    # Make the API call
    response = requests.get(url, params=payload)

    # Check if the API call was successful
    if response.status_code == status.HTTP_200_OK:
        # Print the response as a table

        table = rich.table.Table(title="CEMS2 Machine Control System Plugins")

        table.add_column("Name", min_width=20)
        table.add_column("Type", min_width=20)

        # Loop through the response
        for plugin in response.json():
            table.add_row(
                plugin["name"],
                plugin["type"],
            )

        rich.print(table)
    # If the API call was not successful
    else:
        # Print an error message
        rich.print(f"[red]Error: {response.json()['detail']}[/red]")


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
    if response.status_code == status.HTTP_200_OK:
        # Print the response as a table
        table = rich.table.Table(title="CEMS2 Cloud Analytics System")

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
    if response.status_code == status.HTTP_200_OK:
        # Print the response as a table
        table = rich.table.Table(title="CEMS2 Cloud Analytics System")

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
    if response.status_code == status.HTTP_200_OK:
        # Print the response as a table
        table = rich.table.Table(title="CEMS2 Cloud Analytics System")

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
    if response.status_code == status.HTTP_200_OK:
        # Create the URL for the API call to start the system
        url = f"{API_BASE_URL}/monitoring/cloud-analytics=True"

        # Make the API call
        response = requests.put(url)

        if response.status_code == status.HTTP_200_OK:
            # Print the response as a table
            table = rich.table.Table(title="CEMS2 Cloud Analytics System")

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
    name: Annotated[str, Option(help="Name of the metric.")] = None,
    id: Annotated[str, Option(help="ID of the machine on cems2database.")] = None,
    host: Annotated[str, Option(help="Hostname of the machine.")] = None,
):
    """Get metrics from cems2 cloud analytics system.

    :param name: Name of the metric.
    :type name: str

    :param id: ID of the machine on cems2database.
    :type id: str

    :param hostname: Hostname of the machine.
    :type hostname: str
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
        payload["hostname"] = hostname

    # Make the API call
    response = requests.get(url, params=payload)

    # Check if the API call was successful
    if response.status_code == status.HTTP_200_OK:
        # Print the response as a table

        rich.print(response.json())

        table = rich.table.Table(title="CEMS2 Cloud Analytics System Metrics")

        table.add_column("Name")
        table.add_column("Payload")
        table.add_column("Hostname")
        table.add_column("Collected from")
        table.add_column("Timestamp")

        rich.print(table)
    # If the API call was not successful
    else:
        # Print an error message
        rich.print(f"[red]Error: {response.json()['detail']}[/red]")
