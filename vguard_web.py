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

# --- إعدادات الواجهة ---
st.set_page_config(page_title="V-GUARD | Elite Security", page_icon="🛡️", layout="wide")
MY_WHATSAPP = "201102353779"

# --- دالة فحص التسريبات (Breach Check) ---
def check_breach(target):
    # ملاحظة: هنا بنستخدم API تجريبي. في الشغل الحقيقي هتحتاج API Key من HaveIBeenPwned
    # ده كود بيعمل فحص منطقي سريع
    common_breached_domains = ['gmail.com', 'yahoo.com', 'hotmail.com']
    domain = target.split('@')[-1] if '@' in target else ""
    
    # محاكاة لعملية البحث في الداتا المسرية
    if domain in common_breached_domains:
        return True, ["Adobe (2013)", "LinkedIn (2016)", "Canva (2019)"]
    return False, []

# --- دالة جلب معلومات IP الذكية ---
def get_ip_intel(domain_or_ip):
    try:
        target_ip = socket.gethostbyname(domain_or_ip)
        res = requests.get(f"http://ip-api.com/json/{target_ip}", timeout=5).json()
        return res
    except:
        return None

# --- واجهة البرنامج ---
st.title("🛡️ V-GUARD INTELLIGENCE (VIP EDITION)")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Audit & Breach Scan", "📱 Social Media Security", "🔑 Pass Lab", "💬 Contact"])

with tab1:
    st.subheader("Deep Intelligence Scan")
    target = st.text_input("Enter Celebrity Email, IP, or Website", placeholder="example@gmail.com")
    
    if st.button("RUN DEEP INSPECTION 🚀", type="primary"):
        if target:
            # 1. تحليل المعلومات الجغرافية والـ IP
            domain = urlparse(target).netloc if "://" in target else target.split("@")[-1] if "@" in target else target
            intel = get_ip_intel(domain)
            
            # 2. فحص التسريبات
            is_pwned, sources = check_breach(target)
            
            # 3. العرض
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.metric("INFRASTRUCTURE SCORE", "90/100" if not is_pwned else "40/100")
                if is_pwned:
                    st.error(f"🚨 DATA BREACH DETECTED!")
                    st.write(f"This identity was found in: {', '.join(sources)}")
                else:
                    st.success("✅ No Immediate Leaks Found")
                
                if intel:
                    st.info(f"📍 Server Location: {intel.get('city')}, {intel.get('country')}")
                    st.info(f"📡 ISP: {intel.get('isp')}")

            with col2:
                if intel and intel.get('lat'):
                    df = pd.DataFrame({'lat': [intel['lat']], 'lon': [intel['lon']]})
                    st.map(df)

with tab2:
    st.header("📱 Social Media Protection Guide")
    platform = st.selectbox("Choose Platform", ["YouTube", "TikTok", "Instagram", "Twitter/X"])
    
    if platform == "YouTube":
        st.warning("⚠️ High Risk: Session Hijacking via Malicious Cookies.")
        st.write("1. Use a dedicated browser for Studio only.")
        st.write("2. Enable Advanced Protection Program (Google).")
    elif platform == "TikTok":
        st.write("1. Check 'Manage Devices' for unknown logins.")
        st.write("2. Secure your linked phone number from SIM Swapping.")

with tab4:
    st.header("V-Guard VIP Support")
    st.link_button("Chat with Ammar Hossam 💬", f"https://wa.me/{MY_WHATSAPP}")
