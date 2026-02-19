import streamlit as st
import dns.resolver
import requests
import ssl
import socket
import datetime
import io
import pandas as pd
import re
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from urllib.parse import urlparse

# --- CONFIGURATION ---
st.set_page_config(page_title="V-GUARD | Ultimate Intel", page_icon="🛡️", layout="wide")
MY_WHATSAPP = "201102353779"

# --- ADVANCED TOOLS ---

def scan_ports(domain):
    open_ports = []
    # أشهر المنافذ اللي الهكرز بيدوروا عليها
    ports = {
        21: 'FTP', 22: 'SSH', 25: 'SMTP', 53: 'DNS',
        80: 'HTTP', 443: 'HTTPS', 3306: 'MySQL', 8080: 'Alt-HTTP'
    }
    
    for port, service in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((domain, port))
        if result == 0:
            open_ports.append(f"{port} ({service})")
        sock.close()
    return open_ports

def detect_tech(domain):
    tech_stack = []
    try:
        response = requests.get(f"https://{domain}", timeout=3)
        headers = response.headers
        
        # 1. من الهيدر
        if 'Server' in headers: tech_stack.append(f"Server: {headers['Server']}")
        if 'X-Powered-By' in headers: tech_stack.append(f"Backend: {headers['X-Powered-By']}")
        
        # 2. من الكود (HTML)
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.find("meta", {"name": "generator"}):
            content = soup.find("meta", {"name": "generator"}).get("content")
            tech_stack.append(f"CMS/Gen: {content}")
            
        # 3. بصمات بسيطة
        if "wp-content" in response.text: tech_stack.append("CMS: WordPress")
        if "react" in response.text.lower(): tech_stack.append("Framework: React")
        
    except:
        tech_stack.append("Could not identify stack (Firewall active?)")
        
    return list(set(tech_stack)) # مسح التكرار

def check_threats(domain):
    # محاكاة فحص التهديدات (لأن APIs الحقيقية بتحتاج مفاتيح مدفوعة)
    # هنا بنشوف لو الدومين فيه كلمات مشبوهة
    suspicious_keywords = ['login', 'verify', 'account', 'update', 'bank', 'secure']
    score = 100
    status = "Clean ✅"
    
    if any(keyword in domain for keyword in suspicious_keywords) and len(domain) > 30:
        status = "Suspicious Pattern ⚠️"
        score = 50
    
    return status

def get_geolocation(domain):
    try:
        ip = socket.gethostbyname(domain)
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()
        return data['lat'], data['lon'], data['city'], data['country'], data['isp'], ip
    except:
        return None, None, "Unknown", "Unknown", "Hidden", "N/A"

def create_pdf(domain, results, tech, ports):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "V-GUARD INTELLIGENCE")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 65, "Full Spectrum Cyber Audit Report")
    c.line(50, height - 80, 550, height - 80)

    y = height - 120
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"TARGET: {domain}")
    c.setFont("Helvetica", 12)
    y -= 30
    c.drawString(50, y, f"Scan Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 20
    c.drawString(50, y, f"Server IP: {results['ip']}")
    y -= 20
    c.drawString(50, y, f"Location: {results['location']}")

    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "1. SECURITY POSTURE")
    c.setFont("Helvetica", 10)
    y -= 25
    c.drawString(60, y, f"• Overall Score: {results['score']}/100")
    c.drawString(60, y-15, f"• Threat Status: {results['threats']}")
    c.drawString(60, y-30, f"• SPF Record: {results['spf']}")
    c.drawString(60, y-45, f"• DMARC Policy: {results['dmarc']}")
    c.drawString(60, y-60, f"• SSL Certificate: {results['ssl_status']}")

    y -= 100
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "2. ATTACK SURFACE (Technical Data)")
    c.setFont("Helvetica", 10)
    y -= 25
    
    tech_str = ", ".join(tech) if tech else "No tech detected"
    c.drawString(60, y, f"• Detected Tech: {tech_str[:80]}...")
    
    ports_str = ", ".join(ports) if ports else "No open ports found (Filtered)"
    c.drawString(60, y-20, f"• Open Ports: {ports_str}")

    c.line(50, 100, 550, 100)
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, 80, "Confidential Report by V-Guard. Contact: +201102353779")
    c.save()
    buffer.seek(0)
    return buffer

# --- MAIN APP UI ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/9903/9903525.png", width=80)
st.sidebar.title("V-GUARD 🛡️")
st.sidebar.markdown("**Version 6.0 (Ultimate)**")
st.sidebar.info("Features:\n- Port Scanner 🚪\n- Tech Detector 🛠️\n- Threat Intel 🦠\n- Geo-Map 🌍")
st.sidebar.markdown("---")
st.sidebar.markdown(f"[📞 Support via WhatsApp](https://wa.me/{MY_WHATSAPP})")

