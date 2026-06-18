import typer
import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box

from .config import state
from .ui_core import clear, get_key_timeout, header, typewriter_print, get_bar, console, custom_theme
from .ui_vab import vab_loop
from .ui_station import station_loop
from .ui_tech import tech_loop
from .ui_contracts import contract_loop
from .ui_flight import flight_loop
from rich.layout import Layout
import time
from .data import PLANETS, CONTRACTS

app = typer.Typer()
def render_main():
    clear()
    layout = Layout()
    layout.split_column(Layout(name="h", size=3), Layout(name="m"))
    layout["h"].update(header())
    
    diff_name = {1: "Легкий", 2: "Нормальный", 3: "Реалистичный"}[state.difficulty]
    bases = ", ".join([PLANETS[p]["name"] for p, exists in state.colonies.items() if exists]) or "Нет"
    
    contract_str = "Нет активных миссий"
    if state.active_contract:
        c = next((x for x in CONTRACTS if x["id"] == state.active_contract), None)
        if c:
            contract_str = f"[#EE82EE]{c['name']}[/#EE82EE]"
    
    content = f"""
    [bold #DA70D6]Бюджет (Спонсоры):[/bold #DA70D6] ¤{state.credits:,}
    [bold #DA70D6]Наука (R&D):[/bold #DA70D6] ⚛{state.science}
    [bold #DA70D6]Минералы (Образцы):[/bold #DA70D6] ⚒{state.minerals}
    [bold #DA70D6]Текущая миссия:[/bold #DA70D6] {contract_str}
    
    [bold #DA70D6]Поселения (Базы):[/bold #DA70D6] {bases}
    [bold #DA70D6]Аппаратов на старте:[/bold #DA70D6] {len(state.rockets)}
    [bold #DA70D6]Текущая локация:[/bold #DA70D6] {PLANETS[state.current_planet]['name']}
    
    [bold #9932CC]Уровень симуляции:[/bold #9932CC] {diff_name}
    
    Добро пожаловать в Космический Центр.
    Стройте многоступенчатые аппараты, исследуйте технологии
    и не забывайте про парашюты для ваших пилотов.
    """
    layout["m"].update(Panel(content, title="[bold #9400D3]Космический Центр VoidCorp[/bold #9400D3]", border_style="#8A2BE2", box=box.HEAVY))
    console.print(layout, height=18)
    
    controls = "[VAB] Сборочный Цех | [LAUNCHPAD] Запуск | [R&D] Наука | [MISSION CONTROL] Миссии | [Q] Выход"
    console.print(Panel(Align.center(Text(controls)), style="#BA55D3", box=box.ROUNDED))

def play_prologue():
    clear()
    console.print(Panel(Align.center(Text("КОСМИЧЕСКАЯ ПРОГРАММА VOIDCORP\nВам доверено руководить космическим центром. Исследуйте систему!", style="bold #EE82EE")), style="black on #4B0082", box=box.HEAVY))
    time.sleep(2)
    clear()
    
    typewriter_print("Главный Архитектор: Приветствую! Ты наш новый Директор полетов?", style="bold #DA70D6")
    time.sleep(0.5)
    res = inquirer.prompt([inquirer.List('a', message="Твой ответ", choices=["Кто вы такой?", "Я готов строить ракеты. Введите в курс дела.", "[Молча кивнуть]"])], theme=custom_theme)
    if res is None: return
    
    print()
    typewriter_print("Главный Архитектор: Твоя задача — собирать ракеты с нуля в Сборочном Цехе (VAB).", style="bold #DA70D6")
    time.sleep(0.5)
    typewriter_print("Главный Архитектор: Сначала ставь Капсулу. Потом Разделитель (Декуплер). Потом баки и двигатели.", style="bold #DA70D6")
    time.sleep(0.5)
    typewriter_print("Главный Архитектор: В полете жми [Z] для старта, и [SPACE] для стейджинга!", style="bold #DA70D6")
    time.sleep(0.5)
    
    res = inquirer.prompt([inquirer.List('a', message="Твой ответ", choices=["Понял, приступим.", "Звучит опасно, но я справлюсь."])], theme=custom_theme)
    if res is None: return
    
    print()
    typewriter_print("Главный Архитектор: Отлично. Зайди в Mission Control и возьми контракт на первый прыжок. Удачи.", style="bold #DA70D6")
    time.sleep(1)
    
    state.has_seen_tutorial = True
    state.save_game()

def start():
    clear()
    console.print(Panel(Align.center(Text("VOIDCORP TERMINAL", style="bold #EE82EE")), style="#9932CC", box=box.HEAVY))
    profiles = state.get_all_profiles()
    
    choices = ["[Создать новую космическую программу]"] + profiles
    res = inquirer.prompt([inquirer.List('p', message="Выберите сохранение", choices=choices)], theme=custom_theme)
    if not res: return
    
    if res['p'] == "[Создать новую космическую программу]":
        name_res = inquirer.prompt([inquirer.Text('n', message="Название программы (без пробелов)")], theme=custom_theme)
        if not name_res or not name_res['n']: return
        profile = name_res['n'].strip()
        state.profile_name = profile
    else:
        profile = res['p']
        state.load_game(profile)
        
    if not state.has_seen_tutorial:
        play_prologue()
        
    while True:
        render_main()
        key = get_key_timeout(0.3)
        if key:
            key = key.lower()
            if key == 'q': break
            elif key in ('v', 'м'): vab_loop(); continue
            elif key in ('l', 'д'): flight_loop(); continue
            elif key in ('m', 'ь'): contract_loop(); continue
            elif key in ('r', 'к'): tech_loop(); continue
            elif key in ('s', 'ы'): 
                if state.save_game():
                    console.print(f"[#EE82EE]Сохранение '{state.profile_name}' успешно![/#EE82EE]"); input()
                else:
                    console.print("[#8B008B]Ошибка сохранения.[/#8B008B]"); input()
                continue
        
        choices = [
            "[V] Сборочный Цех (VAB)", 
            "[L] Стартовая площадка (Launchpad)", 
            "[M] Mission Control (Миссии)",
            "[R] Центр Исследований (R&D)",
            "Настройки (Сложность)", 
            "[S] Сохранить Игру", 
            "[Q] Покинуть Космический Центр"
        ]
        res = inquirer.prompt([inquirer.List('a', message="Команда терминала", choices=choices)], theme=custom_theme)
        if res is None: break
        act = res['a']
        
        if act.startswith("[Q]"): break
        elif act.startswith("[V]"): vab_loop()
        elif act.startswith("[L]"): flight_loop()
        elif act.startswith("[M]"): contract_loop()
        elif act.startswith("[R]"): tech_loop()
        elif act.startswith("[S]"):
            if state.save_game():
                console.print(f"[#EE82EE]Сохранение '{state.profile_name}' успешно![/#EE82EE]"); input()
            else:
                console.print("[#8B008B]Ошибка сохранения.[/#8B008B]"); input()
        else:
            opts = ["1 (Легко)", "2 (Норма)", "3 (Реализм)"]
            sel = inquirer.prompt([inquirer.List('d', message="Сложность", choices=opts)], theme=custom_theme)
            if sel: state.set_difficulty(int(sel['d'][0]))
