import json
import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.pool import StaticPool

DB_DIR = os.path.join(os.path.expanduser("~"), ".local", "share", "cosmos")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "cosmos_data.db")

Base = declarative_base()

class ProfileModel(Base):
    __tablename__ = 'profile'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    credits = Column(Integer, default=50000)
    science = Column(Integer, default=0)
    minerals = Column(Integer, default=0)
    difficulty = Column(Integer, default=2)
    current_planet = Column(String, default="Terra")
    has_seen_tutorial = Column(Boolean, default=False)
    active_contract = Column(String, nullable=True)
    
    colonies = relationship("ColonyModel", back_populates="profile", cascade="all, delete-orphan")
    unlocked_techs = relationship("UnlockedTechModel", back_populates="profile", cascade="all, delete-orphan")
    completed_contracts = relationship("CompletedContractModel", back_populates="profile", cascade="all, delete-orphan")
    rockets = relationship("RocketModel", back_populates="profile", cascade="all, delete-orphan")
    settings = relationship("SettingModel", back_populates="profile", cascade="all, delete-orphan")
    scanned_planets = relationship("ScannedPlanetModel", back_populates="profile", cascade="all, delete-orphan")

class ColonyModel(Base):
    __tablename__ = 'colony'
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile.id'))
    planet_id = Column(String, nullable=False)
    profile = relationship("ProfileModel", back_populates="colonies")

class UnlockedTechModel(Base):
    __tablename__ = 'unlocked_tech'
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile.id'))
    tech_id = Column(String, nullable=False)
    profile = relationship("ProfileModel", back_populates="unlocked_techs")

class CompletedContractModel(Base):
    __tablename__ = 'completed_contract'
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile.id'))
    contract_id = Column(String, nullable=False)
    profile = relationship("ProfileModel", back_populates="completed_contracts")

class RocketModel(Base):
    __tablename__ = 'rocket'
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile.id'))
    name = Column(String, nullable=False)
    profile = relationship("ProfileModel", back_populates="rockets")
    stages = relationship("RocketStageModel", back_populates="rocket", cascade="all, delete-orphan", order_by="RocketStageModel.stage_index")

class RocketStageModel(Base):
    __tablename__ = 'rocket_stage'
    id = Column(Integer, primary_key=True)
    rocket_id = Column(Integer, ForeignKey('rocket.id'))
    stage_index = Column(Integer, nullable=False)
    rocket = relationship("RocketModel", back_populates="stages")
    parts = relationship("RocketPartModel", back_populates="stage", cascade="all, delete-orphan", order_by="RocketPartModel.part_order")

class RocketPartModel(Base):
    __tablename__ = 'rocket_part'
    id = Column(Integer, primary_key=True)
    stage_id = Column(Integer, ForeignKey('rocket_stage.id'))
    part_order = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    part_id = Column(String, nullable=False)
    side = Column(String, default="center", nullable=False)
    stage = relationship("RocketStageModel", back_populates="parts")

    def to_dict(self):
        return {"category": self.category, "part_id": self.part_id, "side": self.side}

class ScannedPlanetModel(Base):
    __tablename__ = 'scanned_planet'
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile.id'))
    planet_id = Column(String, nullable=False)
    profile = relationship("ProfileModel", back_populates="scanned_planets")

class SettingModel(Base):
    __tablename__ = 'setting'
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile.id'))
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)
    profile = relationship("ProfileModel", back_populates="settings")

engine = create_engine(f'sqlite:///{DB_PATH}', poolclass=StaticPool, connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)

def upgrade_schema():
    from sqlalchemy import inspect as sa_inspect
    try:
        with engine.connect() as conn:
            inspector = sa_inspect(conn)
            columns = [c['name'] for c in inspector.get_columns('rocket_part')]
            if 'side' not in columns:
                conn.execute("ALTER TABLE rocket_part ADD COLUMN side VARCHAR DEFAULT 'center'")
                conn.commit()
    except Exception:
        pass

upgrade_schema()

SessionLocal = sessionmaker(bind=engine)
