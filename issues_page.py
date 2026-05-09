import streamlit as st
from datetime import datetime
from pymongo import MongoClient
import uuid
import requests
import urllib.parse
from styles import create_feature_card
from language_manager import multilingual_page, translate, get_user_language_code
from deep_translator import GoogleTranslator
from config import config
from modern_ui import modern_header

# --- Configuration from config ---
MONGO_URI = config.MONGODB_URI
YOUTUBE_API_KEY = config.YOUTUBE_API_KEY
MISTRAL_API_KEY = config.MISTRAL_API_KEY
MISTRAL_API_URL = config.MISTRAL_URL
GOOGLE_API_KEY = config.GOOGLE_API_KEY
GOOGLE_CSE_ID = config.GOOGLE_CSE_ID
DEVELOPER_EMAIL = "your.email@example.com"
DEVELOPER_NAME = "Village Gentle Team"

# --- MongoDB Connection ---
@st.cache_resource
def init_mongodb():
    try:
        client = MongoClient(MONGO_URI)
        db = client["village_gentle"]
        collection = db["issues"]
        return collection
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        return None

# --- Helper Functions ---
def call_mistral(prompt):
    """Call Mistral AI for issue analysis"""
    
    try:
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mistral-tiny",
            "messages": [
                {"role": "system", "content": "You are an assistant that analyzes rural village issues and provides practical solutions. Be concise and actionable."},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(MISTRAL_API_URL, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            answer = response.json()['choices'][0]['message']['content']
            
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
            return translate("Unable to analyze issue at the moment. Please try again later.")
    except Exception as e:
        return translate(f"Analysis unavailable: {str(e)}")

def fetch_youtube_videos(query, max_results=3):
    """Fetch relevant YouTube videos"""
    try:
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={YOUTUBE_API_KEY}&maxResults={max_results}&type=video"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            results = response.json().get("items", [])
            videos = []
            for item in results:
                video_id = item["id"].get("videoId")
                title = item["snippet"]["title"]
                if video_id:
                    videos.append({
                        "title": title,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "video_id": video_id
                    })
            return videos
        return []
    except Exception as e:
        st.error(f"Error fetching videos: {str(e)}")
        return []

def search_relevant_authorities(issue_description, location):
    """Search for relevant government authorities"""
    issue_keywords = {
        'water': 'water department irrigation authority',
        'electricity': 'electricity board power department',
        'road': 'public works department PWD road authority',
        'health': 'health department medical officer PHC',
        'education': 'education department school authority',
        'agriculture': 'agriculture department krishi vigyan kendra',
        'police': 'police station law enforcement',
        'sanitation': 'municipal corporation sanitation department'
    }
    
    # Determine issue category
    issue_type = 'government office'
    for keyword, dept in issue_keywords.items():
        if keyword in issue_description.lower():
            issue_type = dept
            break
    
    query = f"{issue_type} {location} contact phone number government office"
    
    try:
        url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={query}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            results = response.json().get("items", [])
            authorities = []
            for item in results[:3]:
                authorities.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                })
            return authorities
        return []
    except Exception as e:
        st.error(f"Error searching authorities: {str(e)}")
        return []

def create_email_link(subject, body):
    """Create mailto link for feedback"""
    subject_encoded = urllib.parse.quote(subject)
    body_encoded = urllib.parse.quote(body)
    return f"mailto:{DEVELOPER_EMAIL}?subject={subject_encoded}&body={body_encoded}"

