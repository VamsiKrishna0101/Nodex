import importlib
import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from watchfiles import watch

console = Console()


def dev(
    target: str = typer.Argument(..., help="Agent to run in format: filename:instance (e.g. agent:app)"),
    input: str = typer.Option("{}", "--input", "-i", help="Initial state as JSON string"),
):
    try:
        initial_state = json.loads(input)
    except json.JSONDecodeError:
        console.print("[red]Error: Invalid JSON input.[/red]")
        raise typer.Exit(1) from None

    try:
        module_name, instance_name = target.split(":")
    except ValueError:
        console.print("[red]Error: Invalid format. Use: nodex dev filename:instance (e.g. agent:app)[/red]")
        raise typer.Exit(1) from None

    sys.path.insert(0, str(Path.cwd()))

    console.print("[cyan]>  nodex dev mode - watching for changes...[/cyan]")
    console.print(f"[dim]   Target: {target}[/dim]")
    console.print()

    _run_agent(module_name, instance_name, initial_state)

    for _changes in watch(Path.cwd(), watch_filter=lambda change, path: path.endswith(".py")):
        console.print()
        console.print("[yellow]File changed - reloading...[/yellow]")
        console.print()

        if module_name in sys.modules:
            del sys.modules[module_name]

        _run_agent(module_name, instance_name, initial_state)


def _run_agent(module_name: str, instance_name: str, initial_state: dict) -> None:
    try:
        module = importlib.import_module(module_name)
        agent = getattr(module, instance_name)
        agent.run(initial_state)
    except ModuleNotFoundError:
        console.print(f"[red]Error: Could not find file: {module_name}.py[/red]")
    except AttributeError:
        console.print(f"[red]Error: Could not find instance '{instance_name}' in {module_name}.py[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
