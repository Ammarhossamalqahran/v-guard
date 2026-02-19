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
import plotly.express as px
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

# --- فحص DNS Records ---
def check_dns(domain):
    results = {}
    try:
        mx = [r.exchange.to_text() for r in dns.resolver.resolve(domain, 'MX')]
        results["MX Records"] = ", ".join(mx)
    except: results["MX Records"] = "❌ Not Found"
    try:
        dmarc = [r.to_text() for r in dns.resolver.resolve("_dmarc."+domain, 'TXT')]
        results["DMARC"] = "✅ Found" if dmarc else "❌ Missing"
    except: results["DMARC"] = "❌ Missing"
    try:
        dkim = [r.to_text() for r in dns.resolver.resolve("default._domainkey."+domain, 'TXT')]
        results["DKIM"] = "✅ Found" if dkim else "❌ Missing"
    except: results["DKIM"] = "❌ Missing"
    return results

# --- فحص HTTP Headers ---
def check_http_headers(domain):
    headers_info = {}
    try:
        resp = requests.get("http://"+domain, timeout=5)
        headers = resp.headers
        headers_info["HSTS"] = "✅ Enabled" if "Strict-Transport-Security" in headers else "❌ Missing"
        headers_info["CSP"] = "✅ Enabled" if "Content-Security-Policy" in headers else "❌ Missing"
        headers_info["X-Frame-Options"] = headers.get("X-Frame-Options", "❌ Missing")
    except Exception as e:
        headers_info["Error"] = str(e)
    return headers_info

# --- CSS للفقاعات ---
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #dbe6f6, #c5796d);
    }
    .bubble {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(12px);
        border-radius: 25px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: 0.3s;
    }
    .bubble:hover {
        background: rgba(255, 255, 255, 0.3);
        box-shadow: 0 0 25px #4CAF50;
        transform: scale(1.03);
    }
    </style>
