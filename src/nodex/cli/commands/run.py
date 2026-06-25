import importlib
import json
import sys
from pathlib import Path

import typer
from rich.console import Console

from nodex.exceptions import NodexConfigError

console = Console()


def run(
    target: str = typer.Argument(..., help="Agent to run in format: filename:instance (e.g. agent:app)"),
    input: str = typer.Option("{}", "--input", "-i", help="Initial state as JSON string"),
):
    try:
        initial_state = json.loads(input)
    except json.JSONDecodeError:
        console.print("[red]Error: Invalid JSON input. Use format: '{\"key\": \"value\"}'[/red]")
        raise typer.Exit(1) from None

    try:
        module_name, instance_name = target.split(":")
    except ValueError:
        console.print("[red]Error: Invalid format. Use: nodex run filename:instance (e.g. agent:app)[/red]")
        raise typer.Exit(1) from None

    sys.path.insert(0, str(Path.cwd()))

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        console.print(f"[red]Error: Could not find file: {module_name}.py[/red]")
        raise typer.Exit(1) from None

    try:
        agent = getattr(module, instance_name)
    except AttributeError:
        console.print(f"[red]Error: Could not find instance '{instance_name}' in {module_name}.py[/red]")
        raise typer.Exit(1) from None

    try:
        agent.run(initial_state)
    except NodexConfigError as e:
        console.print(f"[red]Config error: {e}[/red]")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from None
