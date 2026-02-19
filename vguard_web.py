import streamlit as st
import dns.resolver
import requests
import ssl
import socket
import datetime
import io
import re
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from urllib.parse import urlparse, quote

# --- CONFIGURATION ---
st.set_page_config(page_title="V-GUARD | Security Audit", page_icon="🛡️", layout="wide")
MY_WHATSAPP = "201102353779"
MY_EMAIL = "amarhossam0000@gmail.com"

# --- PDF GENERATION FUNCTION ---
def create_pdf(domain, results, server_info):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "V-GUARD INTELLIGENCE")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 70, "Professional Cyber Security Audit Report")
    c.line(50, height - 80, 550, height - 80)

    # General Info
    c.drawString(50, height - 110, f"Target Domain: {domain}")
    c.drawString(50, height - 125, f"Scan Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.drawString(50, height - 140, f"Server IP: {server_info.get('ip', 'N/A')}")
    c.drawString(50, height - 155, f"Location: {server_info.get('city', 'N/A')}, {server_info.get('country', 'N/A')}")
    
    # Section 1: DNS Security
    y = height - 200
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "1. DNS & Email Security")
    c.setFont("Helvetica", 12)
    y -= 25
    c.drawString(70, y, f"SPF Record: {results['spf']}")
    y -= 20
    c.drawString(70, y, f"DMARC Policy: {results['dmarc']}")

    # Section 2: SSL/TLS
    y -= 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "2. SSL/TLS Certificate")
    c.setFont("Helvetica", 12)
    y -= 25
    c.drawString(70, y, f"Status: {results['ssl_status']}")
    y -= 20
    c.drawString(70, y, f"Expires In: {results['ssl_days']} days")
    
    # Section 3: Headers
    y -= 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "3. Security Headers")
    c.setFont("Helvetica", 12)
    y -= 25
    c.drawString(70, y, f"Clickjacking Protection: {results['clickjacking']}")
    y -= 20
    c.drawString(70, y, f"HSTS (HTTPS Force): {results['hsts']}")

    # Footer
    c.line(50, 100, 550, 100)
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 80, "This report is generated automatically by V-Guard System.")
    c.drawString(50, 65, f"Contact us for fixing these vulnerabilities: +{MY_WHATSAPP}")

    c.save()
    buffer.seek(0)
    return buffer

# --- SIDEBAR ---
with st.sidebar:
    st.title("V-GUARD 🛡️")
    st.info("System Online v5.0")
    st.markdown(f"[Chat on WhatsApp](https://wa.me/{MY_WHATSAPP})")
    st.write("---")
    st.caption("Authored by Ammar Hossam")

# --- MAIN APP ---
st.title("🛡️ V-GUARD INTELLIGENCE SYSTEM")
st.markdown("#### Advanced Cyber Reconnaissance & Audit Tool")

# Tabs
tab1, tab2, tab3 = st.tabs(["🌐 Full Site Audit", "🔑 Password Lab", "📞 Client Support"])

