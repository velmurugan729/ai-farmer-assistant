import streamlit as st
import requests
import json
import base64
import google.generativeai as genai
from firebase_admin import credentials, initialize_app, firestore, auth
from datetime import datetime

# ================== Firebase Configuration ==================
# IMPORTANT: Follow these steps to set up Firebase for your project:
# 1. Create a Firebase project in the Firebase console.
# 2. Go to Project settings > Service accounts > Generate new private key.
# 3. Download the JSON file and save it in your project directory.
# 4. Rename the file to 'firebase-adminsdk.json'.
# 5. This file contains your credentials and should NEVER be committed to a public repository.
#
# IMPORTANT: To run on Streamlit Cloud, you must configure your Firebase
# secrets in the 'Advanced settings' of your app. This code assumes you're
# running locally with the JSON file present.

try:
    if not initialize_app._apps:
        cred = credentials.Certificate("firebase-adminsdk.json")
        initialize_app(cred)
except Exception as e:
    st.error(f"Firebase Initialization Failed: {e}. Please ensure 'firebase-adminsdk.json' is in your project directory.")
    st.stop()

# Initialize Firestore and Auth clients
db = firestore.client()
auth_client = auth.Client()

# Set initial user state
if 'user' not in st.session_state:
    try:
        user_record = auth_client.sign_in_anonymously()
        st.session_state.user = {'uid': user_record.uid}
    except Exception as e:
        st.error(f"Anonymous sign-in failed: {e}")
        st.stop()

# ================== API Key Configuration ==================
# You can get your API keys from Google AI Studio and OpenWeatherMap.
# For Streamlit Cloud, you would store these in a secrets.toml file.
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"

# ================== Gemini API Configuration ==================
genai.configure(api_key=GEMINI_API_KEY)
model_vision = genai.GenerativeModel('gemini-1.5-flash-preview-05-20')
model_chat = genai.GenerativeModel('gemini-1.5-flash-preview-05-20',
    system_instruction="You are a helpful and knowledgeable agricultural assistant. Answer questions about farming, crops, weather, and government policies in a clear, concise, and friendly manner."
)
# Start a persistent chat session
if 'chat_session' not in st.session_state:
    st.session_state.chat_session = model_chat.start_chat(history=[])

