import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from urllib.parse import urlencode
import os
from dotenv import load_dotenv
from models import SessionLocal, User

load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "https://curebot-113207776071.us-central1.run.app"  # or your deployed URL

def login():
    if "email" in st.session_state:
        return
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": REDIRECT_URI,
        "access_type": "offline",
        "prompt": "consent"
    }
    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    st.markdown(f"[🔐 Login with Google]({auth_url})")

def handle_callback():
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]
        session = OAuth2Session(CLIENT_ID, CLIENT_SECRET, redirect_uri=REDIRECT_URI)

        try:
            token = session.fetch_token("https://oauth2.googleapis.com/token", code=code)
            session.token = token
            user_info = session.get("https://www.googleapis.com/oauth2/v2/userinfo").json()

            email = user_info.get("email")
            name = user_info.get("name", "")

            if not email:
                st.error("❌ Failed to get email from Google.")
                st.stop()

            db = SessionLocal()
            existing = db.query(User).filter_by(email=email).first()
            if not existing:
                db.add(User(email=email, name=name))
                db.commit()
            db.close()

            st.session_state["email"] = email
            st.session_state["name"] = name

            # ✅ Clear query parameters using new API
            st.query_params.clear()
            st.rerun()

        except Exception as e:
            st.error(f"Login error: {e}")
            st.stop()
