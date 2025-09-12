import streamlit as st
import requests
import os
import random
import json
from datetime import datetime, timedelta

# ================== WEATHER CONFIG ==================
# Hardcode API key directly for hackathon simplicity
# ⚠️ Replace 'YOUR_API_KEY_HERE' with your actual OpenWeatherMap API key
WEATHER_API_KEY = "YOUR_API_KEY_HERE"

def get_weather(city):
    """Fetch weather info for a city using OpenWeatherMap API"""
    if not WEATHER_API_KEY or WEATHER_API_KEY == "YOUR_API_KEY_HERE":
        return {"error": "API key is missing or not configured."}
    
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

# ================== SAMPLE DATA ==================
market_prices = {
    "Rice": "₹40/kg",
    "Wheat": "₹28/kg",
    "Tomato": "₹20/kg",
    "Cotton": "₹6500/quintal"
}

subsidies = {
    "PM-KISAN": "₹6,000 per year in 3 equal installments.",
    "Fasal Bima Yojana": "Insurance cover against crop failure.",
    "Soil Health Card": "Subsidy on soil testing & nutrients."
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

# ================== SESSION STATE ==================
# Session state for reminders and forum messages
if "reminders" not in st.session_state:
    st.session_state.reminders = []
if "forum_messages" not in st.session_state:
    st.session_state.forum_messages = []

# ================== STREAMLIT APP ==================
st.set_page_config(page_title="AI Farmer Assistant", page_icon="🌱", layout="wide")
st.title("🌱 AI Farmer Assistant")
st.markdown("Expert Help on Demand for Farmers")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🧪 Diagnose Crop",
    "📊 Market Price",
    "🏛 Subsidy Info",
    "⏰ Reminders",
    "💬 Farmer Forum",
    "📞 Call an Expert",
    "🌦 Weather Info"
])

# --- Diagnose Crop ---
with tab1:
    st.header("🧪 Diagnose Crop")
    uploaded = st.file_uploader("Upload crop image", type=["jpg", "png"])
    if uploaded:
        st.image(uploaded, caption="Uploaded Crop Image", use_column_width=True)
        # Dummy prediction
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
        st.info(f"**{scheme}:** {subsidies[scheme]}")

# --- Reminders ---
with tab4:
    st.header("⏰ Set Reminders")
    task = st.text_input("Enter task (e.g., Fertilization, Spraying)", key="reminder_task")
    days = st.slider("Remind me in (days)", 1, 30, 7, key="reminder_days")
    if st.button("Set Reminder", key="set_reminder_btn"):
        remind_date = datetime.now() + timedelta(days=days)
        st.session_state.reminders.append((task, remind_date))
        st.success(f"✅ Reminder set for **{task}** on {remind_date.strftime('%d-%m-%Y')}")
    
    if st.session_state.reminders:
        st.subheader("📌 Your Reminders")
        for task, date in st.session_state.reminders:
            st.write(f"- **{task}** on {date.strftime('%d-%m-%Y')}")

# --- Farmer Forum ---
with tab5:
    st.header("💬 Farmer Forum")
    new_msg = st.text_input("Ask a question or share tips", key="forum_input")
    if st.button("Post", key="forum_post_btn"):
        if new_msg:
            st.session_state.forum_messages.append(new_msg)
            st.success("✅ Posted successfully!")
    
    if st.session_state.forum_messages:
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
    if st.button("Get Weather", key="get_weather_btn"):
        data = get_weather(city)
        if "error" in data:
            st.error(f"❌ {data['error']}")
        else:
            st.success(f"📍 Weather in {data['city']}")
            st.write(f"🌡 Temperature: {data['temp']} °C")
            st.write(f"💧 Humidity: {data['humidity']}%")
            st.write(f"☁ Condition: {data['desc']}")
