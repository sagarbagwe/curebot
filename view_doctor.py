# view_doctors.py
from database import SessionLocal, Doctor

def view_doctors():
    session = SessionLocal()
    doctors = session.query(Doctor).all()
    for doc in doctors:
        print(f"{doc.id}: {doc.name} | {doc.specialization} | {doc.email}")
    session.close()

if __name__ == "__main__":
    view_doctors()
