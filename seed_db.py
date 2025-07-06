from faker import Faker
import random
from database import SessionLocal, Doctor

fake = Faker()

SPECIALIZATIONS = [
    "Cardiologist", "Dermatologist", "Neurologist", "Gynecologist", "Orthopedic",
    "Pediatrician", "Endocrinologist", "Urologist", "ENT", "Gastroenterologist",
    "Psychiatrist", "Oncologist", "Pulmonologist", "Rheumatologist", "Nephrologist",
    "Hematologist", "Allergist", "Immunologist", "Ophthalmologist", "Pathologist",
    "General Physician", "Sexologist", "Dentist", "Diabetologist"
]

def generate_doctors(n=300):
    doctors = []
    for _ in range(n):
        doctors.append(Doctor(
            name=fake.name(),
            specialization=random.choice(SPECIALIZATIONS),
            email=fake.unique.email()
        ))
    return doctors

def seed():
    session = SessionLocal()

    # 🔄 Clear existing doctor data
    session.query(Doctor).delete()
    session.commit()

    # 🌱 Seed new fake doctors
    doctors = generate_doctors()
    session.add_all(doctors)
    session.commit()
    session.close()

    print("✅ Seeded 300 random doctors with various specializations.")

if __name__ == "__main__":
    seed()
