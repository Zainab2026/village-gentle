"""
Quick Demo: Village Gentle Multilingual System
Shows how the translation works across different languages
"""

import streamlit as st
from language_manager import translate, set_user_language, SUPPORTED_LANGUAGES

def demo_translations():
    st.title("🌍 Village Gentle - Multilingual Demo")
    
    st.markdown("""
    ## 🎯 SIH Problem Statement Solution
    
    **Problem**: Language barriers limit farmers' access to modern agri-tech resources
    
    **Solution**: Complete multilingual support for 25+ languages including Indian regional languages
    """)
    
    # Language selection
    st.subheader("🌐 Select Language to See Translation")
    
    demo_languages = ["English", "Hindi", "Bengali", "Tamil", "Telugu", "Marathi", "Gujarati"]
    selected_lang = st.selectbox("Choose Language:", demo_languages)
    
    # Set the language
    set_user_language(selected_lang)
    
    st.markdown("---")
    
    # Demo key phrases
    st.subheader(f"📝 Key App Features in {selected_lang}")
    
    key_features = {
        "App Title": "Village Gentle - Smart Farming Assistant",
        "Navigation": "Navigation Menu",
        "Smart Chatbot": "Smart Chatbot - Get personalized farming advice",
        "Crop Recommendations": "Crop Recommendations - AI-powered suggestions", 
        "Weather Advisory": "Weather Advisory - Real-time weather updates",
        "Healthcare": "Healthcare Assistance - Health guidance for farmers",
        "Economic Opportunities": "Economic Opportunities - Business and funding",
        "Pest Detection": "Pest Detection - AI crop disease identification",
        "Report Issues": "Report Issues - Community problem reporting",
        "Welcome Message": "Welcome back! Ready to optimize your farming journey?",
        "Form Elements": {
            "Submit": "Submit",
            "Cancel": "Cancel", 
            "Search": "Search",
            "Upload": "Upload Image",
            "Processing": "Processing...",
            "Success": "Success! Operation completed.",
            "Error": "Error occurred. Please try again."
        }
    }
    
    # Display translations
    for category, content in key_features.items():
        if isinstance(content, dict):
            st.write(f"**{category}:**")
            for key, value in content.items():
                translated = translate(value)
                st.write(f"  • {key}: `{translated}`")
        else:
            translated = translate(content)
            st.write(f"**{category}:** `{translated}`")
    
    st.markdown("---")
    
    # Interactive demo
    st.subheader("🎮 Interactive Demo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input(translate("Enter your name"), placeholder=translate("Your full name"))
        location = st.text_input(translate("Enter location"), placeholder=translate("Village, District, State"))
        
        if st.button(translate("Submit Form")):
            if name and location:
                st.success(translate(f"Hello {name} from {location}! Welcome to Village Gentle."))
            else:
                st.warning(translate("Please fill all fields"))
    
    with col2:
        st.write(f"**{translate('Current Language')}:** {selected_lang}")
        st.write(f"**{translate('Language Code')}:** {SUPPORTED_LANGUAGES[selected_lang]['code']}")
        st.write(f"**{translate('Native Name')}:** {SUPPORTED_LANGUAGES[selected_lang]['native']}")
    
    # Benefits section
    st.markdown("---")
    st.subheader("✅ Benefits for Farmers")
    
    benefits = [
        "Access farming advice in native language",
        "No language barrier for using modern technology", 
        "Better understanding of agricultural recommendations",
        "Increased adoption of scientific farming practices",
        "Improved crop yields through better information access"
    ]
    
    for benefit in benefits:
        st.write(f"• {translate(benefit)}")
    
    # Technical info
    st.markdown("---")
    st.subheader("🔧 Technical Implementation")
    
    st.code("""
# How to use in your code:
from language_manager import multilingual_page, translate

@multilingual_page
def my_farming_page():
    st.title(translate("Smart Farming Assistant"))
    
    if st.button(translate("Get Crop Recommendation")):
        st.success(translate("Recommendation generated successfully!"))
    """, language="python")
    
    st.markdown("""
    ### 🚀 Key Features:
    - **Real-time Translation**: Instant language switching
    - **Caching System**: Improved performance with local cache
    - **Fallback Support**: Graceful degradation if translation fails
    - **25+ Languages**: Including all major Indian regional languages
    - **Easy Integration**: Simple decorator pattern for existing pages
    """)

if __name__ == "__main__":
    st.set_page_config(
        page_title="Village Gentle Multilingual Demo",
        page_icon="🌍",
        layout="wide"
    )
    demo_translations()