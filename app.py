import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import json
import os
import random
import requests
from datetime import datetime, timedelta

# ================== GEMINI API CONFIG (DISABLED) ==================
# The Gemini API is not used in this version.
# You can re-enable it for the AI Assistant tab later.
# genai.configure(api_key='YOUR_GEMINI_API_KEY')
# model = genai.GenerativeModel('gemini-1.0-pro')

# ================== AI ASSISTANT KNOWLEDGE BASE ==================

market_prices = {
    "Rice": "₹40/kg",
    "Wheat": "₹28/kg",
    "Tomato": "₹20/kg",
    "Cotton": "₹6500/quintal"
}

subsidies = {
  "PM-KISAN": {
    "description_en": "The Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) scheme provides financial support of ₹6,000 per year to eligible farmer families in three equal installments to help them meet farming expenses and domestic needs.",
    "description_ta": "பிரதம மந்திரி கிசான் சம்மான் நிதி (PM-KISAN) திட்டம் தகுதியுள்ள விவசாய குடும்பங்களுக்கு ஆண்டுக்கு ₹6,000 நிதி உதவியை மூன்று சம தவணைகளாக வழங்குகிறது.",
    "link": "https://pmkisan.gov.in/"
  },
  "Fasal Bima Yojana": {
    "description_en": "This scheme provides comprehensive crop insurance against the loss of yield due to non-preventable natural risks like drought, floods, and pests. It aims to stabilize farmers' incomes.",
    "description_ta": "இந்தத் திட்டம் வறட்சி, வெள்ளம் மற்றும் பூச்சிகள் போன்ற தடுக்க முடியாத இயற்கை அபாயங்களால் ஏற்படும் பயிர் இழப்பிற்கு விரிவான பயிர் காப்பீட்டை வழங்குகிறது. இது விவசாயிகளின் வருமானத்தை நிலைநிறுத்துவதை நோக்கமாகக் கொண்டது.",
    "link": "https://pmfby.gov.in/"
  },
  "Soil Health Card": {
    "description_en": "A government-issued report that provides farmers with a detailed nutrient status of their soil, along with recommendations on the appropriate fertilizer dosage and other soil amendments to improve fertility.",
    "description_ta": "இது விவசாயிகளுக்கு அவர்களின் மண்ணின் ஊட்டச்சத்து நிலை குறித்த விரிவான அறிக்கையை வழங்கும் ஒரு அரசு திட்டம். இது மண்ணின் வளத்தை மேம்படுத்த பொருத்தமான உரங்கள் மற்றும் பிற மண் திருத்தங்கள் பற்றிய பரிந்துரைகளையும் வழங்குகிறது.",
    "link": "https://soilhealth.dac.gov.in/"
  }
}

helplines = {
    "Rice": "1800-180-1551",
    "Wheat": "1800-180-1552",
    "Cotton": "1800-180-1553",
    "Tomato": "1800-180-1554"
}

diseases = [
    {"name_en": "Leaf Spot Fungus", "advice_en": "Use copper-based fungicide and avoid excess watering.",
     "name_ta": "இலை புள்ளி பூஞ்சை", "advice_ta": "செம்பு சார்ந்த பூஞ்சைக் கொல்லியைப் பயன்படுத்தவும் மற்றும் அதிகப்படியான நீர் பாய்ச்சுவதைத் தவிர்க்கவும்."},
    {"name_en": "Aphid Pest Attack", "advice_en": "Spray neem oil solution, encourage ladybugs.",
     "name_ta": "அஃபிட் பூச்சி தாக்குதல்", "advice_ta": "வேப்ப எண்ணெய் கரைசலை தெளிக்கவும், லேடிபக் வண்டுகளை ஊக்குவிக்கவும்."},
    {"name_en": "Nitrogen Deficiency", "advice_en": "Add urea or compost rich in nitrogen.",
     "name_ta": "நைட்ரஜன் குறைபாடு", "advice_ta": "யூரியா அல்லது நைட்ரஜன் நிறைந்த உரங்களைச் சேர்க்கவும்."},
    {"name_en": "Healthy Crop", "advice_en": "No issues detected. Keep monitoring regularly.",
     "name_ta": "ஆரோக்கியமான பயிர்", "advice_ta": "எந்த பிரச்சனைகளும் கண்டறியப்படவில்லை. தொடர்ந்து கண்காணிக்கவும்."}
]

