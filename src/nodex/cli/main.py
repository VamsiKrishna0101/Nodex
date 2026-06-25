import typer

from nodex.cli.commands.dev import dev
from nodex.cli.commands.new import new
from nodex.cli.commands.run import run

app = typer.Typer(
    name="nodex",
    help="The Express.js for LangGraph agents.",
    add_completion=False,
)

app.command()(new)
app.command()(run)
app.command()(dev)


if __name__ == "__main__":
    app()
