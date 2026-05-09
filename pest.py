import streamlit as st
import requests
import base64
from language_manager import multilingual_page, translate, get_user_language_code
from deep_translator import GoogleTranslator
from config import config
from modern_ui import modern_header

# =====================
# Keys from config
# =====================
KINDWISE_API_KEY = config.KINDWISE_API_KEY
MISTRAL_API_KEY = config.MISTRAL_API_KEY
YOUTUBE_API_KEY = config.YOUTUBE_API_KEY
GOOGLE_API_KEY = config.GOOGLE_API_KEY
GOOGLE_CSE_ID = config.GOOGLE_CSE_ID

# =====================
# Helper functions
# =====================
def get_google_article(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": 1
    }
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        items = resp.json().get("items", [])
        if items:
            return items[0]["title"], items[0]["link"]
    return None, None

def get_youtube_videos(query):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 2
    }
    resp = requests.get(url, params=params)
    videos = []
    if resp.status_code == 200:
        for item in resp.json().get("items", []):
            video_id = item['id']['videoId']
            videos.append(f"https://www.youtube.com/watch?v={video_id}")
    return videos

def get_mistral_tips(prompt):
    """Get farming tips from Mistral AI using correct API format"""
    
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}", 
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-tiny",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300,
        "temperature": 0.7
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload)
        if resp.status_code == 200:
            data = resp.json()
            answer = data["choices"][0]["message"]["content"]
            
            # Translate response to user's language
            user_lang = get_user_language_code()
            if user_lang != "en":
                try:
                    answer = GoogleTranslator(source="en", target=user_lang).translate(answer)
                except Exception as trans_error:
                    print(f"Translation failed: {trans_error}")
                    answer = f"[{translate('English')}] {answer}"
            
            return answer
        else:
            st.error(f"{translate('Mistral API error')}: {resp.status_code} - {resp.text}")
            return translate("Unable to generate tips at the moment.")
    except Exception as e:
        st.error(f"{translate('Error calling Mistral API')}: {str(e)}")
        return translate("Unable to generate tips at the moment.")

