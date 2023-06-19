"""Actions commands for the cems2cli command line interface."""

import time
from typing import Optional

import requests
import rich
import typer
from fastapi import status as HTTPstatus
from rich.progress import Progress
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

    # Call the common method to process the plugins
    process_plugins(url, str(TITLE + "Plugins"), type, status)


def process_plugins(
    request_url: str, table_title: str, type: str = None, status: str = None
):
    # Create a payload
    payload = {}

    # If the type is not None, add it to the payload
    if type is not None:
        payload["type"] = type

    # If the status is not None, add it to the payload
    if status is not None:
        payload["status"] = status

    # Make the API call
    response = requests.get(request_url, params=payload)

    # Check if the API call was successful
    if response.status_code == HTTPstatus.HTTP_200_OK:
        # Print the response as a table

        table = rich.table.Table(title=table_title)

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


@actions_app.command(
    "optimizations",
    help="Get results of optimizations installed on cems2 machine control system.",
)
# Has an argument called subsystem that is required and has to be or "vm" or "pm"
def optimizations(
    subsystem: str = Argument(
        help="The subsystem to obtain the optimization [VM,PM]",
        case_sensitive=False,
        show_default=False,
    ),
    name: Optional[str] = Option(
        None, "-n", "--name", help="Name of the optimization."
    ),
):
    """Get results of optimizations installed on cems2 machine control system.

    :param subsystem: The subsystem to obtain the optimization [VM,PM]
    :type subsystem: str

    :param name: Name of the optimization.
    :type name: str

    :raises typer.BadParameter: If the subsystem is not "vm" or "pm"
    """
    # Check if the subsystem is "vm" or "pm" or raise an error otherwise
    if subsystem not in ["vm", "pm", "VM", "PM"]:
        raise typer.BadParameter("Subsytem must be either 'vm' or 'pm' or 'VM' or 'PM'")

    # Create the URL for the API call
    url = f"{API_BASE_URL}/actions/"

    # If the subsystem is "vm"
    if subsystem.lower() == "vm":
        # Add "vm" to the URL
        url += "vm-optimizations"

    # If the subsystem is "pm"
    if subsystem.lower() == "pm":
        # Add "pm" to the URL
        url += "pm-optimizations"

    # Create a payload
    payload = {}

    # if the name is not None add it to the payload
    if name is not None:
        payload["name"] = name

    # Make the API call and while waiting for the response, print a rich progress bar
    with rich.progress.Progress(
        rich.progress.TextColumn("[bold]{task.description}"),
        rich.progress.BarColumn(),
        rich.progress.TaskProgressColumn(),
    ) as progress:
        task = progress.add_task(
            "Waiting for optimization...", total=100, start=False, complete=False
        )

        response = requests.get(url, params=payload)

        progress.start_task(task)

        # Updating the progress bar
        for _ in range(100):
            time.sleep(0.005)  # Simulating processing time for each iteration
            progress.update(task, advance=1)

        # Check if the API call was successful
        if response.status_code == HTTPstatus.HTTP_200_OK:
            # If the subsystem is "vm"
            if subsystem.lower() == "vm":
                _print_vm_optimization(response, progress, task)

            # If the subsystem is "pm"
            if subsystem.lower() == "pm":
                _print_pm_optimization(response, progress, task)

        # If the API call was not successful
        else:
            # Print an error message
            rich.print(f"[red]Error: {response.json()['detail']}[/red]")


def _print_vm_optimization(response, progress, task):
    """Print the response of the API call to get the VM optimizations.

    :param response: response of the API call
    :type response: requests.models.Response

    :param progress: rich progress bar
    :type progress: rich.progress.Progress

    :param task: task of the rich progress bar
    :type task: rich.progress.Task
    """
    table = rich.table.Table(title="CEMS2 Machine Control System VM Optimizations")

    # Add headers to the table
    table.add_column("Optimization Name", min_width=20)
    table.add_column("Physical Machine", min_width=20)
    table.add_column("Virtual Machines", min_width=20)

    for optimization_name, optimization_result in response.json().items():
        for pm, vms in optimization_result.items():
            table.add_row(
                optimization_name,
                pm,
                _parse_vm(vms),
            )
    progress.update(task, advance=100)
    # Print the table
    rich.print(table)


def _print_pm_optimization(response, progress, task):
    """Print the response of the API call to get the PM optimizations.

    :param response: response of the API call
    :type response: requests.models.Response

    :param progress: rich progress bar
    :type progress: rich.progress.Progress

    :param task: task of the rich progress bar
    :type task: rich.progress.Task
    """
    table = rich.table.Table(title="CEMS2 Machine Control System PM Optimizations")

    # Add headers to the table
    table.add_column("Optimization Name", min_width=20)
    table.add_column("Physical Machines ON", min_width=20)
    table.add_column("Physical Machines OFF", min_width=20)

    for optimization_name, optimization_result in response.json().items():
        table.add_row(
            optimization_name,
            str(optimization_result["on"]) + "\n",
            str(optimization_result["off"]) + "\n",
        )
    progress.update(task, advance=100)
    # Print the table
    rich.print(table)


def _parse_vm(vms):
    """Parse the response of the API call to get the VMs.

    :param vms: dictionary with the VMs
    :type vms: list[dict]

    :return: VMs parsed as a table
    :rtype: rich.table.Table
    """
    # Create a table
    table = rich.table.Table()

    # Add headers to the table
    table.add_column("VM UUID", min_width=40)
    table.add_column("VCPUs", min_width=5)
    table.add_column("Memory", min_width=10)
    table.add_column("Disk", min_width=10)
    table.add_column("Managed by", min_width=10)

    for vm in vms:
        for vm_uuid, vm_info in vm.items():
            nvcpus = str(vm_info["vcpus"])
            memory = str(vm_info["memory"]["amount"]) + " " + vm_info["memory"]["unit"]
            disk = str(vm_info["disk"]["amount"]) + " " + vm_info["disk"]["unit"]
            managed_by = vm_info["managed_by"]
            table.add_row(vm_uuid, nvcpus, memory, disk, managed_by)

    # Print the table
    return table
