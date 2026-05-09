import streamlit as st
import requests
import folium
from streamlit_folium import folium_static
import json
import re
from language_manager import multilingual_page, translate, get_user_language_code
from deep_translator import GoogleTranslator
from subscription_manager import render_subscription_ui, subscription_manager
from config import config
from modern_ui import modern_header

# ✅ API Keys from config
MISTRAL_API_KEY = config.MISTRAL_API_KEY
GOOGLE_API_KEY = config.GOOGLE_API_KEY
GOOGLE_CSE_ID = config.GOOGLE_CSE_ID
SERPAPI_KEY = config.SERPAPI_KEY
NUTRITIONIX_APP_ID = config.NUTRITIONIX_APP_ID
NUTRITIONIX_APP_KEY = config.NUTRITIONIX_APP_KEY
ORS_API_KEY = config.ORS_API_KEY
MISTRAL_URL = config.MISTRAL_URL
GROQ_API_KEY = config.GROQ_API_KEY
GROQ_API_URL = config.GROQ_API_URL

# 🔄 **Ensure all session state variables are initialized**
for key, default_value in {
    "ai_response": "",
    "healthcare_results": [],
    "recipe_response": "",
    "nutrition_response": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# 📍 **Find Nearby Healthcare Facilities using SerpAPI**
def find_healthcare_facilities_serpapi(location, query="hospitals"):
    """Enhanced healthcare facility search using SerpAPI with detailed information"""
    search_query = f"{query} near {location}"
    
    # First get location coordinates to improve search accuracy
    location_coords = get_basic_location_coordinates(location)
    
    params = {
        "engine": "google_maps",
        "q": search_query,
        "api_key": SERPAPI_KEY,
        "type": "search"
    }
    
    # Add location coordinates if available
    if location_coords:
        lat, lng = location_coords
        params["ll"] = f"@{lat},{lng},15z"
    
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()
        
        if "error" in data:
            st.warning(f"{translate('SerpAPI error')}: {data['error']}")
            return fallback_google_search(location, query)
        
        results = []
        local_results = data.get("local_results", [])
        
        for result in local_results[:5]:  # Get top 5 results
            # Extract GPS coordinates properly
            gps_coords = result.get("gps_coordinates", {})
            if not gps_coords and "latitude" in result and "longitude" in result:
                gps_coords = {"lat": result["latitude"], "lng": result["longitude"]}
            
            facility_info = {
                "title": result.get("title", "Unknown Facility"),
                "address": result.get("address", "Address not available"),
                "phone": result.get("phone", "Phone not available"),
                "rating": result.get("rating", "No rating"),
                "reviews": result.get("reviews", 0),
                "type": result.get("type", "Healthcare Facility"),
                "website": result.get("website", ""),
                "hours": result.get("hours", {}),
                "position": gps_coords,
                "place_id": result.get("place_id", ""),
                "description": result.get("description", ""),
                "price": result.get("price", ""),
                "service_options": result.get("service_options", {})
            }
            results.append(facility_info)
        
        return results if results else fallback_google_search(location, query)
    except Exception as e:
        st.warning(f"{translate('SerpAPI search failed')}: {e}")
        return fallback_google_search(location, query)

# 📍 **Fallback Google Search**
def fallback_google_search(location, query="general hospital"):
    """Fallback to original Google Custom Search if SerpAPI fails"""
    search_query = f"{query} in {location}"
    google_url = f"https://www.googleapis.com/customsearch/v1?q={search_query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"

    try:
        response = requests.get(google_url)
        data = response.json()
        
        results = []
        items = data.get("items", [])[:3]
        
        for item in items:
            facility_info = {
                "title": item.get("title", "Unknown Facility"),
                "address": "Address not available",
                "phone": "Phone not available",
                "rating": "No rating",
                "reviews": 0,
                "type": "Healthcare Facility",
                "website": item.get("link", ""),
                "hours": {},
                "position": {},
                "place_id": "",
                "description": item.get("snippet", "")
            }
            results.append(facility_info)
        
        return results
    except Exception as e:
        st.error(f"{translate('Both SerpAPI and Google search failed')}: {e}")
        return []

# 📌 **Generate Google Maps Link**
def generate_google_maps_link(place_name, location_context=None):
    if location_context:
        query = f"{place_name} {location_context}".replace(' ', '+')
    else:
        query = place_name.replace(' ', '+')
    return f"https://www.google.com/maps/search/?api=1&query={query}"

# 🗺 **Get Basic Location Coordinates**
def get_basic_location_coordinates(location):
    """Get coordinates for a general location (city, area)"""
    try:
        # Try Google Geocoding first for better accuracy
        google_geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={GOOGLE_API_KEY}"
        response = requests.get(google_geocode_url)
        data = response.json()
        
        if data.get("results"):
            location_data = data["results"][0]["geometry"]["location"]
            return [location_data["lat"], location_data["lng"]]
    except Exception as e:
        print(f"Google geocoding error: {e}")
    
    # Fallback to OpenRouteService
    try:
        url = f"https://api.openrouteservice.org/geocode/search?api_key={ORS_API_KEY}&text={location}&size=1"
        response = requests.get(url)
        data = response.json()
        if data.get("features"):
            coords = data["features"][0]["geometry"]["coordinates"]
            return [coords[1], coords[0]]  # Return as [lat, lon]
    except Exception as e:
        print(f"OpenRouteService geocoding error: {e}")
    
    return None

# 🗺 **Get Coordinates using multiple sources**
def get_location_coordinates(place_name, location_context=None, facility_position=None):
    """Enhanced coordinate retrieval with multiple fallback options"""
    
    # First try: Use coordinates from SerpAPI if available
    if facility_position:
        if "lat" in facility_position and "lng" in facility_position:
            return [facility_position["lat"], facility_position["lng"]]
        elif "latitude" in facility_position and "longitude" in facility_position:
            return [facility_position["latitude"], facility_position["longitude"]]
    
    # Second try: Google Geocoding with full address
    search_queries = []
    if location_context:
        search_queries.append(f"{place_name}, {location_context}")
        search_queries.append(f"{place_name} {location_context}")
    search_queries.append(place_name)
    
    for search_text in search_queries:
        try:
            google_geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={search_text}&key={GOOGLE_API_KEY}"
            response = requests.get(google_geocode_url)
            data = response.json()
            
            if data.get("results"):
                location_data = data["results"][0]["geometry"]["location"]
                return [location_data["lat"], location_data["lng"]]
        except Exception as e:
            print(f"Google geocoding error for '{search_text}': {e}")
            continue
    
    # Third try: OpenRouteService geocoding
    for search_text in search_queries:
        try:
            url = f"https://api.openrouteservice.org/geocode/search?api_key={ORS_API_KEY}&text={search_text}&size=1"
            response = requests.get(url)
            data = response.json()
            if data.get("features"):
                coords = data["features"][0]["geometry"]["coordinates"]
                return [coords[1], coords[0]]  # Return as [lat, lon]
        except Exception as e:
            print(f"OpenRouteService geocoding error for '{search_text}': {e}")
            continue
    
    return None

# 🗺 **Generate Enhanced Interactive Map**
def generate_enhanced_map(facility_info, location_context=None):
    """Generate detailed interactive map with facility information"""
    
    coordinates = get_location_coordinates(
        facility_info.get("title", ""), 
        location_context, 
        facility_info.get("position", {})
    )
    
    if coordinates:
        lat, lon = coordinates
        map_ = folium.Map(location=[lat, lon], zoom_start=16)
        
        # Create detailed popup content
        popup_content = f"""
        <div style="width: 300px;">
            <h4>{facility_info.get('title', 'Healthcare Facility')}</h4>
            <p><strong>📍 Address:</strong> {facility_info.get('address', 'Not available')}</p>
            <p><strong>📞 Phone:</strong> {facility_info.get('phone', 'Not available')}</p>
            <p><strong>⭐ Rating:</strong> {facility_info.get('rating', 'No rating')} ({facility_info.get('reviews', 0)} reviews)</p>
            <p><strong>🏥 Type:</strong> {facility_info.get('type', 'Healthcare Facility')}</p>
        </div>
        """
        
        # Add marker with enhanced popup
        folium.Marker(
            [lat, lon], 
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"Click for details about {facility_info.get('title', 'this facility')}",
            icon=folium.Icon(color='red', icon='plus', prefix='fa')
        ).add_to(map_)
        
        return map_
    else:
        # Fallback: create a general area map
        if location_context:
            general_coords = get_location_coordinates(location_context)
            if general_coords:
                lat, lon = general_coords
                map_ = folium.Map(location=[lat, lon], zoom_start=12)
                folium.Marker([lat, lon], 
                            popup=f"General area: {location_context}<br>Facility: {facility_info.get('title', 'Unknown')}", 
                            tooltip="Approximate location",
                            icon=folium.Icon(color='orange', icon='info-sign')).add_to(map_)
                return map_
    return None

# 🧠 **GroqCloud Healthcare Assistant (for main healthcare questions)**
def generate_healthcare_response(prompt):
    """Use GroqCloud for healthcare assistant responses"""
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    healthcare_prompt = f"""You are an intelligent healthcare assistant with expertise in medical advice, health conditions, and wellness. 

Provide helpful, accurate, and practical healthcare guidance for the following question. Always include a disclaimer that this is for informational purposes and users should consult healthcare professionals for serious concerns.

User question: {prompt}

Provide a comprehensive and helpful response."""

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": healthcare_prompt}],
        "max_tokens": 1024,
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            answer = response_data["choices"][0]["message"]["content"]
            
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
            error_msg = f"GroqCloud API Error: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {response.text}"
            
            return translate(f"Sorry, I couldn't process your healthcare question right now. Error: {error_msg}")
            
    except requests.exceptions.Timeout:
        return translate("Sorry, the request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        return translate("Sorry, connection failed. Please check your internet connection.")
    except Exception as e:
        return translate(f"Sorry, I encountered an unexpected error: {str(e)}")

# 🧠 **AI-Powered General Assistant (Mistral for other functions)**
def generate_ai_response(prompt, max_tokens=200):
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    body = {"model": "mistral-medium", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}

    try:
        response = requests.post(MISTRAL_URL, json=body, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
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
        
        # Try alternative model if mistral-medium fails
        body["model"] = "mistral-small"
        response = requests.post(MISTRAL_URL, json=body, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
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
        
        return translate(f"AI service temporarily unavailable. Status: {response.status_code}")
    except Exception as e:
        return translate(f"AI processing error: {str(e)[:100]}...")

# 📝 **Generate Enhanced Facility Summary**
def generate_enhanced_summary(facility_info):
    """Generate comprehensive summary using AI with facility details"""
    
    facility_name = facility_info.get("title", "Healthcare Facility")
    facility_type = facility_info.get("type", "Healthcare Facility")
    rating = facility_info.get("rating", "No rating")
    reviews = facility_info.get("reviews", 0)
    address = facility_info.get("address", "Address not available")
    phone = facility_info.get("phone", "Phone not available")
    
    prompt = f"""Create a comprehensive summary for this healthcare facility:

Name: {facility_name}
Type: {facility_type}
Rating: {rating} ({reviews} reviews)
Address: {address}
Phone: {phone}

Please provide:
1. A brief overview of the facility
2. What services they likely offer based on their type
3. How to contact them
4. Any notable features based on their rating and reviews

Keep it informative and helpful for someone looking for healthcare services."""

    summary = generate_ai_response(prompt, max_tokens=300)
    return summary

# 🍽 **Healthy Recipe Suggestions (GroqCloud for complete responses)**
def get_healthy_recipes(ingredients, condition=None):
    """Use GroqCloud for complete recipe responses"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    if condition:
        recipe_prompt = f"""You are a professional nutritionist and chef. Create a complete, detailed, easy-to-follow recipe using these ingredients: {ingredients} that is specifically beneficial for someone with {condition}.

Format your response exactly as follows:

**Recipe Name**

**Ingredients:**
- List all ingredients with exact quantities
- Include any additional ingredients needed for a complete recipe

**Instructions:**
1. Provide detailed step-by-step cooking instructions
2. Include cooking times and temperatures where applicable
3. Make each step clear and actionable
4. Include serving size information

**Health Benefits for {condition}:**
- Explain specifically why this recipe helps with {condition}
- Mention key nutrients and their benefits
- Include any dietary tips related to the condition

**Nutritional Information (per serving):**
- Approximate calories, protein, carbs, and fiber

Make sure the recipe is complete and practical to follow."""
    else:
        recipe_prompt = f"""You are a professional nutritionist and chef. Create a complete, detailed, easy-to-follow healthy recipe using these ingredients: {ingredients}.

Format your response exactly as follows:

**Recipe Name**

**Ingredients:**
- List all ingredients with exact quantities
- Include any additional ingredients needed for a complete recipe

**Instructions:**
1. Provide detailed step-by-step cooking instructions
2. Include cooking times and temperatures where applicable
3. Make each step clear and actionable
4. Include serving size information

**Health Benefits:**
- Explain the nutritional benefits of this recipe
- Mention key nutrients and their health effects

**Nutritional Information (per serving):**
- Approximate calories, protein, carbs, and fiber

Make sure the recipe is complete and practical to follow."""

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": recipe_prompt}],
        "max_tokens": 1500,  # Increased for complete recipes
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            answer = response_data["choices"][0]["message"]["content"]
            
            # Translate response to user's language
            from language_manager import get_user_language_code, translate
            from deep_translator import GoogleTranslator
            
            user_lang = get_user_language_code()
            if user_lang != "en":
                try:
                    answer = GoogleTranslator(source="en", target=user_lang).translate(answer)
                except Exception as trans_error:
                    print(f"Translation failed: {trans_error}")
                    answer = f"[{translate('English')}] {answer}"
            
            return answer
        else:
            # Fallback to Mistral if GroqCloud fails
            return generate_ai_response(recipe_prompt, max_tokens=800)
            
    except Exception as e:
        # Fallback to Mistral if GroqCloud fails
        return generate_ai_response(recipe_prompt, max_tokens=800)

# 🥗 **Smart Nutrition & Health Guide (GroqCloud for complete responses)**
def get_nutrition_info(food_item):
    """Use GroqCloud for complete nutrition information"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    # First classify the input
    classify_prompt = f"Classify '{food_item}' as either 'food' or 'condition'. Reply with ONLY 'food' or 'condition'."
    
    classify_data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": classify_prompt}],
        "max_tokens": 10,
        "temperature": 0.1
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=classify_data, timeout=15)
        if response.status_code == 200:
            category = response.json()["choices"][0]["message"]["content"].strip().lower().split()[0]
        else:
            category = "food"  # Default to food if classification fails
    except:
        category = "food"  # Default to food if classification fails

    if category == "condition":
        condition_prompt = f"""You are a professional nutritionist. Provide comprehensive dietary guidance for managing {food_item}.

Format your response as:

**Best Foods for {food_item}:**
- List 7-10 specific foods that help manage this condition
- For each food, explain why it's beneficial and how it helps
- Include specific nutrients that make each food helpful

**Foods to Avoid or Limit:**
- List 7-10 foods that should be limited or avoided
- Explain why these foods are problematic for this condition
- Include specific compounds or nutrients that cause issues

**Meal Planning Tips:**
- Provide 3-4 practical dietary tips for managing {food_item}
- Include timing, portion sizes, or preparation methods
- Suggest meal frequency or eating patterns if relevant

**Sample Daily Menu:**
- Provide a brief example of what a day of eating might look like
- Include breakfast, lunch, dinner, and snacks

Keep it comprehensive, accurate, and actionable."""

        nutrition_data = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": condition_prompt}],
            "max_tokens": 1200,
            "temperature": 0.7
        }

    elif category == "food":
        nutrition_prompt = f"""You are a professional nutritionist. Provide comprehensive nutritional information for {food_item} (per 100g serving).

Format your response as:

**Nutritional Profile (per 100g):**
- Calories: [specific amount] kcal
- Protein: [amount] g
- Carbohydrates: [amount] g
- Dietary Fiber: [amount] g
- Total Fat: [amount] g
- Saturated Fat: [amount] g
- Sugar: [amount] g
- Sodium: [amount] mg

**Key Vitamins & Minerals:**
- List the most significant vitamins and minerals with amounts
- Include % Daily Value where applicable
- Explain the health benefits of each key nutrient

**Health Benefits:**
- List 4-6 main health benefits of consuming this food
- Explain how it supports overall health and specific body systems
- Include any disease prevention properties

**Best Ways to Consume:**
- Suggest 3-4 healthy preparation methods
- Tips for maximizing nutritional value
- Any combinations with other foods that enhance absorption

**Considerations:**
- Any potential allergens or side effects
- Who should limit consumption and why
- Storage and freshness tips

Keep it accurate, detailed, and informative."""

        nutrition_data = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": nutrition_prompt}],
            "max_tokens": 1200,
            "temperature": 0.7
        }

    else:
        return "I couldn't determine if this is a food or health condition. Please try again with a clearer input!"

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=nutrition_data, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            answer = response_data["choices"][0]["message"]["content"]
            
            # Translate response to user's language
            from language_manager import get_user_language_code, translate
            from deep_translator import GoogleTranslator
            
            user_lang = get_user_language_code()
            if user_lang != "en":
                try:
                    answer = GoogleTranslator(source="en", target=user_lang).translate(answer)
                except Exception as trans_error:
                    print(f"Translation failed: {trans_error}")
                    answer = f"[{translate('English')}] {answer}"
            
            return answer
        else:
            # Fallback to Mistral if GroqCloud fails
            if category == "condition":
                fallback_prompt = f"""Provide dietary guidance for {food_item}:

**Best Foods for {food_item}:**
- List 5-7 specific foods that help manage this condition
- Explain why each food is beneficial

**Foods to Avoid:**
- List 5-7 foods that should be limited or avoided
- Explain why these foods are problematic

**Additional Tips:**
- Include 2-3 practical dietary tips for managing {food_item}

Keep it informative and actionable."""
                return generate_ai_response(fallback_prompt, max_tokens=400)
            else:
                fallback_prompt = f"""Provide comprehensive nutritional information for {food_item} (per 100g serving):

**Nutritional Profile:**
- Calories, protein, carbs, fiber, fat, saturated fat

**Key Vitamins & Minerals:**
- List significant vitamins and minerals with health benefits

**Health Benefits:**
- List 3-4 main health benefits

**Best Ways to Consume:**
- Suggest healthy preparation methods

Keep it accurate and informative."""
                return generate_ai_response(fallback_prompt, max_tokens=450)
            
    except Exception as e:
        # Fallback to Mistral if GroqCloud fails
        return f"Error getting nutrition info. Please try again. ({str(e)[:50]}...)"

# 📌 **Healthcare Page**
@multilingual_page
def healthcare_page():
    # Check Subscription (Feature ID 2)
    if not render_subscription_ui("Healthcare Assistance", 2):
        return
        
    modern_header(translate("🏥 Healthcare Assistance"), translate("Access medical facilities, get health advice, and discover nutritious recipes for a healthier life."))

    # 🧠 **AI-Powered Healthcare Assistant**
    st.header(translate("🧠 AI-Powered Healthcare Assistant"))
    user_query = st.text_input(translate("Ask a health-related question:"), key="ai_input")
    
    if st.button(translate("Get Advice")):
        if user_query:
            with st.spinner(translate("Getting healthcare advice...")):
                st.session_state.ai_response = generate_healthcare_response(user_query)
    
    if st.session_state.get("ai_response"):
        st.write(f"🤖 *{translate('Healthcare Assistant')}:*\n{st.session_state.ai_response}")

    # 📍 **Find Nearby Healthcare Facilities**
    st.header(translate("📍 Find Nearby Healthcare Facilities"))
    
    col1, col2 = st.columns(2)
    with col1:
        location = st.text_input(translate("Enter your city or location:"), key="location_input")
    with col2:
        facility_types = [
            translate("hospitals"), translate("clinics"), translate("urgent care"), 
            translate("pharmacies"), translate("dental clinics"), translate("eye care"), 
            translate("mental health"), translate("physical therapy")
        ]
        special_need = st.selectbox(
            translate("Type of healthcare facility:"), 
            facility_types,
            key="specialty_input"
        )

    if st.button(translate("🔍 Search Healthcare Facilities"), type="primary"):
        if location:
            with st.spinner(translate("Searching for healthcare facilities...")):
                st.session_state.healthcare_results = find_healthcare_facilities_serpapi(location, special_need)
        else:
            st.warning(translate("Please enter a location to search."))

    if st.session_state.get("healthcare_results"):
        st.success(f"{translate('Found')} {len(st.session_state.healthcare_results)} {translate('healthcare facilities')}:")
        
        for idx, facility in enumerate(st.session_state.healthcare_results):
            with st.expander(f"🏥 {facility.get('title', 'Healthcare Facility')}", expanded=(idx == 0)):
                
                # Create two columns for info and map
                info_col, map_col = st.columns([1, 1])
                
                with info_col:
                    # Display facility information
                    st.markdown(f"**📍 {translate('Address')}:** {facility.get('address', translate('Not available'))}")
                    st.markdown(f"**📞 {translate('Phone')}:** {facility.get('phone', translate('Not available'))}")
                    st.markdown(f"**⭐ {translate('Rating')}:** {facility.get('rating', translate('No rating'))} ({facility.get('reviews', 0)} {translate('reviews')})")
                    st.markdown(f"**🏥 {translate('Type')}:** {facility.get('type', translate('Healthcare Facility'))}")
                    
                    if facility.get('website'):
                        st.markdown(f"**🌐 {translate('Website')}:** [{translate('Visit Website')}]({facility['website']})")
                    
                    # Contact buttons
                    if facility.get('phone') and facility.get('phone') != 'Phone not available':
                        phone_clean = re.sub(r'[^\d+]', '', facility['phone'])
                        st.markdown(f"**📱 {translate('Quick Actions')}:**")
                        st.markdown(f"- [📞 {translate('Call Now')}](tel:{phone_clean})")
                    
                    # Google Maps link
                    maps_link = generate_google_maps_link(facility.get('title', ''), location)
                    st.markdown(f"- [🗺️ {translate('Directions on Google Maps')}]({maps_link})")
                
                with map_col:
                    # Display interactive map
                    map_ = generate_enhanced_map(facility, location)
                    if map_:
                        folium_static(map_, width=350, height=250)
                    else:
                        st.info(f"📍 {translate('Map not available for this location')}")
                
                # AI-generated summary
                st.markdown(f"**🤖 {translate('AI Summary')}:**")
                with st.spinner(translate("Generating summary...")):
                    summary = generate_enhanced_summary(facility)
                st.write(summary)
                
                # Operating hours if available
                if facility.get('hours'):
                    st.markdown(f"**🕒 {translate('Operating Hours')}:**")
                    hours = facility['hours']
                    if isinstance(hours, dict):
                        for day, time in hours.items():
                            st.write(f"- {day}: {time}")
                    else:
                        st.write(hours)
                
                st.markdown("---")

    # 🍽 **Healthy Recipe Suggestions**
    st.header(translate("🍽 Healthy Recipe Suggestions"))
    ingredients = st.text_input(translate("Enter ingredients (comma-separated):"), key="recipe_input")
    health_condition = st.text_input(translate("Health condition or disease (optional):"), key="condition_input", 
                                   help=translate("e.g., diabetes, hypertension, heart disease, etc."))

    if st.button(translate("Get Recipes")):
        if ingredients:
            with st.spinner(translate("Creating your healthy recipe...")):
                st.session_state.recipe_response = get_healthy_recipes(ingredients, health_condition if health_condition else None)

    if st.session_state.get("recipe_response"):
        st.write(f"🍛 *{translate('AI-Generated Recipe')}:*\n{st.session_state.recipe_response}")

    # 🥗 **Personalized Nutrition Information**
    st.header(translate("🥗 Smart Nutrition & Health Guide"))
    food_item = st.text_input(translate("Enter a food item or health condition:"), key="nutrition_input")

    if st.button(translate("Get Nutrition Info")):
        if food_item:
            with st.spinner(translate("Analyzing nutrition information...")):
                st.session_state.nutrition_response = get_nutrition_info(food_item)
        else:
            st.warning(translate("Please enter a food item or health condition."))

    if st.session_state.get("nutrition_response"):
        st.markdown(f"### 📊 {translate('Nutritional Analysis')}")
        st.write(st.session_state.nutrition_response)

# Run the healthcare page
if __name__ == "__main__":
    healthcare_page()