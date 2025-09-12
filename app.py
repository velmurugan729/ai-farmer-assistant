import streamlit as st
import google.generativeai as genai
import json
import os
import random
import requests
from datetime import datetime, timedelta

# ================== GEMINI API CONFIG ==================
# ⚠️ Replace 'YOUR_GEMINI_API_KEY' with your actual key
genai.configure(api_key=AIzaSyBnRvhlrHsYbvOCp2dCdRnz3nHmUc4HKgM)
model = genai.GenerativeModel('gemini-pro')

# ================== AI ASSISTANT KNOWLEDGE BASE ==================

# Define all data here to be used by the AI
market_prices = {
    "Rice": "₹40/kg",
    "Wheat": "₹28/kg",
    "Tomato": "₹20/kg",
    "Cotton": "₹6500/quintal"
}

subsidies = {
  "PM-KISAN": {
    "description": "The Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) scheme provides financial support of ₹6,000 per year to eligible farmer families in three equal installments to help them meet farming expenses and domestic needs.",
    "link": "https://pmkisan.gov.in/"
  },
  "Fasal Bima Yojana": {
    "description": "This scheme provides comprehensive crop insurance against the loss of yield due to non-preventable natural risks like drought, floods, and pests. It aims to stabilize farmers' incomes and encourage them to adopt innovative agricultural practices.",
    "link": "https://pmfby.gov.in/"
  },
  "Soil Health Card": {
    "description": "A government-issued report that provides farmers with a detailed nutrient status of their soil, along with recommendations on the appropriate fertilizer dosage and other soil amendments to improve fertility.",
    "link": "https://soilhealth.dac.gov.in/"
  },
  "Krishi Sinchai Yojana": {
    "description": "The Pradhan Mantri Krishi Sinchai Yojana (PMKSY) focuses on enhancing water use efficiency with the motto 'Per Drop More Crop'. The scheme provides a subsidy for installing micro-irrigation systems, such as drip and sprinkler irrigation.",
    "link": "https://pmksy.gov.in/microirrigation/index.aspx"
  },
  "Interest Subvention Scheme": {
    "description": "Provides concessional short-term agricultural loans to farmers at a low interest rate, with an additional subvention for prompt repayment. This aims to ensure easy and affordable credit availability.",
    "link": "https://agriculture.vikaspedia.in/agriculture-credit/interest-subvention-scheme-for-farmers"
  },
  "Farm Mechanization Scheme": {
    "description": "This scheme provides financial assistance and subsidies to farmers for purchasing modern farm machinery and equipment. The goal is to make farming less labor-intensive, more efficient, and more productive.",
    "link": "https://www.india.gov.in/topics/agriculture/agricultural-machinery"
  },
  "Rashtriya Krishi Vikas Yojana": {
    "description": "The Rashtriya Krishi Vikas Yojana (RKVY) is an umbrella scheme that gives flexibility and autonomy to states to plan and implement agricultural schemes according to their specific needs and priorities.",
    "link": "https://rkvy.nic.in/"
  },
  "National Food Security Mission": {
    "description": "This mission focuses on increasing the production of food grains like rice, wheat, and pulses through the dissemination of improved technologies, farm practices, and resource conservation.",
    "link": "https://www.nfsm.gov.in/"
  }
}

helplines = {
    "Rice": "1800-180-1551",
    "Wheat": "1800-180-1552",
    "Cotton": "1800-180-1553",
    "Tomato": "1800-180-1554"
}

diseases = [
    {"name": "Leaf Spot Fungus", "advice": "Use copper-based fungicide and avoid excess watering."},
    {"name": "Aphid Pest Attack", "advice": "Spray neem oil solution, encourage ladybugs."},
    {"name": "Nitrogen Deficiency", "advice": "Add urea or compost rich in nitrogen."},
    {"name": "Healthy Crop", "advice": "No issues detected. Keep monitoring regularly."}
]