# ================== VOICE ASSISTANT COMPONENT ==================

def voice_to_text_component(language_code: str, key=None):
    """
    A Streamlit component that uses the browser's Web Speech API to get voice input.
    Stores recognized text into st.session_state[key].
    """
    components.html(
        f"""
        <style>
            .listening {{
                animation: pulse 1.5s infinite;
            }}
            @keyframes pulse {{
                0% {{ box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }}
                70% {{ box-shadow: 0 0 0 10px rgba(255, 0, 0, 0); }}
                100% {{ box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }}
            }}
        </style>
        <button id="listenBtn" onclick="startRecognition()" 
            style="background-color: #4CAF50; color: white; padding: 10px 18px; border-radius: 8px; border: none; cursor: pointer; font-size: 16px;">
            🎙️ Start Listening
        </button>
        <script>
            var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '{language_code}';
            recognition.continuous = false;
            recognition.interimResults = false;
            
            var listenBtn = document.getElementById('listenBtn');

            function startRecognition() {{
                listenBtn.innerHTML = '🔴 Listening...';
                listenBtn.classList.add('listening');
                recognition.start();
            }}

            recognition.onresult = function(event) {{
                var recognizedText = event.results[0][0].transcript;
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    key: '{key}',
                    value: recognizedText
                }}, '*');
            }};

            recognition.onend = function() {{
                listenBtn.innerHTML = '🎙️ Start Listening';
                listenBtn.classList.remove('listening');
            }};
        </script>
        """,
        height=50,
        key=key
    )
    # Return value safely from session state
    return st.session_state.get(key, "")

# ================== STREAMLIT APP LAYOUT ==================
st.set_page_config(page_title="AI Farmer Assistant", page_icon="🌱", layout="wide")
st.title("🌱 AI Farmer Assistant")
st.markdown("Expert Help on Demand for Farmers")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab_voice_assistant = st.tabs([
    "🧪 Diagnose Crop",
    "📊 Market Price",
    "🏛 Subsidy Info",
    "⏰ Reminders",
    "💬 Farmer Forum",
    "📞 Call an Expert",
    "🌦 Weather Info",
    "📈 Profit Calc",
    "💧 Water Advice",
    "🎙️ Voice Assistant"
])

# --- Diagnose Crop ---
with tab1:
    st.header("🧪 Diagnose Crop")
    lang = st.radio("Select Language", ('English', 'தமிழ்'), key="diag_lang_radio")
    uploaded = st.file_uploader("Upload crop image", type=["jpg", "png"], key="diagnose_uploader")
    if uploaded:
        st.image(uploaded, caption="Uploaded Crop Image", use_column_width=True)
        prediction = random.choice(diseases)
        
        if lang == 'English':
            st.success(f"**Prediction:** {prediction['name_en']}")
            st.info(f"**Advice:** {prediction['advice_en']}")
        else:
            st.success(f"**கண்டறிதல்:** {prediction['name_ta']}")
            st.info(f"**பரிந்துரை:** {prediction['advice_ta']}")

# --- Market Prices ---
with tab2:
    st.header("📊 Check Market Prices")
    lang = st.radio("Select Language", ('English', 'தமிழ்'), key="market_lang_radio")
    crop = st.selectbox("Select Crop", list(market_prices.keys()), key="market_crop")
    if st.button("Get Price", key="get_price_btn"):
        if lang == 'English':
             st.success(f"💰 Current Market Price of {crop}: {market_prices[crop]}")
        else:
             st.success(f"💰 {crop}-இன் தற்போதைய சந்தை விலை: {market_prices[crop]}")

