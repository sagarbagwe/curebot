# seed_db.py
from database import Doctor, SessionLocal

def seed():
    session = SessionLocal()
    session.query(Doctor).delete()  # 👈 Clear existing data
    session.commit()

    doctors = [
        Doctor(name="Dr. Arjun Singh", specialization="Cardiologist", email="arjun@example.com"),
        Doctor(name="Dr. Meera Das", specialization="Dermatologist", email="meera@example.com"),
        Doctor(name="Dr. Vikram Rao", specialization="Neurologist", email="vikram@example.com"),
        Doctor(name="Dr. Kavita Shah", specialization="Gynecologist", email="kavita@example.com"),
        Doctor(name="Dr. Rahul Sen", specialization="Orthopedic", email="rahul@example.com"),
        Doctor(name="Dr. Anjali Nair", specialization="Pediatrician", email="anjali@example.com"),
        Doctor(name="Dr. Ramesh Kumar", specialization="Cardiologist", email="ramesh@example.com"),
        Doctor(name="Dr. Sneha Jain", specialization="Dermatologist", email="sneha@example.com"),
        Doctor(name="Dr. Alok Verma", specialization="Neurologist", email="alok@example.com"),
        Doctor(name="Dr. Priya Mehta", specialization="Gynecologist", email="priya@example.com"),
        Doctor(name="Dr. Ashok Rana", specialization="Orthopedic", email="ashok@example.com"),
        Doctor(name="Dr. Neha Thakur", specialization="Pediatrician", email="neha@example.com"),
        Doctor(name="Dr. Karan Desai", specialization="Cardiologist", email="karan@example.com"),
        Doctor(name="Dr. Tanya Kapoor", specialization="Dermatologist", email="tanya@example.com"),
        Doctor(name="Dr. Mohan Lal", specialization="Neurologist", email="mohan@example.com"),
        Doctor(name="Dr. Divya Reddy", specialization="Gynecologist", email="divya@example.com"),
        Doctor(name="Dr. Vinay Patel", specialization="Orthopedic", email="vinay@example.com"),
        Doctor(name="Dr. Isha Bansal", specialization="Pediatrician", email="isha@example.com"),
        Doctor(name="Dr. Suresh Menon", specialization="Cardiologist", email="suresh@example.com"),
        Doctor(name="Dr. Ritu Arora", specialization="Dermatologist", email="ritu@example.com"),
    ]

    session.add_all(doctors)
    session.commit()
    print("✅ Database reseeded with new doctors.")
    session.close()

if __name__ == "__main__":
    seed()