# =========================================
# TAB 1: AUDIT + TRACKER + PDF
# =========================================
with tab1:
    target_input = st.text_input("Enter Target URL/Email", placeholder="company.com")
    
    if st.button("INITIATE FULL SCAN 🚀", type="primary"):
        if not target_input:
            st.warning("⚠️ Please enter a target.")
        else:
            # 1. Domain Extraction
            domain = None
            if "@" in target_input and not target_input.startswith("http"):
                domain = target_input.split("@")[1]
            else:
                if not target_input.startswith(("http", "www")): target_input = "https://" + target_input
                try: domain = urlparse(target_input).netloc
                except: domain = None
            
            if domain:
                st.success(f"🎯 Target Locked: {domain}")
                
                # Dictionary to store results for PDF
                scan_data = {
                    "spf": "Not Found ❌", "dmarc": "Not Found ❌",
                    "ssl_status": "Not Secure ❌", "ssl_days": "0",
                    "clickjacking": "Missing ❌", "hsts": "Missing ❌"
                }
                server_data = {"ip": "N/A", "city": "N/A", "country": "N/A"}

                # --- A. SERVER TRACKER (GEO LOCATION) ---
                st.markdown("### 🌍 Server Intelligence")
                try:
                    ip_address = socket.gethostbyname(domain)
                    server_data['ip'] = ip_address
                    
                    # Fetch Geo Info
                    try:
                        geo = requests.get(f"http://ip-api.com/json/{ip_address}").json()
                        if geo['status'] == 'success':
                            server_data['city'] = geo['city']
                            server_data['country'] = geo['country']
                            
                            c1, c2 = st.columns([1, 2])
                            with c1:
                                st.info(f"**IP:** {ip_address}")
                                st.info(f"**ISP:** {geo['isp']}")
                                st.info(f"**Loc:** {geo['city']}, {geo['country']}")
                            with c2:
                                # Map Visualization
                                map_df = pd.DataFrame({'lat': [geo['lat']], 'lon': [geo['lon']]})
                                st.map(map_df, zoom=3)
                        else:
                            st.warning(f"Could not fetch detailed location for IP: {ip_address}")
                    except:
                        st.warning("Geo-location service unavailable.")
                except:
                    st.error("❌ Could not resolve domain to IP.")
                
                st.markdown("---")

                # --- B. SECURITY SCANNING ---
                c1, c2, c3 = st.columns(3)

                # 1. DNS Scan
                with c1:
                    st.subheader("📡 DNS Security")
                    try:
                        ans = dns.resolver.resolve(domain, 'TXT')
                        for r in ans:
                            if "v=spf1" in r.to_text():
                                scan_data['spf'] = "Active ✅"
                                st.success("✅ SPF: Found")
                        if scan_data['spf'] == "Not Found ❌": st.error("❌ SPF: Missing")
                    except: st.error("❌ SPF: Not Found")

                    try:
                        dns.resolver.resolve(f"_dmarc.{domain}", 'TXT')
                        scan_data['dmarc'] = "Active ✅"
                        st.success("✅ DMARC: Found")
                    except: st.error("⚠️ DMARC: Missing")

                # 2. SSL Scan
                with c2:
                    st.subheader("🔒 SSL/TLS")
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
                            if days < 30: st.warning(f"⚠️ Expires in {days} days")
                            else: st.success(f"✅ Valid ({days} days)")
                    except: st.error("❌ SSL Invalid/Http Only")

                # 3. Headers Scan
                with c3:
                    st.subheader("🛡️ HTTP Headers")
                    try:
                        r = requests.get(f"https://{domain}", timeout=5)
                        if 'X-Frame-Options' in r.headers:
                            scan_data['clickjacking'] = "Protected ✅"
                            st.success("✅ Clickjacking: Safe")
                        else: st.error("❌ Clickjacking: Risk")
                        
                        if 'Strict-Transport-Security' in r.headers:
                            scan_data['hsts'] = "Active ✅"
                            st.success("✅ HSTS: Active")
                        else: st.warning("⚠️ HSTS: Inactive")
                    except: st.error("❌ Connection Failed")

                st.markdown("---")
                
                # --- C. PDF REPORT ---
                st.subheader("📄 Report Generation")
                pdf_bytes = create_pdf(domain, scan_data, server_data)
                st.download_button(
                    label="DOWNLOAD OFFICIAL V-GUARD REPORT (PDF)",
                    data=pdf_bytes,
                    file_name=f"VGuard_Report_{domain}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

# =========================================
# TAB 2: PASSWORD LAB
# =========================================
with tab2:
    st.header("Password Strength Analysis")
    password = st.text_input("Enter Password", type="password")
    if st.button("ANALYZE STRENGTH 🔐"):
        score = 0
        feedback = []
        if len(password) >= 8: score += 1
        else: feedback.append("❌ Too Short (Min 8 chars)")
        if re.search(r"[A-Z]", password): score += 1
        else: feedback.append("⚠️ Add Uppercase")
        if re.search(r"[0-9]", password): score += 1
        else: feedback.append("⚠️ Add Numbers")
        if re.search(r"[!@#$%^&*]", password): score += 1
        else: feedback.append("⚠️ Add Symbols")

        if score == 4:
            st.success("🛡️ STATUS: UNBREAKABLE")
            st.progress(100)
        elif score >= 2:
            st.warning("⚠️ STATUS: MODERATE")
            st.progress(50)
        else:
            st.error("❌ STATUS: WEAK")
            st.progress(25)
        for tip in feedback: st.write(tip)

# =========================================
# TAB 3: CONTACT
# =========================================
with tab3:
    st.header("📞 Get Professional Support")
    c1, c2 = st.columns(2)
    with c1:
        st.info("Chat directly with V-Guard Team")
        st.link_button("Start WhatsApp Chat 💬", f"https://wa.me/{MY_WHATSAPP}")
    with c2:
        st.info("Request Detailed Audit via Email")
        subject = quote("V-Guard Security Request")
        body = quote("I need help securing my domain...")
        st.link_button("Send Email 📧", f"mailto:{MY_EMAIL}?subject={subject}&body={body}")
