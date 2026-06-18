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
from .vab import Rocket

SIDE_NAMES = {"center": "ЦЕНТР", "left": "ЛЕВЫЙ БОК", "right": "ПРАВЫЙ БОК"}
SIDE_COLORS = {"center": "#EE82EE", "left": "#00FFFF", "right": "#FFD700"}

def show_part_selector(category, title, columns=("name", "cost")):
    avail = [
        p for p in PARTS[category]
        if (p["tech"] == "basic" or p["id"] in state.unlocked_techs)
        and (category != "utils" or p["id"] != "util_dec")
    ]
    if not avail:
        console.print("[#8B008B]Нет доступных деталей в этой категории![/#8B008B]")
        time.sleep(0.5)
        return None

    choices = []
    for p in avail:
        extra = ""
        if category == "pods":
            extra = f" | Масса: {p.get('mass',0)}т"
        elif category == "tanks":
            extra = f" | Топливо: {p.get('fuel',0)} ед | Масса: {p.get('mass_empty',0)}т"
        elif category == "engines":
            extra = f" | Тяга: {p.get('thrust_atm',0)}/{p.get('thrust_vac',0)} кН | Isp: {p.get('isp','-')}с"
        elif category == "utils":
            extra = ""
        label = f"{p['name']} - {p.get('desc','')[:60]}" if p.get('desc') else p['name']
        label += f" (¤{p['cost']:,}{extra})"
        choices.append(label)

    choices.append("[bold #FF4444]✕ ОТМЕНА[/bold #FF4444]")
    res = inquirer.prompt(
        [inquirer.List('a', message=f"Выберите {title}", choices=choices)],
        theme=custom_theme
    )
    if not res or res['a'].startswith("[bold #FF4444]"):
        return None
    idx = choices.index(res['a'])
    return avail[idx]


