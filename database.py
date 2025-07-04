from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./curebot.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    email = Column(String, nullable=False)

class Prescription(Base):
    __tablename__ = "prescriptions"
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    content = Column(Text)

class Insurance(Base):
    __tablename__ = "insurance"
    id = Column(Integer, primary_key=True)
    provider = Column(String)
    covered_specializations = Column(String)  # comma-separated

Base.metadata.create_all(bind=engine)
