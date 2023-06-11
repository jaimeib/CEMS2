"""Actions commands for the cems2cli command line interface."""

from typing import Optional

import requests
import rich
import typer
from fastapi import status as HTTPstatus
from typer import Argument, Option
from typing_extensions import Annotated

from cems2cli import config_loader

# Get the configuration
CONFIG = config_loader.get_config()

# From the configuration, get the base URL for the API
API_BASE_URL = CONFIG["API"]["URL"]

# Table title
TITLE = "CEMS2 Machine Control System"

# Create a typer app
actions_app = typer.Typer()


@actions_app.command(
    "plugins", help="Get plugins installed on cems2 machine control system."
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
    """Get plugins on cems2 machine control system.

    :param type: Type of the plugin.
    :type type: str

    :param status: Status of the plugin.
    :type status: str
    """
    # Create the URL for the API call
    url = f"{API_BASE_URL}/actions/plugins"

    # Create a payload
    payload = {}

    # If the type is not None, add it to the payload
    if type is not None:
        payload["type"] = type

    # If the status is not None, add it to the payload
    if status is not None:
        payload["status"] = status

    # Make the API call
    response = requests.get(url, params=payload)

    # Check if the API call was successful
    if response.status_code == HTTPstatus.HTTP_200_OK:
        # Print the response as a table

        table = rich.table.Table(title="CEMS2 Machine Control System Plugins")

        table.add_column("Name", min_width=20)
        table.add_column("Type", min_width=20)
        table.add_column("Status", min_width=20)

        # Loop through the response
        for plugin in response.json():
            table.add_row(
                plugin["name"],
                plugin["type"],
                plugin["status"],
            )

        rich.print(table)
    # If the API call was not successful
    else:
        # Print an error message
        rich.print(f"[red]Error: {response.json()['detail']}[/red]")


@actions_app.command(
    "status", help="Get the running status of the cems2 machine control system."
)
def get_status():
    """Get the running status of the cems2 machine control system."""
    # Create the URL for the API call
    url = f"{API_BASE_URL}/actions/machines_control"

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


@actions_app.command("start", help="Start cems2 machine control system.")
def start():
    """Start cems2 machine control system."""

    # Create the URL for the API call
    url = f"{API_BASE_URL}/actions/machines_control=True"

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


@actions_app.command("stop", help="Stop cems2 machine control system.")
def stop():
    """Stop cems2 machine control system."""

    # Create the URL for the API call
    url = f"{API_BASE_URL}/actions/machines_control=False"

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


@actions_app.command("restart", help="Restart cems2 machine control system.")
def restart():
    """Restart cems2 machine control system."""

    # Create the URL for the API call to stop the system
    url = f"{API_BASE_URL}/actions/machines_control=False"

    # Make the API call
    response = requests.put(url)

    # Check if the API call was successful
    if response.status_code == HTTPstatus.HTTP_200_OK:
        # Create the URL for the API call to start the system
        url = f"{API_BASE_URL}/actions/machines_control=True"

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
