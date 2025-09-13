import streamlit as st
import random
import requests
import json
import os
from datetime import datetime, timedelta

WEATHER_API_KEY = "17d7e2b75f830375584c3551f882a13f"  # replace with your real key

def get_weather(city):
    """Fetch weather info for a city using OpenWeatherMap API"""
    if not WEATHER_API_KEY:
        return {"error": "API key missing"}
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={WEATHER_API_KEY}"
    res = requests.get(url).json()
    
    if res.get("cod") != 200:
        return {"error": res.get("message", "Unable to fetch weather")}
    
    return {
        "city": res["name"],
        "temp": res["main"]["temp"],
        "humidity": res["main"]["humidity"],
        "desc": res["weather"][0]["description"].title()
    }    
def get_water_advice(weather_data):
    """Provides watering advice based on weather conditions."""
    if "error" in weather_data:
        return "Unable to get weather data. Please check your city name."

    description = weather_data['desc'].lower()

    if 'rain' in description or 'shower' in description:
        return "🌧 *Rain expected:* No need to water your crops today. Delay irrigation."
    elif 'thunderstorm' in description:
        return "⛈ *Storm alert:* Postpone all watering and field activities to prevent damage."
    elif 'cloud' in description or 'overcast' in description:
        return "☁ *Cloudy day:* You can consider reducing water slightly, as evaporation will be lower."
    elif 'sun' in description or 'clear' in description:
        return "☀ *Sunny & dry:* Water your crops as scheduled. It is a good day for field work."
    else:
        return "💧 *Weather is stable:* Proceed with your usual watering schedule."

# Load data files
with open("data/market.json") as f:
    market_prices = json.load(f)

with open("data/subsidies.json") as f:
    subsidies = json.load(f)

with open("data/helplines.json") as f:
    helplines = json.load(f)

# Dummy disease list
diseases = [
    {"name": "Leaf Spot Fungus", "advice": "Use copper-based fungicide and avoid excess watering."},
    {"name": "Aphid Pest Attack", "advice": "Spray neem oil solution, encourage ladybugs."},
    {"name": "Nitrogen Deficiency", "advice": "Add urea or compost rich in nitrogen."},
    {"name": "Healthy Crop", "advice": "No issues detected. Keep monitoring regularly."}
]

# Session state for reminders & forum
if "reminders" not in st.session_state:
    st.session_state.reminders = []
if "forum" not in st.session_state:
    st.session_state.forum = []

# Streamlit UI
st.set_page_config(page_title="🌱 AI Farmer Assistant", layout="wide")
st.title("🌱 AI Farmer Assistant")
st.write("Expert Help for Farmers — Crop Health • Market Prices • Subsidy Info • Reminders • Forum • Experts 🌦 Weather Information  Profit Calc Water Advice")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "🧪 Diagnose Crop",
    "📊 Market Price",
    "🏛 Subsidy Info",
    "⏰ Reminders",
    "💬 Farmer Forum",
    "📞 Call an Expert",
    "🌦 Weather Info",
    "📈 Profit Calc",
    "💧 Water Advice"
])

# --- Crop Diagnosis ---
with tab1:
    st.header("🧪 Diagnose Crop Disease")
    uploaded = st.file_uploader("Upload a crop image", type=["jpg", "png", "jpeg"])
    if uploaded:
        st.image(uploaded, caption="Uploaded Crop Image", use_column_width=True)
        prediction = random.choice(diseases)  # Dummy prediction
        st.success(f"Prediction: {prediction['name']}")
        st.info(f"Advice: {prediction['advice']}")


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
        # Display the image first
        image_query = subsidies[scheme]['image']
        st.image(f"https://source.unsplash.com/random/800x400/?{image_query}") 
        
        st.info(f"*Description:* {subsidies[scheme]['description']}")
        st.markdown(f"*Official Link:* [Learn more]({subsidies[scheme]['link']})")

# --- Reminders ---
with tab4:
    st.header("⏰ Set Farming Reminders")
    task = st.selectbox("Choose Task", ["Fertilization", "Spraying", "Harvesting"])
    days = st.slider("Remind me in (days)", 1, 30, 7)
    if st.button("Set Reminder"):
        remind_date = datetime.now() + timedelta(days=days)
        st.session_state.reminders.append((task, remind_date))
        st.success(f"✅ Reminder set for {task} on {remind_date.strftime('%d-%m-%Y')}")

    if st.session_state.reminders:
        st.subheader("📌 Your Reminders")
        for task, date in st.session_state.reminders:
            st.write(f"- {task} → {date.strftime('%d-%m-%Y')}")

# --- Farmer Forum ---
with tab5:
    st.header("💬 Farmer Forum")
    user_msg = st.text_input("Ask a question or share a tip")
    if st.button("Post"):
        if user_msg.strip():
            st.session_state.forum.append(user_msg)
            st.success("✅ Posted successfully!")

    if st.session_state.forum:
        st.write("### 🌾 Forum Messages")
        for i, msg in enumerate(st.session_state.forum[::-1], 1):
            st.write(f"{i}. {msg}")

# --- Call an Expert ---
with tab6:
    st.header("📞 Call an Expert")
    crop_expert = st.selectbox("Select Crop", list(helplines.keys()), key="expert_crop")
    if st.button("Get Helpline", key="get_helpline_btn"):
        st.success(f"📞 Official Helpline for {crop_expert}: {helplines[crop_expert]}")
        st.markdown(f"[📲 Call Now](tel:{helplines[crop_expert]})")
        
with tab7:
    st.header("🌦 Weather Information")
    city = st.text_input("Enter your city / village", key="weather_city")
    if st.button("Get Weather", key="get_weather_btn"):
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

    # User Inputs
    crop_select = st.selectbox("Select Crop", list(market_prices.keys()), key="calc_crop")
    land_size = st.number_input("Land Size (in acres)", min_value=0.1, value=1.0, key="land_size")
    cost_of_inputs = st.number_input("Total Cost of Inputs (e.g., seeds, fertilizer) per acre (₹)", min_value=0, value=2500, key="cost_inputs")
    estimated_yield = st.number_input("Estimated Yield (in quintals per acre)", min_value=0.1, value=10.0, key="estimated_yield")

    if st.button("Calculate Profit", key="calculate_btn"):
        try:
            # Retrieve the market price and remove currency symbol
            price_str = market_prices[crop_select].replace('₹', '').replace('/quintal', '').replace('/kg', '')
            current_price = float(price_str)

            # Calculations
            total_cost = land_size * cost_of_inputs
            total_revenue = land_size * estimated_yield * current_price
            net_profit = total_revenue - total_cost

            st.success(f"*Calculations for {crop_select}*")
            st.info(f"💰 *Total Revenue:* ₹{total_revenue:,.2f}")
            st.warning(f"💸 *Total Cost:* ₹{total_cost:,.2f}")
            st.metric(label="📈 *Net Profit*", value=f"₹{net_profit:,.2f}")

        except (ValueError, KeyError) as e:
            st.error("❌ An error occurred. Please check the market price data format.")

# --- Water Advice ---
with tab9:
    st.header("💧 Smart Water Management")
    st.write("Get personalized watering advice based on real-time weather.")

    city_water_advice = st.text_input("Enter your city / village", key="water_city")

    if st.button("Get Advice", key="get_water_advice_btn"):
        if not city_water_advice:
            st.warning("Please enter a city name.")
        else:
            weather_data = get_weather(city_water_advice)
            advice = get_water_advice(weather_data)

            if "error" in advice:
                st.error(f"❌ {advice}")
            else:
                st.success(f"*Advice for {city_water_advice.title()}:*")
                st.info(advice)


