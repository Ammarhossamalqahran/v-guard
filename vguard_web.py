import streamlit as st
import dns.resolver
import requests
import ssl
import socket
import datetime
import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from urllib.parse import urlparse

# --- CONFIG ---
st.set_page_config(page_title="V-GUARD | OSINT Intel", page_icon="🛡️", layout="wide")
MY_WHATSAPP = "201102353779"

# --- OSINT FUNCTIONS ---
def get_advanced_intel(domain):
    intel = {}
    try:
        # 1. Geolocation & IP
        ip = socket.gethostbyname(domain)
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        intel.update({
            "ip": ip, "city": res.get('city'), "country": res.get('country'),
            "isp": res.get('isp'), "lat": res.get('lat'), "lon": res.get('lon')
        })
        
        # 2. MX Records (Mail Servers)
        mx_records = dns.resolver.resolve(domain, 'MX')
        intel['mail_servers'] = [str(r.exchange) for r in mx_records]
        
        # 3. Subdomains (Common Check)
        common_subs = ['www', 'mail', 'api', 'dev', 'staging', 'webmail']
        found_subs = []
        for sub in common_subs:
            try:
                socket.gethostbyname(f"{sub}.{domain}")
                found_subs.append(f"{sub}.{domain}")
            except: pass
        intel['subdomains'] = found_subs
        
    except: pass
    return intel

def create_pdf(domain, results):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, 750, "V-GUARD DEEP INTELLIGENCE REPORT")
    c.setFont("Helvetica", 10)
    c.drawString(50, 735, f"Target: {domain} | Generated: {datetime.datetime.now()}")
    c.line(50, 725, 550, 725)
    
    y = 700
    for section, data in results.items():
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"[{section}]")
        c.setFont("Helvetica", 10)
        y -= 20
        c.drawString(70, y, str(data))
        y -= 30
    c.save()
    buffer.seek(0)
    return buffer

# --- UI ---
st.title("🛡️ V-GUARD | DEEP INTEL")
tab1, tab2, tab3 = st.tabs(["🔍 Deep Audit", "🔑 Password Lab", "💬 Support"])

with tab1:
    target = st.text_input("Enter Target", placeholder="example.com")
    if st.button("RUN DEEP SCAN 🚀", type="primary"):
        if target:
            domain = urlparse(target).netloc if "://" in target else target.split("@")[-1] if "@" in target else target
            with st.spinner("Expanding Research..."):
                intel = get_advanced_intel(domain)
                
                # Layout
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.header("🌐 Core Intel")
                    st.metric("Target IP", intel.get('ip', 'N/A'))
                    st.write(f"**ISP:** {intel.get('isp')}")
                    st.write(f"**Location:** {intel.get('city')}, {intel.get('country')}")
                    
                    st.subheader("📬 Mail Infrastructure")
                    for srv in intel.get('mail_servers', []):
                        st.caption(f"MX: {srv}")

                with c2:
                    st.header("📍 Server Map")
                    if intel.get('lat'):
                        st.map(pd.DataFrame({'lat': [intel['lat']], 'lon': [intel['lon']]}))

                st.markdown("---")
                
                # Advanced Sections
                col_a, col_b = st.columns(2)
                with col_a:
                    st.subheader("📂 Discovered Subdomains")
                    if intel.get('subdomains'):
                        st.success(f"Found {len(intel['subdomains'])} subdomains")
                        for s in intel['subdomains']: st.code(s)
                    else: st.warning("No common subdomains found.")

                with col_b:
                    st.subheader("⚡ Security Score")
                    # فحص SPF/DMARC سريع للسكور
                    score = 0
                    try: 
                        dns.resolver.resolve(domain, 'TXT')
                        score += 50
                    except: pass
                    st.progress(score/100)
                    st.write(f"Security Rating: {score}%")

                # PDF
                pdf = create_pdf(domain, {"IP": intel.get('ip'), "ISP": intel.get('isp'), "Subdomains": intel.get('subdomains')})
                st.download_button("📄 Download Deep Report", pdf, file_name=f"VGuard_Deep_{domain}.pdf")

with tab3:
    st.link_button("Chat on WhatsApp 💬", f"https://wa.me/{MY_WHATSAPP}")
