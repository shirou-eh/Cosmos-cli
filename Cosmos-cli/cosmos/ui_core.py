import os
import sys
import time
import random
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.live import Live
from rich.tree import Tree
from rich import box
from rich.spinner import Spinner
from rich.padding import Padding

console = Console()
from inquirer.themes import load_theme_from_dict

custom_theme = load_theme_from_dict({
    "Question": {
        "mark_color": "magenta",
        "brackets_color": "magenta",
    },
    "List": {
        "selection_color": "black_on_magenta",
        "selection_cursor": ">"
    }
})


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_key_timeout(timeout=0.1):
    if os.name == 'nt':
        try:
            import msvcrt
            end = time.time() + timeout
            while time.time() < end:
                if msvcrt.kbhit():
                    return msvcrt.getch().decode('utf-8', errors='replace')
                time.sleep(0.01)
        except ImportError:
            try:
                import msvcrt
            except ImportError:
                return None
        return None
    else:
        import select
        import tty
        import termios
        fd = sys.stdin.fileno()
        try:
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(sys.stdin.fileno())
                r, w, e = select.select([sys.stdin], [], [], timeout)
                if r:
                    return sys.stdin.read(1)
            except Exception:
                pass
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception:
            pass
        return None

def header():
    logo = "[bold #FF00FF]░█░█░█▀█░█▀▄░█▀▀░█▀█░█░█░███░░░█▀▀░█▀█░█░█░░░█▀▄░█▀█░█▀█░█▀█░█▀▄[/bold #FF00FF]\n[bold #DA70D6]░█▄█░█▀█░█▀▄░█░░░█▀▀░█▄█░░░█░░░░▀▀█░█▀█░█░█░░░█▀▄░█░█░█▀▀░█▀▀░█▀▄[/bold #DA70D6]\n[bold #9400D3]░▀░▀░▀░▀░▀░▀░▀▀▀░▀░░░▀░▀░░░▀░░░░▀▀▀░▀░▀░▀▀▀░░░▀▀░░▀▀▀░▀░░░▀▀▀░▀░▀[/bold #9400D3]"
    return Panel(Align.center(Text.from_ansi(logo, justify="center")), style="#4B0082", border_style="#8A2BE2", box=box.HEAVY)

def typewriter_print(text, style="bold #DA70D6", delay=0.015):
    current = ""
    with Live(refresh_per_second=30, transient=True) as live:
        for char in text:
            current += char
            live.update(Text(current, style=style))
            time.sleep(delay + random.uniform(0, 0.01))
    console.print(Text(text, style=style))

def get_bar(value, max_value, length=30):
    pct = min(1.0, max(0.0, value / max_value)) if max_value > 0 else 0
    filled = int(pct * length)
    empty = length - filled

    if pct < 0.3:
        color = "#FF4444"
    elif pct < 0.6:
        color = "#FFD700"
    else:
        color = "#00FF00"

    return f"[{color}]" + "█" * filled + "[/]" + "[dim #4B0082]░[/]" * empty
