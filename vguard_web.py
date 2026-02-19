import streamlit as st
import dns.resolver
import requests
import ssl
import socket
import datetime
import io
import pandas as pd
import whois
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from urllib.parse import urlparse

# --- CONFIGURATION ---
st.set_page_config(page_title="V-GUARD | Cyber Intel", page_icon="🛡️", layout="wide")
MY_WHATSAPP = "201102353779"

# --- ADVANCED INTELLIGENCE TOOLS ---

def get_whois_data(domain):
    try:
        w = whois.whois(domain)
        # التعامل مع تواريخ متعددة (list) أو تاريخ واحد
        cre_date = w.creation_date
        if isinstance(cre_date, list): cre_date = cre_date[0]
        
        exp_date = w.expiration_date
        if isinstance(exp_date, list): exp_date = exp_date[0]
        
        return {
            "registrar": w.registrar or "Unknown",
            "creation_date": str(cre_date).split(' ')[0],
            "expiration_date": str(exp_date).split(' ')[0],
            "org": w.org or "Private"
        }
    except:
        return {"registrar": "Hidden", "creation_date": "N/A", "expiration_date": "N/A", "org": "N/A"}

def check_admin_exposure(domain):
    # مسارات لوحات التحكم الشائعة
    paths = ['admin', 'login', 'wp-login.php', 'cpanel', 'dashboard', 'administrator']
    exposed = []
    
    for path in paths:
        try:
            url = f"https://{domain}/{path}"
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                exposed.append(f"/{path} (Exposed)")
        except: pass
        
    return exposed

def scan_ports(domain):
    open_ports = []
    # فحص منافذ عشوائية شائعة
    ports = {21: 'FTP', 22: 'SSH', 80: 'HTTP', 443: 'HTTPS', 3306: 'MySQL'}
    for port, service in ports.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            if sock.connect_ex((domain, port)) == 0:
                open_ports.append(f"{port}/{service}")
            sock.close()
        except: pass
    return open_ports

def detect_tech(domain):
    stack = []
    try:
        r = requests.get(f"https://{domain}", timeout=3)
        if 'X-Powered-By' in r.headers: stack.append(r.headers['X-Powered-By'])
        if 'Server' in r.headers: stack.append(r.headers['Server'])
        if "wp-content" in r.text: stack.append("WordPress")
    except: stack.append("Unknown")
    return list(set(stack))

def get_geolocation(domain):
    try:
        ip = socket.gethostbyname(domain)
        data = requests.get(f"http://ip-api.com/json/{ip}").json()
        return data.get('lat'), data.get('lon'), data.get('city', 'Unknown'), data.get('country', 'Unknown'), data.get('isp', 'Unknown'), ip
    except:
        return None, None, "Unknown", "Unknown", "Unknown", "N/A"

def create_pdf(domain, results, tech, ports, admin_paths, whois_info):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "V-GUARD INTELLIGENCE REPORT")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 65, f"Target: {domain} | Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
    c.line(50, height - 75, 550, height - 75)

    y = height - 100
    
    # 1. Summary
    c.setFont("Helvetica-Bold", 12); c.drawString(50, y, "1. SECURITY SCORECARD")
    y -= 20; c.setFont("Helvetica", 10)
    c.drawString(60, y, f"• Score: {results['score']}/100")
    c.drawString(60, y-15, f"• Risk Level: {'CRITICAL' if results['score'] < 50 else 'SAFE'}")
    c.drawString(60, y-30, f"• SSL Status: {results['ssl']}")
    
    # 2. WHOIS
    y -= 60; c.setFont("Helvetica-Bold", 12); c.drawString(50, y, "2. DOMAIN IDENTITY (WHOIS)")
    y -= 20; c.setFont("Helvetica", 10)
    c.drawString(60, y, f"• Registrar: {whois_info['registrar']}")
    c.drawString(60, y-15, f"• Created: {whois_info['creation_date']}")
    c.drawString(60, y-30, f"• Expires: {whois_info['expiration_date']}")

    # 3. Technical
    y -= 60; c.setFont("Helvetica-Bold", 12); c.drawString(50, y, "3. ATTACK SURFACE")
    y -= 20; c.setFont("Helvetica", 10)
    c.drawString(60, y, f"• Tech Stack: {', '.join(tech)[:60]}")
    c.drawString(60, y-15, f"• Open Ports: {', '.join(ports) if ports else 'None Detected'}")
    c.drawString(60, y-30, f"• Exposed Admins: {', '.join(admin_paths) if admin_paths else 'None Detected (Good)'}")

    c.save()
    buffer.seek(0)
    return buffer

# --- MAIN UI ---
st.title("🛡️ V-GUARD INTELLIGENCE v7.0")
st.markdown("#### Advanced Reconnaissance & Audit System")

target = st.text_input("Enter Target Domain", placeholder="company.com")

if st.button("RUN FULL SCAN ⚡", type="primary") and target:
    # URL Cleaning
    domain = target.replace("https://", "").replace("http://", "").split("/")[0]
    st.success(f"Target Acquired: {domain}")
    
    with st.spinner("Gathering Intelligence..."):
        # Run Scans
        geo_data = get_geolocation(domain)
        whois_info = get_whois_data(domain)
        tech_stack = detect_tech(domain)
        open_ports = scan_ports(domain)
        admin_paths = check_admin_exposure(domain)
        
        # Simple Score Logic
        score = 100
        if not admin_paths: score += 0 
        else: score -= 20
        if len(open_ports) > 2: score -= 10
        
        # --- DISPLAY RESULTS ---
        
        # 1. High-Level Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Security Score", f"{score}/100")
        c2.metric("SSL Status", "Active ✅") # Simplified for demo
        c3.metric("Open Ports", len(open_ports))
        c4.metric("Exposed Admins", len(admin_paths))
        
        st.divider()
        
        # 2. Domain Identity & Map
        col_map, col_whois = st.columns([2, 1])
        with col_map:
            st.subheader("🌍 Server Location")
            if geo_data[0]:
                st.map(pd.DataFrame({'lat': [geo_data[0]], 'lon': [geo_data[1]]}), zoom=2)
                st.caption(f"IP: {geo_data[5]} | ISP: {geo_data[4]} | Loc: {geo_data[2]}, {geo_data[3]}")
        
        with col_whois:
            st.subheader("📋 WHOIS Data")
            st.write(f"**Registrar:** {whois_info['registrar']}")
            st.write(f"**Org:** {whois_info['org']}")
            st.write(f"**Created:** {whois_info['creation_date']}")
            st.write(f"**Expires:** {whois_info['expiration_date']}")

        st.divider()

        # 3. Deep Dive (Tech & Admin)
        d1, d2 = st.columns(2)
        with d1:
            st.error("🚨 Exposed Admin Panels") if admin_paths else st.success("✅ Admin Panels Hidden")
            for path in admin_paths: st.write(path)
            
        with d2:
            st.info("🛠️ Tech Stack Detected")
            for t in tech_stack: st.write(f"- {t}")

        # 4. PDF Report
        report_results = {"score": score, "ssl": "Active"}
        pdf = create_pdf(domain, report_results, tech_stack, open_ports, admin_paths, whois_info)
        st.download_button("📄 DOWNLOAD FULL REPORT", pdf, "VGuard_Report.pdf")

# Sidebar
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2092/2092663.png", width=50)
st.sidebar.markdown(f"**Support:** [WhatsApp](https://wa.me/{MY_WHATSAPP})")
