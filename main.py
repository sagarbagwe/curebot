import streamlit as st
from core import get_doctor_specialization
from calendar_api import get_next_available_slots
from models import get_doctors_by_specialization, SessionLocal, Prescription
from vertex_agent import ask_llm
import io
from PyPDF2 import PdfReader




st.set_page_config(page_title="CureBot", layout="centered")
st.title("🩺 CureBot - AI Health Assistant")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Find Doctor", 
    "Ask Medical Question", 
    "Upload Prescription", 
    "Check Insurance",
    "Recommend Lab Tests"
])

# 🧠 Ask Gemini anything
with tab2:
    user_q = st.text_input("Ask a medical question")
    if user_q:
        response = ask_llm(user_q)
        st.write("🤖", response)

# 🩺 Doctor based on symptoms
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

# 📜 Upload prescriptions with summary
with tab3:
    uploaded = st.file_uploader("Upload your prescription (TXT or PDF)", type=["txt", "pdf"])
    if uploaded:
        file_bytes = uploaded.read()
        try:
            if uploaded.type == "application/pdf":
                reader = PdfReader(io.BytesIO(file_bytes))
                content = "\n".join([page.extract_text() or "" for page in reader.pages])
            else:
                content = file_bytes.decode('utf-8')

            # Save to database
            session = SessionLocal()
            session.add(Prescription(filename=uploaded.name, content=content))
            session.commit()
            session.close()

            st.success("📥 Prescription uploaded and saved successfully!")

            # Ask Gemini to summarize
            st.subheader("📄 Prescription Summary")
            summary = ask_llm(f"Summarize this prescription:\n\n{content}")
            st.write("🤖", summary)

        except Exception as e:
            st.error(f"Error processing file: {e}")

# 🧾 Check insurance
with tab4:
    st.subheader("📄 Upload Insurance Policy (PDF)")
    uploaded_policy = st.file_uploader("Upload your insurance policy (PDF)", type=["pdf"])
    insurance_summary = ""

    if uploaded_policy:
        try:
            reader = PdfReader(io.BytesIO(uploaded_policy.read()))
            policy_text = "\n".join([page.extract_text() or "" for page in reader.pages])
            st.success("✅ Policy uploaded successfully")

            # Ask Gemini to extract the benefits
            st.subheader("🔍 Extracted Benefits Summary")
            insurance_summary = ask_llm(
                f"Summarize the key policy benefits and coverage details from this insurance policy:\n\n{policy_text}"
            )
            st.write("🤖", insurance_summary)

        except Exception as e:
            st.error(f"Failed to process PDF: {e}")

    st.markdown("---")
    st.subheader("❓ Ask Insurance-Related Questions")

    insurance_q = st.text_input("Ask a question like:")
    st.caption("Examples: Do I need pre-authorization for dermatology? / Is COVID-19 hospitalization covered by Star Health?")
    
    if insurance_q:
        answer = ask_llm(
            f"The user asked an insurance-related question: \"{insurance_q}\"\n"
            f"If they mentioned a specific provider, answer accordingly. If they have no insurance, suggest relevant Indian government health schemes like Ayushman Bharat."
        )
        st.write("🤖", answer)

    st.markdown("---")
    st.subheader("🆘 No Insurance?")
    if st.button("Show Government Health Schemes"):
        govt_info = ask_llm(
            "The user has no health insurance. Suggest government schemes in India for medical coverage, including free or subsidized care."
        )
        st.write("🏥", govt_info)

# 🔬 Recommend Lab Tests
with tab5:
    test_symptoms = st.text_input("Describe your health issue (e.g., fatigue, hair loss)")
    if test_symptoms:
        prompt = (
            f"A patient reports the following symptoms: \"{test_symptoms}\".\n"
            f"Suggest a list of standard diagnostic lab tests they should consider.\n"
            f"Reply in a bullet list format."
        )
        test_recommendation = ask_llm(prompt)
        st.subheader("🧪 Recommended Lab Tests")
        st.write("🤖", test_recommendation)
