import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from deep_translator import GoogleTranslator
from language_manager import multilingual_page, translate, get_user_language_code
from pymongo import MongoClient
from datetime import datetime
import atexit
from config import config
from modern_ui import modern_header

# ✅ API KEYS from config
GROQ_API_KEY = config.GROQ_API_KEY
WINDY_API_KEY = config.WINDY_API_KEY
ORS_API_KEY = config.ORS_API_KEY

# ✅ MongoDB Atlas Connection
MONGO_URI = config.MONGODB_URI
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["village_gentle"]
weather_chats_collection = db["weather_chats"]

# ✅ Cleanup function to clear chat history on app close
def cleanup_chat_history():
    """Clear chat history when user closes the app"""
    if 'email' in st.session_state and 'session_id' in st.session_state:
        try:
            weather_chats_collection.delete_many({
                "email": st.session_state.email,
                "session_id": st.session_state.session_id
            })
        except:
            pass

# Register cleanup function
atexit.register(cleanup_chat_history)

# ✅ MongoDB Chat History Functions
def save_chat_message(email, session_id, role, content, weather_context):
    """Save a chat message to MongoDB"""
    try:
        weather_chats_collection.insert_one({
            "email": email,
            "session_id": session_id,
            "role": role,
            "content": content,
            "weather_context": weather_context,
            "timestamp": datetime.utcnow()
        })
    except Exception as e:
        st.error(f"Error saving message: {e}")

def load_chat_history(email, session_id):
    """Load chat history from MongoDB"""
    try:
        messages = weather_chats_collection.find({
            "email": email,
            "session_id": session_id
        }).sort("timestamp", 1)
        
        return [{"role": msg["role"], "content": msg["content"]} for msg in messages]
    except Exception as e:
        st.error(f"Error loading chat history: {e}")
        return []

def clear_user_chat_history(email, session_id):
    """Clear chat history for a specific user session"""
    try:
        weather_chats_collection.delete_many({
            "email": email,
            "session_id": session_id
        })
    except Exception as e:
        st.error(f"Error clearing chat history: {e}")

