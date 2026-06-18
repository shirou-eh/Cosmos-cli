import copy
import math
from .data import PARTS
from .config import state

class Stage:
    def __init__(self):
        self.center = []
        self.left = []
        self.right = []

    def all_parts(self):
        return self.center + self.left + self.right

    def has_any_parts(self):
        return bool(self.center or self.left or self.right)


class Rocket:
    def __init__(self, name):
        self.name = name
        self.stages = [Stage()]

    def add_part(self, category, part_id, side="center"):
        part = next((p for p in PARTS[category] if p["id"] == part_id), None)
        if part is None:
            return
        if part_id == "util_dec":
            self.stages.append(Stage())
            return
        target = self.stages[-1]
        col = getattr(target, side)
        col.append({"category": category, "data": copy.deepcopy(part)})

    def remove_last_part(self, side="center"):
        target = self.stages[-1]
        col = getattr(target, side)
        if col:
            col.pop()
            return True
        if side == "center":
            if len(self.stages) > 1 and not target.left and not target.right:
                self.stages.pop()
                return True
        return False

    def get_stage_count(self):
        return len(self.stages)

    def get_total_mass(self):
        mass = 0
        for stage in self.stages:
            for p in stage.all_parts():
                if p["category"] == "tanks":
                    mass += p["data"]["mass_empty"] + (p["data"]["fuel"] * 0.005)
                else:
                    mass += p["data"]["mass"]
        return round(mass, 2)

    def get_delta_v_estimate(self):
        g0 = 9.81
        stage_data = []
        for stage_obj in self.stages:
            stage_parts = stage_obj.all_parts()
            total_mass = 0
            fuel_mass = 0
            isp_avg = 0
            eng_count = 0
            for p in stage_parts:
                if p["category"] == "tanks":
                    f = p["data"]["fuel"]
                    fuel_mass += f * 0.005
                    total_mass += p["data"]["mass_empty"] + (f * 0.005)
                elif p["category"] == "engines":
                    isp_avg += p["data"].get("isp", 300)
                    eng_count += 1
                    total_mass += p["data"]["mass"]
                else:
                    total_mass += p["data"]["mass"]
            stage_data.append({
                "total_mass": total_mass,
                "fuel_mass": fuel_mass,
                "isp_avg": isp_avg / eng_count if eng_count > 0 else 0,
                "eng_count": eng_count,
            })
        stages_dv = []
        upper_mass = sum(s["total_mass"] for s in stage_data)
        for sd in reversed(stage_data):
            upper_mass -= sd["total_mass"]
            s_mass = sd["total_mass"] + upper_mass
            f_mass = sd["fuel_mass"]
            dry = s_mass - f_mass
            if sd["eng_count"] > 0 and f_mass > 0 and dry > 0 and s_mass > dry:
                dv = sd["isp_avg"] * g0 * math.log(s_mass / dry)
                stages_dv.append(dv)
        return sum(stages_dv)

    def get_active_stage_stats(self):
        active_stage = self.stages[-1]
        fuel = 0
        thrust_atm = 0
        thrust_vac = 0
        isp_list = []

        has_parachute = False
        has_drill = False
        has_base = False
        has_pod = False
        has_scanner = False

        for p in active_stage.all_parts():
            if p["category"] == "tanks":
                fuel += p["data"]["fuel"]
            elif p["category"] == "engines":
                thrust_atm += p["data"]["thrust_atm"]
                thrust_vac += p["data"]["thrust_vac"]
                isp_list.append(p["data"].get("isp", 300))
            elif p["data"]["id"] == "util_para": has_parachute = True
            elif p["data"]["id"] == "util_drill": has_drill = True
            elif p["data"]["id"] == "util_base": has_base = True
            elif p["data"]["id"] == "util_scan": has_scanner = True
            elif p["category"] == "pods": has_pod = True

        return {
            "fuel": fuel,
            "thrust_atm": thrust_atm,
            "thrust_vac": thrust_vac,
            "isp": round(sum(isp_list) / len(isp_list)) if isp_list else 300,
            "has_parachute": has_parachute,
            "has_drill": has_drill,
            "has_base": has_base,
            "has_pod": has_pod,
            "has_scanner": has_scanner
        }

    def stage(self):
        if len(self.stages) > 1:
            self.stages.pop()
            return True
        return False

    def get_cost(self):
        cost = 0
        for stage in self.stages:
            for p in stage.all_parts():
                cost += p["data"]["cost"]
        cost += (len(self.stages) - 1) * 800
        return int(cost * state.cost_multiplier)
