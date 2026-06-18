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
import random


def tech_loop():
    while True:
        clear()
        console.print(Panel(f"[bold #EE82EE]Центр Исследований и Разработок (R&D)[/bold #EE82EE]\nДоступно науки: [bold #BA55D3]⚛{state.science}[/bold #BA55D3]", style="#9400D3", box=box.HEAVY))
        
        # Определяем текущую ветку и строим визуальное дерево
        TIERS = ["tier1", "tier2", "tier3", "tier4", "tier5"]
        current_tier = None
        unlocked_count = 0
        total_in_tier = 0
        
        tree_vis = ["[#00FF00]◉ Базовые Технологии[/#00FF00]"]
        for t in TIERS:
            parts_t = []
            for cat in PARTS.values():
                for p in cat:
                    if p["tech"] == t:
                        parts_t.append(p)
            unlocked_t = len([p for p in parts_t if p["id"] in state.unlocked_techs])
            tot_t = len(parts_t)
            
            if unlocked_t == tot_t and tot_t > 0:
                tree_vis.append(f" ┃\n[#00FF00]◉ {TECH_TREE[t]['name']}[/#00FF00]")
            elif unlocked_t < tot_t and current_tier is None:
                current_tier = t
                unlocked_count = unlocked_t
                total_in_tier = tot_t
                tree_vis.append(f" ┃\n[blink #FFA500]◎ {TECH_TREE[t]['name']} (Текущая цель: {unlocked_t}/{tot_t})[/blink #FFA500]")
            else:
                tree_vis.append(f" ┃\n[#808080]○ {TECH_TREE[t]['name']}[/#808080]")
        
        console.print(Panel("\n".join(tree_vis), title="[bold #00FFFF]Дерево Технологий[/bold #00FFFF]", style="#008080", box=box.ROUNDED))
                
        if not current_tier:
            console.print("[#EE82EE]Дерево технологий полностью изучено![/#EE82EE]"); input(); break
            
        t_data = TECH_TREE[current_tier]
        cost = t_data["cost"]
        
        console.print(f"[#DA70D6]Текущая цель исследований: {t_data['name']}[/#DA70D6]")
        console.print(f"[dim]Открыто деталей: {unlocked_count} / {total_in_tier}[/dim]\n")
        
        choices = [f"Инвестировать в исследования (⚛{cost})", "Назад"]
        res = inquirer.prompt([inquirer.List('a', message="R&D Опции", choices=choices)], theme=custom_theme)
        if not res or res['a'] == "Назад": break
        
        if res['a'].startswith("Инвестировать"):
            if state.science >= cost:
                state.science -= cost
                with Live(refresh_per_second=20, transient=True) as live:
                    for _ in range(30):
                        chars = "".join([chr(random.randint(33, 126)) for _ in range(40)])
                        live.update(Panel(f"[bold #BA55D3]{chars}[/bold #BA55D3]", title="[blink]ВЫЧИСЛЕНИЯ...[/blink]", box=box.HEAVY, border_style="#8A2BE2"))
                        time.sleep(0.05)
                
                parts_in_tier = []
                for cat in PARTS.values():
                    for p in cat:
                        if p["tech"] == current_tier and p["id"] not in state.unlocked_techs:
                            parts_in_tier.append(p)
                
                if parts_in_tier:
                    for p in parts_in_tier:
                        state.unlocked_techs.append(p["id"])
                    sys.stdout.write('\a'); sys.stdout.flush()
                    console.print(Panel(f"[blink bold #EE82EE]ИССЛЕДОВАНИЯ ЗАВЕРШЕНЫ![/blink bold #EE82EE]\n[white]Открыта ветка: {t_data['name']}[/white]\n[dim]Все детали ветки разблокированы[/dim]", box=box.HEAVY, border_style="#DA70D6"))
                else:
                    console.print("[#8B008B]Сбой системы. Детали не найдены.[/#8B008B]")
                input()
            else:
                console.print("[#8B008B]Недостаточно очков науки![/#8B008B]"); input()

