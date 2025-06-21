# check_db.py
from database import Doctor, SessionLocal

session = SessionLocal()
doctors = session.query(Doctor).all()

for doc in doctors:
    print(f"{doc.name} | {doc.specialization} | {doc.email}")

session.close()