# ✅ Geocoding with OpenRouteService
def geocode_location(location_query):
    """Convert location name to coordinates using OpenRouteService API"""
    url = "https://api.openrouteservice.org/geocode/search"
    
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }
    
    params = {
        "text": location_query,
        "size": 1
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        if data.get("features") and len(data["features"]) > 0:
            coordinates = data["features"][0]["geometry"]["coordinates"]
            properties = data["features"][0]["properties"]
            
            return {
                "latitude": coordinates[1],
                "longitude": coordinates[0],
                "display_name": properties.get("label", location_query)
            }
        else:
            return None
    except Exception as e:
        st.error(f"{translate('Error geocoding location')}: {e}")
        return None

# ✅ Location Input with Auto-Geocoding
def get_user_location():
    st.write(f"### {translate('📍 Enter Your Location for Accurate Weather Data')}")

    location_input = st.text_input(
        translate("🌍 Enter your location:"), 
        placeholder=translate("e.g., New York, NY or Mumbai, Maharashtra, India")
    )
    
    if location_input:
        with st.spinner("🔍 Finding your location..."):
            location_data = geocode_location(location_input)
            
        if location_data:
            st.success(f"✅ {translate('Found location')}: {location_data['display_name']}")
            st.info(f"📍 {translate('Coordinates')}: {location_data['latitude']:.4f}, {location_data['longitude']:.4f}")
            
            return {
                "city": location_data['display_name'],
                "latitude": location_data['latitude'],
                "longitude": location_data['longitude']
            }
        else:
            st.error(translate("❌ Location not found. Please try a different search term."))
            return None
    else:
        st.warning(translate("⚠️ Please enter a location to get weather data."))
        return None

# ✅ Fetch Weather Data from Open-Meteo API
def get_weather_data(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"

    try:
        response = requests.get(url)
        data = response.json()
        if "hourly" in data and "daily" in data:
            return data
        else:
            st.error(translate("⚠️ Weather data unavailable for this location."))
            return None
    except Exception as e:
        st.error(f"{translate('Error fetching weather data')}: {e}")
        return None

# ✅ Weather Chatbot with Context
def get_weather_chatbot_response(user_question, weather_context, chat_history):
    """Context-aware chatbot that answers questions about weather and farming"""
    
    # Build context prompt
    context_prompt = f"""You are an expert agricultural weather advisor for farmers. You have access to the following weather information:

Location: {weather_context['location']}
Coordinates: {weather_context['latitude']:.4f}, {weather_context['longitude']:.4f}
Max Temperature: {weather_context['max_temp']}°C
Min Temperature: {weather_context['min_temp']}°C
Total Rainfall: {weather_context['rainfall']}mm
Wind Speed: {weather_context['wind_speed']} km/h

Previous Farming Advice Given:
{weather_context['farming_advice']}

Based on this weather data and the conversation history, answer the farmer's question with practical, actionable advice. Be specific, concise, and helpful."""

    # Build conversation messages
    messages = [{"role": "system", "content": context_prompt}]
    
    # Add all chat history from MongoDB (no limit!)
    for msg in chat_history:
        if msg["role"] in ["user", "assistant"]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.7
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers)
        
        if response.status_code == 200:
            answer = response.json().get("choices", [{}])[0].get("message", {}).get("content", "I couldn't generate a response.")
            
            # Translate response to user's language
            user_lang = get_user_language_code()
            if user_lang != "en":
                try:
                    answer = GoogleTranslator(source="en", target=user_lang).translate(answer)
                except Exception as trans_error:
                    print(f"Translation failed: {trans_error}")
            
            return answer
        else:
            return translate("Sorry, I couldn't process your question. Please try again.")
    except Exception as e:
        st.error(f"{translate('Error')}: {e}")
        return translate("Error connecting to AI assistant.")

# ✅ Get AI-Based Farming Insights from GroqCloud AI
def get_farming_insights(weather_data):
    prompt = f"""
    Analyze the following weather conditions and provide farming insights:
    - Max Temperature: {weather_data['daily']['temperature_2m_max'][0]}°C
    - Min Temperature: {weather_data['daily']['temperature_2m_min'][0]}°C
    - Total Rainfall: {weather_data['daily']['precipitation_sum'][0]}mm
    - Wind Speed: {weather_data['hourly']['wind_speed_10m'][0]} km/h

    Based on these conditions, suggest:
    1. Suitable crops to grow.
    2. Weather threats (flood, drought, storm).
    3. Best farming practices for the next week.
    
    Please provide practical, actionable advice for farmers.
    """

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "llama-3.3-70b-versatile",  # Using Llama 3.3 70B - current production model
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.7
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers)
        
        if response.status_code == 200:
            answer = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No insights available.")
            
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
            st.error(f"{translate('GroqCloud API Error')}: {response.status_code} - {response.text}")
            return translate("Error retrieving farming insights from GroqCloud.")
    except Exception as e:
        st.error(f"{translate('Error connecting to GroqCloud')}: {e}")
        return translate("Error retrieving farming insights.")

# ✅ Embed Windy Weather Map
def display_windy_map(lat, lon):
    windy_map_url = f"https://embed.windy.com/embed2.html?lat={lat}&lon={lon}&zoom=7&level=surface&overlay=wind&menu=true&message=true&marker=true&calendar=now&pressure=true&type=map&location=coordinates&detail=true&detailLat={lat}&detailLon={lon}&metricWind=default&metricTemp=default&radarRange=-1"

    st.write(f"### 🌍 {translate('Live Weather Forecast Map')} ")
    st.components.v1.iframe(windy_map_url, width=800, height=500)