# ================== Translations and Mock Data ==================
translations = {
    "en": {
        "title": "Farmer's Assistant",
        "login": "Login",
        "logout": "Logout",
        "dashboard": "Dashboard",
        "diseasePrediction": "Disease Prediction",
        "marketPrice": "Market Price",
        "weather": "Weather Info",
        "profitCalculator": "Profit Calculator",
        "chatbot": "AI Chatbot",
        "subsidies": "Government Subsidies",
        "reminders": "Reminders",
        "forum": "Farmer's Forum",
        "welcome": "Welcome, Farmer!",
        "loginDesc": "You are not logged in. Please log in to access the app.",
        "searchPrice": "Search Price",
        "noInput": "Please enter values for all fields.",
        "uploadImage": "Upload an image of your crop to predict any disease.",
        "predicting": "Analyzing image...",
        "predictionResult": "Prediction Result",
        "diseaseName": "Diagnosis",
        "suggestions": "Suggestions",
        "marketTitle": "Real-time Crop Market Price",
        "selectCrop": "Enter Crop Name",
        "selectCity": "Enter City Name",
        "noMarketData": "No market data found. Try a different crop or city.",
        "weatherTitle": "Weather Information",
        "weatherLocation": "Enter a Location",
        "getWeather": "Get Weather",
        "addReminder": "Add New Reminder",
        "reminderPlaceholder": "e.g., Fertilize tomatoes on August 15th",
        "saveReminder": "Save Reminder",
        "noReminders": "No reminders found.",
        "askQuestion": "Ask a Question or Share a Tip",
        "yourMessage": "Your message...",
        "post": "Post",
        "noPosts": "No posts yet. Be the first to post!",
        "chatbotDesc": "Ask me questions about farming, weather, and more.",
        "chatPlaceholder": "Type your message here...",
        "send": "Send",
        "chatLoading": "Thinking...",
        "emptyChat": "Start a conversation to get started!",
        "chatWelcome": "Hello! I am your AI assistant. How can I help you today?",
    },
    "ta": {
        "title": "விவசாயியின் உதவியாளர்",
        "login": "உள்நுழைவு",
        "logout": "வெளியேறு",
        "dashboard": "கட்டுப்பாட்டுப் பலகம்",
        "diseasePrediction": "நோய் கண்டறிதல்",
        "marketPrice": "சந்தை விலை",
        "weather": "வானிலை தகவல்",
        "profitCalculator": "லாப கால்குலேட்டர்",
        "chatbot": "AI சாட்பாட்",
        "subsidies": "அரசு மானியங்கள்",
        "reminders": "நினைவூட்டல்கள்",
        "forum": "விவசாயிகள் மன்றம்",
        "welcome": "வரவேற்பு, விவசாயி!",
        "loginDesc": "நீங்கள் உள்நுழையவில்லை. பயன்பாட்டை அணுக உள்நுழையவும்.",
        "searchPrice": "விலையைத் தேடு",
        "noInput": "அனைத்து புலங்களுக்கும் மதிப்புகளை உள்ளிடவும்.",
        "uploadImage": "உங்கள் பயிரின் படத்தை பதிவேற்றி, நோயைக் கண்டறியலாம்.",
        "predicting": "படத்தை ஆய்வு செய்கிறது...",
        "predictionResult": "கணிப்பு முடிவு",
        "diseaseName": "கண்டறிதல்",
        "suggestions": "பரிந்துரைகள்",
        "marketTitle": "உண்மையான நேர பயிர் சந்தை விலை",
        "selectCrop": "பயிரின் பெயரை உள்ளிடவும்",
        "selectCity": "நகரத்தின் பெயரை உள்ளிடவும்.",
        "noMarketData": "சந்தை தரவு எதுவும் இல்லை. வேறு பயிர் அல்லது நகரத்தை முயற்சிக்கவும்.",
        "weatherTitle": "வானிலை தகவல்",
        "weatherLocation": "ஒரு இடத்தை உள்ளிடவும்",
        "getWeather": "வானிலை பெறு",
        "addReminder": "புதிய நினைவூட்டலைச் சேர்",
        "reminderPlaceholder": "உதாரணமாக, ஆகஸ்ட் 15 அன்று தக்காளிக்கு உரம் இடுங்கள்",
        "saveReminder": "நினைவூட்டலைச் சேமி",
        "noReminders": "நினைவூட்டல்கள் எதுவும் இல்லை.",
        "askQuestion": "கேள்வி கேட்கவும் அல்லது குறிப்புகளைப் பகிரவும்",
        "yourMessage": "உங்கள் செய்தி...",
        "post": "பதிவிடு",
        "noPosts": "இன்னும் பதிவுகள் இல்லை. முதலில் பதிவிடுங்கள்!",
        "chatbotDesc": "விவசாயம், வானிலை மற்றும் பலவற்றைப் பற்றி என்னிடம் கேளுங்கள்.",
        "chatPlaceholder": "உங்கள் செய்தியை இங்கே தட்டச்சு செய்யவும்...",
        "send": "அனுப்பு",
        "chatLoading": "சிந்தித்துக்கொண்டிருக்கிறது...",
        "emptyChat": "உரையாடலைத் தொடங்கவும்!",
        "chatWelcome": "வணக்கம்! நான் உங்கள் AI உதவியாளர். நான் இன்று எப்படி உதவ முடியும்?",
    }
}
subsidies_data = [
    {"name": "Pradhan Mantri Fasal Bima Yojana", "url": "https://pmfby.gov.in/", "description": "Crop insurance scheme for farmers to provide financial support in case of crop loss."},
    {"name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)", "url": "https://pmkisan.gov.in/", "description": "Provides income support to eligible landholding farmer families."},
]
mock_weather = {
    'chennai': {'temp': '30°C', 'condition': 'Partly Cloudy', 'humidity': '75%'},
    'coimbatore': {'temp': '25°C', 'condition': 'Sunny', 'humidity': '60%'},
}
expert_numbers = [
    {"name": "State Agriculture Department", "number": "1800-123-4567"},
]