# --- Main Issues Page ---
@multilingual_page
def issues_page():
    modern_header(translate("📮 Report a Village Issue"), translate("Help us serve your community better! Report issues affecting your village and get connected with relevant authorities and solutions."))
    
    # Issue reporting form
    with st.form("issue_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(translate("👤 Your Name *"), placeholder=translate("Enter your full name"))
            district = st.text_input(translate("📍 Location *"), placeholder=translate("Village, District, State"))
        
        with col2:
            contact = st.text_input(translate("📞 Contact Number"), placeholder=translate("Your phone number (optional)"))
            scope = st.selectbox(translate("🎯 Who is affected?"), [translate("Only Me"), translate("Few Families"), translate("Whole Village"), translate("Multiple Villages")])

        description = st.text_area(
            translate("📝 Describe the Problem *"), 
            placeholder=translate("Please provide detailed description of the issue..."),
            height=120
        )
        
        # File uploads
        col3, col4 = st.columns(2)
        with col3:
            photo = st.file_uploader(translate("📸 Upload Photo (optional)"), type=["png", "jpg", "jpeg"])
        with col4:
            video = st.file_uploader(translate("🎥 Upload Video (optional)"), type=["mp4", "mov", "avi"])

        submit = st.form_submit_button(translate("🚀 Submit Issue"), type="primary", use_container_width=True)

    # Process form submission
    if submit:
        if not (name and district and description):
            st.warning(translate("⚠️ Please fill in all required fields (marked with *)"))
            return

        # Initialize database
        collection = init_mongodb()
        if collection is None:
            st.error(translate("❌ Unable to connect to database. Please try again later."))
            return

        # Process uploaded files
        file_refs = {}
        if photo:
            file_refs['photo'] = photo.name
        if video:
            file_refs['video'] = video.name

        # AI Analysis
        prompt = f"""
        Issue: {description}
        Location: {district}
        Scope: {scope}
        
        Please analyze this village issue and provide:
        1. Severity level (Low/Medium/High)
        2. Immediate steps the reporter can take
        3. Which government department should handle this
        4. Expected timeline for resolution
        """
        
        with st.spinner(translate("🔍 Analyzing issue with AI...")):
            ai_response = call_mistral(prompt)

        # Determine severity
        severity = "medium"
        if "high" in ai_response.lower() or "urgent" in ai_response.lower():
            severity = "high"
        elif "low" in ai_response.lower() or "minor" in ai_response.lower():
            severity = "low"

        # Save to database
        try:
            record = {
                "_id": str(uuid.uuid4()),
                "name": name,
                "contact": contact,
                "district": district,
                "scope": scope,
                "description": description,
                "ai_analysis": ai_response,
                "severity": severity,
                "media": file_refs,
                "timestamp": datetime.now().isoformat(),
                "status": "submitted"
            }
            collection.insert_one(record)
            st.success(f"✅ {translate('Issue submitted successfully! Reference ID')}: " + record["_id"][:8])
        except Exception as e:
            st.error(f"❌ {translate('Error saving issue')}: {str(e)}")
            return

        # Display results
        st.markdown("---")
        
        # AI Analysis
        severity_color = {"low": "🟢", "medium": "🟡", "high": "🔴"}
        create_feature_card(
            f"AI Analysis {severity_color.get(severity, '🟡')} Severity: {severity.upper()}",
            ai_response,
            "🤖"
        )

        # YouTube videos
        st.subheader(translate("🎥 Helpful Resources"))
        with st.spinner(translate("🔍 Finding relevant videos...")):
            videos = fetch_youtube_videos(f"{description} solution government help")
        
        if videos:
            cols = st.columns(min(len(videos), 3))
            for i, video in enumerate(videos[:3]):
                with cols[i]:
                    st.markdown(f"""
                    <div style="
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 10px;
                        padding: 1rem;
                        margin: 0.5rem 0;
                        border: 1px solid rgba(255, 255, 255, 0.2);
                    ">
                        <h4 style="color: white; font-size: 14px; margin-bottom: 8px;">
                            📺 {video['title'][:50]}...
                        </h4>
                        <a href="{video['url']}" target="_blank" style="
                            color: #4CAF50;
                            text-decoration: none;
                            font-weight: 500;
                        ">🔗 Watch Video</a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info(translate("🎬 No specific videos found. Try searching online for solutions related to your issue."))

        # Government authorities
        st.subheader(translate("🏛️ Relevant Authorities"))
        with st.spinner(translate("🔍 Finding relevant authorities...")):
            authorities = search_relevant_authorities(description, district)
        
        if authorities:
            for auth in authorities:
                st.markdown(f"""
                <div style="
                    background: rgba(33, 150, 243, 0.1);
                    border-radius: 10px;
                    padding: 1rem;
                    margin: 0.5rem 0;
                    border-left: 4px solid #2196F3;
                ">
                    <h4 style="color: #2196F3; margin-bottom: 8px;">{auth['title']}</h4>
                    <p style="color: rgba(255,255,255,0.8); font-size: 14px; margin-bottom: 8px;">
                        {auth['snippet'][:200]}...
                    </p>
                    <a href="{auth['link']}" target="_blank" style="
                        color: #4CAF50;
                        text-decoration: none;
                        font-weight: 500;
                    ">🔗 Visit Website</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            create_feature_card(
                "General Contact Information",
                """
                • **District Collector Office**: Main administrative authority for your district
                • **Block Development Office**: Rural development and welfare schemes  
                • **Panchayat Office**: Local village-level governance
                • **Police Station**: Law and order issues
                • **Primary Health Center (PHC)**: Health-related concerns
                • **Call 1100**: Government helpline for citizen services
                """,
                "📞"
            )

    # Feedback section
    st.markdown("---")
    st.subheader(translate("💬 App Feedback"))
    
    create_feature_card(
        "Help us improve Village Gentle!",
        "Share your experience using this community assistance feature.",
        "⭐"
    )
    
    feedback_col1, feedback_col2 = st.columns([2, 1])
    
    with feedback_col1:
        feedback_text = st.text_area(
            "Your feedback:", 
            placeholder="Tell us how we can make this app better for your community...",
            height=100
        )
    
    with feedback_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📧 Send Feedback", type="secondary", use_container_width=True):
            if feedback_text:
                email_subject = "Village Gentle App Feedback"
                email_body = f"""Hello Village Gentle Team,

Feedback from Issues Page:
{feedback_text}

User: {st.session_state.get('email', 'Anonymous')}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Thank you for creating this helpful community tool!
"""
                email_link = create_email_link(email_subject, email_body)
                st.markdown(f"[📧 Click to send email]({email_link})")
                st.success(translate("✅ Email client opened! Please send the email."))
            else:
                st.warning(translate("⚠️ Please enter your feedback first."))

    # Recent issues (if user wants to see community issues)
    if st.checkbox("👥 View Recent Community Issues"):
        collection = init_mongodb()
        if collection is not None:
            try:
                recent_issues = list(collection.find().sort("timestamp", -1).limit(5))
                if recent_issues:
                    st.subheader(translate("📋 Recent Community Issues"))
                    for issue in recent_issues:
                        severity_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
                        st.markdown(f"""
                        <div style="
                            background: rgba(255, 255, 255, 0.05);
                            border-radius: 8px;
                            padding: 1rem;
                            margin: 0.5rem 0;
                            border-left: 3px solid #4CAF50;
                        ">
                            <p style="color: white; margin: 0;">
                                <strong>{severity_emoji.get(issue.get('severity', 'medium'), '🟡')} 
                                {issue.get('district', 'Unknown Location')}</strong>
                            </p>
                            <p style="color: rgba(255,255,255,0.7); font-size: 14px; margin: 4px 0;">
                                {issue.get('description', '')[:100]}...
                            </p>
                            <p style="color: rgba(255,255,255,0.5); font-size: 12px; margin: 0;">
                                Reported: {issue.get('timestamp', '')[:10]}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(translate("📝 No recent issues found. Be the first to report!"))
            except Exception as e:
                st.error(f"❌ {translate('Error loading recent issues')}: {str(e)}")