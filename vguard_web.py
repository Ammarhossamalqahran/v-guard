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

# --- إعدادات الواجهة الاحترافية ---
st.set_page_config(page_title="V-GUARD | Intelligence System", page_icon="🛡️", layout="wide")

# رقم الواتساب الخاص بك
MY_WHATSAPP = "201102353779"

# --- دالة جلب معلومات السيرفر والخريطة ---
def get_intel(domain):
    try:
        ip = socket.gethostbyname(domain)
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        return {
            "lat": res.get('lat'), "lon": res.get('lon'),
            "city": res.get('city'), "country": res.get('country'),
            "isp": res.get('isp'), "ip": ip, "org": res.get('org')
        }
    except:
        return None

# --- دالة إنشاء تقرير PDF احترافي ---
def create_pdf(domain, data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(50, 750, "V-GUARD SECURITY AUDIT REPORT")
    c.setFont("Helvetica", 12)
    c.drawString(50, 730, f"Target: {domain} | Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
    c.line(50, 720, 550, 720)
    
    y = 680
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Summary of Vulnerabilities:")
    c.setFont("Helvetica", 12)
    y -= 30
    for key, val in data.items():
        c.drawString(70, y, f"• {key}: {val}")
        y -= 25
    
    c.line(50, 100, 550, 100)
    c.drawString(50, 80, "Contact V-Guard for remediation: +201102353779")
    c.save()
    buffer.seek(0)
    return buffer

# --- تصميم الصفحة الرئيسية ---
st.title("🛡️ V-GUARD INTELLIGENCE SYSTEM")
st.markdown("#### Advanced Cyber Reconnaissance & Audit Tool")

tab1, tab2, tab3 = st.tabs(["🔍 Full Site Audit", "🔑 Password Lab", "💬 Client Support"])

with tab1:
    target_input = st.text_input("Enter Email or Website URL", placeholder="example.com")
    
    if st.button("START FULL ANALYSIS 🚀", type="primary"):
        if target_input:
            # استخراج الدومين بذكاء
            domain = urlparse(target_input).netloc if "://" in target_input else target_input.split("@")[-1] if "@" in target_input else target_input
            
            with st.spinner("Gathering Intelligence..."):
                intel = get_intel(domain)
                
                # حساب السكور والفحص التقني
                score = 0
                spf = "Missing ❌"
                try:
                    if any("v=spf1" in r.to_text() for r in dns.resolver.resolve(domain, 'TXT')):
                        spf = "Active ✅"; score += 25
                except: pass
                
                dmarc = "Missing ❌"
                try:
                    dns.resolver.resolve(f"_dmarc.{domain}", 'TXT')
                    dmarc = "Active ✅"; score += 25
                except: pass
                
                ssl_status = "Not Secure ❌"
                try:
                    ctx = ssl.create_default_context()
                    with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
                        s.settimeout(3.0); s.connect((domain, 443))
                        ssl_status = "Encrypted ✅"; score += 25
                except: pass

                # عرض النتائج العلوية (Score + Map)
                col_score, col_map = st.columns([1, 2])
                
                with col_score:
                    st.metric("SECURITY SCORE", f"{score}/100")
                    if score < 50: st.error("CRITICAL RISK")
                    else: st.success("SYSTEM SECURE")
                    
                    if intel:
                        st.write(f"**IP Address:** {intel['ip']}")
                        st.write(f"**ISP:** {intel['isp']}")
                        st.write(f"**Location:** {intel['city']}, {intel['country']}")
                
                with col_map:
                    if intel and intel['lat']:
                        df = pd.DataFrame({'lat': [intel['lat']], 'lon': [intel['lon']]})
                        st.map(df)

                st.markdown("---")
                
                # عرض التفاصيل التقنية (الخانات القديمة)
                st.subheader("🛠️ Technical Vulnerability Details")
                t1, t2, t3 = st.columns(3)
                with t1:
                    st.info("DNS Security")
                    st.write(f"SPF Record: {spf}")
                    st.write(f"DMARC Policy: {dmarc}")
                with t2:
                    st.info("SSL/TLS Encryption")
                    st.write(f"Status: {ssl_status}")
                with t3:
                    st.info("Server Intelligence")
                    st.write(f"Organization: {intel['org'] if intel else 'Unknown'}")

                # زر تحميل التقرير
                report_results = {"Score": f"{score}/100", "SPF": spf, "DMARC": dmarc, "SSL": ssl_status, "IP": intel['ip'] if intel else "N/A"}
                pdf = create_pdf(domain, report_results)
                st.download_button("📄 DOWNLOAD OFFICIAL REPORT (PDF)", pdf, file_name=f"VGuard_Report_{domain}.pdf")

with tab3:
    st.header("Direct Contact")
    st.link_button("Chat with Ammar on WhatsApp 💬", f"https://wa.me/{MY_WHATSAPP}")
