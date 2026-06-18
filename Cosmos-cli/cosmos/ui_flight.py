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
from rich.padding import Padding
import time
import sys
from .flight import FlightSession
from .events import check_random_event
import random
from .ui_station import station_loop

def flight_loop():
    if not state.rockets:
        console.print("[#8B008B]На стартовом столе пусто! Соберите ракету в VAB.[/#8B008B]"); input(); return
        
    rocket = state.rockets.pop()
    flight = FlightSession(rocket, state.current_planet)
    flight.add_log("SAS включен. Системы онлайн. >>> НАЖМИТЕ 'Z' ДЛЯ ЗАПУСКА <<<")
    
    layout = Layout()
    layout.split_column(Layout(name="h", size=3), Layout(name="m", size=15), Layout(name="f", size=3))
    layout["m"].split_row(Layout(name="l", ratio=1), Layout(name="r", ratio=2))
    layout["r"].split_column(Layout(name="rt"), Layout(name="rb", size=6))
    layout["h"].update(header())
    
    overdrive_active = False
    meltdown_timer = 0
    active_reload_window = False
    perfect_stage_boost = False
    base_thrust_atm = flight.thrust_atm
    base_thrust_vac = flight.thrust_vac
    
    def update_flight_ui():
        if flight.rocket.stages:
            active_stage_obj = flight.rocket.stages[-1]
        else:
            active_stage_obj = None

        ascii_lines = []
        s_colors = {"center": "#EE82EE", "left": "#00FFFF", "right": "#FFD700"}
        if not active_stage_obj or not active_stage_obj.has_any_parts():
            ascii_lines.append("  [Декуплер сработал]  ")
        else:
            max_h = 0
            col_parts = {}
            for side in ["left", "center", "right"]:
                col_parts[side] = getattr(active_stage_obj, side, [])
            max_h = max(len(col_parts["left"]), len(col_parts["center"]), len(col_parts["right"]))

            for i in range(max_h):
                row_parts = []
                for side in ["left", "center", "right"]:
                    if i < len(col_parts[side]):
                        p = col_parts[side][i]
                        lines = p["data"]["ascii"].split("\n")
                        for j, line in enumerate(lines):
                            idx = i + j
                            while len(row_parts) <= idx:
                                row_parts.append({"left": "", "center": "", "right": ""})
                            row_parts[idx][side] = line
                    elif i == 0 and side == "left":
                        pass
                # Alternative simpler display: just show center with side indicators
            # Simpler approach: show center column rockets, with [L]/[R] markers
            for i, p in enumerate(col_parts["center"]):
                lines = p["data"]["ascii"].split("\n")
                l_mark = f"[#00FFFF]<[/#00FFFF]" if i < len(col_parts["left"]) else " "
                r_mark = f"[#FFD700]>[/#FFD700]" if i < len(col_parts["right"]) else " "
                for line in lines:
                    ascii_lines.append(f"{l_mark} {line.center(20)} {r_mark}")

        if flight.state in ["FLIGHT", "ORBIT", "PRE-LAUNCH"] and flight.throttle > 0:
            flame_color1 = "#EE82EE"
            flame_color2 = "#DA70D6"
            flame_color3 = "#FFD700"
            flame_color4 = "#FF6600"
            flame_color5 = "#FF4444"
            if flight.throttle > 100:
                ascii_lines.extend([
                    f"[blink bold {flame_color5}]       ║  ║  ║       [/]",
                    f"[blink bold {flame_color4}]      ║  ║║║  ║      [/]",
                    f"[blink bold {flame_color3}]     ║  ║║║║║  ║     [/]",
                    f"[blink bold {flame_color2}]    ║  ║║║║║║║  ║    [/]",
                    f"[blink bold {flame_color1}]   ║  ║║║║║║║║║  ║   [/]",
                    f"[blink bold white]  █║║║║║║║║║║║║║║║║║█ [/]",
                ])
            elif flight.throttle >= 80:
                ascii_lines.extend([
                    f"[bold {flame_color3}]       ║  ║  ║       [/]",
                    f"[bold {flame_color2}]      ║  ║║║  ║      [/]",
                    f"[bold {flame_color1}]     ║  ║║║║║  ║     [/]",
                    f"[bold white]    ║║║║║║║║║║║    [/]",
                    f"[bold {flame_color5}]   █║║║║║║║║║║║█   [/]",
                ])
            elif flight.throttle >= 40:
                ascii_lines.extend([
                    f"[bold {flame_color2}]      ║  ║  ║      [/]",
                    f"[bold {flame_color1}]     ║  ║║║  ║     [/]",
                    f"[bold white]    ║║║║║║║║║    [/]",
                ])
            else:
                ascii_lines.extend([
                    f"[bold {flame_color1}]       ║  ║       [/]",
                    f"[bold white]      ║║║║║      [/]",
                ])

        rocket_view = "\n".join(ascii_lines[-18:])
        
        atm = flight.planet["atmosphere"]
        target_alt = atm * 1.5 if atm > 0 else 100_000
        bar = get_bar(flight.altitude, target_alt, 30)
        
        if flight.state == "ORBIT":
            scale = f"[{flight.planet['name']}] [bold #EE82EE]Орбита (Апоапсис стабилен)[/bold #EE82EE]"
        else:
            scale = f"[{flight.planet['name']}] {bar} [Космос]"
            
        shake_pad = (0, 0, 0, random.randint(0, 3)) if flight.throttle > 80 and flight.altitude < flight.planet['atmosphere'] else (0,0,0,0)
        
        l_panel = Padding(Panel(f"{rocket_view}\n\n[bold #DA70D6]Альтиметр:[/bold #DA70D6] {scale}\n[bold]Статус:[/bold] [blink]{flight.state}[/blink]", title=f"[bold #9400D3]Камера: {flight.planet['name']}[/bold #9400D3]", border_style="#9932CC", box=box.HEAVY), shake_pad)
        layout["l"].update(l_panel)
        
        t = Table(show_header=False, box=None, row_styles=["none", "dim"])
        t.add_column("T", style="#DA70D6")
        t.add_column("V", style="#EE82EE", justify="right")
        
        alt_str = f"{flight.altitude:.1f} м" if flight.altitude < 10000 else f"{flight.altitude/1000:.2f} км"
        t.add_row("Высота", alt_str)
        t.add_row("Скорость (NavBall)", f"{flight.velocity:.1f} м/с")
        
        max_fuel_for_stage = sum([p["data"]["fuel"] for p in active_stage_obj.all_parts() if p["category"] == "tanks"]) if active_stage_obj and active_stage_obj.has_any_parts() else 1
        if max_fuel_for_stage == 0: max_fuel_for_stage = 1
        fuel_bar = get_bar(flight.fuel, max_fuel_for_stage, 15)
        fuel_pct = flight.fuel / max_fuel_for_stage
        
        nonlocal active_reload_window
        if fuel_pct > 0 and fuel_pct < 0.05 and flight.throttle > 0:
            active_reload_window = True
            t.add_row("Топливо", f"[blink bold #8B008B]КРИТИЧЕСКИ МАЛО![/blink bold #8B008B] {fuel_bar}")
        else:
            active_reload_window = False
            t.add_row("Топливо", f"{flight.fuel:.1f} ед. {fuel_bar}")
            
        t.add_row("Тангаж (Pitch)", f"{flight.pitch}°")
        t.add_row("Тяга", f"[bold {'#8B008B' if flight.throttle > 100 else 'white'}]{flight.throttle}%[/]")
        t.add_row("Остаток ступеней", f"{len(flight.rocket.stages)}")
        
        mass = flight.rocket.get_total_mass()
        gravity = flight.planet["gravity"] * state.physics_multiplier
        atm_factor = max(0, 1 - (flight.altitude / flight.planet["atmosphere"])) if flight.planet["atmosphere"] > 0 else 0
        current_max_thrust = (flight.thrust_atm * atm_factor) + (flight.thrust_vac * (1 - atm_factor))
        if perfect_stage_boost:
            current_max_thrust *= 1.5
        denom = mass * gravity
        twr = current_max_thrust / denom if denom != 0 else 0
        twr_color = "#8B008B" if twr < 1.0 else "#EE82EE"
        
        t.add_row("TWR", f"[{twr_color}]{twr:.2f}[/{twr_color}]")
        t.add_row("Time Warp", f"x{flight.time_warp}")
        
        if perfect_stage_boost:
            t.add_row("БАФФ", "[blink bold #EE82EE]ИДЕАЛЬНЫЙ СТЕЙДЖИНГ (+50% ТЯГИ)[/blink bold #EE82EE]")
            
        if overdrive_active:
            t.add_row("[blink bold #8B008B]КРАКЕН АТАКУЕТ (ПЕРЕГРУЗКА)[/blink bold #8B008B]", f"[blink bold #8B008B]{meltdown_timer:.1f} сек[/blink bold #8B008B]")
        
        layout["rt"].update(Panel(t, title=f"[bold #9400D3]Телеметрия: {flight.planet['name']}[/bold #9400D3]", border_style="#4B0082", box=box.ROUNDED))
        
        logs = "\n".join(flight.logs[-8:])
        layout["rb"].update(Panel(f"[bold #DA70D6]Журнал событий:[/bold #DA70D6]\n{logs}", border_style="#DDA0DD", box=box.ROUNDED))
        
        controls = "[W/S] Тангаж | [R/F] Тяга +/- | [Z/X] Тяга MAX/MIN | [Space] Стейджинг | [P] Парашют | [</>] TimeWarp | [M] Компьютер | [Q] Эвакуация"
        layout["f"].update(Panel(Align.center(Text(controls, justify="center")), title="[bold #BA55D3]ПАНЕЛЬ УПРАВЛЕНИЯ[/bold #BA55D3]", style="#EE82EE", box=box.ROUNDED))
        return layout

    with Live(update_flight_ui(), refresh_per_second=30, screen=True) as live:
        last_tick_time = time.time()
        while flight.state not in ["CRASHED"]:
            now = time.time()
            dt = now - last_tick_time
            last_tick_time = now
            
            key = get_key_timeout(0.03)
            
            if key:
                key = key.lower()
                if key in ['q', 'й']:
                    if flight.state in ["PRE-LAUNCH", "LANDED"]:
                        state.rockets.append(rocket)
                    break
                elif key in ['w', 'ц']: flight.pitch = min(90, flight.pitch + 5)
                elif key in ['s', 'ы']: flight.pitch = max(0, flight.pitch - 5)
                elif key in ['r', 'к']: 
                    flight.throttle = min(100, flight.throttle + 10)
                    if flight.state == "PRE-LAUNCH" and flight.throttle > 0:
                        flight.state = "FLIGHT"
                        flight.add_log("ЗАЖИГАНИЕ!", "ALERT")
                elif key in ['f', 'а']: 
                    flight.throttle = max(0, flight.throttle - 10)
                    if flight.throttle <= 100: overdrive_active = False
                elif key in ['z', 'я']:
                    if flight.state == "PRE-LAUNCH":
                        flight.state = "FLIGHT"
                        flight.add_log("ЗАЖИГАНИЕ!", "ALERT")
                    flight.throttle = 100
                    overdrive_active = False
                elif key in ['x', 'ч']: 
                    flight.throttle = 0
                    overdrive_active = False
                elif key == 'o' or key == 'щ':
                    if flight.state in ["FLIGHT", "ORBIT"]:
                        flight.throttle = 150
                        overdrive_active = True
                        meltdown_timer = random.uniform(3.0, 7.0)
                        flight.add_log("OVERDRIVE АКТИВИРОВАН! ВНИМАНИЕ!", "ALERT")
                elif key == ' ':
                    if flight.state in ["FLIGHT", "ORBIT"]: 
                        flight.do_stage()
                        if active_reload_window:
                            perfect_stage_boost = True
                            boost_msg = "ИДЕАЛЬНЫЙ СТЕЙДЖИНГ! ТЯГА УСИЛЕНА НА 50%!"
                            if base_thrust_atm is not None:
                                flight.thrust_atm = base_thrust_atm * 1.5
                                flight.thrust_vac = base_thrust_vac * 1.5
                            flight.add_log(boost_msg, "SUCCESS")
                        else:
                            perfect_stage_boost = False
                elif key in ['p', 'з']: flight.deploy_parachute()
                elif key in ['>', '.', 'ю']: flight.time_warp = min(1000, flight.time_warp * 2)
                elif key in ['<', ',', 'б']: flight.time_warp = max(1, flight.time_warp / 2)
                elif key in ['m', 'ь'] and flight.state in ["ORBIT", "LANDED"]:
                    live.stop()
                    clear()
                    choices = ["Продолжить полет"]
                    if flight.state == "ORBIT":
                        if flight.has_scanner: choices.append("Орбитальный Скан (EVA)")
                        for p in PLANETS.keys():
                            if p != flight.planet_id:
                                choices.append(f"Маневр перехвата: {PLANETS[p]['name']}")
                        if flight.planet.get("is_station"):
                            choices.append("Стыковка (Rendezvous)")
                    elif flight.state == "LANDED":
                        choices.append("Вернуться в Космический Центр (Recover)")
                        if flight.has_drill: choices.append("Сбор образцов грунта")
                        if flight.has_base and not state.colonies.get(flight.planet_id, False):
                            choices.append("Развернуть Базу (Colony)")
                    
                    res = inquirer.prompt([inquirer.List('a', message="Бортовой Компьютер", choices=choices)], theme=custom_theme)
                    if not res: 
                        last_tick_time = time.time()
                        live.start()
                        continue
                    act = res['a']
                    
                    if act == "Стыковка (Rendezvous)":
                        flight.state = "DOCKED"
                        station_loop()
                        break
                    elif act == "Орбитальный Скан (EVA)":
                        flight.add_log(f"Собраны научные данные. Минералов: {flight.planet['minerals']} kt.", "SUCCESS")
                        state.science += 25
                    elif act.startswith("Маневр перехвата:"):
                        dest_name = act.split(": ")[-1]
                        dest_id = next((k for k, v in PLANETS.items() if v["name"] == dest_name), None)
                        if dest_id:
                            flight.change_planet(dest_id)
                        else:
                            flight.add_log(f"Планета {dest_name} не найдена в навигационной базе!", "ALERT")
                    elif act == "Сбор образцов грунта":
                        flight.add_log("Добыто +100 минералов", "SUCCESS")
                        state.minerals += 100
                    elif act == "Развернуть Базу (Colony)":
                        state.colonies[flight.planet_id] = True
                        flight.add_log("База успешно развернута!", "SUCCESS")
                        state.science += 500
                    elif act == "Вернуться в Космический Центр (Recover)":
                        if flight.planet_id == "Terra":
                            state.credits += rocket.get_cost() * 0.5
                            flight.add_log("Аппарат успешно возвращен (Recovered).", "SUCCESS")
                        else:
                            flight.add_log("Аппарат оставлен на поверхности (Debris).", "SUCCESS")
                        break
                    
                    last_tick_time = time.time()
                    live.start()

            if overdrive_active:
                meltdown_timer -= dt * flight.time_warp
                if meltdown_timer <= 0:
                    flight.state = "CRASHED"
                    flight.add_log("ДВИГАТЕЛЬ ВЗОРВАЛСЯ ОТ ПЕРЕГРЕВА! КРАКЕН ПОБЕДИЛ!", "ALERT")

            if flight.state in ["FLIGHT", "ORBIT"]:
                check_random_event(flight)
                flight.tick(dt * flight.time_warp)
                
            if state.active_contract:
                c = next((x for x in CONTRACTS if x["id"] == state.active_contract), None)
                if c:
                    done = False
                    if "target_alt" in c and flight.altitude >= c["target_alt"] and (c["target_planet"] == flight.planet_id or c["target_planet"] == "Any"):
                        done = True
                    if "target_state" in c and flight.state == c["target_state"] and (c["target_planet"] == flight.planet_id or c["target_planet"] == "Any"):
                        done = True
                    if c.get("target_state") == "HEAVY" and c["target_planet"] == flight.planet_id:
                        if flight.rocket.get_total_mass() > 30:
                            done = True
                    if c.get("target_state") == "COLONIZED" and state.colonies.get(c["target_planet"]):
                        done = True
                    if c.get("target_state") == "ESCAPE":
                        g0 = flight.planet["gravity"] * state.physics_multiplier
                        v_esc = (2 * g0 * (600000.0**2) / (600000.0 + flight.altitude)) ** 0.5
                        if flight.velocity > v_esc * 1.1:
                            done = True
                    if done:
                        sci_reward = c.get("science", 50)
                        state.credits += c["reward"]
                        state.science += sci_reward
                        state.completed_contracts.append(c["id"])
                        flight.add_log(f"МИССИЯ ВЫПОЛНЕНА: {c['name']} (+¤{c['reward']:,}, +⚛{sci_reward})", "SUCCESS")
                        state.active_contract = None
                
            live.update(update_flight_ui())
            
    if flight.state == "CRASHED":
        clear()
        skull = """[bold black on #8B008B]
       .ed"""" """"bec.       
     -"           ^""`$      
   ."     ...      ... "     
  /      *  *      *  * \\    
 J      "    "    "    " L   
 |       .ed""   ""bec.  |   
 |      $$$$$   $$$$$    |   
 J       *$$$   $$$$*    F   
  \\       `""   ""`     /    
   *.    [:::: :::::]  .*    
     "-...```   ```...-"     
[/bold black on #8B008B]"""
        console.print(Align.center(skull))
        console.print(Align.center("[bold black on #8B008B] АППАРАТ УНИЧТОЖЕН. МИССИЯ ПРОВАЛЕНА. КОРПОРАЦИЯ НЕСЕТ УБЫТКИ. [/bold black on #8B008B]"))
        input()
    else:
        console.print("[bold #EE82EE]Связь с ЦУП завершена.[/bold #EE82EE]"); input()

