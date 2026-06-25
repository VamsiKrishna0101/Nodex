from pathlib import Path

import typer
from rich.console import Console

console = Console()

AGENT_TEMPLATE = '''from nodex import Agent
from langchain_google_genai import ChatGoogleGenerativeAI

app = Agent(name="{name}", debug=False)
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")


@app.node(next="end")
def start(state):
    query = state.get("query")
    response = llm.invoke(query)
    return {{"output": response.content}}


if __name__ == "__main__":
    trace = app.run({{"query": "Hello from {name}!"}})
'''

ENV_TEMPLATE = """GOOGLE_API_KEY=your_key_here
"""

REQUIREMENTS_TEMPLATE = """nodex
langchain-google-genai
"""


def new(name: str = typer.Argument(..., help="Name of your agent project")):
    project_path = Path(name)

    if project_path.exists():
        console.print(f"[red]Error: Directory '{name}' already exists.[/red]")
        raise typer.Exit(1)

    project_path.mkdir(parents=True)

    agent_file = project_path / "agent.py"
    agent_file.write_text(AGENT_TEMPLATE.format(name=name), encoding="utf-8")

    env_file = project_path / ".env"
    env_file.write_text(ENV_TEMPLATE, encoding="utf-8")

    req_file = project_path / "requirements.txt"
    req_file.write_text(REQUIREMENTS_TEMPLATE, encoding="utf-8")

    gitignore_file = project_path / ".gitignore"
    gitignore_file.write_text(".env\n.venv\n__pycache__\n", encoding="utf-8")

    console.print()
    console.print(f"[green]Created nodex project:[/green] [bold]{name}[/bold]")
    console.print()
    console.print("  [dim]Next steps:[/dim]")
    console.print(f"  [cyan]cd {name}[/cyan]")
    console.print("  [cyan]pip install -r requirements.txt[/cyan]")
    console.print("  [cyan]nodex dev agent:app[/cyan]")
    console.print()