@multilingual_page
def pest_detection_page():
    """Pest and Disease Detection Page - Importable function"""
    modern_header(translate("🌱 Crop & Disease Detection"), translate("Upload an image of your crop to detect diseases, get expert treatment guidance, and access agricultural resources."))
    
    # Visual separator and instruction
    st.markdown("---")
    st.markdown(f"### {translate('📤 Upload Your Crop Image')}")
    st.info(f"💡 **{translate('Tip')}:** {translate('Take clear photos in good lighting for best results!')}")

    uploaded_file = st.file_uploader(
        translate("📸 Upload an image of your crop"), 
        type=["png", "jpg", "jpeg"],
        help=translate("Drag and drop an image here or click to browse")
    )

    if uploaded_file:
        # Display uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        
        with st.spinner("🔍 Analyzing your crop image..."):
            image_bytes = uploaded_file.read()
            base64_image = base64.b64encode(image_bytes).decode('utf-8')

            # Call Kindwise API
            headers = {
                "Api-Key": KINDWISE_API_KEY,
                "Content-Type": "application/json"
            }
            payload = {"images": [base64_image], "similar_images": True}
            
            try:
                resp = requests.post("https://crop.kindwise.com/api/v1/identification", headers=headers, json=payload)

                if resp.status_code in [200, 201]:
                    data = resp.json()
                    
                    # Check if we have results
                    if "result" in data:
                        crop_suggestions = data["result"].get("crop", {}).get("suggestions", [])
                        disease_suggestions = data["result"].get("disease", {}).get("suggestions", [])

                        # Display crop detection results
                        if crop_suggestions:
                            crop = crop_suggestions[0]
                            confidence = crop['probability'] * 100
                            st.success(f"🌱 **{translate('Crop Detected')}:** {crop['name']} ({crop.get('scientific_name', 'N/A')})")
                            st.info(f"**{translate('Confidence')}:** {confidence:.1f}%")

                        # Display disease detection results in organized boxes
                        if disease_suggestions:
                            st.subheader(translate("🦠 Disease Analysis & Treatment Guide"))
                            infected_diseases = []
                            healthy_crop = True

                            for i, disease in enumerate(disease_suggestions[:3]):  # Show top 3
                                confidence = disease['probability'] * 100
                                disease_name = disease['name']
                                scientific_name = disease.get('scientific_name', 'N/A')
                                
                                # Create expandable box for each disease
                                with st.expander(f"🦠 {disease_name} - {confidence:.1f}% {translate('Probability')}", expanded=(i==0)):
                                    
                                    # Disease Information Section
                                    st.markdown(f"### 📋 {translate('Disease Information')}")
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.info(f"**{translate('Common Name')}:** {disease_name}")
                                        st.info(f"**{translate('Scientific Name')}:** {scientific_name}")
                                        st.info(f"**{translate('Detection Confidence')}:** {confidence:.1f}%")
                                    
                                    with col2:
                                        # Get AI summary about the disease
                                        with st.spinner(translate("Getting disease information...")):
                                            disease_prompt = f"""Provide a brief summary about {disease_name} plant disease including:
1. What causes this disease
2. Common symptoms to look for
3. Which crops are most affected
4. Best prevention methods
Keep it concise and farmer-friendly."""
                                            
                                            disease_summary = get_mistral_tips(disease_prompt)
                                            st.success(f"**🤖 {translate('AI Summary')}:**")
                                            st.write(disease_summary)
                                    
                                    # Treatment Recommendations
                                    st.markdown(f"### 💊 {translate('Treatment Recommendations')}")
                                    with st.spinner(translate("Generating treatment plan...")):
                                        treatment_prompt = f"""As an agricultural expert, provide specific treatment recommendations for {disease_name}:
1. Immediate action steps
2. Organic treatment options
3. Chemical treatment if needed
4. Prevention for future crops
5. Timeline for recovery
Keep advice practical for farmers."""
                                        
                                        treatment_advice = get_mistral_tips(treatment_prompt)
                                        st.write(treatment_advice)
                                    
                                    # Resources Section
                                    st.markdown(f"### 📚 {translate('Additional Resources')}")
                                    
                                    # Create tabs for resources
                                    tab1, tab2 = st.tabs([translate("🔗 Articles"), translate("🎥 Videos")])
                                    
                                    with tab1:
                                        # Get Google articles
                                        query = f"{disease_name} plant disease treatment prevention farming"
                                        title, link = get_google_article(query)
                                        if title and link:
                                            st.markdown(f"📰 **{translate('Recommended Article')}:**")
                                            st.markdown(f"🔗 [{title}]({link})")
                                        else:
                                            st.info(translate("No specific articles found"))
                                    
                                    with tab2:
                                        # Get YouTube videos
                                        video_query = f"{disease_name} treatment farming cure prevention"
                                        videos = get_youtube_videos(video_query)
                                        if videos:
                                            st.markdown(f"🎥 **{translate('Educational Videos')}:**")
                                            for j, video in enumerate(videos[:2]):
                                                st.video(video)
                                        else:
                                            st.info(translate("No educational videos found"))
                                
                                if disease['probability'] > 0.3:  # Lower threshold for better detection
                                    infected_diseases.append(disease_name)
                                    healthy_crop = False

                            # Generate AI tips
                            st.subheader(translate("🤖 AI-Powered Farming Tips"))
                            with st.spinner(translate("Generating personalized farming advice...")):
                                if infected_diseases:
                                    prompt = f"""As an expert agricultural advisor, provide detailed, actionable advice for a farmer whose crop is affected by: {', '.join(infected_diseases)}.

Include:
1. Immediate treatment steps
2. Preventive measures for future
3. Organic/chemical treatment options
4. Timeline for recovery
5. When to consult an agricultural expert

Keep the advice practical and easy to understand for farmers."""
                                else:
                                    crop_name = crop['name'] if crop_suggestions else "the crop"
                                    prompt = f"""As an expert agricultural advisor, provide preventive care tips for {crop_name} to maintain healthy growth.

Include:
1. Regular monitoring practices
2. Preventive treatments
3. Optimal growing conditions
4. Common issues to watch for
5. Best practices for healthy crops

Keep the advice practical and easy to understand for farmers."""

                                tips = get_mistral_tips(prompt)
                                st.success(f"✅ **{translate('Expert Recommendations')}:**")
                                st.write(tips)

                            # Additional resources
                            st.subheader(translate("📚 Additional Resources"))
                            
                            # Create tabs for different resources
                            tab1, tab2 = st.tabs([translate("📰 Articles"), translate("🎥 Videos")])
                            
                            with tab1:
                                st.write(f"**{translate('Relevant Articles')}:**")
                                
                                if infected_diseases:
                                    # Show articles for detected diseases
                                    for i, disease in enumerate(infected_diseases[:2]):  # Limit to 2 diseases
                                        st.write(f"**{i+1}. {translate('Treatment for')} {disease}:**")
                                        query = f"{disease} treatment farming prevention"
                                        title, link = get_google_article(query)
                                        if title and link:
                                            st.write(f"🔗 [{title}]({link})")
                                        else:
                                            st.write(f"   {translate('No specific article found')}")
                                        st.write("")
                                
                                elif disease_suggestions:
                                    # Show articles for top diseases even if probability is low
                                    st.write(f"**{translate('Preventive measures for possible diseases')}:**")
                                    top_disease = disease_suggestions[0]['name']
                                    query = f"{top_disease} prevention farming"
                                    title, link = get_google_article(query)
                                    if title and link:
                                        st.write(f"🔗 [{title}]({link})")
                                    else:
                                        st.write(translate("No specific article found"))
                                
                                # Always show general crop care article
                                if crop_suggestions:
                                    crop_name = crop_suggestions[0]['name']
                                    st.write(f"**{translate('General care for')} {crop_name}:**")
                                    query = f"{crop_name} farming best practices care"
                                    title, link = get_google_article(query)
                                    if title and link:
                                        st.write(f"🔗 [{title}]({link})")
                                    else:
                                        st.write(translate("No general care article found"))
                                else:
                                    st.write(f"**{translate('General crop farming')}:**")
                                    query = "crop farming best practices"
                                    title, link = get_google_article(query)
                                    if title and link:
                                        st.write(f"🔗 [{title}]({link})")
                            
                            with tab2:
                                st.write(f"**{translate('Educational Videos')}:**")
                                
                                # Determine what videos to show
                                if infected_diseases:
                                    # Show treatment videos for detected diseases
                                    primary_disease = infected_diseases[0]
                                    st.write(f"**{translate('Treatment videos for')} {primary_disease}:**")
                                    query = f"{primary_disease} treatment farming cure"
                                    videos = get_youtube_videos(query)
                                    
                                    if videos:
                                        for i, vid in enumerate(videos[:2]):
                                            st.write(f"{translate('Video')} {i+1}: {translate('Treatment Guide')}")
                                            st.video(vid)
                                    else:
                                        st.info(f"{translate('No treatment videos found for')} {primary_disease}")
                                
                                elif disease_suggestions:
                                    # Show prevention videos for possible diseases
                                    top_disease = disease_suggestions[0]['name']
                                    st.write(f"**{translate('Prevention videos for')} {top_disease}:**")
                                    query = f"{top_disease} prevention farming"
                                    videos = get_youtube_videos(query)
                                    
                                    if videos:
                                        for i, vid in enumerate(videos[:2]):
                                            st.write(f"{translate('Video')} {i+1}: {translate('Prevention Guide')}")
                                            st.video(vid)
                                    else:
                                        st.info(f"{translate('No prevention videos found for')} {top_disease}")
                                
                                # Always show general farming videos
                                if crop_suggestions:
                                    crop_name = crop_suggestions[0]['name']
                                    st.write(f"**{translate('General')} {crop_name} {translate('farming tips')}:**")
                                    query = f"{crop_name} farming tips cultivation"
                                else:
                                    st.write(f"**{translate('General farming tips')}:**")
                                    query = "crop farming tips best practices"
                                
                                general_videos = get_youtube_videos(query)
                                if general_videos:
                                    for i, vid in enumerate(general_videos[:1]):  # Show 1 general video
                                        st.write(f"{translate('General Farming Tips')}:")
                                        st.video(vid)
                                else:
                                    st.info(translate("No general farming videos found"))

                        else:
                            st.warning(translate("⚠️ No diseases detected in the image. Your crop appears healthy!"))
                            if crop_suggestions:
                                crop_name = crop_suggestions[0]['name']
                                st.info(f"💡 {translate('Continue monitoring your')} {crop_name} {translate('and maintain good farming practices')}.")
                    else:
                        st.error(translate("❌ Unable to analyze the image. Please try with a clearer image of the crop."))

                else:
                    st.error(f"❌ {translate('Image analysis failed. API Error')}: {resp.status_code}")
                    if resp.status_code == 401:
                        st.error(translate("API key authentication failed."))
                    elif resp.status_code == 429:
                        st.error(translate("API rate limit exceeded. Please try again later."))
                    
            except Exception as e:
                st.error(f"❌ {translate('An error occurred during analysis')}: {str(e)}")
                st.info(translate("Please try again with a different image or check your internet connection."))

    else:
        # Instructions when no file is uploaded
        st.info(translate("👆 Please upload an image of your crop to get started!"))
        
        with st.expander(translate("📋 How to get the best results")):
            tips_content = f"""
            **{translate('For accurate detection')}:**
            - 📸 {translate('Take clear, well-lit photos')}
            - 🔍 {translate('Focus on affected areas (leaves, stems, fruits)')}
            - 📏 {translate('Include some healthy parts for comparison')}
            - 🌅 {translate('Natural daylight works best')}
            - 📱 {translate('Avoid blurry or dark images')}
            
            **{translate('Supported formats')}:** PNG, JPG, JPEG
            """
            st.markdown(tips_content)

    # 🐜 **Professional Pest Control Services**
    st.markdown("---")
    st.header(translate("🐜 Professional Pest Control Services"))
    
    # Private Pest Control Service Providers
    st.subheader(translate("🏢 Private Pest Control Service Providers"))
    st.info(translate("These companies offer pest control services tailored for agricultural needs"))
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Silver Sine Bio-Tec
        with st.container():
            st.markdown(f"### 🌱 Silver Sine Bio-Tec")
            st.write(f"📍 **{translate('Location')}:** {translate('Ahmedabad, Gujarat')}")
            st.write(f"🛠️ **{translate('Services')}:** {translate('Agricultural pest control solutions')}")
            st.write(f"🔗 **{translate('Contact')}:** [Silver Sine Bio-Tec](https://silversinebiotech.com)")
            st.markdown("---")
        
        # Rentokil Pest Control India
        with st.container():
            st.markdown(f"### 🐭 Rentokil Pest Control India")
            st.write(f"📍 **{translate('Location')}:** {translate('Pan India Operations')}")
            st.write(f"🎯 **{translate('Specialization')}:** {translate('Professional pest control for agriculture and commercial use')}")
            st.write(f"🔗 **{translate('Contact')}:** [Rentokil Pest Control India](https://www.rentokil-pestcontrolindia.com)")
    
    with col2:
        # Sensation Pest Control Services
        with st.container():
            st.markdown(f"### ⚡ Sensation Pest Control Services")
            st.write(f"🛠️ **{translate('Services')}:** {translate('Integrated Pest Management, fumigation, ship sanitization, anti-termite treatment')}")
            st.write(f"🏆 **{translate('Certifications')}:** WHO, NIPHM, ISO 9001-2015")
            st.write(f"🔗 **{translate('Contact')}:** [Sensation Group India](https://sensationgroupindia.com)")
            st.markdown("---")
        
        # South India Pest Control Private Limited
        with st.container():
            st.markdown(f"### 🌏 South India Pest Control Private Limited")
            st.write(f"📍 **{translate('Location')}:** {translate('Karnataka')}")
            st.write(f"🛠️ **{translate('Services')}:** {translate('Pest control services across India')}")
            st.write(f"🔗 **{translate('Contact')}:** [South India Pest Control](https://www.southindiapestcontrol.com)")

    # Government Support Section
    st.subheader(translate("🏛️ Government Support for Farmers"))
    
    # Create tabs for different government services
    tab1, tab2, tab3, tab4 = st.tabs([
        translate("📞 Kisan Call Centre"), 
        translate("🌱 IPM Scheme"), 
        translate("🛡️ Plant Protection"), 
        translate("🎓 Training Institute")
    ])
    
    with tab1:
        st.markdown(f"### 📞 {translate('Kisan Call Centre (KCC)')}")
        
        # Create info boxes
        col_a, col_b = st.columns(2)
        with col_a:
            st.info(f"📱 **{translate('Helpline')}:** 1800-180-1551 {translate('or')} 1551")
            st.info(f"🕕 **{translate('Availability')}:** 6:00 AM {translate('to')} 10:00 PM, 7 {translate('days a week')}")
        
        with col_b:
            st.success(f"🛠️ **{translate('Services')}:** {translate('Market information, support programs for farmers')}")
            st.success(f"🏢 **{translate('Provider')}:** IFFCO Kisan Sanchar Limited")
        
        st.write(f"🔗 **{translate('More Info')}:** [Kisan Call Centre](https://mkisan.gov.in)")
    
    with tab2:
        st.markdown(f"### 🌱 {translate('Integrated Pest Management Scheme')}")
        st.write(f"🎯 **{translate('Objective')}:** {translate('Promote sustainable pest control methods to keep pest populations below economic threshold levels')}")
        st.info(f"💡 {translate('This scheme focuses on eco-friendly pest management practices')}")
        st.write(f"🔗 **{translate('More Info')}:** [IPM Scheme](https://www.india.gov.in/spotlight/integrated-pest-management-scheme)")
    
    with tab3:
        st.markdown(f"### 🛡️ {translate('Directorate of Plant Protection, Quarantine & Storage (PPQS)')}")
        st.write(f"🛠️ **{translate('Role')}:** {translate('Implements plant protection measures, quarantine regulations, and storage practices')}")
        st.info(f"📋 {translate('Provides guidelines and regulations for plant health protection')}")
        st.write(f"🌐 **{translate('Website')}:** [PPQS](https://www.ppqs.gov.in)")
    
    with tab4:
        st.markdown(f"### 🎓 {translate('National Institute of Plant Health Management (NIPHM)')}")
        st.write(f"🎯 **{translate('Role')}:** {translate('Provides training and research in plant health management')}")
        st.info(f"📚 {translate('Offers courses and certification programs for farmers and professionals')}")
        st.write(f"🌐 **{translate('Website')}:** [NIPHM](https://www.niphm.gov.in)")

    # Quick Contact Section
    st.markdown("---")
    st.subheader(translate("⚡ Quick Emergency Contacts"))
    
    emergency_cols = st.columns(3)
    
    with emergency_cols[0]:
        st.error(f"🚨 **{translate('Pest Emergency')}**\n📞 1800-180-1551")
    
    with emergency_cols[1]:
        st.warning(f"🌾 **{translate('Crop Advisory')}**\n📞 1800-180-1551")
    
    with emergency_cols[2]:
        st.info(f"💡 **{translate('General Help')}**\n📞 1551")

# For standalone testing
if __name__ == "__main__":
    import streamlit as st
    st.set_page_config(page_title="Pest Detection", page_icon="🌱", layout="wide")
    pest_detection_page()