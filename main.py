import streamlit as st
import io
from PyPDF2 import PdfReader
from datetime import datetime

from core import get_doctor_specialization
from calendar_api import get_next_available_slots
from vertex_agent import ask_llm
from auth import login, handle_callback
from models import (
    get_doctors_by_specialization,
    SessionLocal,
    Prescription,
    Appointment,
    log_search,
    get_latest_search_result,
    save_appointment
)

# -------------------- Page Config --------------------
st.set_page_config(page_title="CureBot", layout="centered")

# -------------------- Handle Login --------------------
if "email" not in st.session_state:
    handle_callback()
    login()
    st.stop()

user_email = st.session_state["email"]

# -------------------- Sidebar --------------------
st.sidebar.write(f"👤 Logged in as: {st.session_state.get('name', '')} ({user_email})")

# Show Upcoming Appointment
with SessionLocal() as session:
    upcoming = session.query(Appointment)\
        .filter(Appointment.user_email == user_email)\
        .order_by(Appointment.timestamp.desc())\
        .first()

if upcoming:
    st.sidebar.markdown("### 📅 Upcoming Appointment")
    st.sidebar.info(
        f"**Doctor**: {upcoming.doctor_name}\n\n"
        f"**Email**: {upcoming.doctor_email}\n\n"
        f"**Slot**: {upcoming.slot}"
    )

if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📋 Quick Info")

doctor = get_latest_search_result(user_email, "doctor")
if doctor:
    st.sidebar.markdown("**🧑‍⚕️ Last Searched Specialization**")
    st.sidebar.info(doctor)

summary = get_latest_search_result(user_email, "prescription")
if summary:
    st.sidebar.markdown("**📄 Prescription Summary**")
    st.sidebar.success(summary[:200] + "...")

lab = get_latest_search_result(user_email, "lab_test")
if lab:
    st.sidebar.markdown("**🧪 Last Lab Test Suggestion**")
    st.sidebar.write(lab)

# -------------------- Title --------------------
st.title("🩺 CureBot - AI Health Assistant")

# -------------------- Tabs --------------------
tab1, tab2, tab3, tab4, tab5,tab6 = st.tabs([
    "Find Doctor", 
    "Ask Medical Question", 
    "Upload Prescription", 
    "Check Insurance",
    "Recommend Lab Tests",
    "AI Health Risk Report"
])

# -------------------- Tab 1: Find Doctor --------------------
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas

with tab1:
    symptoms = st.text_input("Describe your symptoms")

    if st.button("🔍 Analyze Symptoms") and symptoms:
        with st.spinner("🤖 Analyzing your symptoms..."):
            specialization = get_doctor_specialization(symptoms)

        st.session_state["specialization"] = specialization
        st.success(f"You should see a **{specialization}**")
        log_search(user_email, "doctor", symptoms, specialization)

    if "specialization" in st.session_state:
        specialization = st.session_state["specialization"]
        doctors = get_doctors_by_specialization(specialization)

        if doctors:
            selected_doctor = st.selectbox(
                "Choose a doctor", 
                doctors, 
                key="doctor_select", 
                format_func=lambda d: f"{d.name} ({d.email})"
            )
            slots = get_next_available_slots()
            selected_slot = st.selectbox("📅 Choose a slot", slots, key="slot_select")

            if st.button("Book Appointment"):
                save_appointment(
                    user_email=user_email,
                    doctor_name=selected_doctor.name,
                    doctor_email=selected_doctor.email,
                    slot=selected_slot
                )
                st.success(f"✅ Appointment booked with **{selected_doctor.name}** at **{selected_slot}**")
                log_search(user_email, "appointment", f"{selected_doctor.name} - {specialization}", selected_slot)

                # Generate PDF confirmation
                buffer = BytesIO()
                pdf = canvas.Canvas(buffer)
                pdf.setFont("Helvetica", 12)

                y = 800
                pdf.drawString(50, y, "CureBot Appointment Confirmation")
                y -= 30
                pdf.drawString(50, y, f"🧑‍⚕️ Doctor: {selected_doctor.name}")
                y -= 20
                pdf.drawString(50, y, f"📧 Doctor Email: {selected_doctor.email}")
                y -= 20
                pdf.drawString(50, y, f"📅 Slot: {selected_slot}")
                y -= 20
                pdf.drawString(50, y, f"👤 Patient: {st.session_state.get('name', 'User')}")
                y -= 20
                pdf.drawString(50, y, f"📧 Patient Email: {user_email}")
                y -= 20
                pdf.drawString(50, y, f"🕒 Booked At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                pdf.showPage()
                pdf.save()
                buffer.seek(0)

                st.download_button(
                    label="📄 Download Appointment PDF",
                    data=buffer,
                    file_name=f"appointment_{selected_doctor.name.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("No doctors available for that specialization.")

# -------------------- Tab 2: Ask Medical Question --------------------
with tab2:
    user_q = st.text_input("Ask a medical question")
    if user_q and st.button("💬 Get Answer"):
        with st.spinner("🤖 Thinking..."):
            response = ask_llm(user_q)
        st.write("🤖", response)
        log_search(user_email, "medical_question", user_q, response)

# -------------------- Tab 3: Upload Prescription --------------------
with tab3:
    uploaded = st.file_uploader("Upload your prescription (TXT or PDF)", type=["txt", "pdf"])
    language = st.selectbox("🌍 Select summary language", ["English", "Hindi", "Marathi", "German", "French", "Spanish"])

    if uploaded and st.button("📑 Analyze Prescription"):
        try:
            file_bytes = uploaded.read()
            if uploaded.type == "application/pdf":
                reader = PdfReader(io.BytesIO(file_bytes))
                content = "\n".join([page.extract_text() or "" for page in reader.pages])
            else:
                content = file_bytes.decode("utf-8")

            with SessionLocal() as session:
                session.add(Prescription(filename=uploaded.name, content=content))
                session.commit()

            prompt = f"Summarize this prescription in {language}:\n\n{content}"
            with st.spinner("🤖 Summarizing your prescription..."):
                summary = ask_llm(prompt)

            st.success("📥 Prescription uploaded successfully!")
            st.subheader("📄 Prescription Summary")
            st.write("🤖", summary)
            log_search(user_email, "prescription", content, summary)

        except Exception as e:
            st.error(f"Error reading file: {e}")

# -------------------- Tab 4: Insurance --------------------
with tab4:
    st.subheader("📄 Upload Insurance Policy (PDF)")
    uploaded_policy = st.file_uploader("Upload your insurance policy (PDF)", type=["pdf"])

    if uploaded_policy and st.button("🔍 Summarize Policy"):
        try:
            reader = PdfReader(io.BytesIO(uploaded_policy.read()))
            policy_text = "\n".join([page.extract_text() or "" for page in reader.pages])

            with st.spinner("🤖 Analyzing your policy..."):
                summary = ask_llm(f"Summarize policy benefits:\n\n{policy_text}")
            st.success("✅ Policy uploaded successfully")
            st.subheader("🔍 Extracted Benefits")
            st.write("🤖", summary)

            log_search(user_email, "insurance_summary", policy_text, summary)

        except Exception as e:
            st.error(f"Failed to read PDF: {e}")

    st.markdown("---")
    st.subheader("❓ Ask Insurance Questions")
    insurance_q = st.text_input("Your insurance question")
    if insurance_q and st.button("❓ Ask Insurance Bot"):
        with st.spinner("🤖 Processing your question..."):
            answer = ask_llm(
                f"The user asked an insurance-related question: \"{insurance_q}\".\n"
                "If provider is mentioned, answer accordingly. If not insured, suggest Indian government schemes like Ayushman Bharat."
            )
        st.write("🤖", answer)
        log_search(user_email, "insurance_question", insurance_q, answer)

    if st.button("🆘 Show Govt Schemes"):
        with st.spinner("🤖 Fetching government schemes..."):
            schemes = ask_llm("Suggest Indian government schemes for uninsured patients.")
        st.write("🏥", schemes)
        log_search(user_email, "govt_schemes", "uninsured", schemes)

# -------------------- Tab 5: Lab Tests --------------------
with tab5:
    st.subheader("🩺 Symptom-Based Lab Test Assistant")

    common_symptoms = [
        "Fatigue", "Hair loss", "Fever", "Chest pain", "Headache", 
        "Stomach ache", "Joint pain", "Back pain", "Dizziness", "Shortness of breath"
    ]

    selected_symptom = st.selectbox("Select a common symptom (or enter below):", common_symptoms)
    custom_symptom = st.text_input("Or describe your own symptom", "")
    final_symptom = custom_symptom.strip() if custom_symptom.strip() else selected_symptom

    if st.button("🔎 Analyze"):
        if final_symptom:
            prompt = f"A patient reports: \"{final_symptom}\".\nWhat diagnostic lab tests should they take? Respond in bullet points."
            with st.spinner("🤖 Analyzing your symptoms..."):
                lab_response = ask_llm(prompt)

            st.subheader("🧪 Recommended Lab Tests")
            st.write("🤖", lab_response)
            log_search(user_email, "lab_test", final_symptom, lab_response)

            if st.checkbox("🧠 Show possible causes and treatments"):
                causes_prompt = f"The patient mentioned symptoms like: {final_symptom}. What could be the possible causes or types?"
                with st.spinner("🤖 Identifying causes/types..."):
                    causes = ask_llm(causes_prompt)
                st.subheader("🧠 Possible Causes / Types")
                st.write("🤖", causes)

                treatment_prompt = f"What are the possible treatments for someone showing these symptoms: {final_symptom}?"
                with st.spinner("💊 Fetching treatment options..."):
                    treatments = ask_llm(treatment_prompt)
                st.subheader("💊 Suggested Treatments / Actions")
                st.write("🤖", treatments)

                log_search(user_email, "lab_followup", final_symptom, f"{causes}\n{treatments}")
        else:
            st.warning("Please enter or select a symptom first.")



#tab6 AI-Powered Health Risk Report


with tab6:
    st.subheader("📊 AI-Powered Health Risk Report")

    symptoms = st.text_area("📝 Describe your symptoms", "")
    prescription_file = st.file_uploader("📄 Upload your prescription (TXT or PDF)", type=["txt", "pdf"])

    if "payment_done" not in st.session_state:
        st.session_state["payment_done"] = False

    if st.button("🧠 Generate Risk Report (₹49)") and (symptoms or prescription_file):
        st.session_state["payment_requested"] = True
        st.info("🔒 Please confirm payment to proceed...")

    if st.session_state.get("payment_requested") and not st.session_state["payment_done"]:
        if st.button("✅ Simulate Payment Success"):
            st.session_state["payment_done"] = True
            st.rerun()

    if st.session_state.get("payment_done"):
        content = ""
        if prescription_file:
            try:
                file_bytes = prescription_file.read()
                if prescription_file.type == "application/pdf":
                    reader = PdfReader(io.BytesIO(file_bytes))
                    content = "\n".join([page.extract_text() or "" for page in reader.pages])
                else:
                    content = file_bytes.decode("utf-8")
            except Exception as e:
                st.error(f"Failed to read prescription: {e}")
                st.stop()

        full_prompt = (
            f"Patient's symptoms: {symptoms}\n"
            f"Prescription details: {content}\n\n"
            "Generate a detailed health risk report with:\n"
            "- Possible chronic risks (diabetes, BP, cholesterol, etc.)\n"
            "- Early warning signs\n"
            "- Lifestyle & diet recommendations\n"
            "- Mention urgency if needed."
        )

        with st.spinner("🧠 Generating your risk report..."):
            report = ask_llm(full_prompt)

        st.success("✅ Health Risk Report Generated")
        st.text_area("📋 Risk Report", report, height=300)
        log_search(user_email, "health_risk_report", f"{symptoms}\n{content}", report)

        # Reset session states so it doesn't regenerate on rerun
        st.session_state["payment_done"] = False
        st.session_state["payment_requested"] = False