# Set initial state
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [{"sender": "bot", "text": translations[st.session_state.language]["chatWelcome"]}]

# --- Functions ---
def get_translation():
    return translations[st.session_state.language]

def set_page(page_name):
    st.session_state.page = page_name

def handle_login():
    try:
        # Sign in anonymously as a demonstration
        user_record = auth_client.sign_in_anonymously()
        st.session_state.user = {'uid': user_record.uid}
        set_page('dashboard')
    except Exception as e:
        st.error(f"Login failed: {e}")

def handle_logout():
    st.session_state.user = None
    set_page('login')

def add_reminder(new_reminder):
    if st.session_state.user and new_reminder:
        db.collection(f"users/{st.session_state.user['uid']}/reminders").add({
            "text": new_reminder,
            "timestamp": datetime.now()
        })
        st.success("Reminder added!")
    else:
        st.error("Please log in and enter a reminder.")

def post_to_forum(new_post):
    if st.session_state.user and new_post:
        db.collection("forum_posts").add({
            "userId": st.session_state.user['uid'],
            "text": new_post,
            "timestamp": datetime.now()
        })
        st.success("Post submitted!")
    else:
        st.error("Please log in and enter a message.")

def handle_predict_disease(uploaded_file):
    if uploaded_file:
        with st.spinner("Analyzing image..."):
            encoded_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
            response = model_vision.generate_content([
                "Analyze this crop image and provide a diagnosis and treatment plan. Respond in Tamil.",
                {"mime_type": uploaded_file.type, "data": encoded_image}
            ])
            st.session_state.disease_prediction = response.text.strip()
            
def handle_get_market_price(crop_name, city_name):
    with st.spinner("Searching..."):
        try:
            prompt = f"Find the latest market price of {crop_name} in {city_name} in Indian Rupees. Provide the source URL. Response in Tamil."
            response = genai.GenerativeModel(
                'gemini-1.5-flash-preview-05-20',
                tools=[genai.Tool.from_google_search()]
            ).generate_content(prompt)
            st.session_state.market_price = response.text.strip()
        except Exception as e:
            st.session_state.market_price = f"Failed to fetch market data: {e}. No market data found."

def handle_chatbot_message(prompt):
    st.session_state.chat_messages.append({"sender": "user", "text": prompt})
    with st.spinner("Thinking..."):
        try:
            response = st.session_state.chat_session.send_message(prompt, stream=True)
            response_text = ""
            for chunk in response:
                response_text += chunk.text
            st.session_state.chat_messages.append({"sender": "bot", "text": response_text})
        except Exception as e:
            st.error(f"An error occurred: {e}")

# --- UI Layout ---
t = get_translation()
st.set_page_config(layout="wide", page_title=t["title"])
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    </style>
    <script src="https://cdn.tailwindcss.com"></script>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title(t["title"])
    if st.button(t['language'] if st.session_state.language == 'en' else 'English'):
        st.session_state.language = 'ta' if st.session_state.language == 'en' else 'en'
        st.experimental_rerun()

    if st.session_state.user:
        st.write(f"Logged in as: {st.session_state.user['uid'][:8]}...")
        if st.button(t['dashboard'], use_container_width=True):
            set_page('dashboard')
        if st.button(t['diseasePrediction'], use_container_width=True):
            set_page('diseasePrediction')
        if st.button(t['marketPrice'], use_container_width=True):
            set_page('marketPrice')
        if st.button(t['weather'], use_container_width=True):
            set_page('weather')
        if st.button(t['profitCalculator'], use_container_width=True):
            set_page('profitCalculator')
        if st.button(t['chatbot'], use_container_width=True):
            set_page('chatbot')
        if st.button(t['subsidies'], use_container_width=True):
            set_page('subsidies')
        if st.button(t['reminders'], use_container_width=True):
            set_page('reminders')
        if st.button(t['forum'], use_container_width=True):
            set_page('forum')
        st.markdown("---")
        if st.button(t['logout'], use_container_width=True):
            handle_logout()
    else:
        st.warning(t['loginDesc'])
        if st.button(t['login'], use_container_width=True):
            handle_login()

