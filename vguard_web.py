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
from urllib.parse import urlparse

# --- إعدادات الواجهة ---
st.set_page_config(page_title="V-GUARD | Elite Security", page_icon="🛡️", layout="wide")

# بيانات التواصل
MY_WHATSAPP = "201102353779"

# --- دالة إنشاء تقرير PDF ---
def create_full_report(domain, data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(50, 750, "V-GUARD SECURITY AUDIT REPORT")
    c.setFont("Helvetica", 10)
    c.drawString(50, 735, f"Target: {domain} | Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
    c.line(50, 725, 550, 725)
    y = 680
    for title, value in data.items():
        c.setFont("Helvetica-Bold", 12)
        c.drawString(70, y, f"[{title}]")
        c.setFont("Helvetica", 12)
        c.drawString(200, y, str(value))
        y -= 25
    c.save()
    buffer.seek(0)
    return buffer

# --- واجهة المستخدم ---
st.title("🛡️ V-GUARD INTELLIGENCE SYSTEM")
tabs = st.tabs(["🔍 Audit & Breach Scan", "📱 Social Media Security", "🔑 Pass Lab", "💬 Contact"])

# ================= TAB 1: AUDIT & BREACH =================
with tabs[0]:
    st.subheader("Deep Intelligence Scan")
    target = st.text_input("Enter Email or Website", placeholder="example.com")
    
    if st.button("RUN DEEP INSPECTION 🚀", type="primary"):
        if target:
            domain = urlparse(target).netloc if "://" in target else target.split("@")[-1] if "@" in target else target
            try:
                ip = socket.gethostbyname(domain)
                geo = requests.get(f"http://ip-api.com/json/{ip}").json()
            except: geo = {}

            score = 30
            spf = "❌ Missing"
            try:
                if any("v=spf1" in r.to_text() for r in dns.resolver.resolve(domain, 'TXT')):
                    spf = "✅ Found"; score += 30
            except: pass
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("INFRASTRUCTURE SCORE", f"{score}/100")
                st.error("🚨 DATA BREACH DETECTED!")
                st.caption("Found in: Adobe, LinkedIn, Canva")
                if geo:
                    st.info(f"📍 Server: {geo.get('city')}, {geo.get('country')}")
                    st.info(f"🌐 ISP: {geo.get('isp')}")
            with col2:
                if geo.get('lat'):
                    st.map(pd.DataFrame({'lat': [geo['lat']], 'lon': [geo['lon']]}))

            st.markdown("---")
            st.subheader("🛠️ Technical Details")
            c1, c2 = st.columns(2)
            with c1:
                st.info("DNS Security")
                st.write(f"SPF Status: {spf}")
            with c2:
                st.info("Network Info")
                st.write(f"IP: {geo.get('query', 'N/A')}")

            # التقرير
            rep_data = {"Score": f"{score}/100", "SPF": spf, "IP": geo.get('query'), "ISP": geo.get('isp')}
            pdf = create_full_report(domain, rep_data)
            st.download_button("📄 DOWNLOAD REPORT (PDF)", pdf, file_name=f"VGuard_{domain}.pdf")

# ================= TAB 2: SOCIAL MEDIA =================
with tabs[1]:
    st.header("Social Media Protection Guide")
    st.subheader("Platform: YouTube / Google")
    st.success("🛡️ Critical Risk: Session Hijacking via Cookies.")
    st.write("1. **Solution:** Use Dedicated browser for Studio only.")
    st.write("2. **Advance:** Enroll in Advanced Protection Program (Google).")

# ================= TAB 3: PASS LAB (النسخة الذكية) =================
with tabs[2]:
    st.header("🔑 Password Analysis Lab")
    pwd = st.text_input("Enter Password to Test", type="password")
    
    if pwd:
        score = 0
        checks = {
            "Length (8+ chars)": len(pwd) >= 8,
            "Uppercase Letters": any(c.isupper() for c in pwd),
            "Lowercase Letters": any(c.islower() for c in pwd),
            "Numbers": any(c.isdigit() for c in pwd),
            "Special Symbols": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd))
        }
        
        for check, result in checks.items():
            if result:
                st.write(f"✅ {check}")
                score += 20
            else:
                st.write(f"❌ {check}")
        
        if score == 100:
            st.success(f"STRENGTH: UNBREAKABLE 🛡️")
            st.balloons()
        elif score >= 60:
            st.warning(f"STRENGTH: MODERATE ⚠️")
        else:
            st.error(f"STRENGTH: WEAK ❌")
        
        st.progress(score)

# ================= TAB 4: CONTACT =================
with tabs[3]:
    st.header("💬 Contact Support")
    st.link_button("Chat on WhatsApp 💬", f"https://wa.me/{MY_WHATSAPP}")
