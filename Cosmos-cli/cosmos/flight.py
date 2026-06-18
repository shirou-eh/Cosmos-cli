from .data import PLANETS, PARTS
from .config import state
import math
import random

class FlightSession:
    @property
    def altitude(self):
        return math.hypot(getattr(self, 'pos_x', 0), getattr(self, 'pos_y', 600000.0)) - 600000.0
        
    @altitude.setter
    def altitude(self, value):
        r = math.hypot(getattr(self, 'pos_x', 0), getattr(self, 'pos_y', 600000.0))
        if r == 0:
            self.pos_x = 0.0
            self.pos_y = 600000.0 + value
        else:
            scale = (600000.0 + value) / r
            self.pos_x *= scale
            self.pos_y *= scale

    @property
    def velocity(self):
        return math.hypot(getattr(self, 'vel_x', 0), getattr(self, 'vel_y', 0))

    @velocity.setter
    def velocity(self, value):
        if value == 0:
            self.vel_x = 0.0
            self.vel_y = 0.0

    @property
    def vertical_speed(self):
        r = math.hypot(getattr(self, 'pos_x', 0), getattr(self, 'pos_y', 600000.0))
        if r == 0: return 0.0
        return (getattr(self, 'pos_x', 0) * getattr(self, 'vel_x', 0) + getattr(self, 'pos_y', 600000.0) * getattr(self, 'vel_y', 0)) / r

    def __init__(self, rocket, origin_planet="Terra"):
        self.rocket = rocket
        self.planet_id = origin_planet
        self.planet = PLANETS[self.planet_id]
        
        self.pos_x = 0.0
        self.pos_y = 600000.0
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.accumulator = 0.0
        self.periapsis = 0.0
        
        self.update_active_stats()
        
        self.altitude = 0.0
        self.velocity = 0.0
        self.apoapsis = 0.0
        self.pitch = 90.0
        self.throttle = 0.0
        self.time_warp = 1
        self.parachute_deployed = False
        
        self.state = "PRE-LAUNCH"
        self.logs = []
        
    def update_active_stats(self):
        stats = self.rocket.get_active_stage_stats()
        self.fuel = stats["fuel"]
        self.thrust_atm = stats["thrust_atm"]
        self.thrust_vac = stats["thrust_vac"]
        self.isp = stats["isp"]
        self.has_parachute = stats["has_parachute"]
        self.has_drill = stats["has_drill"]
        self.has_base = stats["has_base"]
        self.has_scanner = stats.get("has_scanner", False)
        
    def add_log(self, msg, type="INFO"):
        color = "#8A2BE2" if type == "INFO" else "red" if type == "ALERT" else "green"
        self.logs.append(f"[{color}][{type}][/{color}] {msg}")
        if len(self.logs) > 10:
            self.logs.pop(0)

    def lose_fuel(self, amount):
        self.fuel -= amount
        if self.fuel < 0:
            self.fuel = 0
        self._sync_fuel()

    def add_pitch_wobble(self, amount):
        self.pitch += random.uniform(-amount, amount)

    def deploy_parachute(self):
        if self.has_parachute and self.altitude < self.planet["atmosphere"]:
            if self.vertical_speed < 0:
                self.parachute_deployed = True
                self.add_log("Парашюты успешно раскрыты!", "SUCCESS")
        else:
            self.add_log("Невозможно выпустить парашюты (атмосфера/скорость)!", "ALERT")

    def do_stage(self):
        if self.rocket.stage():
            self.add_log("Ступень отстрелена! Двигатели следующей ступени готовы.", "ALERT")
            self.update_active_stats()
        else:
            self.add_log("Больше нет ступеней для отстрела!", "ALERT")

    def change_planet(self, new_planet_id):
        if self.state == "ORBIT":
            self.planet_id = new_planet_id
            self.planet = PLANETS[new_planet_id]
            self.add_log(f"Перелет к {self.planet['name']} завершен.", "SUCCESS")
            
            self.altitude = self.planet["atmosphere"] + 50000
            self.fuel -= 200 # Расход на перелет
            
            if self.fuel < 0:
                self.add_log("Топливо кончилось во время маневра. Ракета потеряна в пустоте.", "ALERT")
                self.state = "CRASHED"
            else:
                self._sync_fuel()
                R = 600000.0
                r = R + self.altitude
                g0 = self.planet["gravity"] * state.physics_multiplier
                mu = g0 * (R**2)
                v_circ = math.sqrt(mu / r) if r > 0 else 0
                self.pos_x = 0.0
                self.pos_y = r
                self.vel_x = v_circ
                self.vel_y = 0.0

    def _sync_fuel(self):
        active = self.rocket.stages[-1]
        remaining = self.fuel
        active_parts = active.all_parts()
        
        total_max_f = sum((next((t["fuel"] for t in PARTS["tanks"] if t["id"] == p["data"]["id"]), p["data"].get("fuel", 0))) for p in active_parts if p["category"] == "tanks")
        if remaining > total_max_f:
            remaining = total_max_f
            self.fuel = total_max_f
            
        for p in active_parts:
            if p["category"] == "tanks":
                tank_data = next((t for t in PARTS["tanks"] if t["id"] == p["data"]["id"]), None)
                max_f = tank_data["fuel"] if tank_data else p["data"]["fuel"]
                if remaining >= max_f:
                    p["data"]["fuel"] = max_f
                    remaining -= max_f
                else:
                    p["data"]["fuel"] = remaining
                    remaining = 0
        # If remaining > 0, it means we have more fuel than tanks can hold.
        # Ensure self.fuel reflects the actual stored fuel plus the excess.
        # Actually it's best to just let self.fuel be the exact sum, or keep it.
        # Let's keep it, meaning excess is stored 'magically' without breaking the loop.

    def tick(self, duration_s):
        if self.state in ["CRASHED", "LANDED", "PRE-LAUNCH", "DOCKED"]:
            return
            
        if not hasattr(self, 'accumulator'):
            self.accumulator = 0.0
            
        self.accumulator += duration_s
        dt = 0.05
        
        while self.accumulator >= dt:
            self._physics_step(dt)
            self.accumulator -= dt

    def _physics_step(self, dt):
        mass = self.rocket.get_total_mass()
        if mass <= 0: mass = 1.0
        
        R = 600000.0
        g0 = self.planet["gravity"] * state.physics_multiplier
        G0_STD = 9.81
        fuel_consumption = (self.thrust_vac * (self.throttle / 100.0) * dt) / (self.isp * G0_STD) * 200.0
        
        is_fuel_empty = False
        if fuel_consumption > 0:
            if self.fuel <= 0:
                is_fuel_empty = True
                if not getattr(self, '_meco_logged', False):
                    self.add_log("MECO: Топливо исчерпано в этой ступени!", "ALERT")
                    self._meco_logged = True
            elif self.fuel < fuel_consumption:
                self.fuel = 0
                self._sync_fuel()
                if not getattr(self, '_meco_logged', False):
                    self.add_log("MECO: Топливо исчерпано в этой ступени!", "ALERT")
                    self._meco_logged = True
            else:
                self.fuel -= fuel_consumption
                self._sync_fuel()
                self._meco_logged = False
        else:
            is_fuel_empty = (self.fuel <= 0)
            if not is_fuel_empty:
                self._meco_logged = False

        def get_accel(px, py, vx, vy, current_mass, empty_fuel):
            r = math.hypot(px, py)
            if r == 0: return 0.0, 0.0
            
            g_mag = g0 * ((R / r)**2)
            g_x = -g_mag * (px / r)
            g_y = -g_mag * (py / r)
            
            alt = r - R
            atm_factor = (max(0, 1 - (alt / self.planet["atmosphere"]))**3) if self.planet["atmosphere"] > 0 else 0
            
            if empty_fuel:
                actual_thrust = 0.0
            else:
                current_max_thrust = (self.thrust_atm * atm_factor) + (self.thrust_vac * (1 - atm_factor))
                actual_thrust = current_max_thrust * (self.throttle / 100.0) * state.physics_multiplier
                
            up_x = px / r
            up_y = py / r
            right_x = py / r
            right_y = -px / r
            
            pitch_rad = math.radians(self.pitch)
            t_up = actual_thrust * math.sin(pitch_rad)
            t_right = actual_thrust * math.cos(pitch_rad)
            
            thrust_x = t_up * up_x + t_right * right_x
            thrust_y = t_up * up_y + t_right * right_y
            
            v_mag = math.hypot(vx, vy)
            drag_coeff = 0.005 * state.physics_multiplier
            if self.parachute_deployed:
                drag_coeff = 5.0 * state.physics_multiplier * (atm_factor ** 0.3)
                
            if v_mag > 0:
                f_drag_mag = drag_coeff * atm_factor * v_mag * v_mag
                drag_accel = f_drag_mag / current_mass
                # Ограничитель сопротивления (чтобы не улететь назад при большом dt)
                if drag_accel * dt > v_mag:
                    f_drag_mag = (v_mag / dt) * current_mass
                drag_x = -f_drag_mag * (vx / v_mag)
                drag_y = -f_drag_mag * (vy / v_mag)
            else:
                drag_x, drag_y = 0.0, 0.0
                
            ax = (thrust_x + drag_x) / current_mass + g_x
            ay = (thrust_y + drag_y) / current_mass + g_y
            return ax, ay

        def get_derivatives(px, py, vx, vy):
            ax, ay = get_accel(px, py, vx, vy, mass, is_fuel_empty)
            return vx, vy, ax, ay

        # RK4 Integrator
        v1x, v1y, a1x, a1y = get_derivatives(self.pos_x, self.pos_y, self.vel_x, self.vel_y)
        v2x, v2y, a2x, a2y = get_derivatives(self.pos_x + v1x*dt/2, self.pos_y + v1y*dt/2, self.vel_x + a1x*dt/2, self.vel_y + a1y*dt/2)
        v3x, v3y, a3x, a3y = get_derivatives(self.pos_x + v2x*dt/2, self.pos_y + v2y*dt/2, self.vel_x + a2x*dt/2, self.vel_y + a2y*dt/2)
        v4x, v4y, a4x, a4y = get_derivatives(self.pos_x + v3x*dt, self.pos_y + v3y*dt, self.vel_x + a3x*dt, self.vel_y + a3y*dt)

        self.pos_x += (dt / 6.0) * (v1x + 2*v2x + 2*v3x + v4x)
        self.pos_y += (dt / 6.0) * (v1y + 2*v2y + 2*v3y + v4y)
        self.vel_x += (dt / 6.0) * (a1x + 2*a2x + 2*a3x + a4x)
        self.vel_y += (dt / 6.0) * (a1y + 2*a2y + 2*a3y + a4y)
        
        r = math.hypot(self.pos_x, self.pos_y)
        alt = r - R
        v_mag = math.hypot(self.vel_x, self.vel_y)
        radial_vel = (self.pos_x * self.vel_x + self.pos_y * self.vel_y) / r if r > 0 else 0
        
        mu = g0 * (R**2)
        E = (v_mag**2)/2.0 - mu / r
        h = self.pos_x * self.vel_y - self.pos_y * self.vel_x
        
        if E >= 0:
            self.apoapsis = float('inf')
            self.periapsis = float('inf')
        else:
            a = -mu / (2.0 * E)
            val = 1.0 + (2.0 * E * h**2) / (mu**2)
            e = math.sqrt(max(0.0, val))
            self.apoapsis = a * (1.0 + e) - R
            self.periapsis = a * (1.0 - e) - R

        if alt >= self.planet["atmosphere"]:
            if self.periapsis > self.planet["atmosphere"]:
                if self.state != "ORBIT":
                    self.state = "ORBIT"
                    self.add_log("Стабильная орбита достигнута!", "SUCCESS")
            else:
                if self.state != "FLIGHT":
                    self.state = "FLIGHT"
                    if not getattr(self, '_space_logged', False):
                        self.add_log("Суборбитальный полет в космосе.")
                        self._space_logged = True
        else:
            self._space_logged = False
            if self.state == "ORBIT":
                self.state = "FLIGHT"
                self.add_log("Вход в атмосферу! Торможение об воздух.", "ALERT")
                
        if alt <= 0:
            if r > 0:
                scale = R / r
                self.pos_x *= scale
                self.pos_y *= scale
                
            if v_mag > 20:
                if self.state != "CRASHED":
                    self.state = "CRASHED"
                    self.add_log(f"КАТАСТРОФА! Удар со скоростью {abs(v_mag):.1f} м/с.", "ALERT")
                self.vel_x = 0.0
                self.vel_y = 0.0
            elif v_mag <= 2.0 and radial_vel <= 0.5:
                if self.state != "LANDED":
                    self.state = "LANDED"
                    self.add_log("Мягкая посадка!", "SUCCESS")
                    state.current_planet = self.planet_id
                self.vel_x = 0.0
                self.vel_y = 0.0
            else:
                self.vel_x *= 0.9
                self.vel_y *= 0.9
