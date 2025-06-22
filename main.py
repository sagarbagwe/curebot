import streamlit as st
from core import get_doctor_specialization
from calendar_api import get_next_available_slots
from models import get_doctors_by_specialization, SessionLocal, Prescription
from vertex_agent import ask_llm
from auth import login, handle_callback

import io
from PyPDF2 import PdfReader

# Set page config early
st.set_page_config(page_title="CureBot", layout="centered")

# 🔐 Handle Google Login
if "email" not in st.session_state:
    handle_callback()
    login()
    st.stop()

# Sidebar - show user info & logout
st.sidebar.write(f"👤 Logged in as: {st.session_state.get('name', '')} ({st.session_state['email']})")
if st.sidebar.button("🚪 Logout"):
    for key in ["email", "name"]:
        st.session_state.pop(key, None)
    st.rerun()

# Page Title
st.title("🩺 CureBot - AI Health Assistant")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Find Doctor", 
    "Ask Medical Question", 
    "Upload Prescription", 
    "Check Insurance",
    "Recommend Lab Tests"
])

# Tab 1: Find Doctor
with tab1:
    symptoms = st.text_input("Describe your symptoms")
    if symptoms:
        specialization = get_doctor_specialization(symptoms)
        st.success(f"You should see a **{specialization}**")
        doctors = get_doctors_by_specialization(specialization)
        if doctors:
            for doc in doctors:
                st.write(f"👨‍⚕️ {doc.name} — {doc.email}")
            slots = get_next_available_slots()
            slot = st.selectbox("📅 Choose a slot", slots)
            if st.button("Book Appointment"):
                st.success(f"✅ Appointment booked for **{slot}**")
        else:
            st.warning("No doctors available for that specialization.")

# Tab 2: Ask Medical Question
with tab2:
    user_q = st.text_input("Ask a medical question")
    if user_q:
        response = ask_llm(user_q)
        st.write("🤖", response)

# Tab 3: Upload Prescription
with tab3:
    uploaded = st.file_uploader("Upload your prescription (TXT or PDF)", type=["txt", "pdf"])
    language = st.selectbox("🌍 Select summary language", ["English", "Hindi", "Marathi", "German", "French", "Spanish"])

    if uploaded:
        try:
            file_bytes = uploaded.read()
            if uploaded.type == "application/pdf":
                reader = PdfReader(io.BytesIO(file_bytes))
                content = "\n".join([page.extract_text() or "" for page in reader.pages])
            else:
                content = file_bytes.decode("utf-8")

            # Save to DB
            session = SessionLocal()
            session.add(Prescription(filename=uploaded.name, content=content))
            session.commit()
            session.close()

            st.success("📥 Prescription uploaded successfully!")
            prompt = f"Summarize this prescription in {language}:\n\n{content}"
            summary = ask_llm(prompt)
            st.subheader("📄 Prescription Summary")
            st.write("🤖", summary)

        except Exception as e:
            st.error(f"Error reading file: {e}")

# Tab 4: Insurance Assistant
with tab4:
    st.subheader("📄 Upload Insurance Policy (PDF)")
    uploaded_policy = st.file_uploader("Upload your insurance policy (PDF)", type=["pdf"])
    if uploaded_policy:
        try:
            reader = PdfReader(io.BytesIO(uploaded_policy.read()))
            policy_text = "\n".join([page.extract_text() or "" for page in reader.pages])
            st.success("✅ Policy uploaded successfully")
            st.subheader("🔍 Extracted Benefits")
            summary = ask_llm(f"Summarize policy benefits:\n\n{policy_text}")
            st.write("🤖", summary)
        except Exception as e:
            st.error(f"Failed to read PDF: {e}")

    st.markdown("---")
    st.subheader("❓ Ask Insurance Questions")
    insurance_q = st.text_input("Your insurance question")
    if insurance_q:
        answer = ask_llm(
            f"The user asked an insurance-related question: \"{insurance_q}\".\n"
            "If provider is mentioned, answer accordingly. If not insured, suggest Indian government schemes like Ayushman Bharat."
        )
        st.write("🤖", answer)

    if st.button("🆘 Show Govt Schemes"):
        schemes = ask_llm("Suggest Indian government schemes for uninsured patients.")
        st.write("🏥", schemes)

# Tab 5: Lab Test Recommendations
with tab5:
    test_symptoms = st.text_input("Enter your symptoms (e.g., fatigue, hair loss)")
    if test_symptoms:
        prompt = f"A patient reports: \"{test_symptoms}\".\nWhat diagnostic lab tests should they take? Respond in bullet points."
        response = ask_llm(prompt)
        st.subheader("🧪 Recommended Lab Tests")
        st.write("🤖", response)
