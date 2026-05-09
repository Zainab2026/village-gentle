import streamlit as st
import numpy as np
import requests
import base64
import json
from io import BytesIO
from PIL import Image
from groq import Groq
from language_manager import multilingual_page, translate, get_user_language_code
from deep_translator import GoogleTranslator
from config import config
from modern_ui import modern_header

# API Keys from config
GROK_API_KEY = config.GROQ_API_KEY
SERPAPI_KEY = config.SERPAPI_KEY
HF_TOKEN = config.HF_TOKEN

# AI-powered recommendation functions
def get_ai_crop_suggestions(N, P, K, temperature, humidity, ph, rainfall):
    """Get AI-powered crop suggestions based on input parameters"""
    try:
        serpapi_url = "https://serpapi.com/search"
        conditions = []
        if temperature < 20:
            conditions.append("cold weather crops")
        elif temperature > 30:
            conditions.append("hot weather crops")
        else:
            conditions.append("moderate climate crops")
            
        if rainfall < 600:
            conditions.append("drought resistant")
        elif rainfall > 1200:
            conditions.append("high rainfall")
            
        if ph < 6.5:
            conditions.append("acidic soil")
        elif ph > 7.5:
            conditions.append("alkaline soil")
            
        query = f"best crops for {' '.join(conditions)} farming India agriculture"
        
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": 3,
            "gl": "in",
            "hl": "en"
        }
        
        response = requests.get(serpapi_url, params=params)
        data = response.json()
        
        suggestions = []
        organic_results = data.get("organic_results", [])
        
        for result in organic_results[:3]:
            suggestions.append({
                "source": result.get("displayed_link", "Agricultural Source"),
                "title": result.get("title", "Crop Recommendation"),
                "description": result.get("snippet", "No description available"),
                "link": result.get("link", "#")
            })
        
        return suggestions
        
    except Exception as e:
        return [{"source": "Error", "title": "Unable to fetch suggestions", "description": str(e), "link": "#"}]

def get_market_rates(crop_name):
    """Get current market rates for the recommended crop"""
    try:
        serpapi_url = "https://serpapi.com/search"
        query = f"{crop_name} price today India mandi rate market price per quintal"
        
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": 2,
            "gl": "in",
            "hl": "en"
        }
        
        response = requests.get(serpapi_url, params=params)
        data = response.json()
        
        price_info = []
        organic_results = data.get("organic_results", [])
        
        for result in organic_results[:2]:
            price_info.append({
                "source": result.get("displayed_link", "Market Source"),
                "title": result.get("title", "Price Information"),
                "snippet": result.get("snippet", "No price data available"),
                "link": result.get("link", "#")
            })
        
        return price_info
        
    except Exception:
        return [{"source": "Error", "title": "Price data unavailable", "snippet": "Unable to fetch current prices", "link": "#"}]

def get_ai_crop_recommendation(N, P, K, temperature, humidity, ph, rainfall, soil_type):
    """Get 100% AI-powered primary crop recommendation using Groq"""
    try:
        client = Groq(api_key=GROK_API_KEY)
        
        prompt = f"""You are an expert agricultural scientist for Indian farming.

Given these soil and climate parameters:
- Nitrogen (N): {N} kg/ha
- Phosphorus (P): {P} kg/ha
- Potassium (K): {K} kg/ha
- Soil pH: {ph}
- Soil Type: {soil_type}
- Temperature: {temperature}°C
- Humidity: {humidity}%
- Rainfall: {rainfall} mm/year

Recommend the SINGLE BEST crop for these conditions in India.

Consider:
1. Nutrient requirements matching NPK levels
2. Climate suitability (temperature, humidity, rainfall)
3. Soil pH compatibility
4. Common crops grown in India
5. Economic viability

Return ONLY the crop name, nothing else. One word or two words maximum.
Examples: "Rice", "Wheat", "Cotton", "Sugarcane", "Maize"
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an agricultural expert. Return only the crop name."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=50
        )
        
        crop = response.choices[0].message.content.strip()
        return crop
        
    except Exception as e:
        st.error(f"Could not get AI crop recommendation: {str(e)}")
        return "Rice"  # Fallback

def get_intelligent_fertilizer(N, P, K, ph, crop_name):
    """Get 100% dynamic AI-powered fertilizer recommendation using Groq"""
    try:
        client = Groq(api_key=GROK_API_KEY)
        
        prompt = f"""You are an expert agronomist specializing in fertilizer recommendations for Indian farmers.

