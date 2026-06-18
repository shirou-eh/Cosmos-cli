from .config import state
from .data import PARTS, PLANETS, TECH_TREE, CONTRACTS
from .ui_core import clear, get_key_timeout, header, typewriter_print, get_bar, console, custom_theme
import inquirer
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.live import Live
from rich.tree import Tree
from rich import box
from rich.spinner import Spinner
import time
import sys


def contract_loop():
    while True:
        clear()
        console.print(Panel("[bold #EE82EE]MISSION CONTROL (ЦУП)[/bold #EE82EE]", style="#9400D3", box=box.ROUNDED))
        
        if state.active_contract:
            c = next((x for x in CONTRACTS if x["id"] == state.active_contract), None)
            if not c:
                state.active_contract = None
                continue
            t = Table(show_header=False, box=box.SIMPLE, style="#DA70D6")
            t.add_column("Поле", style="#BA55D3")
            t.add_column("Значение", style="#EE82EE")
            t.add_row("Миссия", c['name'])
            t.add_row("Брифинг", c['desc'])
            t.add_row("Аванс/Награда", f"¤{c['reward']:,}")
            t.add_row("Научные данные", f"⚛{c.get('science', 0)}")
            t.add_row("Статус", "[blink]В ПРОЦЕССЕ[/blink]")
            
            console.print(t)
            res = inquirer.prompt([inquirer.List('a', message="Опции", choices=["Отменить миссию", "Назад"])], theme=custom_theme)
            if res and res['a'] == "Отменить миссию":
                state.active_contract = None
                console.print("[#8B008B]Миссия отменена. Спонсоры недовольны.[/#8B008B]"); input()
            else:
                break
        else:
            avail = [c for c in CONTRACTS if c["id"] not in state.completed_contracts and all(p in state.completed_contracts for p in c.get("prereq", []))]
            if not avail:
                console.print("[#DA70D6]Нет доступных миссий. Ждите предложений спонсоров.[/#DA70D6]"); input(); break
                
            choices = [f"{c['name']} (Награда: ¤{c['reward']:,} | Наука: ⚛{c.get('science', 0)})" for c in avail] + ["Выход из ЦУП"]
            res = inquirer.prompt([inquirer.List('a', message="Доступные миссии", choices=choices)], theme=custom_theme)
            if not res or res['a'] == "Выход из ЦУП": break
            
            c = avail[choices.index(res['a'])]
            state.active_contract = c["id"]
            console.print(f"[#EE82EE]Миссия '{c['name']}' принята! Спонсоры ожидают результатов.[/#EE82EE]"); input()

