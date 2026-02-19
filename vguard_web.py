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

# --- الإعدادات الأساسية ---
st.set_page_config(page_title="V-GUARD | Global Intel", page_icon="🛡️", layout="wide")
MY_WHATSAPP = "201102353779"

# --- دوال جلب البيانات ---
def get_detailed_intel(domain):
    try:
        ip = socket.gethostbyname(domain)
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        return res
    except:
        return None

def create_pro_pdf(domain, results):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 25)
    c.setStrokeColorRGB(0, 0.7, 0)
    c.drawString(50, 750, "V-GUARD DEEP INTELLIGENCE REPORT")
    c.setFont("Helvetica", 10)
    c.drawString(50, 735, f"Security Audit for: {domain} | Generated: {datetime.datetime.now()}")
    c.line(50, 725, 550, 725)
    
    y = 680
    for key, val in results.items():
        c.setFont("Helvetica-Bold", 12)
        c.drawString(70, y, f"[{key}]")
        c.setFont("Helvetica", 12)
        c.drawString(180, y, f"{val}")
        y -= 30
    
    c.save()
    buffer.seek(0)
    return buffer

# --- واجهة المستخدم ---
st.title("🛡️ V-GUARD INTELLIGENCE SYSTEM")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 Full Audit Dashboard", "🔐 Password Lab", "📞 Contact"])

with tab1:
    target = st.text_input("Enter URL or Email to Inspect", placeholder="example.com")
    
    if st.button("EXECUTE DEEP SCAN 🚀", type="primary"):
        if target:
            # استخراج الدومين
            domain = urlparse(target).netloc if "://" in target else target.split("@")[-1] if "@" in target else target
            
            with st.spinner("Analyzing Global Infrastructure..."):
                intel = get_detailed_intel(domain)
                
                # فحص DNS و SSL
                score = 0
                spf = "❌ Missing"
                try:
                    if any("v=spf1" in r.to_text() for r in dns.resolver.resolve(domain, 'TXT')):
                        spf = "✅ Protected"; score += 30
                except: pass
                
                dmarc = "❌ Missing"
                try:
                    dns.resolver.resolve(f"_dmarc.{domain}", 'TXT')
                    dmarc = "✅ Active"; score += 30
                except: pass
                
                ssl_val = "❌ Not Secure"
                try:
                    ssl.create_default_context().wrap_socket(socket.socket(), server_hostname=domain).connect((domain, 443))
                    ssl_val = "✅ Encrypted"; score += 40
                except: pass

                # --- العرض الرئيسي (Score + Map) ---
                col_left, col_right = st.columns([1, 2])
                
                with col_left:
                    st.subheader("Security Score")
                    color = "red" if score < 50 else "orange" if score < 80 else "green"
                    st.markdown(f"<h1 style='text-align: center; color: {color};'>{score}/100</h1>", unsafe_allow_html=True)
                    
                    if intel:
                        st.info(f"**IP:** {intel.get('query')}")
                        st.info(f"**ISP:** {intel.get('isp')}")
                        st.info(f"**Org:** {intel.get('org')}")
                        st.info(f"**Location:** {intel.get('city')}, {intel.get('country')}")
                
                with col_right:
                    st.subheader("Server Geolocation")
                    if intel and intel.get('lat'):
                        df = pd.DataFrame({'lat': [intel['lat']], 'lon': [intel['lon']]})
                        st.map(df, zoom=3)

                st.markdown("---")
                
                # --- عرض البيانات التقنية (اللي كانت ناقصة) ---
                st.subheader("🛠️ Technical Deep Dive")
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.markdown("### DNS Security")
                    st.write(f"**SPF Record:** {spf}")
                    st.write(f"**DMARC Policy:** {dmarc}")
                    
                with c2:
                    st.markdown("### Encryption")
                    st.write(f"**SSL Status:** {ssl_val}")
                    st.write("**HTTPS:** Forced" if score > 70 else "**HTTPS:** Optional")

                with c3:
                    st.markdown("### Infrastructure")
                    st.write(f"**ASN:** {intel.get('as') if intel else 'N/A'}")
                    st.write(f"**Timezone:** {intel.get('timezone') if intel else 'N/A'}")

                # --- زر تحميل التقرير الشامل ---
                report_data = {
                    "Total Score": f"{score}/100",
                    "SPF Status": spf,
                    "DMARC Status": dmarc,
                    "SSL Status": ssl_val,
                    "Server IP": intel.get('query') if intel else "Unknown",
                    "ISP": intel.get('isp') if intel else "Unknown",
                    "Location": f"{intel.get('city')}, {intel.get('country')}" if intel else "Unknown"
                }
                pdf = create_pro_pdf(domain, report_data)
                st.download_button("📄 DOWNLOAD FULL PDF REPORT", pdf, file_name=f"VGuard_{domain}.pdf")

with tab3:
    st.header("V-Guard Emergency Support")
    st.link_button("Chat on WhatsApp 💬", f"https://wa.me/{MY_WHATSAPP}")
