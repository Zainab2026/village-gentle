import streamlit as st
import base64

def get_base64_image(image_path):
    """Convert image to base64 string for CSS embedding"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

def load_village_gentle_styles():
    """Apply Village Gentle glassmorphism styling with gentle.jpg background"""
    
    # Get base64 encoded background image
    bg_image = get_base64_image("gentle.jpg")
    
    # Background CSS with fallback
    if bg_image:
        background_css = f"""
        .stApp {{
            background: linear-gradient(rgba(14, 17, 23, 0.85), rgba(14, 17, 23, 0.85)), 
                       url(data:image/jpeg;base64,{bg_image}) center/cover no-repeat fixed;
            min-height: 100vh;
        }}
        """
    else:
        background_css = """
        .stApp {
            background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 50%, #81C784 100%);
            min-height: 100vh;
        }
        """
    
    css = f"""
    <style>
    /* Village Gentle Custom Styles */
    
    /* Main App Background */
    {background_css}
    
    /* Header Styling */
    .main-header {{
        background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    .main-header h1 {{
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }}
    
    .main-header p {{
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
    }}
    
    /* Auth Container */
    .auth-container {{
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 3rem;
        margin: 2rem auto;
        max-width: 500px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        border: 2px solid rgba(76, 175, 80, 0.3);
    }}
    
    /* Auth Container Text Colors */
    .auth-container h1,
    .auth-container h2,
    .auth-container h3 {{
        color: #2E7D32 !important;
        font-weight: 700;
    }}
    
    .auth-container p,
    .auth-container div,
    .auth-container span {{
        color: #424242 !important;
    }}
    
    .auth-container .gradient-text {{
        background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    /* Card Styling */
    .feature-card {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }}
    
    .feature-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
        background: rgba(255, 255, 255, 0.15);
    }}
    
    /* Button Styling */
    .stButton > button {{
        background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.4);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(46, 125, 50, 0.6);
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
    }}
    
    /* Input Styling - Adaptive for both light and dark backgrounds */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {{
        background: rgba(255, 255, 255, 0.15) !important;
        border: 2px solid rgba(76, 175, 80, 0.6) !important;
        border-radius: 10px !important;
        color: white !important;
        backdrop-filter: blur(10px);
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {{
        border-color: #4CAF50 !important;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.4) !important;
        background: rgba(255, 255, 255, 0.25) !important;
        color: white !important;
    }}
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {{
        color: rgba(255, 255, 255, 0.7) !important;
    }}
    
    /* Auth Container Input Styling - Special case for auth page */
    .auth-container .stTextInput > div > div > input,
    .auth-container .stTextArea > div > div > textarea,
    .auth-container .stNumberInput > div > div > input {{
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(76, 175, 80, 0.4) !important;
        color: #2E7D32 !important;
        font-weight: 600;
    }}
    
    .auth-container .stTextInput > div > div > input:focus,
    .auth-container .stTextArea > div > div > textarea:focus,
    .auth-container .stNumberInput > div > div > input:focus {{
        background: white !important;
        border-color: #4CAF50 !important;
        color: #2E7D32 !important;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.3) !important;
    }}
    
    .auth-container .stTextInput > div > div > input::placeholder,
    .auth-container .stTextArea > div > div > textarea::placeholder {{
        color: rgba(46, 125, 50, 0.6) !important;
    }}
    
    /* Input Labels - Adaptive */
    .stTextInput > label,
    .stTextArea > label,
    .stNumberInput > label {{
        color: white !important;
        font-weight: 600 !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    }}
    
    /* Auth Container Labels */
    .auth-container .stTextInput > label,
    .auth-container .stTextArea > label,
    .auth-container .stNumberInput > label {{
        color: #2E7D32 !important;
        font-weight: 700 !important;
        text-shadow: none;
    }}
    
    /* Select box styling */
    .stSelectbox > div > div {{
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        backdrop-filter: blur(5px);
    }}
    
    /* Sidebar Styling */
    .css-1d391kg {{
        background: #262730 !important;
        backdrop-filter: blur(10px);
    }}
    
    /* Additional sidebar selectors for different Streamlit versions */
    .css-1d391kg, 
    [data-testid="stSidebar"],
    .stSidebar > div,
    section[data-testid="stSidebar"] {{
        background: #262730 !important;
    }}
    
    /* Success/Error Messages */
    .stSuccess {{
        background: rgba(76, 175, 80, 0.1);
        border: 1px solid rgba(76, 175, 80, 0.3);
        border-radius: 10px;
        backdrop-filter: blur(5px);
    }}
    
    .stError {{
        background: rgba(244, 67, 54, 0.1);
        border: 1px solid rgba(244, 67, 54, 0.3);
        border-radius: 10px;
        backdrop-filter: blur(5px);
    }}
    
    .stWarning {{
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-radius: 10px;
        backdrop-filter: blur(5px);
    }}
    
    .stInfo {{
        background: rgba(33, 150, 243, 0.1);
        border: 1px solid rgba(33, 150, 243, 0.3);
        border-radius: 10px;
        backdrop-filter: blur(5px);
    }}
    
    /* Navigation Styling */
    .nav-item {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }}
    
    .nav-item:hover {{
        background: rgba(255, 255, 255, 0.2);
        transform: translateX(5px);
    }}
    
    /* Enhanced Radio Button Styling */
    .stRadio > div {{
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }}
    
    .stRadio > div > label {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
    }}
    
    .stRadio > div > label:hover {{
        background: rgba(255, 255, 255, 0.2);
        transform: translateX(5px);
    }}
    
    /* Progress Bar Styling */
    .stProgress > div > div {{
        background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%);
        border-radius: 10px;
    }}
    
    /* Glassmorphism Effect */
    .glass-effect {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }}
    
    /* Gradient Text */
    .gradient-text {{
        background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }}
    
    /* Chat Message Styling */
    .chat-message {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4CAF50;
    }}
    
    .user-message {{
        background: rgba(76, 175, 80, 0.2);
        border-left-color: #4CAF50;
        margin-left: 2rem;
    }}
    
    .bot-message {{
        background: rgba(46, 125, 50, 0.2);
        border-left-color: #2E7D32;
        margin-right: 2rem;
    }}
    
    /* Dataframe styling */
    .stDataFrame {{
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }}
    
    /* File uploader styling */
    .stFileUploader > div {{
        background: rgba(255, 255, 255, 0.1);
        border: 2px dashed rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }}
    
    .stFileUploader > div:hover {{
        border-color: #4CAF50;
        background: rgba(76, 175, 80, 0.1);
    }}
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {{
        .main-header h1 {{
            font-size: 2rem;
        }}
        
        .auth-container {{
            margin: 1rem;
            padding: 2rem;
        }}
        
        .feature-card {{
            padding: 1.5rem;
        }}
    }}
    
    /* Loading Animation */
    .loading-spinner {{
        border: 4px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top: 4px solid #4CAF50;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }}
    
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* ========================================
       FORCED DARK THEME - OVERRIDE ALL SYSTEM PREFERENCES
       ======================================== */
    
    /* Force dark theme on ALL elements regardless of system preference */
    *, *::before, *::after {{
        color-scheme: dark !important;
    }}
    
    /* Override Streamlit's default colors */
    .stApp, .stApp * {{
        color-scheme: dark !important;
    }}
    
    /* Main text colors - FORCED WHITE */
    .stMarkdown, .stMarkdown *,
    .stText, .stText *,
    p, div, span, h1, h2, h3, h4, h5, h6,
    .css-1d391kg, .css-1d391kg *,
    .stSidebar, .stSidebar *,
    .element-container, .element-container *,
    .block-container, .block-container * {{
        color: white !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    }}
    
    /* Navigation text - FORCED WHITE */
    .stRadio > div > label,
    .stRadio > div > label *,
    .stSelectbox > div,
    .stSelectbox > div *,
    .stSelectbox option {{
        color: white !important;
    }}
    
    /* Input labels - FORCED WHITE */
    .stTextInput > label,
    .stTextArea > label,
    .stNumberInput > label,
    .stSelectbox > label,
    .stFileUploader > label,
    .stDateInput > label,
    .stTimeInput > label {{
        color: white !important;
        font-weight: 600 !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    }}
    
    /* Chat messages - FORCED WHITE */
    .chat-message, .chat-message * {{
        color: white !important;
    }}
    
    /* Feature cards - FORCED WHITE */
    .feature-card, .feature-card *,
    .glass-effect, .glass-effect * {{
        color: white !important;
    }}
    
    /* Force all Streamlit components to use white text */
    .stButton, .stButton *,
    .stDownloadButton, .stDownloadButton *,
    .stCheckbox, .stCheckbox *,
    .stRadio, .stRadio *,
    .stSlider, .stSlider *,
    .stProgress, .stProgress *,
    .stSpinner, .stSpinner *,
    .stDataFrame, .stDataFrame *,
    .stTable, .stTable *,
    .stMetric, .stMetric *,
    .stColumns, .stColumns *,
    .stTabs, .stTabs *,
    .stExpander, .stExpander *,
    .stContainer, .stContainer * {{
        color: white !important;
    }}
    
    /* Override any system light mode attempts */
    @media (prefers-color-scheme: light) {{
        *, *::before, *::after {{
            color: white !important;
            color-scheme: dark !important;
        }}
        
        .stApp {{
            color-scheme: dark !important;
        }}
        
        /* Force all text to be white even in light mode */
        .stMarkdown, .stText, p, div, span, h1, h2, h3, h4, h5, h6,
        label, .stRadio label, .stCheckbox label, .stSelectbox label {{
            color: white !important;
        }}
    }}
    
    /* General Label styling - FORCED WHITE */
    label, label *,
    .stMarkdown label,
    .stRadio label,
    .stCheckbox label,
    .stSelectbox label {{
        color: white !important;
    }}
    
    /* ========================================
       FORCE ALL LINKS TO BE BLUE
       ======================================== */
    
    /* All link elements - FORCED BLUE */
    a, a:link, a:visited, a:hover, a:active,
    .stMarkdown a, .stMarkdown a:link, .stMarkdown a:visited, .stMarkdown a:hover, .stMarkdown a:active,
    .stText a, .stText a:link, .stText a:visited, .stText a:hover, .stText a:active,
    div a, div a:link, div a:visited, div a:hover, div a:active,
    p a, p a:link, p a:visited, p a:hover, p a:active,
    span a, span a:link, span a:visited, span a:hover, span a:active {{
        color: #2196F3 !important;
        text-decoration: underline !important;
        font-weight: 500 !important;
    }}
    
    /* Link hover effects */
    a:hover, .stMarkdown a:hover, .stText a:hover, div a:hover, p a:hover, span a:hover {{
        color: #1976D2 !important;
        text-decoration: underline !important;
        opacity: 0.8;
    }}
    
    /* Links in expandable sections */
    .streamlit-expanderContent a,
    .streamlit-expanderContent a:link,
    .streamlit-expanderContent a:visited,
    .streamlit-expanderContent a:hover,
    .streamlit-expanderContent a:active {{
        color: #2196F3 !important;
        text-decoration: underline !important;
    }}
    
    /* Links in cards and containers */
    .feature-card a, .feature-card a:link, .feature-card a:visited, .feature-card a:hover, .feature-card a:active,
    .glass-effect a, .glass-effect a:link, .glass-effect a:visited, .glass-effect a:hover, .glass-effect a:active,
    .chat-message a, .chat-message a:link, .chat-message a:visited, .chat-message a:hover, .chat-message a:active {{
        color: #2196F3 !important;
        text-decoration: underline !important;
    }}
    
    /* Override any white text on links */
    * a, * a:link, * a:visited, * a:hover, * a:active {{
        color: #2196F3 !important;
        text-decoration: underline !important;
    }}
    
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

def create_main_header(title, subtitle=""):
    """Create a styled main header"""
    st.markdown(f"""
    <div class="main-header">
        <h1>{title}</h1>
        {f'<p>{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def create_feature_card(title, content, icon="🌾"):
    """Create a styled feature card"""
    st.markdown(f"""
    <div class="feature-card">
        <h3>{icon} {title}</h3>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)

def create_glass_container(content):
    """Create a glass effect container"""
    st.markdown(f"""
    <div class="glass-effect" style="padding: 1.5rem; margin: 1rem 0;">
        {content}
    </div>
    """, unsafe_allow_html=True)

def create_custom_card(title, content, icon="🔮"):
    """Create a custom styled card for issues page"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(139, 195, 74, 0.1));
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    ">
        <h3 style="
            color: #2E7D32;
            font-size: 18px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        ">{icon} {title}</h3>
        <div style="
            color: #424242;
            font-size: 14px;
            line-height: 1.6;
            white-space: pre-wrap;
        ">{content}</div>
    </div>
    """, unsafe_allow_html=True)

def create_authority_card(title, snippet, link):
    """Create a card for government authority information"""
    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(33, 150, 243, 0.2);
        border-left: 4px solid #2196F3;
    ">
        <h4 style="
            color: #1976D2;
            font-size: 16px;
            margin-bottom: 8px;
            line-height: 1.4;
        ">{title}</h4>
        <p style="
            color: #666;
            font-size: 14px;
            margin-bottom: 12px;
            line-height: 1.5;
        ">{snippet}</p>
        <a href="{link}" target="_blank" style="
            color: #2196F3;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
        ">Learn More →</a>
    </div>
    """, unsafe_allow_html=True)