Given the following soil parameters and crop:
- Nitrogen (N): {N} kg/ha
- Phosphorus (P): {P} kg/ha
- Potassium (K): {K} kg/ha
- Soil pH: {ph}
- Crop: {crop_name}

Recommend the BEST fertilizer for this crop and soil condition. Consider:
1. Current NPK levels and what the crop needs
2. pH adjustments if needed
3. Common fertilizers available in India

Provide your recommendation in this EXACT format (one line):
[Fertilizer Name with NPK ratio]

Examples: "NPK 20-20-20 (Balanced)", "Urea 46-0-0 + Lime", "DAP 18-46-0"

Be specific and practical. Return ONLY the fertilizer recommendation, nothing else."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a precise agronomist. Return only the fertilizer name."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=100
        )
        
        fertilizer = response.choices[0].message.content.strip()
        return translate(fertilizer)
        
    except Exception as e:
        st.warning(f"Could not get AI fertilizer recommendation: {str(e)}")
        return translate("NPK 20-20-20 (Balanced) - Consult local agricultural expert")

def analyze_soil_image(image_file):
    """Analyze soil image using Groq's Vision Model (llama-3.2-90b-vision-preview)"""
    try:
        image = Image.open(image_file)
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        client = Groq(api_key=GROK_API_KEY)
        
        prompt = """Analyze this soil image carefully. You are an expert agronomist assistant for Indian farmers.

Identify and provide detailed analysis including:
- Soil color and texture (sandy/clay/loam)
- Moisture level (dry/moderate/wet)
- Estimated Nitrogen content (N in kg/ha, range 0-500)
- Estimated Phosphorus content (P in kg/ha, range 0-50)
- Estimated Potassium content (K in kg/ha, range 0-350)
- Estimated pH level (range 4-9)
- Soil type (Black/Red/Alluvial/Clay/Sandy/Loamy)
- Visible crop residue or organic matter
- Soil health indicators
- Recommended crops for this soil in India
- Fertilizer recommendations (NPK ratio)

Be specific with numbers and provide detailed observations."""

        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,
            temperature=0.2
        )
        
        analysis_text = response.choices[0].message.content
        return analysis_text
        
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def extract_parameters_from_analysis(analysis_text):
    """Extract numerical parameters from AI analysis text using Groq for 100% dynamic parsing"""
    try:
        # Use Groq to parse the LLaVA analysis into structured JSON
        client = Groq(api_key=GROK_API_KEY)
        
        parsing_prompt = f"""You are a data extraction expert. Extract soil parameters from the following soil analysis text.

Analysis Text:
{analysis_text}

Extract and return ONLY a valid JSON object with these exact keys (no additional text):
{{
    "N": <nitrogen value in kg/ha as float>,
    "P": <phosphorus value in kg/ha as float>,
    "K": <potassium value in kg/ha as float>,
    "ph": <pH value as float>,
    "soil_type": "<one of: Black, Red, Alluvial, Clay, Sandy, Loamy>"
}}

Rules:
- If a value is not explicitly mentioned, make a reasonable estimate based on soil description
- N range: 0-500, P range: 0-50, K range: 0-350, pH range: 4-9
- Return ONLY the JSON object, no other text
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a precise data extraction assistant. Return only valid JSON."},
                {"role": "user", "content": parsing_prompt}
            ],
            temperature=0.1,
            max_tokens=200
        )
        
        # Parse the JSON response
        json_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if json_text.startswith("```"):
            json_text = json_text.split("```")[1]
            if json_text.startswith("json"):
                json_text = json_text[4:]
        
        params = json.loads(json_text)
        
        # Validate ranges
        params['N'] = max(0.0, min(500.0, float(params['N'])))
        params['P'] = max(0.0, min(50.0, float(params['P'])))
        params['K'] = max(0.0, min(350.0, float(params['K'])))
        params['ph'] = max(4.0, min(9.0, float(params['ph'])))
        
        return params
        
    except Exception as e:
        st.error(f"❌ Failed to extract soil parameters: {str(e)}")
        st.error("Please try uploading a clearer soil image or contact support.")
        return None

def get_alternative_crops(primary_crop, N, P, K, temperature, humidity, ph, rainfall, soil_type, category):
    """Get 100% dynamic alternative crop suggestions using Groq AI"""
    try:
        client = Groq(api_key=GROK_API_KEY)
        
        if category == "climate":
            focus = f"Focus on crops that thrive in these climate conditions: Temperature={temperature}°C, Humidity={humidity}%, Rainfall={rainfall}mm/year"
        elif category == "market":
            focus = "Focus on high-value cash crops with good market demand and prices in India"
        elif category == "soil":
            focus = f"Focus on crops optimized for this soil: pH={ph}, N={N}, P={P}, K={K}, Type={soil_type}"
        else:
            focus = "General alternatives"
        
        prompt = f"""You are an agricultural expert for Indian farmers.

