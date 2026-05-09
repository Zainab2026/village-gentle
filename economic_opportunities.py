import streamlit as st
import requests
from language_manager import multilingual_page, translate, get_user_language_code
from deep_translator import GoogleTranslator
from subscription_manager import render_subscription_ui, subscription_manager
from config import config
from modern_ui import modern_header

# ✅ API Keys from config
YOUTUBE_API_KEY = config.YOUTUBE_API_KEY
MISTRAL_API_KEY = config.MISTRAL_API_KEY
SERPAPI_KEY = config.SERPAPI_KEY

# ✅ Ensure previous results persist across interactions
if "skill_videos" not in st.session_state:
    st.session_state.skill_videos = None
if "business_advice" not in st.session_state:
    st.session_state.business_advice = None
if "market_insights" not in st.session_state:
    st.session_state.market_insights = None
if "government_schemes" not in st.session_state:
    st.session_state.government_schemes = None

# 📚 **Fetch Educational Videos (YouTube API)**
def fetch_educational_videos(query):
    youtube_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults=3&key={YOUTUBE_API_KEY}"
    try:
        response = requests.get(youtube_url)
        data = response.json()
        return data.get("items", [])
    except Exception:
        return []

# 🧠 **AI-Powered Business & Career Guidance (Mistral AI)**
def generate_ai_advice(prompt):
    
    mistral_url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "mistral-medium",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 250
    }

    try:
        response = requests.post(mistral_url, json=body, headers=headers)
        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        
        # Translate response to user's language
        user_lang = get_user_language_code()
        if user_lang != "en":
            try:
                answer = GoogleTranslator(source="en", target=user_lang).translate(answer)
            except Exception as trans_error:
                print(f"Translation failed: {trans_error}")
                answer = f"[{translate('English')}] {answer}"
        
        return answer
    except Exception:
        return translate("Error processing request.")

