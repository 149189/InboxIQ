# streamlit_app.py
import streamlit as st
import requests

# set this to your backend
BACKEND_URL = "http://localhost:8000"

# Helper that safely returns JSON or error info
def safe_post(path, payload):
    url = BACKEND_URL + path
    try:
        res = requests.post(url, json=payload, timeout=15)
    except Exception as e:
        return {"ok": False, "error": f"Request failed: {e}", "status": None, "text": None}

    # Provide full debug info if not JSON
    ct = res.headers.get("Content-Type", "")
    if "application/json" in ct:
        try:
            return {"ok": True, "status": res.status_code, "json": res.json()}
        except Exception as e:
            return {"ok": False, "error": f"JSON parse error: {e}", "status": res.status_code, "text": res.text}
    else:
        # not JSON (likely HTML 404/500)
        return {"ok": False, "error": "Non-JSON response", "status": res.status_code, "text": res.text[:2000]}

def register_user(username, password):
    return safe_post("/auth_app/register/", {"username": username, "password": password})

def login_user(username, password):
    return safe_post("/auth_app/login/", {"username": username, "password": password})

def compose_llm(user_id, prompt):
    # matches /inboxiq_llm/compose/ from scaffold
    return safe_post("/inboxiq_llm/compose/", {"user_id": user_id, "prompt": prompt, "tone": "concise"})

# Streamlit UI
st.title("InboxIQ Backend Tester")

with st.expander("Auth"):
    st.subheader("Register / Login")
    u = st.text_input("Username", value="demo")
    p = st.text_input("Password", value="password123", type="password")
    if st.button("Register"):
        r = register_user(u, p)
        st.write(r)
    if st.button("Login"):
        r = login_user(u, p)
        st.write(r)
        # login in your scaffold returns JSON with id/username on success
        if r.get("ok") and r["json"].get("id"):
            st.session_state.user_id = r["json"]["id"]
            st.success("Logged in")

with st.expander("LLM / Compose"):
    prompt = st.text_area("Prompt", value="Draft a follow-up to Priya about the Q3 report.")
    user_id = st.session_state.get("user_id")
    if st.button("Compose Drafts"):
        if not user_id:
            st.error("Login first (obtain user_id).")
        else:
            r = compose_llm(user_id, prompt)
            st.write(r)
            if r.get("ok"):
                st.json(r["json"])
            else:
                st.error(f"Error: {r.get('error')}, status={r.get('status')}")
                if r.get("text"):
                    st.code(r["text"][:1000])