""", unsafe_allow_html=True)

# --- واجهة المستخدم ---
st.title("🛡️ V-GUARD INTELLIGENCE SYSTEM")
tabs = st.tabs(["🔍 Intelligence Hub", "📱 Social Media", "🛡️ Cybersecurity Awareness", "🔑 Pass Lab", "🕵️ Dark Web", "💬 Contact"])

# ================= 1. INTELLIGENCE HUB =================
with tabs[0]:
    st.markdown('<div class="bubble">', unsafe_allow_html=True)
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

            dns_data = check_dns(domain)
            http_headers = check_http_headers(domain)
            ssl_data = check_ssl(domain)

            st.metric("SECURITY SCORE", f"{score}/100")
            st.info(f"**IP:** {ip}\n\n**ISP:** {geo.get('isp', 'N/A')}\n\n**Loc:** {geo.get('city', 'N/A')}")

            st.markdown("### 🧩 DNS & Email Security")
            st.json(dns_data)

            st.markdown("### 🔐 SSL Research")
            st.json(ssl_data)

            st.markdown("### 🌐 HTTP Security Headers")
            st.json(http_headers)

            st.markdown("### 📊 Security Dashboard")
            df = pd.DataFrame({
                "Category": ["SPF", "DMARC", "DKIM", "SSL", "Score"],
                "Value": [
                    1 if spf == "✅ Secured" else 0,
                    1 if dns_data["DMARC"] == "✅ Found" else 0,
                    1 if dns_data["DKIM"] == "✅ Found" else 0,
                    1 if "Issuer" in ssl_data else 0,
                    score/100
                ]
            })
            fig = px.bar(df, x="Category", y="Value", title="Security Indicators", color="Category")
            st.plotly_chart(fig, use_container_width=True)

            tech_data = {"IP Address": ip, "SPF Status": spf, "Location": geo.get('city'), "ISP": geo.get('isp')}
            tech_data.update(dns_data)
            tech_data.update(http_headers)
            pdf = generate_pdf(domain, tech_data)
            st.download_button("📄 DOWNLOAD FULL REPORT", pdf, file_name=f"VGuard_{domain}.pdf")

        else:
            st.warning("Please enter a target first!")
    st.markdown('</div>', unsafe_allow_html=True)

# ================= 2. SOCIAL MEDIA =================
with tabs[1]:
    st.markdown('<div class="bubble">', unsafe_allow_html=True)
    st.header("📱 Social Media Security")
    st.write("### 🎥 YouTube / Google")
    st.write("- Use **Dedicated browser** for Studio only.")
    st.write("- Enroll in **Advanced Protection Program**.")
    st.write("- Use Hardware Security Keys (U2F).")
    st.markdown("---")
    st.write("### 📸 Instagram / Meta")
    st.write("- Disable SMS 2FA; use **Auth Apps**.")
    st.write("- Monitor 'Login Activity' regularly.")
    st.markdown('</div>', unsafe_allow_html=True)

# ================= 3. CYBERSECURITY AWARENESS =================
with tabs[2]:
    st.markdown('<div class="bubble">', unsafe_allow_html=True)
    st.header("🛡️ Cybersecurity Awareness")
    st.write("### Common Threats")
    st.write("- Phishing attacks via email and SMS.")
    st.write("- Ransomware targeting businesses.")
    st.write("- Social engineering and identity theft.")
    st.markdown("---")
    st.write("### Best Practices")
    st.write("- Always update your software and systems.")
    st.write("- Use strong, unique passwords with a password manager.")
    st.write("- Enable multi-factor authentication everywhere.")
    st.write("- Train employees on cybersecurity awareness.")
    st.markdown('</div>', unsafe_allow_html=True)

# ================= 4. PASS LAB =================
with tabs[3]:
    st.markdown('<div class="bubble">', unsafe_allow_html=True)
    st.header("🔑 Advanced Password Intelligence")
    pwd = st.text_input("Test Password Entropy", type="password")
    if pwd:
        has_upper = any(c.isupper() for c in pwd)
        has_num = any(c.isdigit() for c in pwd)
        has_sym = bool(re.search(r"[!@#$%^&*]", pwd))
        length_ok = len(pwd) >= 12
        p_score = sum([has_upper, has_num, has_sym, length_ok]) * 25

        st.progress(p_score / 100)
        st.write(f"**Entropy Strength:** {p_score}%")

        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.write("Uppercase: " + ("✅" if has_upper else "❌"))
        col_b.write("Numbers: " + ("✅" if has_num else "❌"))
        col_c.write("Symbols: " + ("✅" if has_sym else "❌"))
        col_d.write("Length ≥ 12: " + ("✅" if length_ok else "❌"))

        # نصائح إضافية
        st.markdown("### 🔒 Recommendations")
        if p_score < 50:
            st.error("Weak password! Consider adding uppercase, numbers, symbols, and making it longer.")
        elif p_score < 75:
            st.warning("Medium strength. Add more complexity for better protection.")
        else:
            st.success("Strong password! Good job.")
    st.markdown('</div>', unsafe_allow_html=True)

# ================= 5. DARK WEB =================
with tabs[4]:
    st.markdown('<div class="bubble">', unsafe_allow_html=True)
    st.header("🕵️ Dark Web Intelligence")
    st.info("Checking leaked credentials & breaches...")
    email_check = st.text_input("Enter Email to Check Breaches")
    if email_check:
        st.warning("⚠️ Demo Mode: Connect to HaveIBeenPwned API for real results.")
        st.write(f"Results for {email_check}: Potential leaks found in demo mode.")
    st.markdown('</div>', unsafe_allow_html=True)

# ================= 6. CONTACT =================
with tabs[5]:
    st.markdown('<div class="bubble">', unsafe_allow_html=True)
    st.header("💬 Connect with V-Guard")
    st.write("24/7 Professional Emergency Response.")
    st.link_button("Chat on WhatsApp 💬", f"https://wa.me/{MY_WHATSAPP}", type="primary")
    st.write(f"📧 Direct Email: {MY_EMAIL}")
    st.write("🌐 Website: Coming Soon")
    st.markdown('</div>', unsafe_allow_html=True)
