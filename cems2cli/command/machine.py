"""Machine commands for the cems2cli command line interface."""

from typing import Optional

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

# STATUS_STRINGS
ON = "[green]ON[/green]"
OFF = "[red]OFF[/red]"

# Create a typer app
machine_app = typer.Typer()


# Command to get machine information
@machine_app.command(
    "inventory",
    help="Get machines information.",
)
def get_machine(
    host: Optional[str] = Option(
        None,
        "-h",
        "--host",
        help="Hostname of the machine.",
        case_sensitive=True,
        show_default=False,
    ),
    id: Optional[str] = Option(
        None,
        "-i",
        "--id",
        help="ID of the machine.",
        show_default=False,
        case_sensitive=True,
    ),
    group: Optional[str] = Option(
        None,
        "-g",
        "--group",
        help="Groupname of the machine.",
        case_sensitive=True,
        show_default=False,
    ),
    brand: Optional[str] = Option(
        None,
        "-b",
        "--brand",
        help="Brand name of the machine.",
        case_sensitive=True,
        show_default=False,
    ),
    connector: Optional[str] = Option(
        None,
        "-c",
        "--connector",
        help="Connector name.",
        case_sensitive=False,
        show_default=False,
    ),
    energy: Optional[str] = Option(
        None,
        "-e",
        "--energy",
        help="Energy status.",
        case_sensitive=False,
        show_default=False,
    ),
    monitoring: Optional[str] = Option(
        None,
        "-m",
        "--monitoring",
        help="Monitoring.",
        case_sensitive=False,
        show_default=False,
    ),
    available: Optional[str] = Option(
        None,
        "-a",
        "--available",
        help="Available.",
        case_sensitive=False,
        show_default=False,
    ),
):
    """Get machines information.

    :param hostname: Hostname of the machine.
    :type hostname: str

    :param id: ID of the machine.
    :type id: str

    :param group: Groupname of the machine.
    :type group: str

    :param brand: Brand name of the machine.
    :type brand: str

    :param connector: Connector name.
    :type connector: str

    :param energy: Energy status.
    :type energy: str

    :param monitoring: Monitoring.
    :type monitoring: str

    :param available: Available.
    :type available: str
    """

    request = f"{API_BASE_URL}/machines"
    payload = {}

    # Check that only one identifier was provided
    if host and id:
        rich.print("[red]ERROR: Only one identifier can be provided.[/red]")
        exit(1)

    # Add the identifier to the request if it was provided
    if host:
        request += f"/hostname={host}"

    elif id:
        request += f"/id={id}"

    else:
        # Make the request with the filters provided
        payload = add_filters(group, brand, connector, energy, monitoring, available)

    # Get the machine information
    response = requests.get(request, params=payload)

    # Check if the request was successful
    if response.status_code == status.HTTP_200_OK:
        # If it was, print the machine information as a table

        # Create a table
        table = rich.table.Table(title="CEMS2 Machines Information")

        # Add headers to the table
        add_machine_headers(table)

        # Add rows to the table
        # If the response is a list, add all the machines to the table
        if isinstance(response.json(), list):
            for machine in response.json():
                data = parse_machines(machine)
                table.add_row(*data.values())
        else:
            # If the response is a dictionary, add the machine to the table
            data = parse_machines(response.json())
            table.add_row(*data.values())

        # Print the table
        rich.print(table)

    else:
        # If it wasn't, print the error message
        rich.print(f"[red]{response.json()}[/red]")


def add_filters(group, brand, connector, energy, monitoring, available):
    # Make the request with the filters provided
    filters = {}

    # Add the groupname to the filters if it was provided
    if group:
        filters["group_name"] = group

    # Add the brand to the filters if it was provided
    if brand:
        filters["brand_model"] = brand

    # Add the connector to the filters if it was provided
    if connector:
        filters["connector"] = connector

    # Add the energy status to the filters if it was provided
    if energy:
        filters["energy_status"] = energy

    # Add the monitoring status to the filters if it was provided
    if monitoring:
        filters["monitoring"] = monitoring

    # Add the available status to the filters if it was provided
    if available:
        filters["available"] = available

    return filters


# Command to update monitoring flag
@machine_app.command("monitor", help="Update monitoring flag.")
def update_monitoring(
    monitoring: str,
    host: Optional[str] = Option(
        None,
        "-h",
        "--host",
        help="Hostname of the machine.",
        case_sensitive=True,
        show_default=False,
    ),
    id: Optional[str] = Option(
        None,
        "-i",
        "--id",
        help="ID of the machine.",
        show_default=False,
        case_sensitive=True,
    ),
):
    """Update monitoring flag.

    :param hostname: Hostname of the machine.
    :type hostname: str

    :param id: ID of the machine.
    :type id: str

    :param monitoring: Monitoring status of the machine.
    :type monitoring: str
    """

    request = f"{API_BASE_URL}/machines"

    # Check that only one identifier was provided
    if host and id:
        rich.print("[red]ERROR: Only one identifier can be provided.[/red]")
        exit(1)

    # Add the identifier to the request if it was provided
    if host:
        request += f"/hostname={host}"

    elif id:
        request += f"/id={id}"

    else:
        rich.print("[red]ERROR: No identifier provided.[/red]")
        exit(1)

    # Create the URL for the API call
    url = f"{request}?monitoring={monitoring}"

    # Make the API call
    response = requests.patch(url)

    # Check if the API call was successful
    if response.status_code == status.HTTP_200_OK:
        # Print the response as a table
        table = rich.table.Table(title="CEMS2 Machines Information")

        # Add headers to the table
        add_machine_headers(table)

        data = parse_machines(response.json())
        table.add_row(*data.values())

        # Print the table
        rich.print(table)

    # If the API call was not successful
    else:
        # Print an error message
        rich.print(f"[red]Error: {response.json()['detail']}[/red]")


def add_machine_headers(table):
    table.add_column("ID", style="cyan")
    table.add_column("Hostname")
    table.add_column("Groupname")
    table.add_column("Brand Model")
    table.add_column("Management IP")
    table.add_column("Management Username")
    table.add_column("Management Password")
    table.add_column("Connector Name")
    table.add_column("Energy Status")
    table.add_column("Monitoring Flag")
    table.add_column("Available Flag")


def parse_machines(machine):
    # Add a row to the table if the machine is available print it in green, otherwise print it in red
    data = {}
    data["id"] = str(machine["id"])
    data["hostname"] = machine["hostname"]
    data["groupname"] = machine["groupname"]
    data["brand_model"] = machine["brand_model"]
    data["management_ip"] = machine["management_ip"]
    data["management_username"] = machine["management_username"]
    data["management_password"] = machine["management_password"]
    data["connector"] = machine["connector"]
    if machine["energy_status"]:
        data["energy_status"] = ON
    else:
        data["energy_status"] = OFF
    if machine["monitoring"]:
        data["monitoring"] = ON
    else:
        data["monitoring"] = OFF
    if machine["available"]:
        data["available"] = ON
    else:
        data["available"] = OFF

    return data
