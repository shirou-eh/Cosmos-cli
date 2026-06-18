import json
import copy

class GameState:
    def __init__(self):
        self.credits = 50_000
        self.science = 0
        self.minerals = 0
        self.difficulty = 2
        self.rockets = []
        self.current_planet = "Terra"
        
        self.colonies = {}
        self.settings = {}
        self.has_seen_tutorial = False
        
        self.unlocked_techs = ["basic"]
        self.active_contract = None
        self.completed_contracts = []
        self.scanned_planets = set()
        
        self.physics_multiplier = 1.0
        self.cost_multiplier = 1.0
        self.profile_name = "default"
        
    def set_difficulty(self, level: int):
        self.difficulty = level
        if level == 1:
            self.physics_multiplier = 0.5
            self.cost_multiplier = 0.5
        elif level == 2:
            self.physics_multiplier = 1.0
            self.cost_multiplier = 1.0
        elif level == 3:
            self.physics_multiplier = 1.5
            self.cost_multiplier = 2.0

    def set_setting(self, key: str, value: str):
        self.settings[key] = str(value)
        
    def get_setting(self, key: str, default: str = None) -> str:
        return self.settings.get(key, default)

    def get_all_profiles(self):
        try:
            from .database import SessionLocal, ProfileModel
            with SessionLocal() as db:
                return [p.name for p in db.query(ProfileModel).all()]
        except:
            return []

    def save_game(self):
        from .database import SessionLocal, ProfileModel, ColonyModel, UnlockedTechModel, CompletedContractModel, RocketModel, RocketStageModel, RocketPartModel, SettingModel, ScannedPlanetModel
        try:
            with SessionLocal() as db:
                profile = db.query(ProfileModel).filter(ProfileModel.name == self.profile_name).first()
                if not profile:
                    profile = ProfileModel(name=self.profile_name)
                    db.add(profile)
                
                profile.credits = self.credits
                profile.science = self.science
                profile.minerals = self.minerals
                profile.difficulty = self.difficulty
                profile.current_planet = self.current_planet
                profile.has_seen_tutorial = self.has_seen_tutorial
                profile.active_contract = self.active_contract

                db.query(ColonyModel).filter(ColonyModel.profile_id == profile.id).delete()
                for p_id, exists in self.colonies.items():
                    if exists:
                        db.add(ColonyModel(profile=profile, planet_id=p_id))
                
                db.query(UnlockedTechModel).filter(UnlockedTechModel.profile_id == profile.id).delete()
                for t in self.unlocked_techs:
                    db.add(UnlockedTechModel(profile=profile, tech_id=t))
                    
                db.query(CompletedContractModel).filter(CompletedContractModel.profile_id == profile.id).delete()
                for c in self.completed_contracts:
                    db.add(CompletedContractModel(profile=profile, contract_id=c))

                db.query(SettingModel).filter(SettingModel.profile_id == profile.id).delete()
                for k, v in self.settings.items():
                    db.add(SettingModel(profile=profile, key=str(k), value=str(v)))

                db.query(ScannedPlanetModel).filter(ScannedPlanetModel.profile_id == profile.id).delete()
                for p_id in self.scanned_planets:
                    db.add(ScannedPlanetModel(profile=profile, planet_id=p_id))

                db.query(RocketModel).filter(RocketModel.profile_id == profile.id).delete()
                for r in self.rockets:
                    r_model = RocketModel(profile=profile, name=r.name)
                    db.add(r_model)
                    for i, stage in enumerate(r.stages):
                        s_model = RocketStageModel(rocket=r_model, stage_index=i)
                        db.add(s_model)
                        order = 0
                        for side_name in ["center", "left", "right"]:
                            col = getattr(stage, side_name, [])
                            for j, part in enumerate(col):
                                p_model = RocketPartModel(
                                    stage=s_model, part_order=order,
                                    category=part["category"], part_id=part["data"]["id"],
                                    side=side_name
                                )
                                db.add(p_model)
                                order += 1

                db.commit()
            return True
        except Exception as e:
            print("SAVE ERROR:", e)
            return False

    def load_game(self, profile_name):
        from .database import SessionLocal, ProfileModel
        from .vab import Rocket
        from .data import PARTS
        
        self.profile_name = profile_name
        try:
            with SessionLocal() as db:
                profile = db.query(ProfileModel).filter(ProfileModel.name == self.profile_name).first()
                if not profile:
                    # Not found, initialization default values will be kept
                    return True
                
                self.credits = profile.credits
                self.science = profile.science
                self.minerals = profile.minerals
                self.set_difficulty(profile.difficulty)
                self.current_planet = profile.current_planet
                self.has_seen_tutorial = profile.has_seen_tutorial
                self.active_contract = profile.active_contract
                
                self.colonies = {c.planet_id: True for c in profile.colonies}
                self.settings = {s.key: s.value for s in profile.settings}
                self.unlocked_techs = [t.tech_id for t in profile.unlocked_techs]
                self.completed_contracts = [c.contract_id for c in profile.completed_contracts]
                self.scanned_planets = {s.planet_id for s in profile.scanned_planets}
                
                self.rockets = []
                for r_model in profile.rockets:
                    from .vab import Stage
                    r = Rocket(r_model.name)
                    r.stages = []
                    for s_model in r_model.stages:
                        stage = Stage()
                        for p_model in s_model.parts:
                            part_data = next((p for p in PARTS.get(p_model.category, []) if p["id"] == p_model.part_id), None)
                            if part_data:
                                col_name = getattr(p_model, 'side', 'center')
                                col = getattr(stage, col_name, stage.center)
                                col.append({"category": p_model.category, "data": copy.deepcopy(part_data)})
                        r.stages.append(stage)
                    self.rockets.append(r)
                
            return True
        except Exception as e:
            print("LOAD ERROR:", e)
            return False

state = GameState()
