import streamlit as st
import base64

import os

def get_base64_image(image_path):
    try:
        # Use absolute path to ensure it works on all platforms
        abs_path = os.path.join(os.getcwd(), image_path)
        with open(abs_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

def apply_modern_ui():
    """Apply a modern, Next.js-like UI overhaul to Streamlit"""
    
    bg_image = get_base64_image("gentle.png")
    bg_style = ""
    if bg_image:
        bg_style = f"""
        background: linear-gradient(rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.9)), 
                   url(data:image/jpeg;base64,{bg_image}) center/cover no-repeat fixed;
        """
    else:
        bg_style = "background: #0F172A;"

    css = f"""
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    
    <style>
    /* Base Overrides */
    * {{
        font-family: 'Outfit', sans-serif !important;
    }}

    .stApp {{
        {bg_style}
        color: #F8FAFC !important;
    }}

    /* Hide Streamlit Elements */
    [data-testid="stHeader"], 
    [data-testid="stSidebar"], 
    [data-testid="stToolbar"],
    footer {{
        display: none !important;
    }}

    .block-container {{
        padding-top: 0.5rem !important;
        max-width: 1200px !important;
    }}

    /* Premium Tab Navigation (Top Nav) */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
        background-color: rgba(15, 23, 42, 0.9) !important;
        backdrop-filter: blur(20px);
        padding: 0.5rem 1rem;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: sticky;
        top: 0;
        z-index: 1000;
        margin-bottom: 2rem;
        justify-content: flex-start;
        overflow-x: auto;
        overflow-y: hidden;
        scroll-behavior: smooth;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }}

    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {{
        display: none;
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 45px;
        white-space: nowrap;
        flex-shrink: 0;
        background-color: transparent !important;
        border: none !important;
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        padding: 0 0.75rem !important;
    }}

    .stTabs [data-baseweb="tab"]:hover {{
        color: #10B981 !important;
        background-color: rgba(16, 185, 129, 0.05) !important;
        border-radius: 10px !important;
    }}

    .stTabs [aria-selected="true"] {{
        color: #10B981 !important;
        background-color: transparent !important;
    }}

    .stTabs [data-baseweb="tab-highlight"] {{
        background-color: #10B981 !important;
        height: 2px !important;
        border-radius: 2px !important;
    }}



    /* Modern Cards */
    .modern-card {{
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .modern-card:hover {{
        transform: translateY(-8px);
        background: rgba(30, 41, 59, 0.7);
        border-color: rgba(16, 185, 129, 0.3);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    }}

    /* Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2) !important;
    }}

    .stButton > button:hover {{
        transform: scale(1.02) !important;
        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4) !important;
    }}

    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #F8FAFC !important;
        padding: 0.8rem 1rem !important;
    }}

    .stTextInput > div > div > input:focus {{
        border-color: #10B981 !important;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2) !important;
    }}

    /* Auth Container */
    .auth-container {{
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 24px !important;
        padding: 3rem !important;
        margin: 2rem auto !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5) !important;
    }}

    .auth-container h1, .auth-container h2, .auth-container h3 {{
        color: #F8FAFC !important;
    }}

    .auth-container p, .auth-container span, .auth-container label {{
        color: #94A3B8 !important;
    }}

    /* Animations */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .animate-fade-in {{
        animation: fadeIn 0.6s ease-out forwards;
    }}
    </style>
    
    <script>
    function setNav(page) {{
        const streamlitDoc = window.parent.document;
        const buttons = streamlitDoc.querySelectorAll('button');
        for (const btn of buttons) {{
            if (btn.innerText.includes(page)) {{
                btn.click();
                break;
            }}
        }}
    }}
    </script>
    """
    st.markdown(css, unsafe_allow_html=True)


def global_branding():
    """Render a global branding header at the very top"""
    st.markdown(f"""
    <div style="text-align: center; padding: 1.5rem 0 0.5rem 0; margin-bottom: 1rem;">
        <div style="display: inline-flex; align-items: center; justify-content: center; gap: 1rem; padding: 0.8rem 2.5rem; background: rgba(30, 41, 59, 0.4); backdrop-filter: blur(10px); border-radius: 50px; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);">
            <span style="font-size: 2.2rem; filter: drop-shadow(0 0 10px rgba(16, 185, 129, 0.4));">🌿</span>
            <h1 style="margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px; background: linear-gradient(135deg, #F8FAFC 0%, #10B981 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Village Gentle</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

def modern_header(title, subtitle=""):
    st.markdown(f"""
    <div class="animate-fade-in" style="text-align: center; margin-bottom: 3rem;">
        <h1 style="font-size: 3.5rem; font-weight: 800; margin-bottom: 1rem; background: linear-gradient(135deg, #F8FAFC 0%, #94A3B8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{title}</h1>
        <p style="font-size: 1.2rem; color: #94A3B8; max-width: 700px; margin: 0 auto;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def modern_card(title, content, icon="✨"):
    st.markdown(f"""
    <div class="modern-card animate-fade-in">
        <div style="font-size: 2rem; margin-bottom: 1rem;">{icon}</div>
        <h3 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem; color: #F8FAFC;">{title}</h3>
        <p style="color: #94A3B8; line-height: 1.6;">{content}</p>
    </div>
    """, unsafe_allow_html=True)