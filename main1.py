import streamlit as st
import re
from datetime import datetime
from auth import auth_ui
from styles import load_village_gentle_styles, create_main_header, create_feature_card
from language_manager import multilingual_page, get_ui_text, translate, create_language_selector, init_language_system
from config import config
from modern_ui import apply_modern_ui, modern_header, modern_card, global_branding

# ✅ Set page config
st.set_page_config(
    page_title="Village Gentle", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# ✅ Apply modern styling
apply_modern_ui()

# ✅ Global Branding (Logo & Title)
global_branding()

# ✅ Language Selector (Main Page)
create_language_selector(sidebar=False)

# ✅ Force custom theme and hide settings menu
st.markdown("""
<script>
(function() {
    function hideSettingsMenu() {
        const settingsButton = document.querySelector('[data-testid="stToolbar"]');
        const mainMenu = document.querySelector('#MainMenu');
        if (settingsButton) settingsButton.style.display = 'none';
        if (mainMenu) mainMenu.style.visibility = 'hidden';
    }
    hideSettingsMenu();
    const observer = new MutationObserver(hideSettingsMenu);
    observer.observe(document.body, { childList: true, subtree: true });
})();
</script>
""", unsafe_allow_html=True)

# ✅ Session defaults
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ✅ User Info & Logout (Main Page - moved from sidebar)
if st.session_state.logged_in:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"👤 **{translate('Logged in as')}:** {st.session_state.email}")
    with col2:
        if st.button(f"🚪 {translate('Logout')}", key="main_logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# ✅ Block access if not logged in
if not st.session_state.logged_in:
    # Use a placeholder to ensure auth UI is isolated and can be cleared
    auth_placeholder = st.empty()
    with auth_placeholder.container():
        auth_ui()
    st.stop()

# ✅ Initialize language system
init_language_system()
ui_text = get_ui_text()

# ✅ Validate API keys
if not config.validate_keys():
    st.stop()

# Navigation options
nav_options = {
    f"🏠 {translate('Home')}": "home",
    f"💬 {ui_text['smart_chatbot']}": "chatbot",
    f"📋 {ui_text['crop_recommendations']}": "crop", 
    f"🌦 {ui_text['weather_advisory']}": "weather",
    f"🏥 {ui_text['healthcare_assistance']}": "healthcare",
    f"📈 {ui_text['economic_opportunities']}": "economic",
    f"🌱 {ui_text['pest_detection']}": "pest",
    f"🐞 {ui_text['report_issues']}": "issues"
}

# ✅ Native Easy Navigation using Tabs at the TOP
tabs = st.tabs(list(nav_options.keys()))

for i, (label, feature_id) in enumerate(nav_options.items()):
    with tabs[i]:
        if feature_id == "home":
            # Welcome Header
            modern_header(translate("Village Gentle"), translate("Your intelligent companion for modern agriculture"))
            
            # User welcome message
            modern_card(
                ui_text["welcome_back"],
                f"{ui_text['hello_farmer'].replace('Farmer', st.session_state.get('email', 'Farmer'))}",
                "👋"
            )
            
            # Quick links or summary could go here
            st.markdown(f"### {translate('Explore our features using the navigation bar above!')}")
            
        elif feature_id == "chatbot":
            from chatbot_page import chatbot_page
            chatbot_page()
        elif feature_id == "crop":
            from recommendation_page import recommendation_page
            recommendation_page()
        elif feature_id == "weather":
            from weather_advisory import weather_advisory
            weather_advisory()
        elif feature_id == "healthcare":
            from healthcare import healthcare_page
            healthcare_page()
        elif feature_id == "economic":
            from economic_opportunities import economic_opportunities_page
            economic_opportunities_page()
        elif feature_id == "pest":
            from pest import pest_detection_page
            pest_detection_page()
        elif feature_id == "issues":
            from issues_page import issues_page
            issues_page()

# ✅ Enhanced Footer
st.markdown(f"""
<div style="
    margin-top: 3rem;
    padding: 2rem;
    text-align: center;
    background: rgba(30, 41, 59, 0.5);
    border-radius: 20px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
">
    <p style="color: #94A3B8; margin: 0;">
        {translate('Made with ❤ for farmers everywhere')}
    </p>
</div>
""", unsafe_allow_html=True)