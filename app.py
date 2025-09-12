import streamlit as st
from openai import OpenAI
import json
import os
import random
import requests
from datetime import datetime, timedelta

# ================== API CONFIG ==================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_OPENWEATHER_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# ================== DATA ==================
market_prices = {
    "Rice": {"price": 4000, "unit": "quintal"},
    "Wheat": {"price": 2800, "unit": "quintal"},
    "Tomato": {"price": 2000, "unit": "quintal"},
    "Cotton": {"price": 6500, "unit": "quintal"}
}

subsidies = {
  "PM-KISAN": {
    "description": "₹6,000 per year to eligible farmer families in 3 installments.",
    "link": "https://pmkisan.gov.in/"
  },
  "Fasal Bima Yojana": {
    "description": "Crop insurance against drought, floods, pests, etc.",
    "link": "https://pmfby.gov.in/"
  },
  "Soil Health Card": {
    "description": "Provides soil nutrient status and fertilizer recommendations.",
    "link": "https://soilhealth.dac.gov.in/"
  },
  "Krishi Sinchai Yojana": {
    "description": "Water-use efficiency with subsidies for drip/sprinkler irrigation.",
    "link": "https://pmksy.gov.in/microirrigation/index.aspx"
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

# ================== WEATHER HELPER ==================
def get_weather(city):
    if OPENWEATHER_API_KEY.startswith("YOUR_"):
        return {"error": "❌ Please set your OpenWeather API key."}
    try:
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
    except Exception as e:
        return {"error": str(e)}

def get_water_advice(weather_data):
    if "error" in weather_data:
        return weather_data["error"]
    desc = weather_data['desc'].lower()
    if 'rain' in desc: return "🌧️ Rain expected: No need to water."
    if 'thunder' in desc: return "⛈️ Storm alert: Postpone irrigation."
    if 'cloud' in desc: return "☁️ Cloudy: Reduce water slightly."
    if 'sun' in desc or 'clear' in desc: return "☀️ Sunny: Water as scheduled."
    return "💧 Normal: Continue usual watering."

# ================== AI HELPER ==================
def create_knowledge_base():
    persona = (
        "You are the 'AI Farmer Assistant', a friendly and concise expert for farmers. "
        "Provide crop prices, subsidies, helplines, and advice only from the given data."
    )
    current_date = datetime.now().strftime("%B %d, %Y")
    current_location = "Chennai, Tamil Nadu"
    knowledge_base = f"""
    {persona}

    Date: {current_date}, Location: {current_location}.

    Market Prices (per quintal): {json.dumps(market_prices)}
    Subsidies: {json.dumps(subsidies)}
    Helplines: {json.dumps(helplines)}

    Rules:
    - Only use provided data.
    - If info not available, say you don't have it.
    - Be clear and encouraging.
    """
    return knowledge_base

def get_ai_response_openai(user_query):
    try:
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "system", "content": create_knowledge_base()}
            ]
        st.session_state.messages.append({"role": "user", "content": user_query})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages,
            temperature=0.6,
            max_tokens=300
        )

        reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        return f"⚠️ AI Error: {e}"

# ================== STREAMLIT APP ==================
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
    uploaded = st.file_uploader("Upload crop image", type=["jpg", "png"])
    if uploaded:
        st.image(uploaded, caption="Uploaded Crop Image", use_column_width=True)
        prediction = random.choice(diseases)
        st.success(f"**Prediction:** {prediction['name']}")
        st.info(f"**Advice:** {prediction['advice']}")

# --- Market Prices ---
with tab2:
    st.header("📊 Check Market Prices")
    crop = st.selectbox("Select Crop", list(market_prices.keys()))
    if st.button("Get Price"):
        price = market_prices[crop]['price']
        st.success(f"💰 {crop}: ₹{price}/quintal")

# --- Subsidy Info ---
with tab3:
    st.header("🏛 Government Subsidy Info")
    scheme = st.selectbox("Select Scheme", list(subsidies.keys()))
    if st.button("Get Info"):
        st.info(subsidies[scheme]['description'])
        st.markdown(f"[Learn more]({subsidies[scheme]['link']})")

# --- Reminders ---
with tab4:
    st.header("⏰ Set Reminders")
    task = st.text_input("Enter task")
    days = st.slider("Remind me in (days)", 1, 30, 7)
    if st.button("Set Reminder"):
        if task:
            remind_date = datetime.now() + timedelta(days=days)
            st.session_state.setdefault("reminders", []).append((task, remind_date))
            st.success(f"✅ Reminder set for {task} on {remind_date:%d-%m-%Y}")
    if st.session_state.get("reminders"):
        st.subheader("📌 Your Reminders")
        for task, date in st.session_state.reminders:
            st.write(f"- {task} on {date:%d-%m-%Y}")

# --- Forum ---
with tab5:
    st.header("💬 Farmer Forum")
    new_msg = st.text_input("Share a message")
    if st.button("Post"):
        if new_msg:
            st.session_state.setdefault("forum_messages", []).append(new_msg)
            st.success("✅ Posted!")
    if st.session_state.get("forum_messages"):
        st.subheader("Community Messages")
        for i, msg in enumerate(reversed(st.session_state.forum_messages), 1):
            st.write(f"{i}. {msg}")

# --- Expert ---
with tab6:
    st.header("📞 Call an Expert")
    crop_expert = st.selectbox("Select Crop", list(helplines.keys()))
    if st.button("Get Helpline"):
        st.success(f"📞 {helplines[crop_expert]}")
        st.markdown(f"[📲 Call Now](tel:{helplines[crop_expert]})")

# --- Weather ---
with tab7:
    st.header("🌦 Weather Info")
    city = st.text_input("Enter city / village")
    if st.button("Get Weather"):
        if not city:
            st.warning("Please enter a city")
        else:
            data = get_weather(city)
            if "error" in data:
                st.error(f"❌ {data['error']}")
            else:
                st.success(f"📍 {data['city']}")
                st.write(f"🌡 {data['temp']} °C")
                st.write(f"💧 {data['humidity']}%")
                st.write(f"☁ {data['desc']}")

# --- Profit Calc ---
with tab8:
    st.header("📈 Profit Calculator")
    crop = st.selectbox("Select Crop", list(market_prices.keys()))
    land = st.number_input("Land Size (acres)", min_value=0.1, value=1.0)
    cost_inputs = st.number_input("Cost of Inputs per acre (₹)", min_value=0, value=2500)
    yield_est = st.number_input("Yield (quintals per acre)", min_value=0.1, value=10.0)
    if st.button("Calculate"):
        try:
            price = market_prices[crop]['price']
            total_cost = land * cost_inputs
            total_revenue = land * yield_est * price
            net_profit = total_revenue - total_cost
            st.success(f"**{crop}** Profit Estimation")
            st.info(f"💰 Revenue: ₹{total_revenue:,.2f}")
            st.warning(f"💸 Cost: ₹{total_cost:,.2f}")
            st.metric("📈 Net Profit", f"₹{net_profit:,.2f}")
        except Exception as e:
            st.error(f"Error: {e}")

# --- Water Advice ---
with tab9:
    st.header("💧 Water Advice")
    city_water = st.text_input("Enter city / village (for weather)")
    if st.button("Get Advice"):
        if not city_water:
            st.warning("Enter a city name")
        else:
            data = get_weather(city_water)
            st.info(get_water_advice(data))

# --- AI Assistant ---
with tab_gen_ai:
    st.header("🧠 Ask AI Assistant")
    query = st.text_input("Ask your question")
    if st.button("Ask"):
        if query:
            st.write(get_ai_response_openai(query))
