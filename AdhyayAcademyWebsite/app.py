import streamlit as st
from PIL import Image
import qrcode
from io import BytesIO
import os

# Page configuration
st.set_page_config(
    page_title="Adhyay Academy – Bavdhan",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Google Analytics
st.markdown("""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-LZDNYMTKYS"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-LZDNYMTKYS');
    </script>
""", unsafe_allow_html=True)

# Custom CSS for deep blue and golden yellow theme (Light & Dark mode compatible)
st.markdown("""
    <style>
        /* Light mode */
        @media (prefers-color-scheme: light) {
            :root {
                --primary-color: #1a3a5c;
                --accent-color: #ffc107;
                --text-color: #333;
                --light-bg: #f8f9fa;
                --border-color: #1a3a5c;
                --section-bg: #ffffff;
                --page-bg: #e8f1f8;
            }
            
            h2, h3 {
                color: #1a3a5c !important;
            }
        }
        
        /* Dark mode */
        @media (prefers-color-scheme: dark) {
            :root {
                --primary-color: #ffd700;
                --accent-color: #ffd700;
                --text-color: #e8e8e8;
                --light-bg: #2d3748;
                --border-color: #ffd700;
                --section-bg: #1e1e2e;
                --page-bg: #0f1419;
            }
            
            h2, h3 {
                color: #ffd700 !important;
            }
        }
        
        /* Common styles */
        * {
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--page-bg) !important;
        }
        
        .main {
            max-width: 900px;
            margin: 0 auto;
            background-color: var(--page-bg);
        }
        
        .main-title {
            font-size: 42px;
            font-weight: bold;
            text-align: center;
            margin: 5px 0 2px 0;
            color: #ffc107;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .subtitle {
            font-size: 18px;
            text-align: center;
            margin: 2px 0 5px 0;
            font-weight: 500;
            color: inherit;
        }
        
        .section-title {
            font-size: 28px;
            font-weight: bold;
            margin-top: 8px;
            margin-bottom: 8px;
            text-align: center;
            padding-bottom: 6px;
            border-bottom: 3px solid var(--accent-color);
        }
        
        .section-content {
            font-size: 16px;
            line-height: 1.9;
            padding: 20px;
            border-radius: 8px;
            background-color: var(--light-bg);
            color: var(--text-color);
            border-left: 4px solid var(--accent-color);
        }
        
        .contact-item {
            font-size: 15px;
            margin: 4px 0;
            padding: 8px;
            border-radius: 6px;
            background-color: var(--light-bg);
            color: var(--text-color);
            border-left: 4px solid var(--accent-color);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .footer {
            text-align: center;
            font-size: 15px;
            margin-top: 8px;
            padding: 12px;
            border-radius: 10px;
            background: linear-gradient(135deg, #1a3a5c 0%, #2d5a8c 100%);
            color: #ffffff;
        }
        
        .footer h3 {
            color: #ffc107 !important;
            font-size: 18px;
            margin: 2px 0;
        }
        
        .footer p {
            margin: 2px 0 !important;
            font-size: 11px;
        }
        
        .register-btn {
            background: linear-gradient(135deg, #ffc107 0%, #ffb300 100%);
            color: #1a3a5c;
            padding: 14px 28px;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 4px 8px rgba(255, 193, 7, 0.3);
        }
        
        .register-btn:hover {
            background: linear-gradient(135deg, #ffb300 0%, #ff9800 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(255, 193, 7, 0.4);
        }
        
        .qr-label {
            font-weight: bold;
            margin-bottom: 8px;
            font-size: 14px;
            color: var(--text-color);
        }
        
        .divider {
            margin: 6px 0;
            border-top: 2px solid var(--border-color);
        }
        
        .map-link {
            color: var(--accent-color);
            text-decoration: none;
            font-weight: bold;
        }
        
        .map-link:hover {
            text-decoration: underline;
        }
    </style>
""", unsafe_allow_html=True)

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Logo
logo_path = os.path.join(current_dir, "logo.png")
try:
    logo = Image.open(logo_path)
    st.image(logo, use_container_width=True)
except FileNotFoundError:
    st.warning(f"⚠️ Logo not found at {logo_path}")

# Main Title
st.markdown("<div class='main-title' style='font-size: clamp(24px, 6vw, 38px); white-space: nowrap;'>🎓 Adhyay Academy (अध्याय अकॅडमी, बावधन)</div>", unsafe_allow_html=True)

# Subheading
st.markdown(
    "<h2 style='text-align: center; margin: 0px 0; font-size: clamp(14px, 4vw, 18px);'>Best CBSE Coaching in Bavdhan</h2>",
    unsafe_allow_html=True
)

# Key Details - No spacing
st.markdown("""
    <div style='text-align: center; display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin: 2px 0;'>
        <h3 style='font-size: 15px; margin: 0;'>⏱️ Batch Starts 1st April onwards</h3>
        <h3 style='font-size: 15px; margin: 0;'>⭐ Top 15 – Limited Seats!</h3>
    </div>
    <div style='text-align: center; margin: 0;'>
        <p style='font-size: 13px; color: var(--accent-color); font-weight: bold; margin: 2px 0;'>✨ Free 1 Week Demo Class ✨</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# Registration Button and QR Code
st.markdown("<div class='section-title'>📝 Register Now</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 12px; margin: 2px 0;'><i>Click to register or scan QR code</i></p>", unsafe_allow_html=True)

col1, col2 = st.columns([1.2, 1])

# Registration Button
with col1:
    st.markdown("""
    <a href='https://forms.gle/aeJ8rivrVKYmkVxy9' target='_blank' style='text-decoration: none;'>
        <button class='register-btn'>📋 Click to Register →</button>
    </a>
    """, unsafe_allow_html=True)

# QR Code
with col2:
    st.markdown("<div class='qr-label'>Scan QR</div>", unsafe_allow_html=True)
    
    qr_path = os.path.join(current_dir, "registration_qr.png")
    
    if os.path.exists(qr_path):
        qr_image = Image.open(qr_path)
        st.image(qr_image, use_container_width=True)
    else:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data("https://forms.gle/aeJ8rivrVKYmkVxy9")
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="#1a3a5c", back_color="#ffffff")
        
        qr_bytes = BytesIO()
        qr_image.save(qr_bytes, format="PNG")
        qr_bytes.seek(0)
        
        st.image(qr_bytes, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# Address Section
st.markdown("<div class='section-title'>📍 Location</div>", unsafe_allow_html=True)

col_addr, col_map = st.columns([1, 1])

with col_addr:
    st.markdown("""
    <div class='section-content' style='text-align: center;'>
        <b>301, Sushant Complex</b><br>
        Near Suryadatta College<br>
        Patilnagar, Bavdhan<br>
        <span style='color: #ffc107; font-weight: bold;'>Pune, Maharashtra</span>
    </div>
    """, unsafe_allow_html=True)

with col_map:
    st.markdown("""
    <div class='section-content' style='text-align: center; display: flex; flex-direction: column; justify-content: center; height: 100%;'>
        <a href='https://maps.app.goo.gl/w1R8CnZozLrspfEs5' target='_blank' class='map-link' style='font-size: 15px; margin: 8px 0;'>
            🗺️ View on Google Maps
        </a>
        <p style='font-size: 12px; color: var(--text-color); margin-top: 6px;'>Get directions & navigate easily</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# Contact Section
st.markdown("<div class='section-title'>📞 Contact Us</div>", unsafe_allow_html=True)

st.markdown("""
<div style='display: flex; justify-content: space-around; flex-wrap: wrap; gap: 8px;'>
    <div class='contact-item' style='flex: 1; min-width: 140px;'>
        <span>👨‍🏫 <b>Shubham Sir</b><br>📱 9561600698</span>
    </div>
    <div class='contact-item' style='flex: 1; min-width: 140px;'>
        <span>👨‍🏫 <b>Pravin Sir</b><br>📱 8796676332</span>
    </div>
    <div class='contact-item' style='flex: 1; min-width: 140px;'>
        <span>👩‍🏫 <b>Sujata Ma'am</b><br>📱 7898271093</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class='footer'>
    <h3>🎯 Enroll Now – Limited Seats Available!</h3>
    <p style='color: #ccc;'>© 2026 Adhyay Academy – Bavdhan | All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)

# Social Media Links
st.markdown("<div style='text-align: center; margin-top: 8px;'><b style='color: #1a3a5c; font-size: 13px;'>Follow Us</b></div>", unsafe_allow_html=True)

col_ig, col_fb, col_goog = st.columns(3)

with col_ig:
    st.markdown("""
    <a href='https://www.instagram.com/adhyay_academy/' target='_blank' style='text-decoration: none; display: block; text-align: center;'>
        <div style='background-color: #E4405F; color: white; padding: 10px 16px; border-radius: 6px; font-weight: bold; font-size: 13px; cursor: pointer;'>📷 Instagram</div>
    </a>
    """, unsafe_allow_html=True)

with col_fb:
    st.markdown("""
    <a href='https://m.facebook.com/people/Adhyay-Academy/61568877721892/' target='_blank' style='text-decoration: none; display: block; text-align: center;'>
        <div style='background-color: #1877F2; color: white; padding: 10px 16px; border-radius: 6px; font-weight: bold; font-size: 13px; cursor: pointer;'>f Facebook</div>
    </a>
    """, unsafe_allow_html=True)

with col_goog:
    st.markdown("""
    <a href='https://share.google/Zq7iyTorWjHU9SueH' target='_blank' style='text-decoration: none; display: block; text-align: center;'>
        <div style='background-color: #4285F4; color: white; padding: 10px 16px; border-radius: 6px; font-weight: bold; font-size: 13px; cursor: pointer;'>🔍 Google</div>
    </a>
    """, unsafe_allow_html=True)