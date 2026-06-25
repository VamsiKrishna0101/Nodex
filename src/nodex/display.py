from rich.console import Console

from nodex.types import ExecutionTrace, NodeResult, NodeStatus

console = Console()

DIVIDER = "-" * 50


class Display:
    def __init__(self, debug: bool = False):
        self.debug = debug

    def print_header(self, agent_name: str) -> None:
        console.print()
        console.print(f">  nodex running - [bold cyan]{agent_name}[/bold cyan]")
        console.print(f"[dim]{DIVIDER}[/dim]")

    def print_divider(self) -> None:
        console.print(f"[dim]{DIVIDER}[/dim]")

    def print_node_result(self, result: NodeResult) -> None:
        if result.status == NodeStatus.SUCCESS:
            self._print_success(result)
        elif result.status == NodeStatus.FAILURE:
            self._print_failure(result)
        elif result.status == NodeStatus.SKIPPED:
            self._print_skipped(result)
        elif result.status == NodeStatus.RETRYING:
            self._print_retrying(result)

    def _print_success(self, result: NodeResult) -> None:
        line = (
            f"[green]OK[/green]  [bold]{result.node_name:<15}[/bold]"
            f"->  [cyan]{result.duration}s[/cyan]"
            f"  |  tokens: {result.tokens}"
            f"  |  [yellow]${result.cost:.4f}[/yellow]"
        )
        if result.retries > 0:
            line += f"  |  [yellow]retried: {result.retries}x[/yellow]"
        console.print(line)

    def _print_failure(self, result: NodeResult) -> None:
        console.print(
            f"[red]ERR[/red] [bold]{result.node_name:<15}[/bold]"
            f"->  [cyan]{result.duration}s[/cyan]"
            f"  |  [red bold]FAILED[/red bold]"
        )
        if result.error:
            console.print(f"    [dim]- Reason: {result.error}[/dim]")
        if self.debug and result.output:
            console.print(f"    [dim]- Output: {result.output}[/dim]")

    def _print_skipped(self, result: NodeResult) -> None:
        console.print(
            f"[yellow]SKIP[/yellow] [bold]{result.node_name:<15}[/bold]"
            f"[dim]skipped[/dim]"
        )

    def _print_retrying(self, result: NodeResult) -> None:
        console.print(
            f"[yellow]RETRY[/yellow] [bold]{result.node_name:<15}[/bold]"
            f"[yellow]retrying ({result.retries}/{result.retries})...[/yellow]"
        )

    def print_error(self, node_name: str, reason: str, trace: list[str]) -> None:
        console.print()
        console.print(f"[red bold]Node '{node_name}' failed[/red bold]")
        console.print(f"   [dim]- Reason: {reason}[/dim]")
        if trace:
            trace_str = " -> ".join(trace) + " <- HERE"
            console.print(f"   [dim]- Trace: {trace_str}[/dim]")

    def print_trace(self, trace: ExecutionTrace) -> None:
        self.print_divider()

        failed = sum(1 for r in trace.results if r.status == NodeStatus.FAILURE)
        total_nodes = len(trace.results)

        if trace.success:
            status = "[green bold]OK  Completed[/green bold]"
        else:
            status = "[red bold]ERR Failed[/red bold]"

        console.print(
            f"{status}"
            f"  |  [cyan]{trace.total_duration}s[/cyan]"
            f"  |  [yellow]${trace.total_cost:.4f}[/yellow]"
            f"  |  {total_nodes} nodes"
            f"  |  {failed} failed"
            f"  |  tokens: {trace.total_tokens}"
        )
        console.print()

    def print_retrying_live(self, node_name: str, attempt: int, max_retries: int) -> None:
        console.print(
            f"[yellow]RETRY[/yellow] [bold]{node_name}[/bold]"
            f"  [dim]retrying ({attempt}/{max_retries})...[/dim]"
        )