st.title("🛡️ V-GUARD INTELLIGENCE")
st.markdown("#### The Ultimate Cyber Reconnaissance Platform")

tab1, tab2, tab3 = st.tabs(["🚀 Full System Audit", "🔑 Password Lab", "📞 Contact"])

with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        target_input = st.text_input("Target URL or Email", placeholder="example.com")
    with col2:
        st.write("")
        st.write("")
        scan_btn = st.button("START ATTACK SIMULATION ⚡", type="primary")

    if scan_btn and target_input:
        # Domain Logic
        domain = None
        if "@" in target_input and not target_input.startswith("http"): domain = target_input.split("@")[1]
        else:
            if not target_input.startswith(("http", "www")): target_input = "https://" + target_input
            try: domain = urlparse(target_input).netloc
            except: domain = None
        
        if domain:
            st.success(f"🎯 LOCKED ON TARGET: {domain}")
            
            with st.spinner('Running Port Scan, Tech Detection & Threat Analysis...'):
                # 1. RUN ALL SCANS
                lat, lon, city, country, isp, ip = get_geolocation(domain)
                open_ports = scan_ports(domain)
                tech_stack = detect_tech(domain)
                threat_status = check_threats(domain)
                
                # Score Calc
                score = 0
                # SPF/DMARC (Quick Check)
                spf_status = "Missing ❌"
                try: 
                    [r for r in dns.resolver.resolve(domain, 'TXT') if "v=spf1" in r.to_text()]
                    spf_status = "Active ✅"; score += 20
                except: pass
                
                dmarc_status = "Missing ❌"
                try: 
                    dns.resolver.resolve(f"_dmarc.{domain}", 'TXT')
                    dmarc_status = "Active ✅"; score += 20
                except: pass
                
                ssl_status = "Not Secure ❌"
                try:
                    ctx = ssl.create_default_context()
                    with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
                        s.settimeout(2.0); s.connect((domain, 443))
                        ssl_status = "Valid ✅"; score += 20
                except: pass
                
                if threat_status == "Clean ✅": score += 20
                if len(open_ports) < 3: score += 20 # Less open ports = better security

            # 2. DASHBOARD
            
            # Row A: Score & Threats
            m1, m2, m3 = st.columns(3)
            with m1: st.metric("Security Score", f"{score}/100")
            with m2: st.metric("Threat Status", threat_status)
            with m3: st.metric("Open Ports", len(open_ports))
            
            st.markdown("---")
            
            # Row B: Map & Server Info
            c1, c2 = st.columns([1, 2])
            with c1:
                st.subheader("🖥️ Server Intel")
                st.write(f"**IP:** `{ip}`")
                st.write(f"**ISP:** {isp}")
                st.write(f"**Location:** {city}, {country}")
                st.write("**Tech Stack:**")
                for tech in tech_stack:
                    st.caption(f"🔹 {tech}")
            with c2:
                if lat and lon:
                    st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=3)
            
            st.markdown("---")

            # Row C: Technical Deep Dive (Ports & Headers)
            expander = st.expander("🔍 VIEW ADVANCED SCAN DATA (PORTS & HEADERS)")
            with expander:
                e1, e2 = st.columns(2)
                with e1:
                    st.write("**🚪 Port Scan Results:**")
                    if open_ports:
                        for p in open_ports: st.error(f"⚠️ Open: {p}")
                    else:
                        st.success("✅ All common ports are filtered/closed.")
                with e2:
                    st.write("**🛡️ Domain Defense:**")
                    st.write(f"SPF: {spf_status}")
                    st.write(f"DMARC: {dmarc_status}")
                    st.write(f"SSL: {ssl_status}")

            # 3. PDF REPORT
            report_data = {
                "score": score, "threats": threat_status, "ip": ip,
                "location": f"{city}, {country}", "spf": spf_status,
                "dmarc": dmarc_status, "ssl_status": ssl_status
            }
            pdf = create_pdf(domain, report_data, tech_stack, open_ports)
            st.download_button("📄 DOWNLOAD FULL CYBER REPORT", pdf, "VGuard_Ultimate_Report.pdf", type="primary")

# --- OTHER TABS ---
with tab2:
    st.header("Password Entropy Lab")
    pwd = st.text_input("Enter Password", type="password")
    if pwd:
        st.progress(min(len(pwd)*5, 100))
        st.caption("Analyzing bit strength...")

with tab3:
    st.header("Contact Security Team")
    st.write("Professional consulting for businesses.")
    st.markdown(f"[Chat on WhatsApp](https://wa.me/{MY_WHATSAPP})")