# Main Content
if st.session_state.page == 'login':
    st.header(t['title'])
    st.info(t['loginDesc'])
elif st.session_state.page == 'dashboard':
    st.header(t['dashboard'])
    st.success(t['welcome'])
    st.write("Dashboard content goes here.")

elif st.session_state.page == 'diseasePrediction':
    st.header(t['diseasePrediction'])
    st.write(t['uploadImage'])
    uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
        handle_predict_disease(uploaded_file)
        if 'disease_prediction' in st.session_state:
            st.subheader(t['predictionResult'])
            st.write(st.session_state.disease_prediction)

elif st.session_state.page == 'marketPrice':
    st.header(t['marketPrice'])
    crop_name = st.text_input(t['selectCrop'], key="crop_input")
    city_name = st.text_input(t['selectCity'], key="city_input")
    
    if st.button(t['searchPrice']):
        handle_get_market_price(crop_name, city_name)
    
    if 'market_price' in st.session_state:
        st.write(st.session_state.market_price)

elif st.session_state.page == 'weather':
    st.header(t['weather'])
    location = st.text_input(t['weatherLocation'])
    if st.button(t['getWeather']):
        if location.lower() in mock_weather:
            data = mock_weather[location.lower()]
            st.write(f"**Temperature:** {data['temp']}")
            st.write(f"**Condition:** {data['condition']}")
            st.write(f"**Humidity:** {data['humidity']}")
        else:
            st.error("Weather data not available for this location.")

elif st.session_state.page == 'profitCalculator':
    st.header(t['profitCalculator'])
    yield_val = st.number_input(t['yield'], min_value=0)
    cost_val = st.number_input(t['cost'], min_value=0)
    selling_price_val = st.number_input(t['sellingPrice'], min_value=0)
    
    if st.button(t['calculate']):
        if yield_val > 0 and cost_val > 0 and selling_price_val > 0:
            total_revenue = yield_val * selling_price_val
            profit = total_revenue - cost_val
            st.success(f"**{t['profit']}:** ₹{profit}")
        else:
            st.error(t['noInput'])

elif st.session_state.page == 'chatbot':
    st.header(t['chatbot'])
    st.write(t['chatbotDesc'])
    
    chat_container = st.container()
    
    for msg in st.session_state.chat_messages:
        with chat_container:
            with st.chat_message(msg["sender"]):
                st.markdown(msg["text"])
    
    prompt = st.chat_input(t["chatPlaceholder"])
    
    if prompt:
        handle_chatbot_message(prompt)
        st.experimental_rerun()

elif st.session_state.page == 'subsidies':
    st.header(t['subsidies'])
    for subsidy in subsidies_data:
        st.markdown(f"**[{subsidy['name']}]({subsidy['url']})**")
        st.write(subsidy['description'])

elif st.session_state.page == 'reminders':
    st.header(t['reminders'])
    new_reminder = st.text_input(t['reminderPlaceholder'])
    if st.button(t['addReminder']):
        add_reminder(new_reminder)
            
    reminders_ref = db.collection(f"users/{st.session_state.user['uid']}/reminders")
    reminders = reminders_ref.order_by("timestamp").stream()
    
    st.subheader("Your Reminders")
    reminders_found = False
    for reminder in reminders:
        reminders_found = True
        doc_data = reminder.to_dict()
        st.write(f"- {doc_data['text']}")
    if not reminders_found:
        st.info(t['noReminders'])

elif st.session_state.page == 'forum':
    st.header(t['forum'])
    st.write(f"Your ID: `{st.session_state.user['uid'][:8]}...`")
    
    new_post = st.text_area(t['yourMessage'])
    if st.button(t['post']):
        post_to_forum(new_post)

    st.subheader("Community Posts")
    posts_ref = db.collection("forum_posts")
    posts = posts_ref.order_by("timestamp", direction="DESCENDING").limit(20).stream()

    posts_found = False
    for post in posts:
        posts_found = True
        doc_data = post.to_dict()
        st.markdown(f"**User:** `{doc_data['userId'][:8]}...`")
        st.write(doc_data['text'])
        st.write("---")
    
    if not posts_found:
        st.info(t['noPosts'])