# 💰 **Get Farming Item Prices & Information using SERPAPI**
def get_commodity_prices(farming_item, location="India"):
    """Fetch latest prices and information for any farming item using SERPAPI"""
    serpapi_url = "https://serpapi.com/search"
    
    # Enhanced query for farming items - more flexible
    if location and location.strip():
        price_query = f"{farming_item} price cost rate {location} India farming agriculture market"
    else:
        price_query = f"{farming_item} price cost rate India farming agriculture market mandi"
    
    params = {
        "engine": "google",
        "q": price_query,
        "api_key": SERPAPI_KEY,
        "num": 6,
        "gl": "in",  # India geolocation
        "hl": "en"   # English language
    }
    
    try:
        response = requests.get(serpapi_url, params=params)
        data = response.json()
        
        organic_results = data.get("organic_results", [])
        
        if not organic_results:
            return f"❌ {translate('No information found for')} '{farming_item}'. {translate('Try different keywords or check spelling.')}"
        
        # Look for price information in results
        price_info = f"📊 **{translate('Latest Information for')} '{farming_item}'**\n"
        if location and location.strip():
            price_info += f"📍 **{translate('Location')}:** {location}\n\n"
        
        # Categorize results
        price_results = []
        general_results = []
        
        for result in organic_results[:5]:
            title = result.get("title", "No Title")
            snippet = result.get("snippet", "No description available.")
            link = result.get("link", "#")
            source = result.get("displayed_link", "Unknown Source")
            
            # Check if result likely contains price information
            price_keywords = ["price", "cost", "rate", "₹", "rupee", "per", "quintal", "kg", "ton"]
            if any(keyword in title.lower() or keyword in snippet.lower() for keyword in price_keywords):
                price_results.append({
                    "title": title, "snippet": snippet, "link": link, "source": source
                })
            else:
                general_results.append({
                    "title": title, "snippet": snippet, "link": link, "source": source
                })
        
        # Display price information first
        if price_results:
            price_info += f"💰 **{translate('Price Information')}:**\n\n"
            for i, result in enumerate(price_results[:3], 1):
                price_info += f"**{i}. {result['title']}**\n"
                price_info += f"📍 *{translate('Source')}:* {result['source']}\n"
                price_info += f"💵 *{translate('Details')}:* {result['snippet']}\n"
                price_info += f"🔗 [{translate('View Details')}]({result['link']})\n\n"
        
        # Display general information
        if general_results:
            price_info += f"📋 **{translate('General Information')}:**\n\n"
            for i, result in enumerate(general_results[:2], 1):
                price_info += f"**{i}. {result['title']}**\n"
                price_info += f"📍 *{translate('Source')}:* {result['source']}\n"
                price_info += f"📝 *{translate('Details')}:* {result['snippet']}\n"
                price_info += f"🔗 [{translate('Read More')}]({result['link']})\n\n"
        
        # Add contextual tips based on farming item type
        price_info += f"💡 **{translate('Tips')}:**\n"
        
        item_lower = farming_item.lower()
        if any(word in item_lower for word in ["seed", "seeds"]):
            price_info += f"• {translate('Buy certified seeds from authorized dealers')}\n"
            price_info += f"• {translate('Check seed germination rate before purchase')}\n"
            price_info += f"• {translate('Store seeds in cool, dry place')}\n"
        elif any(word in item_lower for word in ["fertilizer", "urea", "dap", "npk"]):
            price_info += f"• {translate('Buy fertilizers based on soil test results')}\n"
            price_info += f"• {translate('Check manufacturing date and expiry')}\n"
            price_info += f"• {translate('Compare prices across different brands')}\n"
        elif any(word in item_lower for word in ["tractor", "equipment", "machine"]):
            price_info += f"• {translate('Consider both new and used equipment options')}\n"
            price_info += f"• {translate('Check warranty and service availability')}\n"
            price_info += f"• {translate('Evaluate financing options available')}\n"
        elif any(word in item_lower for word in ["pesticide", "insecticide", "fungicide"]):
            price_info += f"• {translate('Use pesticides as per recommended dosage')}\n"
            price_info += f"• {translate('Check for organic alternatives')}\n"
            price_info += f"• {translate('Follow safety guidelines during application')}\n"
        else:
            price_info += f"• {translate('Compare prices from multiple sources')}\n"
            price_info += f"• {translate('Consider seasonal price variations')}\n"
            price_info += f"• {translate('Check quality certifications')}\n"
        
        price_info += f"• {translate('Consult local agricultural experts for guidance')}\n"
        
        return price_info
        
    except Exception as e:
        return f"{translate('Error fetching information')}: {str(e)}\n\n{translate('Please try again with different keywords or check your internet connection.')}"

# 💼 **Market Insights & Business Opportunities (SERPAPI - Indian Market Focus)**
def get_indian_market_insights(query):
    """Fetch Indian market insights and business opportunities using SERPAPI"""
    serpapi_url = "https://serpapi.com/search"
    
    # Enhanced query for Indian market context
    indian_query = f"{query} India business opportunities funding schemes government loans"
    
    params = {
        "engine": "google",
        "q": indian_query,
        "api_key": SERPAPI_KEY,
        "num": 5,
        "gl": "in",  # India geolocation
        "hl": "en"   # English language
    }
    
    try:
        response = requests.get(serpapi_url, params=params)
        data = response.json()
        
        results = []
        organic_results = data.get("organic_results", [])
        
        for result in organic_results[:4]:  # Get top 4 results
            results.append({
                "title": result.get("title", "No Title"),
                "link": result.get("link", "#"),
                "snippet": result.get("snippet", "No description available."),
                "source": result.get("displayed_link", "Unknown Source")
            })
        
        return results
    except Exception as e:
        st.error(f"{translate('Error fetching market insights')}: {str(e)}")
        return []

