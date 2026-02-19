import streamlit as st
import dns.resolver
import requests
import socket
import datetime
import io
import re
import pandas as pd
import ssl
import OpenSSL
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from urllib.parse import urlparse

# --- الإعدادات العامة ---
st.set_page_config(page_title="V-GUARD | Intelligence", page_icon="🛡️", layout="wide")
MY_WHATSAPP = "201102353779"
MY_EMAIL = "amarhossam0000@gmail.com"

# --- دالة إنشاء التقرير PDF ---
def generate_pdf(domain, data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(50, 750, "V-GUARD SECURITY AUDIT")
    c.setFont("Helvetica", 10)
    c.drawString(50, 730, f"Target: {domain} | Date: {datetime.datetime.now().date()}")
    c.line(50, 720, 550, 720)
    y = 680
    for k, v in data.items():
        if y < 100:
            c.showPage()
            y = 750
        c.drawString(70, y, f"• {k}: {v}")
        y -= 25
    c.save()
    buffer.seek(0)
    return buffer

# --- فحص SSL ---
def check_ssl(domain):
    try:
        cert = ssl.get_server_certificate((domain, 443))
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
        return {
            "Issuer": x509.get_issuer().CN,
            "Valid From": x509.get_notBefore().decode(),
            "Valid Until": x509.get_notAfter().decode(),
            "Version": x509.get_version(),
            "Serial Number": x509.get_serial_number()
        }
    except Exception as e:
        return {"Error": str(e)}

# --- واجهة المستخدم ---
st.title("🛡️ V-GUARD INTELLIGENCE SYSTEM")
tabs = st.tabs(["🔍 Intelligence Hub", "📱 Social Media", "🔑 Pass Lab", "🕵️ Dark Web", "💬 Contact"])

# ================= 1. INTELLIGENCE HUB =================
with tabs[0]:
    st.subheader("Deep Infrastructure Reconnaissance")
    target = st.text_input("Enter Target Domain/Email", placeholder="example.com", key="main_input")
    
    if st.button("EXECUTE SCAN 🚀", type="primary"):
        if target:
            if "@" in target:
                domain = target.split("@")[-1]
            else:
                parsed = urlparse(target)
                domain = parsed.netloc if parsed.netloc else parsed.path

            try:
                ip = socket.gethostbyname(domain)
                geo = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
            except:
                geo = {}
                ip = "0.0.0.0"

            score = 20
            spf = "❌ Missing"
            try:
                if any("v=spf1" in r.to_text() for r in dns.resolver.resolve(domain, 'TXT')):
                    spf = "✅ Secured"; score += 40
            except:
                pass

            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("SECURITY SCORE", f"{score}/100")
                st.error("🚨 BREACH ALERT!")
                st.info(f"**IP:** {ip}\n\n**ISP:** {geo.get('isp', 'N/A')}\n\n**Loc:** {geo.get('city', 'N/A')}")
            with c2:
                if geo.get('lat') and geo.get('lon'):
                    st.map(pd.DataFrame({'lat': [geo['lat']], 'lon': [geo['lon']]}))
            
            st.markdown("---")
            st.subheader("Technical Vulnerabilities")
            tech_data = {"IP Address": ip, "SPF Status": spf, "Location": geo.get('city'), "ISP": geo.get('isp')}
            st.json(tech_data)
            
            pdf = generate_pdf(domain, tech_data)
            st.download_button("📄 DOWNLOAD FULL REPORT", pdf, file_name=f"VGuard_{domain}.pdf")

            st.markdown("### 🔐 SSL Research")
            ssl_data = check_ssl(domain)
            st.json(ssl_data)

        else:
            st.warning("Please enter a target first!")

# ================= 2. SOCIAL MEDIA =================
with tabs[1]:
    st.header("📱 Professional Protection Guide")
    st.warning("Critical Risk: Session Hijacking via Malicious Cookies.")
    st.write("### 🎥 YouTube / Google")
    st.write("- Use **Dedicated browser** for Studio only.")
    st.write("- Enroll in **Advanced Protection Program**.")
    st.write("- Use Hardware Security Keys (U2F).")
    st.markdown("---")
    st.write("### 📸 Instagram / Meta")
    st.write("- Disable SMS 2FA; use **Auth Apps**.")
    st.write("- Monitor 'Login Activity' regularly.")

# ================= 3. PASS LAB =================
with tabs[2]:
    st.header("🔑 Advanced Password Intelligence")
    pwd = st.text_input("Test Password Entropy", type="password")
    if pwd:
        has_upper = any(c.isupper() for c in pwd)
        has_num = any(c.isdigit() for c in pwd)
        has_sym = bool(re.search(r"[!@#$%^&*]", pwd))
        p_score = sum([has_upper, has_num, has_sym, len(pwd) >= 12]) * 25
        
        st.progress(p_score / 100)
        st.write(f"**Entropy Strength:** {p_score}%")
        col_a, col_b, col_c = st.columns(3)
        col_a.write("Uppercase: " + ("✅" if has_upper else "❌"))
        col_b.write("Numbers: " + ("✅" if has_num else "❌"))
        col_c.write("Symbols: " + ("✅" if has_sym else "❌"))

# ================= 4. DARK WEB =================
with tabs[3]:
    st.header("🕵️ Dark Web Intelligence")
    st.info("Checking leaked credentials & breaches...")
    email_check = st.text_input("Enter Email to Check Breaches")
    if email_check:
        st.warning("⚠️ Demo Mode: Connect to HaveIBeenPwned API for real results.")
        st.write(f"Results for {email_check}: Potential leaks found in demo mode.")

# ================= 5. CONTACT =================
with tabs[4]:
    st.header("💬 Connect with V-Guard")
    st.write("24/7 Professional Emergency Response.")
    st.link_button("Chat on WhatsApp 💬", f"https://wa.me/{MY_WHATSAPP}", type="primary")
    st.write(f"Direct Email: {MY_EMAIL}")