# ✅ Weather Advisory Page
@multilingual_page
def weather_advisory():
    modern_header(translate("🌤️ Smart Weather Advisory"), translate("Real-time weather monitoring and AI-powered agricultural guidance for your location."))

    # 🌍 Get User Location
    user_location = get_user_location()
    if not user_location:
        return  # Stop execution if no location is entered

    lat, lon = user_location["latitude"], user_location["longitude"]

    # ☁️ Fetch Weather Data
    weather_data = get_weather_data(lat, lon)

    if weather_data:
        st.write(f"### 📊 {translate('Weather Forecast Overview')}")

        # 📈 Display Temperature & Precipitation Trends
        hourly_time = pd.date_range(start=pd.Timestamp.now(), periods=24, freq="h")
        hourly_temp = weather_data["hourly"]["temperature_2m"][:24]
        hourly_precip = weather_data["hourly"]["precipitation"][:24]

        temp_df = pd.DataFrame({"Time": hourly_time, translate("Temperature (°C)"): hourly_temp})
        precip_df = pd.DataFrame({"Time": hourly_time, translate("Precipitation (mm)"): hourly_precip})

        fig_temp = px.line(temp_df, x="Time", y=translate("Temperature (°C)"), title=translate("🌡️ Temperature Trend (Next 24 Hours)"))
        fig_precip = px.bar(precip_df, x="Time", y=translate("Precipitation (mm)"), title=translate("🌧️ Precipitation Forecast (Next 24 Hours)"))

        st.plotly_chart(fig_temp)
        st.plotly_chart(fig_precip)

        # 🗺️ Display Windy Weather Forecast Map
        display_windy_map(lat, lon)

        # 🌾 Get AI-Powered Farming Insights
        st.write(f"### 🌾 {translate('AI-Powered Farming Advice')}")
        farming_advice = get_farming_insights(weather_data)
        st.info(farming_advice)
        
        # 💬 Interactive Weather Chatbot with MongoDB Persistence
        st.markdown("---")
        st.write(f"### 💬 {translate('Ask Weather Questions')}")
        st.caption(translate("Have specific questions about the weather or farming advice? Ask our AI assistant!"))
        
        # Initialize session ID for this weather session
        if 'weather_session_id' not in st.session_state or st.session_state.get('last_location') != user_location['city']:
            st.session_state.weather_session_id = f"{st.session_state.email}_{user_location['city']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            st.session_state.last_location = user_location['city']
            # Clear old chat history for this location
            clear_user_chat_history(st.session_state.email, st.session_state.weather_session_id)
        
        # Store weather context
        weather_context = {
            'location': user_location['city'],
            'latitude': lat,
            'longitude': lon,
            'max_temp': weather_data['daily']['temperature_2m_max'][0],
            'min_temp': weather_data['daily']['temperature_2m_min'][0],
            'rainfall': weather_data['daily']['precipitation_sum'][0],
            'wind_speed': weather_data['hourly']['wind_speed_10m'][0],
            'farming_advice': farming_advice
        }
        
        # Load chat history from MongoDB
        chat_history = load_chat_history(st.session_state.email, st.session_state.weather_session_id)
        
        # Display chat history
        for message in chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Clear chat button
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("🗑️ Clear", help=translate("Clear chat history")):
                clear_user_chat_history(st.session_state.email, st.session_state.weather_session_id)
                st.rerun()
        
        # Chat input
        if user_question := st.chat_input(translate("Ask about weather, crops, or farming practices...")):
            # Save user message to MongoDB
            save_chat_message(
                st.session_state.email,
                st.session_state.weather_session_id,
                "user",
                user_question,
                weather_context
            )
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(user_question)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner(translate("🤔 Thinking...")):
                    # Reload chat history for context
                    updated_history = load_chat_history(st.session_state.email, st.session_state.weather_session_id)
                    response = get_weather_chatbot_response(
                        user_question, 
                        weather_context,
                        updated_history
                    )
                    st.markdown(response)
            
            # Save assistant response to MongoDB
            save_chat_message(
                st.session_state.email,
                st.session_state.weather_session_id,
                "assistant",
                response,
                weather_context
            )
            
            st.rerun()


if __name__ == "__main__":
    weather_advisory()