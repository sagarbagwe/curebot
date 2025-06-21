# database.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./curebot.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    email = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

def get_doctors_by_specialization(specialty: str):
    session = SessionLocal()
    docs = (
        session.query(Doctor)
        .filter(Doctor.specialization.ilike(f"%{specialty}%"))
        .all()
    )
    session.close()
    return docs
