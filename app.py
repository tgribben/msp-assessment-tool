import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="MSP Insight Engine", page_icon="🛡️", layout="wide")

# --- SIDEBAR (SETTINGS) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/900/900782.png", width=100) # Placeholder Logo
    st.title("Settings")
    
    # Securely get API Key
    if 'GOOGLE_API_KEY' in st.secrets:
        api_key = st.secrets['GOOGLE_API_KEY']
    else:
        api_key = st.text_input("Enter Google API Key", type="password")
        
    st.info("✅ Standardized Assessment Form Mode")

# --- MAIN APP LOGIC ---
st.title("🛡️ MSP Technology Assessment Tool")
st.markdown("Select the current state of the client's environment below.")

# --- THE ASSESSMENT FORM ---

# SECTION 1: CLIENT DETAILS
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Name", placeholder="Acme Manufacturing")
        industry = st.selectbox("Industry", ["Manufacturing", "Healthcare", "Legal", "Finance", "Retail", "Non-Profit", "Other"])
    with col2:
        compliance_target = st.selectbox("Compliance Target", ["General Security Best Practice", "ISO 27001", "NIST 800-171 (CMMC)", "HIPAA", "FTC Safeguards", "Cyber Insurance Renewal"])
        staff_count = st.number_input("Staff Count", min_value=1, value=25)

st.markdown("---")

# SECTION 2: INFRASTRUCTURE (DROPDOWNS)
with st.expander("Step 1: Infrastructure & Hardware", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        server_status = st.selectbox("Server Status", [
            "Cloud Only (SharePoint/Azure/AWS)", 
            "Hybrid (Cloud + On-Prem)", 
            "On-Premise Only (Legacy)",
            "No Server / Peer-to-Peer"
        ])
        
        server_os = st.multiselect("Server OS Versions Found", [
            "Windows Server 2022 (Current)",
            "Windows Server 2019 (Current)",
            "Windows Server 2016 (Aging)",
            "Windows Server 2012 R2 (EOL - Critical Risk)",
            "Windows Server 2008 or Older (EOL - Critical Risk)",
            "Linux",
            "N/A"
        ])

    with c2:
        workstation_age = st.selectbox("Average Workstation Age", [
            "< 3 Years (Modern)", 
            "3-5 Years (Aging)", 
            "5+ Years (Obsolete/Slow)", 
            "Mixed / Unknown"
        ])
        
        email_platform = st.selectbox("Email Platform", [
            "Microsoft 365 (Business Premium)", 
            "Microsoft 365 (Standard/Basic)",
            "Google Workspace", 
            "On-Premise Exchange (High Risk)",
            "POP3 / IMAP (ISP Email)"
        ])

# SECTION 3: SECURITY POSTURE
with st.expander("Step 2: Security Layer", expanded=False):
    c3, c4 = st.columns(2)
    with c3:
        firewall = st.selectbox("Firewall / Edge", [
            "Next-Gen (Fortinet, Palo Alto, SonicWall Gen7)", 
            "Legacy Enterprise (Old SonicWall, Cisco ASA)", 
            "ISP Modem / Consumer Router (Best Buy)", 
            "None / Unknown"
        ])
        
        backups = st.selectbox("Backup Strategy", [
            "Image-Based + Cloud (Immutable)", 
            "Local Only (USB/NAS)", 
            "File-Level Only (Carbonite/Dropbox)",
            "No Backups Found"
        ])
        
    with c4:
        mfa_status = st.selectbox("MFA (Multi-Factor Auth) Status", [
            "Enforced on All Users", 
            "Enforced on Admin Only", 
            "Optional / Inconsistent", 
            "Not Enabled"
        ])
        
        security_tools = st.multiselect("Existing Security Tools Detected", [
            "Managed Antivirus (Standard)",
            "EDR/MDR (SentinelOne, CrowdStrike, Huntress)",
            "DNS Filtering (Cisco Umbrella)",
            "Email Security (Proofpoint, Avanan, IronScales)",
            "SIEM / Log Collection",
            "None / Windows Defender Only"
        ])

# SECTION 4: ADDITIONAL CONTEXT
with st.expander("Step 3: Specific Observations (Optional)", expanded=False):
    extra_notes = st.text_area("Any specific 'Gotchas' or unique apps? (e.g., 'Uses QuickBooks 2018', 'Staff shares passwords')", height=100)


# --- AI GENERATION LOGIC ---
def generate_report(api_key, client, industry, target, infra_data):
    try:
        # Try latest model first, fallback to standard pro
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
        except:
            model = genai.GenerativeModel('gemini-1.5-flash-002')
            
        genai.configure(api_key=api_key)
        
        # We construct a readable string from the dropdown data for the AI
        prompt = f"""
        You are a Senior vCISO for a top-tier MSP. 
        Create a formal Technology Assessment Report for:
        Client: {client}
        Industry: {industry}
        Target Framework: {target}
        
        ASSESSMENT DATA:
        - Server Infrastructure: {infra_data['server_status']}
        - Server OS Details: {', '.join(infra_data['server_os'])}
        - Workstation Age: {infra_data['workstation_age']}
        - Email System: {infra_data['email_platform']}
        - Firewall: {infra_data['firewall']}
        - Backup System: {infra_data['backups']}
        - MFA Status: {infra_data['mfa_status']}
        - Security Stack: {', '.join(infra_data['security_tools'])}
        - Additional Notes: {infra_data['extra_notes']}
        
        INSTRUCTIONS:
        1. Analyze the dropdown data. If they selected "Windows 2012" or "No MFA", flag these as CRITICAL RISKS immediately.
        2. Tone: Professional, consultative, urgency without fear-mongering.
        3. Compare their current stack against the '{target}' requirements.
        
        STRUCTURE:
        ## Executive Summary
        (2-3 sentences max. High-level verdict.)
        
        ## Scorecard (Use Emojis)
        - Infrastructure: [Score/Status]
        - Security: [Score/Status]
        - Compliance Readiness: [Score/Status]
        
        ## Critical Risk Analysis
        (Identify top 3 gaps based on the dropdowns. Explain Business Impact.)
        
        ## Recommended Roadmap
        (Phase 1: Immediate Fixes, Phase 2: Modernization)
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- GENERATE BUTTON ---
if st.button("🚀 Generate Assessment Report", type="primary"):
    if not api_key:
        st.error("Please enter an API Key in the sidebar.")
    else:
        # Package the data
        infra_data = {
            "server_status": server_status,
            "server_os": server_os,
            "workstation_age": workstation_age,
            "email_platform": email_platform,
            "firewall": firewall,
            "backups": backups,
            "mfa_status": mfa_status,
            "security_tools": security_tools,
            "extra_notes": extra_notes
        }
        
        with st.spinner("Analyzing configuration against industry standards..."):
            report_content = generate_report(api_key, client_name, industry, compliance_target, infra_data)
            
            st.success("Analysis Complete!")
            st.markdown("---")
            st.markdown(report_content)
            
            st.download_button(
                label="📥 Download Report",
                data=report_content,
                file_name=f"{client_name}_Assessment.md",
                mime="text/markdown"
            )
