"""Machine commands for the cems2cli command line interface."""

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
    host: Annotated[str, Option(help="Hostname of the machine.")] = None,
    id: Annotated[str, Option(help="ID of the machine.")] = None,
    group: Annotated[str, Option(help="Groupname of the machine.")] = None,
    brand: Annotated[str, Option(help="Brand name of the machine.")] = None,
    energy: Annotated[str, Option(help="Energy status of the machine.")] = None,
    monitoring: Annotated[str, Option(help="Monitoring status of the machine.")] = None,
    available: Annotated[str, Option(help="Available status of the machine.")] = None,
):
    """Get machines information.

    :param hostname: Hostname of the machine.
    :type hostname: str

    :param id: ID of the machine.
    :type id: str

    :param groupname: Groupname of the machine.
    :type groupname: str

    :param brand_name: Brand name of the machine.
    :type brand_name: str

    :param energy_status: Energy status of the machine.
    :type energy_status: str

    :param monitoring: Monitoring status of the machine.
    :type monitoring: str

    :param available: Available status of the machine.
    :type available: str
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
        # Add the groupname to the request if it was provided
        if group:
            request += url_next_concater(request) + f"group_name={group}"

        # Add the brand name to the request if it was provided
        if brand:
            request += url_next_concater(request) + f"brand_name={brand}"

        if energy:
            request += url_next_concater(request) + f"energy_status={energy}"

        if monitoring:
            request += url_next_concater(request) + f"monitoring={monitoring}"

        if available:
            request += url_next_concater(request) + f"available={available}"

    print(request)

    # Get the machine information
    response = requests.get(request)

    print(response)

    # Check if the request was successful
    if response.status_code == status.HTTP_200_OK:
        # If it was, print the machine information as a table

        # Create a table
        table = rich.table.Table(title="Machines Information")

        # Add headers to the table
        add_machine_headers(table)

        # Add rows to the table
        for machine in response.json():
            data = parse_machines(machine)
            table.add_row(*data.values())

        # Print the table
        rich.print(table)

    else:
        # If it wasn't, print the error message
        rich.print(f"[red]{response.json()}[/red]")


def url_next_concater(url):
    # Find if the url has a ? or not
    if "?" in url:
        return "&"
    else:
        return "?"


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


# Command to update monitoring flag
@machine_app.command("monitor", help="Update monitoring flag.")
def update_monitoring(
    status: str,
    host: Annotated[str, Option(help="Hostname of the machine.")] = None,
    id: Annotated[str, Option(help="ID of the machine.")] = None,
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

    # Add the monitoring flag to the request if it was provided
    request += f"/monitoring?monitoring={status}"

    print(request)

    # Get the machine information
    response = requests.patch(request)

    print(response)

    # Create a table
    table = rich.table.Table(title="Machines Information")

    # Add headers to the table
    add_machine_headers(table)

    # Add rows to the table
    for machine in response.json():
        data = parse_machines(machine)
        table.add_row(*data.values())

    # Print the table
    rich.print(table)
