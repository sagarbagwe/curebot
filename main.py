# main.py
import streamlit as st
from core import get_doctor_specialization
from calendar_api import get_next_available_slots
from database import get_doctors_by_specialization

st.set_page_config(page_title="CureBot", layout="centered")
st.title("🩺 CureBot - AI Health Assistant")

symptom_input = st.text_input("Describe your symptoms")

if symptom_input:
    st.info("🤖 Analyzing…")
    specialization = get_doctor_specialization(symptom_input)
    st.success(f"You should see a **{specialization}**")

    doctors = get_doctors_by_specialization(specialization)
    if docs := doctors:
        st.subheader("Available Doctors")
        for doc in docs:
            st.write(f"- **{doc.name}** — {doc.email}")

        slots = get_next_available_slots()
        selected_slot = st.selectbox("📅 Choose an appointment slot", slots)

        if st.button("Book Appointment"):
            st.success(f"✅ Appointment booked for {selected_slot}")
    else:
        st.warning("No doctors found for that specialization.")
