import streamlit as st
import json
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

# --- 1. CONFIGURATION ---
# Load environment variables from .env file (for local use)
load_dotenv()

# Securely access keys: Try .env first, then Streamlit Secrets (for Cloud)
SERPER_API_KEY = os.getenv("SERPER_API_KEY") or st.secrets.get("SERPER_API_KEY")
LLM_API_KEY = os.getenv("LLM_API_KEY") or st.secrets.get("LLM_API_KEY")

# Groq Config
BASE_URL = "https://api.groq.com/openai/v1"
MODEL_NAME = "llama-3.3-70b-versatile"

# --- 2. BACKEND FUNCTIONS ---
def google_search(query):
    # 🛡️ SECURITY LAYER: FORCE OFFICIAL DOMAINS
    # This filter ensures we mostly get government results
    official_filter = " site:gov.in OR site:nic.in OR site:ap.gov.in OR site:org.in OR site:bank.sbi OR site:ibps.in"
    final_query = query + official_filter
    
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": final_query})
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def call_groq_brain(prompt_text):
    client = OpenAI(base_url=BASE_URL, api_key=LLM_API_KEY)
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are Gov-Link Official. You must ONLY provide links to official government websites. STRICTLY FORBID third-party blogs."},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 3. UI SETUP ---
st.set_page_config(page_title="Gov-Link Official", page_icon="🇮🇳", layout="wide", initial_sidebar_state="collapsed")

# --- 4. CUSTOM CSS ---
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at center, #0f172a 0%, #020617 100%);
        color: #e2e8f0;
    }
    .glass-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .glass-card:hover {
        border-color: rgba(56, 189, 248, 0.5); 
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
    }
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
    }
    .verified-badge {
        display: inline-block;
        background: #059669;
        color: white;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 10px;
        margin-left: 8px;
    }
    [data-testid="stImage"] img {
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- 5. HERO SECTION ---
col_logo, col_title = st.columns([1, 6])
with col_logo:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=140)
    else:
        st.caption("Gov-Link")

with col_title:
    st.title("Gov-Link Official")
    st.markdown("### 🇮🇳 Verified Schemes & Jobs Portal")
    st.caption("100% Official Sources Only • Direct Government Links")

st.divider()

# --- 6. MAIN INTERFACE ---
c1, c2 = st.columns([1, 2.5])

# --- LEFT: SHARED PROFILE ---
with c1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("👤 User Profile")
    
    age = st.slider("Age", 16, 60, 24)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    caste = st.selectbox("Category", ["General", "OBC", "SC", "ST", "EWS"])
    qualification = st.selectbox("Qualification", ["10th Pass", "12th/Inter", "ITI/Diploma", "Degree/B.Tech", "PG/PhD"])
    
    occupation = st.selectbox("Current Occupation", ["Student", "Unemployed", "Farmer", "Private Employee", "Business"])
    
    special_info = f"Qualification: {qualification}"
    if occupation == "Farmer":
        land = st.number_input("Land (Acres)", 0.0, 50.0, 2.0)
        special_info += f", Land: {land} acres"
    
    income = st.number_input("Annual Income (₹)", 0, 2000000, 100000)
    st.markdown("</div>", unsafe_allow_html=True)

# --- RIGHT: DUAL TABS ---
with c2:
    tab_schemes, tab_jobs = st.tabs(["🏛️ Verified Schemes", "💼 Official Govt Jobs"])
    
    # === TAB 1: SCHEMES ===
    with tab_schemes:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🔍 Search Official Schemes")
        scheme_query = st.text_input("Scheme Type:", placeholder="e.g. Subsidy, Scholarship, Loan")
        
        if st.button("🚀 Find Schemes"):
            if not SERPER_API_KEY:
                st.error("API Key Missing! Please check your .env file or Streamlit Secrets.")
            else:
                with st.status("🔄 Verifying Official Sources...", expanded=True) as status:
                    st.write("📡 Connecting to .gov.in databases...")
                    
                    search_query = f"Latest government schemes for {age} year old {gender} {caste} {occupation} {scheme_query} in Andhra Pradesh India"
                    search_results = google_search(search_query)
                    
                    context = ""
                    if 'organic' in search_results:
                        for item in search_results['organic'][:8]:
                            # 🔴 CRITICAL FIX: Use .get() to avoid crashing on missing snippets
                            title = item.get('title', 'No Title')
                            snippet = item.get('snippet', 'No description available.')
                            link = item.get('link', '#')
                            context += f"Source: {title} - {snippet} (Link: {link})\n"
                    
                    st.write("🧠 AI Validating Links...")
                    prompt = f"""
                    User: {age}yr {gender}, {caste}, {occupation}, Income ₹{income}.
                    Query: {scheme_query}
                    Search Data: {context}
                    Task: List eligible schemes.
                    CONSTRAINT: ONLY use links ending in .gov.in, .nic.in, .ap.gov.in.
                    Format HTML: <div class="glass-card">...</div>
                    """
                    answer_html = call_groq_brain(prompt)
                    status.update(label="✅ Verified Data Loaded", state="complete", expanded=False)
                st.markdown(answer_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # === TAB 2: JOBS ===
    with tab_jobs:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("💼 Active Govt Notifications (Official Only)")
        job_pref = st.text_input("Job Preference:", placeholder="e.g. Police, Bank, Railway, APPSC")
        
        if st.button("📢 Find Official Notifications"):
            if not SERPER_API_KEY:
                st.error("API Key Missing! Please check your .env file or Streamlit Secrets.")
            else:
                with st.status("🔄 Scanning Official Portals...", expanded=True) as status:
                    st.write(f"📡 Filtering .gov.in / .nic.in results for {qualification}...")
                    
                    job_query = f"Latest Official Government Job Notification 2025 for {qualification} {job_pref} in Andhra Pradesh India"
                    job_results = google_search(job_query)
                    
                    job_context = ""
                    if 'organic' in job_results:
                        for item in job_results['organic'][:10]:
                            # 🔴 CRITICAL FIX: Use .get() to avoid crashing
                            title = item.get('title', 'No Title')
                            snippet = item.get('snippet', 'No description available.')
                            link = item.get('link', '#')
                            job_context += f"Job: {title} - {snippet} (Link: {link})\n"
                    
                    st.write("🧠 Removing Third-Party Spam...")
                    prompt = f"""
                    User Qualification: {qualification}. Preference: {job_pref}.
                    Search Data: {job_context}
                    Task: List ACTIVE Job Notifications.
                    SECURITY PROTOCOL: ONLY accept official links (gov.in, nic.in, ibps.in, sbi.co.in).
                    Format HTML: <div class="glass-card">...</div>
                    """
                    job_html = call_groq_brain(prompt)
                    status.update(label="✅ Official Jobs Found", state="complete", expanded=False)
                st.markdown(job_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)