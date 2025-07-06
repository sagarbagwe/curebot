from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# ------------------------ Database Configuration ------------------------

DATABASE_URL = "sqlite:///./curebot.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# ------------------------ Models ------------------------

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    email = Column(String, nullable=False)

class Prescription(Base):
    __tablename__ = "prescriptions"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content = Column(Text, nullable=False)

class Insurance(Base):
    __tablename__ = "insurance"
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False)
    covered_specializations = Column(String, nullable=False)

class SearchLog(Base):
    __tablename__ = "search_logs"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    type = Column(String, nullable=False)  # doctor, lab_test, prescription, etc.
    query = Column(Text, nullable=False)
    result = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=False)
    doctor_name = Column(String, nullable=False)
    doctor_email = Column(String, nullable=False)
    slot = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# ------------------------ Utility Functions ------------------------

def get_doctors_by_specialization(specialty: str):
    with SessionLocal() as session:
        return session.query(Doctor).filter(Doctor.specialization.ilike(f"%{specialty}%")).all()

def check_insurance_coverage(provider: str, specialization: str) -> bool:
    with SessionLocal() as session:
        entries = session.query(Insurance).filter(Insurance.provider.ilike(f"%{provider}%")).all()
        for entry in entries:
            covered = [s.strip().lower() for s in entry.covered_specializations.split(",")]
            if specialization.lower() in covered:
                return True
    return False

def log_search(email: str, search_type: str, query: str, result: str):
    with SessionLocal() as session:
        session.add(SearchLog(
            email=email,
            type=search_type,
            query=query,
            result=result
        ))
        session.commit()

def get_latest_search_result(email: str, search_type: str):
    with SessionLocal() as session:
        log = session.query(SearchLog)\
            .filter_by(email=email, type=search_type)\
            .order_by(SearchLog.timestamp.desc())\
            .first()
        return log.result if log else None

def save_appointment(user_email: str, doctor_name: str, doctor_email: str, slot: str):
    with SessionLocal() as session:
        session.add(Appointment(
            user_email=user_email,
            doctor_name=doctor_name,
            doctor_email=doctor_email,
            slot=slot
        ))
        session.commit()

# ------------------------ Create Tables ------------------------

Base.metadata.create_all(bind=engine)