# 🇮🇳 **Get Indian Government Schemes & Funding**
def get_government_schemes():
    """Fetch information about Indian government schemes for rural development and business"""
    schemes_query = "Indian government schemes rural development startup funding MUDRA loan Stand Up India"
    
    serpapi_url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": schemes_query,
        "api_key": SERPAPI_KEY,
        "num": 4,
        "gl": "in",
        "hl": "en"
    }
    
    try:
        response = requests.get(serpapi_url, params=params)
        data = response.json()
        
        schemes = []
        organic_results = data.get("organic_results", [])
        
        for result in organic_results[:3]:
            schemes.append({
                "title": result.get("title", "No Title"),
                "link": result.get("link", "#"),
                "snippet": result.get("snippet", "No description available."),
                "source": result.get("displayed_link", "Government Source")
            })
        
        return schemes
    except Exception:
        return []

# 📌 **Skill Development & Economic Opportunities Page**
@multilingual_page
def economic_opportunities_page():
    # Check Subscription (Feature ID 1)
    if not render_subscription_ui("Economic Opportunities", 1):
        return

    modern_header(translate("📈 Skill Development & Economic Opportunities"), translate("Empowering rural communities through skill acquisition, market insights, and government support."))

    # 📚 **Educational Videos**
    st.header(translate("📚 Learn New Skills"))
    topic = st.text_input(translate("What do you want to learn?"), key="skill_input")
    
    if st.button(translate("Search Videos")):
        st.session_state.skill_videos = fetch_educational_videos(topic)

    # ✅ Display videos (Keep showing until new input)
    if st.session_state.skill_videos:
        for video in st.session_state.skill_videos:
            title = video["snippet"]["title"]
            video_id = video["id"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            st.video(video_url)
            st.write(f"🎥 **{title}**")

    # 📊 **Agrimarket 2.0 - Official Market Prices**
    st.header(translate("📊 Official Market Prices"))
    
    # 🏛️ **Compact Agrimarket 2.0 Card**
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #43A047 0%, #2E7D32 100%); 
                padding: 25px; 
                border-radius: 12px; 
                margin-bottom: 20px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 250px;">
                <h3 style="color: white; margin: 0 0 8px 0; font-size: 24px;">
                    🏛️ Agrimarket 2.0
                </h3>
                <p style="color: #E8F5E9; margin: 0 0 12px 0; font-size: 13px;">
                    {translate('Official Government Mandi Prices')}
                </p>
                <a href="https://agmarknet.gov.in/" target="_blank" 
                   style="background: white; 
                          color: #2E7D32; 
                          padding: 10px 24px; 
                          border-radius: 6px; 
                          text-decoration: none; 
                          font-weight: 600;
                          font-size: 14px;
                          display: inline-block;
                          box-shadow: 0 2px 6px rgba(0,0,0,0.2);">
                    🌾 {translate('Check Prices')} →
                </a>
            </div>
            <div style="flex: 1; min-width: 250px; text-align: right; margin-top: 10px;">
                <div style="color: white; font-size: 12px; line-height: 1.8;">
                    ✅ {translate('Daily Updated')}<br>
                    📊 {translate('All India Coverage')}<br>
                    🌾 {translate('Official Data')}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Features in compact format
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: #E8F5E9; padding: 15px; border-radius: 8px; text-align: center;">
            <div style="font-size: 28px; margin-bottom: 8px;">📊</div>
            <div style="font-weight: 600; color: #2E7D32; margin-bottom: 5px;">{translate('Mandi Prices')}</div>
            <div style="font-size: 12px; color: #666;">{translate('Real-time rates')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: #FFF3E0; padding: 15px; border-radius: 8px; text-align: center;">
            <div style="font-size: 28px; margin-bottom: 8px;">🌾</div>
            <div style="font-weight: 600; color: #F57C00; margin-bottom: 5px;">{translate('All Crops')}</div>
            <div style="font-size: 12px; color: #666;">{translate('Complete coverage')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: #E3F2FD; padding: 15px; border-radius: 8px; text-align: center;">
            <div style="font-size: 28px; margin-bottom: 8px;">📈</div>
            <div style="font-weight: 600; color: #1976D2; margin-bottom: 5px;">{translate('Trends')}</div>
            <div style="font-size: 12px; color: #666;">{translate('Historical data')}</div>
        </div>
        """, unsafe_allow_html=True)

    # 🇮🇳 **Indian Market Insights & Business Opportunities**
    st.header(translate("🇮🇳 Indian Market Insights & Business Opportunities"))
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(translate("🔍 Market Research"))
        market_query = st.text_input(translate("Search Indian market opportunities:"), 
                                   placeholder=translate("e.g., agriculture technology, rural business, food processing"), 
                                   key="market_input")
        
        if st.button(translate("Get Market Insights"), key="market_btn"):
            with st.spinner(translate("🔍 Researching Indian market...")):
                st.session_state.market_insights = get_indian_market_insights(market_query)
    
    with col2:
        st.subheader(translate("🏛️ Government Schemes"))
        if st.button(translate("Show Government Funding Schemes"), key="schemes_btn"):
            with st.spinner(translate("📋 Fetching government schemes...")):
                st.session_state.government_schemes = get_government_schemes()

    # ✅ Display Market Insights
    if st.session_state.market_insights:
        st.subheader(translate("📊 Market Insights & Opportunities"))
        for idx, item in enumerate(st.session_state.market_insights, 1):
            with st.expander(f"💼 {translate('Opportunity')} {idx}: {item['title'][:50]}..."):
                st.write(f"**🔗 {translate('Source')}:** {item['source']}")
                st.write(f"**📝 {translate('Description')}:** {item['snippet']}")
                st.write(f"**🌐 {translate('Link')}:** [{translate('Read More')}]({item['link']})")

    # ✅ Display Government Schemes
    if st.session_state.government_schemes:
        st.subheader(translate("🏛️ Government Funding Schemes"))
        for idx, scheme in enumerate(st.session_state.government_schemes, 1):
            with st.expander(f"🎯 {translate('Scheme')} {idx}: {scheme['title'][:50]}..."):
                st.write(f"**🏢 {translate('Source')}:** {scheme['source']}")
                st.write(f"**📋 {translate('Details')}:** {scheme['snippet']}")
                st.write(f"**🔗 {translate('Apply')}:** [{translate('Visit Official Site')}]({scheme['link']})")
    
    # 💡 **Quick Access to Popular Indian Schemes**
    st.subheader(translate("⚡ Popular Indian Business Schemes"))
    
    schemes_info = {
        translate("🏦 MUDRA Loan"): translate("Micro Units Development & Refinance Agency - Loans up to ₹10 lakhs for small businesses"),
        translate("🚀 Stand Up India"): translate("Bank loans for SC/ST and women entrepreneurs (₹10 lakh to ₹1 crore)"),
        translate("🌾 PM-KISAN"): translate("Direct income support to farmers - ₹6,000 per year"),
        translate("🏭 Startup India"): translate("Government initiative for startup ecosystem development"),
        translate("👩‍💼 Mahila Udyam Nidhi"): translate("Scheme for women entrepreneurs with easy loan access")
    }
    
    for scheme, description in schemes_info.items():
        st.info(f"**{scheme}**: {description}")

    # 🏛️ **Enhanced Government Support for Farmers**
    st.markdown("---")
    st.header(translate("🏛️ Comprehensive Government Support for Farmers"))
    
    # Create tabs for different types of support
    support_tab1, support_tab2, support_tab3, support_tab4 = st.tabs([
        translate("📞 Helpline Services"), 
        translate("💰 Financial Support"), 
        translate("🌱 Agricultural Programs"), 
        translate("🎓 Training & Education")
    ])
    
    with support_tab1:
        st.subheader(translate("📞 Farmer Helpline Services"))
        
        # Kisan Call Centre
        with st.container():
            st.markdown(f"### 📱 {translate('Kisan Call Centre (KCC)')}")
            
            col_help1, col_help2 = st.columns(2)
            with col_help1:
                st.success(f"📞 **{translate('Helpline Numbers')}:**")
                st.write(f"• 🇮🇳 1800-180-1551")
                st.write(f"• 📱 1551 ({translate('Mobile')})")
                st.write(f"• 🕕 **{translate('Timing')}:** 6:00 AM - 10:00 PM")
                st.write(f"• 📅 **{translate('Days')}:** 7 {translate('days a week')}")
            
            with col_help2:
                st.info(f"🛠️ **{translate('Services Provided')}:**")
                st.write(f"• 📊 {translate('Market price information')}")
                st.write(f"• 🌾 {translate('Crop advisory services')}")
                st.write(f"• 🌦️ {translate('Weather information')}")
                st.write(f"• 💊 {translate('Pest and disease management')}")
                st.write(f"• 🏛️ {translate('Government scheme information')}")
            
            st.write(f"🏢 **{translate('Provider')}:** IFFCO Kisan Sanchar Limited")
            st.write(f"🔗 **{translate('Website')}:** [Kisan Call Centre](https://mkisan.gov.in)")
        
        # Emergency Contacts
        st.markdown("---")
        st.subheader(translate("🚨 Emergency Agricultural Contacts"))
        
        emergency_cols = st.columns(3)
        with emergency_cols[0]:
            st.error(f"🚨 **{translate('Crop Emergency')}**\n📞 1800-180-1551\n🕕 24/7 {translate('Available')}")
        
        with emergency_cols[1]:
            st.warning(f"🌾 **{translate('Disease Outbreak')}**\n📞 1800-180-1551\n📧 {translate('Report immediately')}")
        
        with emergency_cols[2]:
            st.info(f"💡 **{translate('General Advisory')}**\n📞 1551\n💬 {translate('SMS Service Available')}")
    
    with support_tab2:
        st.subheader(translate("💰 Financial Support Schemes"))
        
        # Enhanced financial schemes
        financial_schemes = [
            {
                "name": translate("🏦 PM-KISAN Samman Nidhi"),
                "amount": "₹6,000 " + translate("per year"),
                "description": translate("Direct income support to small and marginal farmers"),
                "eligibility": translate("Farmers with cultivable land up to 2 hectares"),
                "link": "https://pmkisan.gov.in"
            },
            {
                "name": translate("🌾 Pradhan Mantri Fasal Bima Yojana"),
                "amount": translate("Premium subsidy up to 90%"),
                "description": translate("Crop insurance scheme for farmers"),
                "eligibility": translate("All farmers growing notified crops"),
                "link": "https://www.pmfby.gov.in"
            },
            {
                "name": translate("💳 Kisan Credit Card (KCC)"),
                "amount": translate("Credit limit based on land holding"),
                "description": translate("Easy access to credit for agricultural needs"),
                "eligibility": translate("All farmers including tenant farmers"),
                "link": "https://www.nabard.org"
            },
            {
                "name": translate("🏦 MUDRA Yojana"),
                "amount": "₹10 " + translate("lakhs maximum"),
                "description": translate("Micro-finance for small businesses and farming"),
                "eligibility": translate("Non-corporate, non-farm small/micro enterprises"),
                "link": "https://www.mudra.org.in"
            }
        ]
        
        for scheme in financial_schemes:
            with st.expander(f"💰 {scheme['name']}"):
                col_fin1, col_fin2 = st.columns(2)
                with col_fin1:
                    st.success(f"💵 **{translate('Amount')}:** {scheme['amount']}")
                    st.info(f"📋 **{translate('Description')}:** {scheme['description']}")
                
                with col_fin2:
                    st.write(f"✅ **{translate('Eligibility')}:** {scheme['eligibility']}")
                    st.write(f"🔗 **{translate('Apply Online')}:** [{translate('Official Website')}]({scheme['link']})")
    
    with support_tab3:
        st.subheader(translate("🌱 Agricultural Development Programs"))
        
        # Agricultural programs
        ag_programs = [
            {
                "name": translate("🌱 Integrated Pest Management (IPM)"),
                "objective": translate("Promote sustainable pest control methods"),
                "benefits": translate("Reduces chemical pesticide use, maintains ecological balance"),
                "contact": "PPQS - Plant Protection Division"
            },
            {
                "name": translate("🚜 Sub-Mission on Agricultural Mechanization"),
                "objective": translate("Promote farm mechanization for higher productivity"),
                "benefits": translate("Subsidies on farm equipment, custom hiring centers"),
                "contact": "Department of Agriculture & Cooperation"
            },
            {
                "name": translate("💧 Pradhan Mantri Krishi Sinchayee Yojana"),
                "objective": translate("Improve water use efficiency in agriculture"),
                "benefits": translate("Drip irrigation, sprinkler systems, water conservation"),
                "contact": "Ministry of Jal Shakti"
            },
            {
                "name": translate("🌾 National Food Security Mission"),
                "objective": translate("Increase production of rice, wheat, pulses, and coarse cereals"),
                "benefits": translate("Seeds, fertilizers, technology demonstration"),
                "contact": "Department of Agriculture & Cooperation"
            }
        ]
        
        for program in ag_programs:
            with st.container():
                st.markdown(f"### {program['name']}")
                col_ag1, col_ag2 = st.columns(2)
                
                with col_ag1:
                    st.info(f"🎯 **{translate('Objective')}:** {program['objective']}")
                    st.success(f"✅ **{translate('Benefits')}:** {program['benefits']}")
                
                with col_ag2:
                    st.write(f"📞 **{translate('Contact')}:** {program['contact']}")
                    st.write(f"📧 **{translate('For more details')}:** {translate('Contact your local agriculture office')}")
                
                st.markdown("---")
    
    with support_tab4:
        st.subheader(translate("🎓 Training & Education Programs"))
        
        # Training institutions and programs
        training_info = [
            {
                "name": translate("🎓 National Institute of Plant Health Management (NIPHM)"),
                "location": translate("Hyderabad, Telangana"),
                "services": translate("Training in plant health management, IPM, pesticide management"),
                "website": "https://www.niphm.gov.in",
                "programs": translate("Certificate courses, diploma programs, workshops")
            },
            {
                "name": translate("🌾 Indian Council of Agricultural Research (ICAR)"),
                "location": translate("New Delhi (Multiple centers across India)"),
                "services": translate("Agricultural research, education, and extension"),
                "website": "https://icar.org.in",
                "programs": translate("Farmer training programs, technology demonstrations")
            },
            {
                "name": translate("📚 Krishi Vigyan Kendras (KVKs)"),
                "location": translate("District level centers across India"),
                "services": translate("Local agricultural extension and training"),
                "website": "https://www.icar.org.in/en/krishi-vigyan-kendras",
                "programs": translate("Skill development, technology transfer, demonstrations")
            }
        ]
        
        for training in training_info:
            with st.expander(f"🎓 {training['name']}"):
                col_train1, col_train2 = st.columns(2)
                
                with col_train1:
                    st.info(f"📍 **{translate('Location')}:** {training['location']}")
                    st.success(f"🛠️ **{translate('Services')}:** {training['services']}")
                
                with col_train2:
                    st.write(f"📚 **{translate('Programs')}:** {training['programs']}")
                    st.write(f"🌐 **{translate('Website')}:** [{translate('Visit')}]({training['website']})")

    # Quick Reference Card
    st.markdown("---")
    st.subheader(translate("📋 Quick Reference Card"))
    
    quick_ref_cols = st.columns(2)
    
    with quick_ref_cols[0]:
        st.markdown(f"### 📞 {translate('Important Numbers')}")
        st.code(f"""
{translate('Kisan Call Centre')}: 1800-180-1551
{translate('Emergency Helpline')}: 1551
{translate('PM-KISAN Helpline')}: 155261
{translate('Soil Health Card')}: 1800-180-1551
        """)
    
    with quick_ref_cols[1]:
        st.markdown(f"### 🌐 {translate('Important Websites')}")
        st.markdown(f"""
- [PM-KISAN](https://pmkisan.gov.in)
- [Crop Insurance](https://www.pmfby.gov.in)
- [Kisan Call Centre](https://mkisan.gov.in)
- [ICAR](https://icar.org.in)
- [Agriculture Portal](https://www.agricoop.nic.in)
        """)

# ✅ Ensure seamless import into `main1.py`
if __name__ == "__main__":
    economic_opportunities_page()