def render_vab_ui(rocket, msg="", combo_count=0, current_side="center"):
    layout = Layout()
    layout.split_column(Layout(name="h", size=3), Layout(name="m"))
    layout["m"].split_row(Layout(name="l", ratio=1), Layout(name="r", ratio=2))
    layout["h"].update(header())

    max_h = 15
    center_lines = []
    left_lines = []
    right_lines = []
    for stage in rocket.stages:
        for col, lines_list in [("center", center_lines), ("left", left_lines), ("right", right_lines)]:
            parts = getattr(stage, col)
            for p in parts:
                plines = p["data"]["ascii"].split("\n")
                for line in plines:
                    lines_list.append(line.center(len(line) + 4))

    max_lines = max(len(center_lines), len(left_lines), len(right_lines), 1)
    rocket_rows = []
    for i in range(max_lines):
        l = left_lines[i] if i < len(left_lines) else " " * 10
        c = center_lines[i] if i < len(center_lines) else " " * 10
        r = right_lines[i] if i < len(right_lines) else " " * 10
        row = f"[#00FFFF]{l}[/#00FFFF]  [#EE82EE]{c}[/#EE82EE]  [#FFD700]{r}[/#FFD700]"
        rocket_rows.append(row)

    ascii_rocket = "\n".join(rocket_rows[-max_h:])
    if not ascii_rocket.strip() or ascii_rocket.replace(" ", "").replace("\n", "").replace("[", "").replace("]", "").replace("/", "").replace("#", "").strip() == "":
        ascii_rocket = "  [Пустой чертеж]\n  [Выберите детали]"

    side_indicator = f"[{SIDE_COLORS[current_side]}]{'◄' if current_side == 'left' else ' '} {SIDE_NAMES[current_side]} {'►' if current_side == 'right' else ' '}[/{SIDE_COLORS[current_side]}]"

    content = f"[bold #EE82EE]{ascii_rocket}[/bold #EE82EE]\n\n[bold #DDA0DD]{side_indicator}[/bold #DDA0DD]"
    layout["l"].update(Panel(content, title="[bold #9400D3]Сборочный Цех (VAB)[/bold #9400D3]", box=box.DOUBLE_EDGE, border_style="#8A2BE2"))

    total_mass = rocket.get_total_mass()
    cost = rocket.get_cost()
    act = rocket.get_active_stage_stats()

    dv = rocket.get_delta_v_estimate()
    t = Table(show_header=False, box=None, row_styles=["none", "dim"])
    t.add_column("Параметр", style="#DA70D6")
    t.add_column("Значение", style="#EE82EE", justify="right")
    dv_color = "#00FF00" if dv > 4000 else "#FFD700" if dv > 1000 else "#FF4444"
    t.add_row("Общая Масса", f"{total_mass} т.")
    t.add_row("Ступеней", f"{len(rocket.stages)}")
    t.add_row("Δv (расчёт)", f"[{dv_color}]{dv:.0f} м/с[/{dv_color}]")
    t.add_row("Тяга (Атм/Вак)", f"{act['thrust_atm']}/{act['thrust_vac']} кН")
    t.add_row("Isp (средний)", f"{act['isp']} с")

    denom = total_mass * PLANETS[state.current_planet]["gravity"] * state.physics_multiplier
    twr = act['thrust_atm'] / denom if denom != 0 else 0
    twr_color = "#FF4444" if twr < 1.0 else ("#FFD700" if twr < 1.5 else "#00FF00")
    t.add_row("[bold]TWR (Атм)[/bold]", f"[{twr_color} bold]{twr:.2f}[/{twr_color} bold]")
    t.add_row("Стоимость", f"¤{cost:,}")

    booster_info = ""
    for i, stage in enumerate(rocket.stages):
        info = []
        if stage.left:
            info.append(f"[#00FFFF]{len(stage.left)} деталей слева[/#00FFFF]")
        if stage.right:
            info.append(f"[#FFD700]{len(stage.right)} деталей справа[/#FFD700]")
        if info:
            booster_info += f"\nСтупень {i}: {', '.join(info)}"

    discount_text = f"\n[blink bold #FF00FF]COMBO x{combo_count}! СКИДКА {combo_count*5}%[/blink bold #FF00FF]" if combo_count > 1 else ""

    r_panel = Panel(t, title=f"[bold #9400D3]Проект: {rocket.name}[/bold #9400D3]", border_style="#4B0082", box=box.ROUNDED)
    controls = (
        "[1] Ком.модуль | [2] Баки | [3] Двигатели | [4] Утилиты | [5] Разделитель\n"
        "[A] Сторона: ЦЕНТР/ЛЕВО/ПРАВО | [U] Отмена | [ENTER] Старт | [Q] Выход"
    )
    controls_panel = Panel(Align.center(Text(controls, justify="center")), style="#DA70D6", box=box.ROUNDED, title="[#FF00FF]УПРАВЛЕНИЕ[/#FF00FF]")
    msg_panel = Panel(f"{msg}{discount_text}{booster_info}", style="bold #BA55D3" if combo_count > 0 else "#DDA0DD", box=box.ROUNDED)

    right_layout = Layout()
    right_layout.split_column(
        Layout(r_panel, size=9),
        Layout(Panel(msg_panel, style="#DDA0DD", box=box.ROUNDED)),
        Layout(controls_panel, size=5)
    )
    layout["r"].update(right_layout)

    tree = Tree("[bold #FFD700]СБОРКА[/bold #FFD700]")
    for i, stage in enumerate(rocket.stages):
        lbl = f"Ступень {i} (Верх)" if i == 0 else f"Ступень {i}"
        stage_node = tree.add(f"[#EE82EE]{lbl}[/#EE82EE]")
        for side_name, side_color in [("center", "#EE82EE"), ("left", "#00FFFF"), ("right", "#FFD700")]:
            parts = getattr(stage, side_name)
            if parts:
                col_node = stage_node.add(f"[{side_color}]├ {SIDE_NAMES[side_name]}[/{side_color}]")
                for p in parts:
                    col_node.add(f"{p['data']['name']} (¤{p['data']['cost']})")

    layout["r"].split_column(
        Layout(r_panel, size=9),
        Layout(Panel(tree, border_style="#4B0082", box=box.ROUNDED)),
        Layout(msg_panel, size=4),
        Layout(controls_panel, size=5)
    )
    return layout


