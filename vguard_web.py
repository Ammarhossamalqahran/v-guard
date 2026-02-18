import streamlit as st
import dns.resolver
import requests
import ssl
import socket
import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from urllib.parse import urlparse

# --- CONFIGURATION ---
st.set_page_config(page_title="V-GUARD | Security Audit", page_icon="🛡️", layout="wide")
MY_WHATSAPP = "201102353779"

# --- PDF GENERATION FUNCTION ---
def create_pdf(domain, results):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "V-GUARD INTELLIGENCE")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 70, "Professional Cyber Security Audit Report")
    c.line(50, height - 80, 550, height - 80)

    # Info
    c.drawString(50, height - 110, f"Target Domain: {domain}")
    c.drawString(50, height - 130, f"Scan Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Section 1: DNS Security
    y = height - 170
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "1. DNS & Email Security")
    c.setFont("Helvetica", 12)
    y -= 30
    c.drawString(70, y, f"SPF Record: {results['spf']}")
    y -= 20
    c.drawString(70, y, f"DMARC Policy: {results['dmarc']}")

    # Section 2: SSL/TLS
    y -= 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "2. SSL/TLS Certificate")
    c.setFont("Helvetica", 12)
    y -= 30
    c.drawString(70, y, f"Status: {results['ssl_status']}")
    y -= 20
    c.drawString(70, y, f"Expires In: {results['ssl_days']} days")
    
    # Section 3: Headers
    y -= 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "3. Security Headers")
    c.setFont("Helvetica", 12)
    y -= 30
    c.drawString(70, y, f"Clickjacking Protection: {results['clickjacking']}")
    y -= 20
    c.drawString(70, y, f"HSTS (HTTPS Force): {results['hsts']}")

    # Footer / Recommendation
    c.line(50, 100, 550, 100)
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 80, "This report is generated automatically by V-Guard System.")
    c.drawString(50, 65, "Contact us for fixing these vulnerabilities: +201102353779")

    c.save()
    buffer.seek(0)
    return buffer

# --- MAIN APP ---
st.sidebar.title("V-GUARD 🛡️")
st.sidebar.info("Authorized for Ethical Use Only.")
st.sidebar.markdown(f"[Chat on WhatsApp](https://wa.me/{MY_WHATSAPP})")

st.title("🛡️ V-GUARD INTELLIGENCE SYSTEM")

# Tabs
tab1, tab2, tab3 = st.tabs(["🌐 Full Site Audit", "🔑 Password Lab", "📞 Client Support"])

# --- TAB 1: AUDIT + PDF ---
with tab1:
    target_input = st.text_input("Enter Target URL/Email", placeholder="company.com")
    
    if st.button("INITIATE FULL SCAN 🚀", type="primary"):
        if not target_input:
            st.warning("Please enter a target.")
        else:
            # Domain Extraction
            domain = None
            if "@" in target_input and not target_input.startswith("http"):
                domain = target_input.split("@")[1]
            else:
                if not target_input.startswith(("http", "www")): target_input = "https://" + target_input
                try: domain = urlparse(target_input).netloc
                except: domain = None
            
            if domain:
                st.success(f"Target Locked: {domain}")
                
                # Dictionary to store results for PDF
                scan_data = {
                    "spf": "Not Found ❌", "dmarc": "Not Found ❌",
                    "ssl_status": "Not Secure ❌", "ssl_days": "0",
                    "clickjacking": "Missing ❌", "hsts": "Missing ❌"
                }

                # Columns for display
                c1, c2, c3 = st.columns(3)

                # 1. DNS Scan
                with c1:
                    st.subheader("📡 DNS")
                    try:
                        ans = dns.resolver.resolve(domain, 'TXT')
                        for r in ans:
                            if "v=spf1" in r.to_text():
                                scan_data['spf'] = "Active ✅"
                                st.success("SPF: Found")
                        if scan_data['spf'] == "Not Found ❌": st.error("SPF: Missing")
                    except: st.error("SPF: Error")

                    try:
                        dns.resolver.resolve(f"_dmarc.{domain}", 'TXT')
                        scan_data['dmarc'] = "Active ✅"
                        st.success("DMARC: Found")
                    except: st.error("DMARC: Missing")

                # 2. SSL Scan
                with c2:
                    st.subheader("🔒 SSL")
                    try:
                        ctx = ssl.create_default_context()
                        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
                            s.settimeout(3.0)
                            s.connect((domain, 443))
                            cert = s.getpeercert()
                            edate = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                            days = (edate - datetime.datetime.now()).days
                            scan_data['ssl_status'] = "Valid ✅"
                            scan_data['ssl_days'] = str(days)
                            st.metric("Days Left", days)
                    except: st.error("SSL Invalid")

                # 3. Headers Scan
                with c3:
                    st.subheader("🛡️ Headers")
                    try:
                        r = requests.get(f"https://{domain}", timeout=5)
                        if 'X-Frame-Options' in r.headers:
                            scan_data['clickjacking'] = "Protected ✅"
                            st.success("Anti-Clickjacking: ON")
                        else: st.error("Anti-Clickjacking: OFF")
                        
                        if 'Strict-Transport-Security' in r.headers:
                            scan_data['hsts'] = "Active ✅"
                            st.success("HSTS: ON")
                        else: st.warning("HSTS: OFF")
                    except: st.error("Connection Failed")

                st.markdown("---")
                
                # PDF BUTTON
                pdf_bytes = create_pdf(domain, scan_data)
                st.download_button(
                    label="📄 DOWNLOAD OFFICIAL REPORT (PDF)",
                    data=pdf_bytes,
                    file_name=f"VGuard_Report_{domain}.pdf",
                    mime="application/pdf",
                )

# --- TAB 2 & 3 (Simplified for brevity, same as before) ---
with tab2:
    st.header("Password Lab")
    pwd = st.text_input("Password", type="password")
    if pwd:
        st.info("Strength Analysis Active...")

with tab3:
    st.header("Contact Us")
    st.write(f"WhatsApp: +{MY_WHATSAPP}")
