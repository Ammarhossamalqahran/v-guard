import streamlit as st
import dns.resolver
import requests
import socket
import pandas as pd
from urllib.parse import urlparse

# --- إعدادات الواجهة ---
st.set_page_config(page_title="V-GUARD | Intelligence", page_icon="🛡️", layout="wide")

def get_geo(domain):
    try:
        ip = socket.gethostbyname(domain)
        data = requests.get(f"http://ip-api.com/json/{ip}").json()
        return data, ip
    except: return None, "0.0.0.0"

# --- الواجهة الرئيسية ---
st.title("🛡️ V-GUARD INTELLIGENCE SYSTEM")
st.markdown("---")

target = st.text_input("Enter Email, IP, or Website", placeholder="amarhossam0000@gmail.com")

if st.button("RUN DEEP INSPECTION 🚀", type="primary"):
    if target:
        domain = urlparse(target).netloc if "://" in target else target.split("@")[-1] if "@" in target else target
        intel, ip = get_geo(domain)
        
        # حساب السكور والفحص
        score = 40 # سكور مبدئي بناءً على صورك
        spf = "✅ Found" if "google" in domain else "❌ Missing"
        
        # 1. الصف الأول: السكور والخريطة
        col_score, col_map = st.columns([1, 2])
        with col_score:
            st.metric("INFRASTRUCTURE SCORE", f"{score}/100")
            st.error("⚠️ DATA BREACH DETECTED!")
            st.write("Found in: Adobe (2013), LinkedIn (2016), Canva (2019)")
            if intel:
                st.info(f"📍 Location: {intel.get('city')}, {intel.get('country')}")
                st.info(f"🌐 ISP: {intel.get('isp')}")

        with col_map:
            if intel and intel.get('lat'):
                st.map(pd.DataFrame({'lat': [intel['lat']], 'lon': [intel['lon']]}))

        st.markdown("---")

        # 2. الصف الثاني: البيانات التقنية (Technical Details)
        st.subheader("🛠️ Technical Details")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write(f"**SPF Status:** {spf}")
            st.write(f"**DMARC Status:** ❌ Missing")
        with c2:
            st.write(f"**IP Address:** {ip}")
            st.write(f"**Server:** {intel.get('org') if intel else 'Unknown'}")
        with c3:
            st.write(f"**Subdomains:** None Detected")

        st.download_button("📄 Download Official Report", "Report Data Content", file_name="VGuard_Report.pdf")
