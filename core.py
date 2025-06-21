# core.py
from vertex_agent import ask_llm

def get_doctor_specialization(symptoms: str) -> str:
    prompt = (
        f"You are a medical assistant. A user says: \"{symptoms}\".\n"
        "What type of doctor should they see? (e.g., Cardiologist, Dermatologist)\n"
        "Reply with a single word: the doctor specialization."
    )
    reply = ask_llm(prompt)
    return reply.strip().split()[0]
