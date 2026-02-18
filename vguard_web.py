import streamlit as st
import dns.resolver
import re
from urllib.parse import urlparse

# 1. إعدادات الصفحة (Tab Title & Icon)
st.set_page_config(page_title="V-GUARD Intelligence", page_icon="🛡️", layout="centered")

# 2. العنوان الرئيسي
st.title("🛡️ V-GUARD INTELLIGENCE")
st.markdown("### Cyber Security Audit System | v2.1")
st.info("System Status: Online | Secure Connection Established")

# 3. إنشاء التبويبات
tab1, tab2 = st.tabs(["🌐 Target Scanner", "🔑 Password Intelligence"])

# --- TAB 1: DOMAIN SCANNER ---
with tab1:
    st.header("Domain Vulnerability Scanner")
    target_input = st.text_input("Enter Email OR URL (e.g., admin@site.com)", placeholder="https://example.com")
    
    if st.button("SCAN TARGET 🚀"):
        if not target_input:
            st.warning("⚠️ Please enter a target first!")
        else:
            # استخراج الدومين
            domain = None
            if "@" in target_input and not target_input.startswith("http"):
                domain = target_input.split("@")[1]
            else:
                if not target_input.startswith(("http", "www")):
                    target_input = "https://" + target_input
                try:
                    domain = urlparse(target_input).netloc
                except:
                    domain = None

            if domain:
                st.success(f"[*] Target Locked: {domain}")
                
                # فحص SPF
                st.markdown("---")
                st.write("**📡 Checking DNS Records...**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    try:
                        answers = dns.resolver.resolve(domain, 'TXT')
                        spf_found = False
                        for r in answers:
                            if "v=spf1" in r.to_text():
                                spf_found = True
                                st.success("✅ SPF Record: Found")
                                st.code(r.to_text())
                        if not spf_found:
                            st.error("❌ SPF Missing (Spoofing Risk!)")
                    except:
                        st.error("❌ SPF Check Failed")

                with col2:
                    try:
                        dmarc = f"_dmarc.{domain}"
                        ans = dns.resolver.resolve(dmarc, 'TXT')
                        st.success("✅ DMARC: Active")
                        st.code(ans[0].to_text())
                    except:
                        st.error("⚠️ DMARC Missing (High Risk!)")
                
                st.markdown("---")
                if spf_found:
                    st.balloons() # احتفال لو الموقع محمي
            else:
                st.error("❌ Invalid Input Format!")

# --- TAB 2: PASSWORD CHECKER ---
with tab2:
    st.header("Password Strength Analysis")
    password = st.text_input("Enter Password to Test", type="password")
    
    if st.button("ANALYZE STRENGTH 🔐"):
        score = 0
        feedback = []

        if len(password) >= 8: score += 1
        else: feedback.append("❌ Too Short (Min 8 chars)")

        if re.search(r"[A-Z]", password): score += 1
        else: feedback.append("⚠️ Add Uppercase (A-Z)")

        if re.search(r"[0-9]", password): score += 1
        else: feedback.append("⚠️ Add Numbers (0-9)")

        if re.search(r"[!@#$%^&*]", password): score += 1
        else: feedback.append("⚠️ Add Symbols (!@#$)")

        if score == 4:
            st.success("🛡️ STATUS: UNBREAKABLE")
            st.progress(100)
        elif score >= 2:
            st.warning("⚠️ STATUS: MODERATE")
            st.progress(50)
        else:
            st.error("❌ STATUS: WEAK")
            st.progress(25)
            
        for tip in feedback:
            st.write(tip)