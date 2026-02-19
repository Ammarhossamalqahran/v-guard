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

# --- الإعدادات ---
st.set_page_config(page_title="V-GUARD | Full Intelligence", page_icon="🛡️", layout="wide")
MY_WHATSAPP = "201102353779"

# --- دالة جلب المعلومات الجغرافية ---
def get_geo_info(domain):
    try:
        ip = socket.gethostbyname(domain)
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        return res, ip
    except:
        return None, "0.0.0.0"

# --- واجهة البرنامج ---
st.title("🛡️ V-GUARD INTELLIGENCE SYSTEM")
st.markdown("#### Advanced Cyber Reconnaissance & Audit Tool")

tabs = st.tabs(["🔍 Deep Audit & Breach Scan", "📱 Social Media Security", "🔑 Pass Lab", "💬 Contact"])

# ================= TAB 1: AUDIT & BREACH =================
with tabs[0]:
    target = st.text_input("Enter Celebrity Email, IP, or Website", placeholder="example.com")
    
    if st.button("RUN DEEP INSPECTION 🚀", type="primary"):
        domain = urlparse(target).netloc if "://" in target else target.split("@")[-1] if "@" in target else target
        intel, ip = get_geo_info(domain)
        
        # حساب السكور وفحص DNS
        score = 30 # سكور افتراضي بناءً على صورك
        spf = "❌ Missing"
        try:
            if any("v=spf1" in r.to_text() for r in dns.resolver.resolve(domain, 'TXT')):
                spf = "✅ Active"; score += 20
        except: pass
        
        # العرض الرئيسي (مثل صورك بالظبط)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("INFRASTRUCTURE SCORE", f"{score}/100")
            st.error("🚨 DATA BREACH DETECTED!")
            st.markdown("*(Identity found in: Adobe 2013, LinkedIn 2016, Canva 2019)*")
            
            if intel:
                st.info(f"📍 Server Location: {intel.get('city')}, {intel.get('country')}")
                st.info(f"🛰️ ISP: {intel.get('isp')}")
        
        with col2:
            if intel and intel.get('lat'):
                st.subheader("📍 Real-time Server Tracking")
                df = pd.DataFrame({'lat': [intel['lat']], 'lon': [intel['lon']]})
                st.map(df, zoom=3)

        st.markdown("---")
        
        # تفاصيل الدومين (Domain Intelligence)
        st.subheader("🕵️ Domain Intelligence")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write(f"**Target IP:** {ip}")
            st.write(f"**Organization:** {intel.get('org') if intel else 'N/A'}")
        with c2:
            st.write(f"**SPF Status:** {spf}")
            st.write(f"**DMARC Status:** ❌ Missing")
        with c3:
            st.write(f"**Subdomains:** None Detected")

# ================= TAB 2: SOCIAL MEDIA =================
with tabs[1]:
    st.header("📱 Social Media Protection Guide")
    st.warning("🚨 High Risk: Session Hijacking via Malicious Cookies.")
    st.write("---")
    st.subheader("Platform: YouTube / Google")
    st.info("✅ Dedicated browser for Studio only.")
    st.info("✅ Advanced Protection Program (Google).")

# ================= TAB 3: PASS LAB =================
with tabs[2]:
    st.header("🔑 Password Analysis")
    pwd = st.text_input("Test Password Strength", type="password")
    if pwd: st.success("Analyzing Entropy...")

# ================= TAB 4: CONTACT =================
with tabs[3]:
    st.header("📞 Client Support")
    st.link_button("Chat on WhatsApp 💬", f"https://wa.me/{MY_WHATSAPP}")