# --- Subsidy Info ---
with tab3:
    st.header("🏛 Government Subsidy Info")
    lang = st.radio("Select Language", ('English', 'தமிழ்'), key="subsidy_lang_radio")
    scheme = st.selectbox("Select Scheme", list(subsidies.keys()), key="subsidy_scheme")
    if st.button("Get Info", key="get_subsidy_btn"):
        if lang == 'English':
            st.info(f"**Description:** {subsidies[scheme]['description_en']}")
        else:
            st.info(f"**விளக்கம்:** {subsidies[scheme]['description_ta']}")
        st.markdown(f"**Official Link:** [Learn more]({subsidies[scheme]['link']})")

# --- Reminders ---
with tab4:
    st.header("⏰ Set Reminders")
    task = st.text_input("Enter task (e.g., Fertilization, Spraying)", key="reminder_task")
    days = st.slider("Remind me in (days)", 1, 30, 7, key="reminder_days")
    if st.button("Set Reminder", key="set_reminder_btn"):
        if task:
            remind_date = datetime.now() + timedelta(days=days)
            if "reminders" not in st.session_state:
                st.session_state.reminders = []
            st.session_state.reminders.append((task, remind_date))
            st.success(f"✅ Reminder set for **{task}** on {remind_date.strftime('%d-%m-%Y')}")
    
    if "reminders" in st.session_state and st.session_state.reminders:
        st.subheader("📌 Your Reminders")
        for task, date in st.session_state.reminders:
            st.write(f"- **{task}** on {date.strftime('%d-%m-%Y')}")

# --- Farmer Forum ---
with tab5:
    st.header("💬 Farmer Forum")
    new_msg = st.text_input("Ask a question or share tips", key="forum_input")
    if st.button("Post", key="forum_post_btn"):
        if new_msg:
            if "forum_messages" not in st.session_state:
                st.session_state.forum_messages = []
            st.session_state.forum_messages.append(new_msg)
            st.success("✅ Posted successfully!")
    
    if "forum_messages" in st.session_state and st.session_state.forum_messages:
        st.subheader("Community Messages")
        for i, msg in enumerate(reversed(st.session_state.forum_messages), 1):
            st.write(f"{i}. {msg}")

# --- Call an Expert ---
with tab6:
    st.header("📞 Call an Expert")
    crop_expert = st.selectbox("Select Crop", list(helplines.keys()), key="expert_crop")
    if st.button("Get Helpline", key="get_helpline_btn"):
        st.success(f"📞 Official Helpline for {crop_expert}: {helplines[crop_expert]}")
        st.markdown(f"[📲 Call Now](tel:{helplines[crop_expert]})")

# --- Weather Info ---
with tab7:
    st.header("🌦 Weather Information")
    city = st.text_input("Enter your city / village", key="weather_city")
    OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"
    
    def get_weather(city):
        if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "YOUR_OPENWEATHER_API_KEY":
            return {"error": "API key is missing or not configured."}
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={OPENWEATHER_API_KEY}"
        res = requests.get(url).json()
        if res.get("cod") != 200:
            return {"error": res.get("message", "Unable to fetch weather")}
        return {
            "city": res["name"],
            "temp": res["main"]["temp"],
            "humidity": res["main"]["humidity"],
            "desc": res["weather"][0]["description"].title()
        }

    if st.button("Get Weather", key="get_weather_btn"):
        if not city:
            st.warning("Please enter a city name.")
        else:
            data = get_weather(city)
            if "error" in data:
                st.error(f"❌ {data['error']}")
            else:
                st.success(f"📍 Weather in {data['city']}")
                st.write(f"🌡 Temperature: {data['temp']} °C")
                st.write(f"💧 Humidity: {data['humidity']}%")
                st.write(f"☁ Condition: {data['desc']}")