def create_knowledge_base():
    """Generates a text-based knowledge base for the AI from your app's data."""
    persona = "You are a helpful AI assistant for farmers, named the 'AI Farmer Assistant'. Your primary goal is to provide expert, on-demand help to farmers. You are a source of truth for all things farming, including crop prices, government schemes, and weather. Be concise and friendly."

    current_date = datetime.now().strftime("%B %d, %Y")
    current_location = "Chennai, Tamil Nadu"
    
    knowledge_base = f"""
    {persona}

    Today's date is {current_date} and the current location is {current_location}.

    Here is the data you must use. Do not use any other external knowledge or information.
    - **Market Prices:** {json.dumps(market_prices)}
    - **Government Subsidies:** {json.dumps(subsidies)}
    - **Helpline Numbers:** {json.dumps(helplines)}
    
    **Instructions:**
    - Use the provided data to answer questions directly.
    - If a farmer asks for information not in the data, state that you do not have that specific information.
    - Be conversational and encouraging.
    - Keep your responses under 3 sentences unless more detail is requested.
    """
    return knowledge_base

def get_ai_response_gemini(user_query):
    """Handles conversational turns with the Gemini API."""
    try:
        if "chat_session" not in st.session_state:
            st.session_state.chat_session = model.start_chat(history=[])
            # Prime the model with the knowledge base
            st.session_state.chat_session.send_message(create_knowledge_base())
            
        response = st.session_state.chat_session.send_message(user_query)
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"

# ================== STREAMLIT APP LAYOUT ==================
st.set_page_config(page_title="AI Farmer Assistant", page_icon="🌱", layout="wide")
st.title("🌱 AI Farmer Assistant")
st.markdown("Expert Help on Demand for Farmers")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab_gen_ai = st.tabs([
    "🧪 Diagnose Crop",
    "📊 Market Price",
    "🏛 Subsidy Info",
    "⏰ Reminders",
    "💬 Farmer Forum",
    "📞 Call an Expert",
    "🌦 Weather Info",
    "📈 Profit Calc",
    "💧 Water Advice",
    "🧠 AI Assistant"
])

# --- Diagnose Crop ---
with tab1:
    st.header("🧪 Diagnose Crop")
    uploaded = st.file_uploader("Upload crop image", type=["jpg", "png"], key="diagnose_uploader")
    if uploaded:
        st.image(uploaded, caption="Uploaded Crop Image", use_column_width=True)
        prediction = random.choice(diseases)
        st.success(f"**Prediction:** {prediction['name']}")
        st.info(f"**Advice:** {prediction['advice']}")

# --- Market Prices ---
with tab2:
    st.header("📊 Check Market Prices")
    crop = st.selectbox("Select Crop", list(market_prices.keys()), key="market_crop")
    if st.button("Get Price", key="get_price_btn"):
        st.success(f"💰 Current Market Price of {crop}: {market_prices[crop]}")

# --- Subsidy Info ---
with tab3:
    st.header("🏛 Government Subsidy Info")
    scheme = st.selectbox("Select Scheme", list(subsidies.keys()), key="subsidy_scheme")
    if st.button("Get Info", key="get_subsidy_btn"):
        st.info(f"**Description:** {subsidies[scheme]['description']}")
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
    
    # ⚠️ Replace 'YOUR_OPENWEATHER_API_KEY' with your actual key
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

# --- Generative AI Assistant ---
with tab_gen_ai:
    st.header("🧠 AI Farmer Assistant")
    st.write("I am a conversational AI. Ask me anything about farming!")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])
        # Prime the model with the knowledge base
        st.session_state.chat_session.send_message(create_knowledge_base())
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_query := st.chat_input("How can I help you today?"):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.spinner("Thinking..."):
            ai_response = get_ai_response_gemini(user_query)
        
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        with st.chat_message("assistant"):
            st.markdown(ai_response)