def vab_loop():
    rocket = Rocket(f"KSP-Mk{len(state.rockets)+1}")
    combo_count = 0
    last_action_time = time.time()
    msg = "[#DDA0DD]Добро пожаловать в VAB. Используйте кнопки.[/#DDA0DD]"
    current_side = "center"

    clear()
    with Live(render_vab_ui(rocket, msg, combo_count, current_side), refresh_per_second=30, screen=True) as live:
        while True:
            key = get_key_timeout(0.03)
            now = time.time()
            changed = False
            if now - last_action_time > 2.0:
                if combo_count > 0:
                    combo_count = 0
                    changed = True

            if key:
                key = key.lower()
                success = False

                if key == 'q':
                    break

                elif key in ('\n', '\r'):
                    cost = max(0, rocket.get_cost())
                    discount = min(50, combo_count * 5)
                    final_cost = int(cost * (1 - discount / 100.0))

                    if not rocket.get_active_stage_stats()["has_pod"]:
                        msg = "[#FF4444]Ракете нужен командный модуль![/#FF4444]"
                        changed = True
                    elif state.credits >= final_cost:
                        live.stop()
                        clear()
                        with Live(Spinner("dots", text="[#BA55D3]Перемещение на стартовый стол...[/#BA55D3]"), refresh_per_second=20, transient=True):
                            time.sleep(1.0)
                        state.credits -= final_cost
                        state.rockets.append(rocket)
                        console.print(f"[#00FF00]Ракета готова. Списано ¤{final_cost:,}[/#00FF00]")
                        input()
                        break
                    else:
                        msg = "[#FF4444]Недостаточно средств![/#FF4444]"
                        changed = True

                elif key in ('a', 'ф'):
                    sides = ["center", "left", "right"]
                    idx = sides.index(current_side)
                    current_side = sides[(idx + 1) % 3]
                    side_names_display = {"center": "ЦЕНТР", "left": "ЛЕВЫЙ БОК", "right": "ПРАВЫЙ БОК"}
                    msg = f"[#DDA0DD]Установка: {side_names_display[current_side]}[/#DDA0DD]"
                    changed = True

                elif key == '1':
                    live.stop()
                    clear()
                    sel = show_part_selector("pods", "командный модуль")
                    if sel:
                        rocket.add_part("pods", sel["id"], current_side)
                        success = True
                        msg = f"[#00FF00]Установлен: {sel['name']}[/#00FF00]"
                    else:
                        msg = "[#FFD700]Выбор отменён[/#FFD700]"
                    live.start()

                elif key == '2':
                    live.stop()
                    clear()
                    sel = show_part_selector("tanks", "топливный бак")
                    if sel:
                        rocket.add_part("tanks", sel["id"], current_side)
                        success = True
                        msg = f"[#00FF00]Установлен: {sel['name']}[/#00FF00]"
                    else:
                        msg = "[#FFD700]Выбор отменён[/#FFD700]"
                    live.start()

                elif key == '3':
                    live.stop()
                    clear()
                    sel = show_part_selector("engines", "двигатель")
                    if sel:
                        rocket.add_part("engines", sel["id"], current_side)
                        success = True
                        msg = f"[#00FF00]Установлен: {sel['name']}[/#00FF00]"
                    else:
                        msg = "[#FFD700]Выбор отменён[/#FFD700]"
                    live.start()

                elif key == '4':
                    live.stop()
                    clear()
                    sel = show_part_selector("utils", "утилиту")
                    if sel:
                        if sel["id"] == "util_dec":
                            rocket.add_part("utils", "util_dec", "center")
                        else:
                            rocket.add_part("utils", sel["id"], current_side)
                        success = True
                        msg = f"[#00FF00]Установлена: {sel['name']}[/#00FF00]"
                    else:
                        msg = "[#FFD700]Выбор отменён[/#FFD700]"
                    live.start()

                elif key == '5':
                    rocket.add_part("utils", "util_dec"); success = True
                    msg = "[#FFD700]Установлен декуплер (разделитель)![/#FFD700]"

                elif key == 'u':
                    if rocket.remove_last_part(current_side):
                        msg = "[#FFA500]Деталь удалена.[/#FFA500]"
                    else:
                        msg = "[#FF4444]Нечего удалять.[/#FF4444]"

                if success:
                    combo_count += 1
                    last_action_time = now
                    if combo_count > 1:
                        sys.stdout.write('\a')
                        sys.stdout.flush()
                changed = True

            if changed:
                live.update(render_vab_ui(rocket, msg, combo_count, current_side))