# --- Cost & Profit Calculator ---
with tab8:
    st.header("📈 Cost & Profit Calculator")
    st.write("Estimate your potential profit based on costs and market prices.")
    crop_select = st.selectbox("Select Crop", list(market_prices.keys()), key="calc_crop")
    land_size = st.number_input("Land Size (in acres)", min_value=0.1, value=1.0, key="land_size")
    cost_of_inputs = st.number_input("Total Cost of Inputs (e.g., seeds, fertilizer) per acre (₹)", min_value=0, value=2500, key="cost_inputs")
    estimated_yield = st.number_input("Estimated Yield (in quintals per acre)", min_value=0.1, value=10.0, key="estimated_yield")
    if st.button("Calculate Profit", key="calculate_btn"):
        try:
            price_str = market_prices[crop_select].replace('₹', '').replace('/quintal', '').replace('/kg', '')
            current_price = float(price_str)
            total_cost = land_size * cost_of_inputs
            total_revenue = land_size * estimated_yield * current_price
            net_profit = total_revenue - total_cost
            st.success(f"**Calculations for {crop_select}**")
            st.info(f"💰 **Total Revenue:** ₹{total_revenue:,.2f}")
            st.warning(f"💸 **Total Cost:** ₹{total_cost:,.2f}")
            st.metric(label="📈 **Net Profit**", value=f"₹{net_profit:,.2f}")
        except (ValueError, KeyError) as e:
            st.error("❌ An error occurred. Please check the market price data format.")

# --- Water Advice ---
with tab9:
    st.header("💧 Smart Water Management")
    st.write("Get personalized watering advice based on real-time weather.")
    def get_water_advice(weather_data):
        if "error" in weather_data:
            return f"Error: {weather_data['error']}"
        description = weather_data['desc'].lower()
        if 'rain' in description or 'shower' in description:
            return "🌧️ **Rain expected:** No need to water your crops today. Delay irrigation."
        elif 'thunderstorm' in description:
            return "⛈️ **Storm alert:** Postpone all watering and field activities to prevent damage."
        elif 'cloud' in description or 'overcast' in description:
            return "☁️ **Cloudy day:** You can consider reducing water slightly, as evaporation will be lower."
        elif 'sun' in description or 'clear' in description:
            return "☀️ **Sunny & dry:** Water your crops as scheduled. It is a good day for field work."
        else:
            return "💧 **Weather is stable:** Proceed with your usual watering schedule."
    city_water_advice = st.text_input("Enter your city / village", key="water_city_input")
    if st.button("Get Advice", key="get_water_advice_btn"):
        if not city_water_advice:
            st.warning("Please enter a city name.")
        else:
            data = get_weather(city_water_advice)
            advice = get_water_advice(data)
            st.info(advice)

# --- Multilingual Voice-to-Text Chatbot (Prototype) ---
with tab_voice_assistant:
    st.header("🎙️ Multilingual Voice Assistant")
    st.write("Click and speak a command. Responses are translated for a prototype demo.")

    lang_choice = st.selectbox("Select language for voice recognition", 
                               ['English', 'தமிழ்'], index=0, key="voice_lang_select")
    
    language_codes = {'English': 'en-IN', 'தமிழ்': 'ta-IN'}
    
    voice_query = voice_to_text_component(language_codes[lang_choice], key="voice_input")

    if voice_query:
        st.write(f"You said: **{voice_query}**")
        
        query = voice_query.lower()

        if lang_choice == 'English':
            if "price of" in query:
                crop = query.split("price of")[-1].strip().title()
                price = market_prices.get(crop, "Price not found.")
                st.success(f"The market price for {crop} is: {price}")
            elif "about" in query and "pm-kisan" in query:
                st.info(subsidies["PM-KISAN"]["description_en"])
            elif "weather" in query:
                st.warning("Sorry, I can't check the weather with my voice commands yet.")
            else:
                st.warning("I'm sorry, I couldn't understand that command. Try asking for a crop price or a subsidy description.")
        else: # Tamil
            if "விலை" in query or "rate" in query:
                if "அரிசி" in query:
                    crop = "Rice"
                elif "தக்காளி" in query:
                    crop = "Tomato"
                else:
                    crop = "Not found"
                
                if crop in market_prices:
                    st.success(f"{crop}-இன் தற்போதைய சந்தை விலை: {market_prices[crop]}")
                else:
                    st.warning("மன்னிக்கவும்