Primary recommended crop: {primary_crop}

Soil & Climate Parameters:
- Nitrogen: {N} kg/ha
- Phosphorus: {P} kg/ha  
- Potassium: {K} kg/ha
- pH: {ph}
- Soil Type: {soil_type}
- Temperature: {temperature}°C
- Humidity: {humidity}%
- Rainfall: {rainfall} mm/year

{focus}

Suggest 3 alternative crops (different from {primary_crop}) that would work well.

Return ONLY a JSON array of crop names, nothing else:
["Crop1", "Crop2", "Crop3"]

Example: ["Wheat", "Mustard", "Chickpea"]"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an agricultural expert. Return only a JSON array."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=100
        )
        
        crops_text = response.choices[0].message.content.strip()
        
        # Remove markdown if present
        if crops_text.startswith("```"):
            crops_text = crops_text.split("```")[1]
            if crops_text.startswith("json"):
                crops_text = crops_text[4:]
        
        crops = json.loads(crops_text)
        return crops[:3]  # Ensure max 3
        
    except Exception as e:
        st.warning(f"Could not get alternative crops: {str(e)}")
        return []

def calculate_productivity_estimate(crop_name, N, P, K, temperature, humidity, ph, rainfall):
    """Calculate 100% dynamic AI-powered productivity estimate using Groq"""
    try:
        client = Groq(api_key=GROK_API_KEY)
        
        prompt = f"""You are an agricultural yield prediction expert for Indian farming.

Given these parameters:
- Crop: {crop_name}
- Nitrogen (N): {N} kg/ha
- Phosphorus (P): {P} kg/ha
- Potassium (K): {K} kg/ha
- Temperature: {temperature}°C
- Humidity: {humidity}%
- Soil pH: {ph}
- Rainfall: {rainfall} mm/year

Estimate the realistic yield for this crop in tons per hectare under these conditions in India.

Consider:
1. Typical yields for this crop in India
2. Impact of soil nutrients (NPK)
3. Climate suitability (temperature, humidity, rainfall)
4. pH impact on nutrient availability

Return ONLY a single number (the estimated yield in tons/hectare). No text, no units, just the number.
Example: 4.5"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a yield prediction expert. Return only a number."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        yield_text = response.choices[0].message.content.strip()
        # Extract number from response
        import re
        number_match = re.search(r'(\d+\.?\d*)', yield_text)
        if number_match:
            estimated_yield = float(number_match.group(1))
            return round(estimated_yield, 2)
        else:
            return 3.0  # Minimal fallback
        
    except Exception as e:
        st.warning(f"Could not estimate yield: {str(e)}")
        return 3.0  # Minimal fallback

@multilingual_page
def recommendation_page():
    modern_header(translate("🌾 Crop & Fertilizer Recommendations"), translate("AI-powered soil analysis and personalized crop suggestions for your farm."))
    
    # Image Upload Section
    st.subheader(translate("📸 Upload Soil Image"))
    st.info(translate("Upload a clear photo of your field soil for AI-powered analysis"))
    
    uploaded_image = st.file_uploader(
        translate("Choose a soil image..."), 
        type=['jpg', 'jpeg', 'png'],
        help=translate("Upload a clear photo of your field soil")
    )
    
    # Initialize session state
    if 'soil_params' not in st.session_state:
        st.session_state.soil_params = None
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False
    
    if uploaded_image is not None:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(uploaded_image, caption=translate("Uploaded Soil Image"), use_container_width=True)
        
        with col2:
            if st.button(translate("🔍 Analyze Soil Image with AI"), type="primary"):
                with st.spinner(translate("🤖 Analyzing soil image...")):
                    analysis = analyze_soil_image(uploaded_image)
                    st.session_state.soil_analysis = analysis
                    st.session_state.soil_params = extract_parameters_from_analysis(analysis)
                    
                    if st.session_state.soil_params is not None:
                        st.session_state.analysis_done = True
                        st.success(translate("✅ Soil analysis complete!"))
                    else:
                        st.session_state.analysis_done = False
                        st.error(translate("❌ Could not analyze the image. Please try a clearer soil photo."))
            
            if 'soil_analysis' in st.session_state and st.session_state.analysis_done:
                with st.expander(translate("📋 View AI Analysis Details")):
                    st.write(st.session_state.soil_analysis)
    
    # Only show weather inputs and recommendations if soil analysis is done
    if st.session_state.analysis_done and st.session_state.soil_params:
        st.markdown("---")
        
        # Get values from AI analysis
        N = st.session_state.soil_params['N']
        P = st.session_state.soil_params['P']
        K = st.session_state.soil_params['K']
        ph = st.session_state.soil_params['ph']
        soil_type = st.session_state.soil_params['soil_type']
        
        # Display detected soil parameters
        st.success(f"🧪 **{translate('Detected Soil Parameters')}:** N={N} kg/ha | P={P} kg/ha | K={K} kg/ha | pH={ph} | {translate('Type')}={soil_type}")
        
        st.subheader(translate("🌤️ Weather & Climate Information"))
        st.caption(translate("Please provide current weather conditions for your location"))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            temperature = st.number_input(translate('🌡️ Temperature (°C)'), min_value=0.0, max_value=50.0, step=1.0, value=25.0)
        with col2:
            humidity = st.number_input(translate('💧 Humidity (%)'), min_value=0.0, max_value=100.0, step=1.0, value=60.0)
        with col3:
            rainfall = st.number_input(translate('🌧️ Rainfall (mm/year)'), min_value=0.0, max_value=3000.0, step=50.0, value=800.0)

        if st.button(translate("🔎 Get AI-Powered Recommendations"), type="primary"):
            with st.spinner(translate("🤖 Analyzing your inputs and generating personalized recommendations...")):
                
                # Primary Crop Prediction - 100% AI-powered
                primary_crop = get_ai_crop_recommendation(N, P, K, temperature, humidity, ph, rainfall, soil_type)
                
                # Get AI-powered additional suggestions
                ai_suggestions = get_ai_crop_suggestions(N, P, K, temperature, humidity, ph, rainfall)
                
                # Primary Fertilizer Recommendation - 100% AI-powered
                primary_fertilizer = get_intelligent_fertilizer(N, P, K, ph, primary_crop)

            # Display Primary Recommendation
            st.markdown(f"### 🎯 {translate('Primary Recommendation')}")
            
            with st.container():
                col1, col2 = st.columns(2)
                
                with col1:
                    st.success(f"🌾 **{translate('Best Crop')}:** {primary_crop}")
                    
                    productivity = calculate_productivity_estimate(primary_crop, N, P, K, temperature, humidity, ph, rainfall)
                    st.info(f"📊 **{translate('Estimated Yield')}:** {productivity} {translate('tons/hectare')}")
                    
                    market_info = get_market_rates(primary_crop)
                    if market_info:
                        st.markdown(f"💰 **{translate('Current Market Rates')}:**")
                        for price in market_info[:1]:
                            st.write(f"📈 {price['snippet'][:100]}...")
                            st.write(f"🔗 [{translate('View Details')}]({price['link']})")
                
                with col2:
                    st.success(f"💊 **{translate('Best Fertilizer')}:** {primary_fertilizer}")
                    
                    st.info(f"📋 **{translate('Application Guidelines')}:**")
                    st.write(f"• {translate('Apply during soil preparation')}")
                    st.write(f"• {translate('Split application for better absorption')}")
                    st.write(f"• {translate('Follow soil test recommendations')}")
                    
                    st.write(f"💵 **{translate('Estimated Cost')}:** ₹2,500-4,000 {translate('per hectare')}")

            # Alternative Recommendations Section - 100% Dynamic
            st.markdown(f"### 🔄 {translate('Alternative Crop Suggestions')}")
            
            with st.spinner(translate("🤖 Generating alternative crop suggestions...")):
                climate_crops = get_alternative_crops(primary_crop, N, P, K, temperature, humidity, ph, rainfall, soil_type, "climate")
                market_crops = get_alternative_crops(primary_crop, N, P, K, temperature, humidity, ph, rainfall, soil_type, "market")
                soil_crops = get_alternative_crops(primary_crop, N, P, K, temperature, humidity, ph, rainfall, soil_type, "soil")
            
            tab1, tab2, tab3 = st.tabs([
                translate("🌱 Climate-Based"), 
                translate("💰 Market-Based"), 
                translate("🌿 Soil-Based")
            ])
            
            with tab1:
                st.markdown(f"**{translate('Based on your climate conditions')}:**")
                
                if climate_crops:
                    for i, crop in enumerate(climate_crops[:2], 1):
                        with st.expander(f"🌾 {translate('Option')} {i}: {crop}"):
                            productivity = calculate_productivity_estimate(crop, N, P, K, temperature, humidity, ph, rainfall)
                            st.write(f"📊 **{translate('Estimated Yield')}:** {productivity} {translate('tons/hectare')}")
                            st.write(f"🌡️ **{translate('Climate Suitability')}:** {translate('Optimized for your conditions')}")
                            
                            alt_market = get_market_rates(crop)
                            if alt_market:
                                st.write(f"💰 **{translate('Market Info')}:** {alt_market[0]['snippet'][:80]}...")
                else:
                    st.info(translate("No alternative climate-based crops available"))
            
            with tab2:
                st.markdown(f"**{translate('High-value market crops')}:**")
                
                if market_crops:
                    for i, crop in enumerate(market_crops[:2], 1):
                        with st.expander(f"💰 {translate('High-Value Option')} {i}: {crop}"):
                            productivity = calculate_productivity_estimate(crop, N, P, K, temperature, humidity, ph, rainfall)
                            st.write(f"📊 **{translate('Estimated Yield')}:** {productivity} {translate('tons/hectare')}")
                            
                            alt_market = get_market_rates(crop)
                            if alt_market:
                                st.write(f"💵 **{translate('Market Info')}:** {alt_market[0]['snippet'][:100]}...")
                else:
                    st.info(translate("No alternative market-based crops available"))
            
            with tab3:
                st.markdown(f"**{translate('Optimized for your soil conditions')}:**")
                
                if soil_crops:
                    for i, crop in enumerate(soil_crops[:2], 1):
                        with st.expander(f"🪨 {translate('Soil-Optimized Option')} {i}: {crop}"):
                            productivity = calculate_productivity_estimate(crop, N, P, K, temperature, humidity, ph, rainfall)
                            st.write(f"📊 **{translate('Estimated Yield')}:** {productivity} {translate('tons/hectare')}")
                            st.write(f"🧪 **{translate('Soil Compatibility')}:** {translate('Optimized for your soil')}")
                else:
                    st.info(translate("No alternative soil-based crops available"))

            # Additional AI Insights
            st.markdown(f"### 🤖 {translate('AI-Powered Market Insights')}")
            
            if ai_suggestions:
                for i, suggestion in enumerate(ai_suggestions[:2], 1):
                    with st.expander(f"🔍 {translate('Market Insight')} {i}: {suggestion['title'][:50]}..."):
                        st.write(f"**📰 {translate('Source')}:** {suggestion['source']}")
                        st.write(f"**📝 {translate('Details')}:** {suggestion['description']}")
                        st.write(f"**🔗 {translate('Read More')}:** [{translate('Full Article')}]({suggestion['link']})")

            # Fertilizer Alternatives
            st.markdown(f"### 💊 {translate('Fertilizer Alternatives & Combinations')}")
            
            fert_col1, fert_col2 = st.columns(2)
            
            with fert_col1:
                st.markdown(f"**{translate('Organic Options')}:**")
                organic_options = [
                    f"🌿 {translate('Compost + Vermicompost')}",
                    f"🐄 {translate('Farm Yard Manure (FYM)')}",
                    f"🌱 {translate('Green Manure (Legume crops)')}",
                    f"🦴 {translate('Bone Meal + Neem Cake')}"
                ]
                for option in organic_options:
                    st.write(f"• {option}")
            
            with fert_col2:
                st.markdown(f"**{translate('Chemical Combinations')}:**")
                chemical_options = [
                    f"⚗️ NPK 12-32-16 + {translate('Micronutrients')}",
                    f"⚗️ Urea + SSP + MOP",
                    f"⚗️ DAP + {translate('Potash')} + {translate('Zinc Sulphate')}",
                    f"⚗️ {translate('Complex fertilizer')} 20-20-0-13"
                ]
                for option in chemical_options:
                    st.write(f"• {option}")

            # Recommendations and Warnings
            st.subheader(translate("⚠️ Important Recommendations:"))
            out_of_range = False
            if N > 480:
                st.warning(translate("🔺 Nitrogen is too high. Consider planting leguminous crops or using organic manure."))
                out_of_range = True
            if P > 22:
                st.warning(translate("🔺 Phosphorus is too high. Avoid phosphorus-rich fertilizers."))
                out_of_range = True
            if K > 280:
                st.warning(translate("🔺 Potassium is too high. Use crops that uptake high potassium."))
                out_of_range = True
            if ph < 6.0:
                st.warning(translate("🟠 Soil is too acidic. Use lime to increase pH."))
                out_of_range = True
            if ph > 8.5:
                st.warning(translate("🟠 Soil is too alkaline. Use sulfur or organic compost."))
                out_of_range = True
            if temperature < 15:
                st.warning(translate("❄️ Temperature is too low. Consider greenhouse farming to regulate temperature."))
                out_of_range = True
            if temperature > 35:
                st.warning(translate("🔥 Temperature is too high. Ensure adequate irrigation and mulching."))
                out_of_range = True
            if humidity < 40:
                st.warning(translate("💧 Humidity is too low. Use irrigation to increase moisture."))
                out_of_range = True
            if humidity > 70:
                st.warning(translate("💨 Humidity is too high. Ensure proper ventilation to reduce fungal diseases."))
                out_of_range = True
            if rainfall < 500:
                st.warning(translate("🌵 Rainfall is too low. Consider drought-resistant crops."))
                out_of_range = True
            if rainfall > 1500:
                st.warning(translate("🌊 Rainfall is too high. Ensure proper drainage to prevent waterlogging."))
                out_of_range = True

            if out_of_range:
                st.warning(translate("❗ For the given parameters, adjustments are recommended for optimal results."))
    else:
        st.info(translate("👆 Please upload a soil image and click 'Analyze' to get started!"))


if __name__ == "__main__":
    recommendation_page()