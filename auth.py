# auth.py
import streamlit as st
from pymongo import MongoClient
import hashlib
from styles import load_village_gentle_styles
from language_manager import translate, create_language_selector, set_user_language
from config import config
from modern_ui import apply_modern_ui


# ✅ MongoDB Atlas Connection from config
MONGO_URI = config.MONGODB_URI
client = MongoClient(MONGO_URI)
db = client["village_gentle"]
users_collection = db["users"]

# ✅ Password Hasher
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ✅ Register New User
def register_user(email, password):
    if users_collection.find_one({"email": email}):
        return False, "❌ Email already registered!"
    hashed_pw = hash_password(password)
    users_collection.insert_one({"email": email, "password": hashed_pw})
    return True, "✅ Registered successfully!"

# ✅ Validate Login
def login_user(email, password):
    hashed_pw = hash_password(password)
    user = users_collection.find_one({"email": email, "password": hashed_pw})
    return user is not None

# ✅ Enhanced Auth UI with glassmorphism styling
def auth_ui():
    # Initialize language system
    if 'user_language' not in st.session_state:
        st.session_state.user_language = 'English'
        st.session_state.user_language_code = 'en'
    
    # Apply styling
    apply_modern_ui()
    
    # Language selector will be available after login
    
    # ✅ Signal Flutter that auth page is ready
    st.markdown("""
    <script>
        window.villageGentleReady = true;
        window.authPageLoaded = true;
        console.log('Village Gentle Auth Ready!');
    </script>
    """, unsafe_allow_html=True)
    
    # Center the auth container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Welcome header with gradient
        st.markdown(f"""
        <div class="auth-container">
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem; background: linear-gradient(135deg, #10B981 0%, #3B82F6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Village Gentle</h1>
                <p style="color: #94A3B8 !important; font-size: 1.1rem; font-weight: 500;">{translate("Your intelligent farming companion")}</p>
            </div>
        """, unsafe_allow_html=True)

        if "auth_tab" not in st.session_state:
            st.session_state.auth_tab = "Login"  # Set Login as default tab

        # Enhanced tab selection
        st.markdown(f"### {translate('Choose your action:')}")
        tab_col1, tab_col2 = st.columns(2)
        
        with tab_col1:
            if st.button(f"🔑 {translate('Login')}", use_container_width=True, type="primary" if st.session_state.auth_tab == "Login" else "secondary"):
                st.session_state.auth_tab = "Login"
                st.rerun()
        
        with tab_col2:
            if st.button(f"📝 {translate('Register')}", use_container_width=True, type="primary" if st.session_state.auth_tab == "Register" else "secondary"):
                st.session_state.auth_tab = "Register"
                st.rerun()

        st.markdown("---")

        # ✅ Pre-fill dummy only on Login tab
        email_default = "your.email@gmail.com" if st.session_state.auth_tab == "Login" else ""
        password_default = "password@1234" if st.session_state.auth_tab == "Login" else ""

        # Enhanced form styling
        if st.session_state.auth_tab == "Login":
            st.markdown(f"### 🔑 {translate('Welcome back!')}")
            st.markdown(f"*{translate('Use the pre-filled credentials or enter your own')}*")
        else:
            st.markdown(f"### 📝 {translate('Create your account')}")
            st.markdown(f"*{translate('Join the farming community')}*")

        email = st.text_input(translate("📧 Email Address"), value=email_default,
                            placeholder=translate("Enter your email address"),
                            help=translate("We'll never share your email with anyone else"))
        
        password = st.text_input(translate("🔒 Password"), type="password", value=password_default,
                               placeholder=translate("Enter your password"),
                               help=translate("Choose a strong password with at least 6 characters"))

        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.auth_tab == "Register":
            if st.button("🚀 Create Account", use_container_width=True, type="primary"):
                if email and password and len(password) >= 6:
                    with st.spinner("Creating your account..."):
                        success, msg = register_user(email, password)
                        if success:
                            st.success(msg)
                            st.balloons()
                            st.session_state.auth_tab = "Login"
                            st.rerun()
                        else:
                            st.error(msg)
                elif len(password) < 6:
                    st.warning(translate("⚠ Password must be at least 6 characters long."))
                else:
                    st.warning(translate("⚠ Please fill both email and password."))

        elif st.session_state.auth_tab == "Login":
            if st.button("🔑 Sign In", use_container_width=True, type="primary"):
                if email and password and email != "xxxx" and password != "xxxx":
                    with st.spinner("Signing you in..."):
                        if login_user(email, password):
                            st.success(translate("✅ Welcome back! Redirecting..."))
                            st.session_state.logged_in = True
                            st.session_state.email = email
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(translate("❌ Invalid credentials. Please check your email and password."))
                else:
                    st.warning(translate("⚠ Please fill both email and password."))

        # Additional info section
        st.markdown("---")
        if st.session_state.auth_tab == "Login":
            st.markdown("""
            <div style="text-align: center; color: #424242 !important; font-size: 0.9rem;">
                <p style="color: #424242 !important;">Don't have an account? Click <strong style="color: #2E7D32;">Register</strong> above</p>
                <p style="color: #424242 !important;">🔒 Your data is secure and encrypted</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; color: #424242 !important; font-size: 0.9rem;">
                <p style="color: #424242 !important;">Already have an account? Click <strong style="color: #2E7D32;">Login</strong> above</p>
                <p style="color: #424242 !important;">🌾 Join our community of smart farmers</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Feature highlights
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"### ✨ {translate('What you will get access to')}:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card" style="text-align: center;">
            <h3>🤖 Smart Chatbot</h3>
            <p>Get personalized farming advice powered by AI</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card" style="text-align: center;">
            <h3>🌦️ Weather Advisory</h3>
            <p>Real-time weather updates for better crop planning</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card" style="text-align: center;">
            <h3>🌱 Pest Detection</h3>
            <p>AI-powered crop disease identification and solutions</p>
        </div>
        """, unsafe_allow_html=True)