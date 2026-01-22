import streamlit as st
import google.generativeai as genai
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="MSP Insight Engine", page_icon="🛡️", layout="wide")

# --- SIDEBAR (SETTINGS) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/900/900782.png", width=100) # Placeholder Logo
    st.title("Settings")
    
    # Securely get API Key from Streamlit Secrets or User Input
    if 'GOOGLE_API_KEY' in st.secrets:
        api_key = st.secrets['GOOGLE_API_KEY']
    else:
        api_key = st.text_input("Enter Google API Key", type="password")
        
    st.info("💡 This tool transforms raw notes into client-ready executive reports.")

# --- MAIN APP LOGIC ---
st.title("🛡️ MSP Technology Assessment Tool")
st.markdown("Enter the client details below to generate an **Executive Risk Report**.")

# 1. INPUT FORM
col1, col2 = st.columns(2)
with col1:
    client_name = st.text_input("Client Name", placeholder="Acme Manufacturing")
    industry = st.selectbox("Industry", ["Manufacturing", "Healthcare", "Legal", "Finance", "Retail", "Other"])
with col2:
    compliance_target = st.selectbox("Compliance Target", ["General Security Best Practice", "ISO 27001", "NIST 800-171 (CMMC)", "HIPAA", "FTC Safeguards"])
    staff_count = st.number_input("Staff Count", min_value=1, value=50)

st.subheader("📝 Technician Notes")
raw_notes = st.text_area(
    "Paste raw inventory, observations, or scan results here:", 
    height=200, 
    placeholder="Example:\n- Server 2012 in the closet (hot)\n- Users share passwords\n- No MFA on O365\n- Backups are on a USB drive"
)

# 2. THE AI BRAIN
def generate_report(api_key, client, industry, target, notes):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro') # Free, fast model
        
        prompt = f"""
        You are a Senior vCISO for a top-tier MSP. 
        Create a formal Technology Assessment Report for:
        Client: {client}
        Industry: {industry}
        Target Framework: {target}
        
        Technician Notes:
        {notes}
        
        INSTRUCTIONS:
        1. Analyze the notes for risks relative to the Industry and Target Framework.
        2. Tone: Professional, consultative, urgency without fear-mongering.
        3. Output Format: Markdown.
        
        STRUCTURE:
        ## Executive Summary
        (2-3 sentences max. High-level verdict.)
        
        ## Critical Risk Analysis
        (Identify top 3 gaps. For each gap, explain the 'Business Impact' - why they lose money or reputation.)
        
        ## Strategic Roadmap
        (Phase 1: Immediate Remediation, Phase 2: Modernization)
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# 3. GENERATE BUTTON
if st.button("🚀 Generate Assessment Report", type="primary"):
    if not api_key:
        st.error("Please enter an API Key in the sidebar to proceed.")
    elif not raw_notes:
        st.warning("Please enter some technician notes first.")
    else:
        with st.spinner("Analyzing infrastructure & cross-referencing compliance standards..."):
            report_content = generate_report(api_key, client_name, industry, compliance_target, raw_notes)
            
            # Display Result
            st.success("Assessment Complete!")
            st.markdown("---")
            st.markdown(report_content)
            
            # Download Button
            st.download_button(
                label="📥 Download Report as Text",
                data=report_content,
                file_name=f"{client_name}_Assessment.md",
                mime="text/markdown"
            )
