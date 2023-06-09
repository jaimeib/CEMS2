"""cems2cli main module."""

import typer

import cems2cli.command.actions
import cems2cli.command.machine
import cems2cli.command.monitoring

# Create a typer app
main_app = typer.Typer()

# Add subcommands to the main app
main_app.add_typer(cems2cli.command.actions.actions_app, name="actions")
main_app.add_typer(cems2cli.command.machine.machine_app, name="machine")
main_app.add_typer(cems2cli.command.monitoring.monitoring_app, name="monitoring")

if __name__ == "__main__":
    main_app()
