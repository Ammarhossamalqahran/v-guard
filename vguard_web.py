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

# --- إعدادات الصفحة ---
st.set_page_config(page_title="V-GUARD | Intel", page_icon="🛡️", layout="wide")
MY_WHATSAPP = "201102353779"

# --- دالة جلب الموقع الجغرافي ---
def get_geolocation(domain):
    try:
        ip = socket.gethostbyname(domain)
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        return res.get('lat'), res.get('lon'), res.get('city'), res.get('country'), res.get('isp'), ip
    except:
        return None, None, "Unknown", "Unknown", "Unknown", "0.0.0.0"

# --- دالة إنشاء التقرير PDF ---
def create_pdf(domain, results):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, 750, "V-GUARD SECURITY REPORT")
    c.setFont("Helvetica", 12)
    c.drawString(50, 730, f"Target: {domain} | Date: {datetime.datetime.now().date()}")
    c.line(50, 720, 550, 720)
    y = 690
    for key, val in results.items():
        c.drawString(70, y, f"• {key}: {val}")
        y -= 25
    c.save()
    buffer.seek(0)
    return buffer

# --- واجهة المستخدم ---
st.title("🛡️ V-GUARD INTELLIGENCE")
tab1, tab2, tab3 = st.tabs(["🔍 Site Audit", "🔑 Pass Lab", "💬 Support"])

with tab1:
    target = st.text_input("Enter Email or URL", placeholder="example.com")
    if st.button("RUN AUDIT 🚀", type="primary"):
        if target:
            # تنظيف الدومين
            domain = urlparse(target).netloc if "://" in target else target.split("@")[-1] if "@" in target else target
            
            # فحص البيانات
            lat, lon, city, country, isp, ip = get_geolocation(domain)
            
            # حساب السكور
            score = 0
            spf = "❌"
            try:
                if any("v=spf1" in r.to_text() for r in dns.resolver.resolve(domain, 'TXT')):
                    spf = "✅"; score += 25
            except: pass
            
            dmarc = "✅" if score >= 25 else "❌" # مبدئياً
            try:
                dns.resolver.resolve(f"_dmarc.{domain}", 'TXT')
                dmarc = "✅"; score += 25
            except: dmarc = "❌"

            # العرض
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("SECURITY SCORE", f"{score}/100")
                st.write(f"**IP:** {ip}")
                st.write(f"**Location:** {city}, {country}")
                st.write(f"**ISP:** {isp}")
            
            with c2:
                if lat and lon:
                    df = pd.DataFrame({'lat': [lat], 'lon': [lon]})
                    st.map(df)
            
            st.markdown("---")
            st.subheader("Technical Details")
            st.write(f"SPF Status: {spf}")
            st.write(f"DMARC Status: {dmarc}")
            
            # زر التحميل
            pdf = create_pdf(domain, {"Score": score, "IP": ip, "Location": city, "SPF": spf})
            st.download_button("📄 Download Report", pdf, file_name="report.pdf")

with tab3:
    st.link_button("Chat on WhatsApp 💬", f"https://wa.me/{MY_WHATSAPP}")
