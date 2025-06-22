from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./curebot.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)


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
    covered_specializations = Column(String)


def get_doctors_by_specialization(specialty: str):
    session = SessionLocal()
    doctors = (
        session.query(Doctor)
        .filter(Doctor.specialization.ilike(f"%{specialty}%"))
        .all()
    )
    session.close()
    return doctors


def check_insurance_coverage(provider: str, specialization: str):
    session = SessionLocal()
    result = session.query(Insurance).filter(
        Insurance.provider.ilike(f"%{provider}%")
    ).all()
    session.close()

    for entry in result:
        covered = [s.strip().lower() for s in entry.covered_specializations.split(",")]
        if specialization.lower() in covered:
            return True
    return False


# Create all tables
Base.metadata.create_all(bind=engine)
