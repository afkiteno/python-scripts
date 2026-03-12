import requests
from rich.console import Console
from rich.table import Table

def unc_east_coast():
    console = Console()
    try:
        response = requests.get("https://uncletopia.com/api/servers/state", timeout=10)
        servers = response.json().get('servers', [])
        servers = sorted(servers, key=lambda s: s.get('players', 0), reverse=True)

        table = Table(style="bold magenta")
        
        table.add_column("Server Name", style="cyan", no_wrap=True)
        table.add_column("Players", justify="center")
        table.add_column("Map", style="yellow")

        for s in servers:
            full_name = s.get('name', '')
            if any(city in full_name for city in ["Chicago", "New York"]):
                parts = full_name.split(" | ")
                
                try:
                    brand = parts[0]
                    city  = f"{parts[1]:<13}"
                    num   = f"{parts[2]:^1}"
                    tags  = f"{parts[3]:<10}"
                    clean_name = f"{brand} | {city} | {num} | {tags}"
                except IndexError:
                    clean_name = full_name

                p_now = s.get('players', 0)
                p_max = s.get('max_players', 24)
                p_count = f"{p_now:>2}/{p_max:<2}"
                
                color = "[red]" if p_now >= p_max else "[green]"
                table.add_row(clean_name, f"{color}{p_count}[/]", s.get('map'))

        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")

if __name__ == "__main__":
    unc_east_coast()