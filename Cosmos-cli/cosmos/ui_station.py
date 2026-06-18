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


def station_loop():
    while True:
        clear()
        console.print(Panel("[bold #DDA0DD]Космическая Станция 'Void-Альфа'[/bold #DDA0DD]\nТут полно инженеров Корпорации.", style="#9932CC", box=box.HEAVY))
        choices = ["Поговорить с Инженером", "Сдать образцы грунта (Минералы)", "Отстыковаться"]
        res = inquirer.prompt([inquirer.List('a', message="Станция", choices=choices)], theme=custom_theme)
        if res is None: break
        act = res['a']
        
        if act == "Поговорить с Инженером":
            typewriter_print("Инженер: Эй, Архитектор просил передать, чтобы ты добавил больше бустеров.", style="#BA55D3")
            input()
        elif act == "Сдать образцы грунта (Минералы)":
            if state.minerals > 0:
                profit = state.minerals * 1500
                typewriter_print(f"Научный сотрудник: Отличные образцы! Перевожу ¤{profit:,} на ваш счет.", style="#EE82EE")
                state.credits += profit
                state.minerals = 0
            else:
                typewriter_print("Научный сотрудник: У вас нет образцов. Возвращайтесь, когда соберете грунт.", style="#DA70D6")
            input()
        elif act == "Отстыковаться":
            break

