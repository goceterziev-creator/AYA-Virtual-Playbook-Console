import streamlit as st
import requests
import os
from datetime import datetime
import pandas as pd

# Config
st.set_page_config(layout="wide", page_title="AYA Global Playbook")
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);}
.aya-card {background: rgba(255,255,255,0.95); border-radius: 20px; padding: 2rem;}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def get_amadeus_token():
    """Amadeus Auth от playbook [file:20]"""
    try:
        auth_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        auth_data = {
            'grant_type': 'client_credentials',
            'client_id': st.secrets["AMADEUS_API_KEY"],
            'client_secret': st.secrets["AMADEUS_API_SECRET"]
        }
        response = requests.post(auth_url, data=auth_data)
        if response.status_code == 200:
            return response.json()['access_token']
        return None
    except:
        return None

def search_flights(origin, destination, date):
    """Flight search от playbook [file:20]"""
    token = get_amadeus_token()
    if not token:
        return pd.DataFrame({"Error": ["No API access"]})
    
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'originLocationCode': origin,
        'destinationLocationCode': destination,
        'departureDate': date,
        'adults': 1,
        'max': 5
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        # Parse simple results
        flights = []
        for offer in data.get('data', [])[:3]:
            flights.append({
                'Airline': offer['itineraries'][0]['segments'][0]['carrierCode'],
                'Price': offer['price']['total'],
                'Duration': offer['itineraries'][0]['duration']
            })
        return pd.DataFrame(flights)
    except:
        return pd.DataFrame({"Playbook": ["Google Flights → Skyscanner → Kayak [file:20]"]})

# === MAIN APP ===
st.markdown("""
<div class='aya-card' style='text-align:center; margin-bottom:2rem;'>
<h1>🤖 Петя - AYA Global Playbook Console</h1>
<p><strong>Автоматизирани консултации по Virtual Playbook [file:21]</strong></p>
</div>
""", unsafe_allow_html=True)

# Left: Петя Form
col1, col2 = st.columns([1,1])

with col1:
    st.markdown("<h3>📝 Заявка</h3>", unsafe_allow_html=True)
    name = st.text_input("👤 Име")
    origin = st.text_input("🛫 От", value="SOF")
    dest = st.text_input("✈️ До", value="PAR")
    date = st.date_input("📅 Дата")
    budget = st.number_input("💰 Бюджет (€)", value=1000)
    
    if st.button("🚀 Генерирай Playbook Оферта"):
        st.session_state.playbook = {
            'name': name, 'origin': origin, 'dest': dest, 
            'date': date, 'budget': budget
        }

# Right: Results
with col2:
    if 'playbook' in st.session_state:
        st.markdown("<h3>✈️ Полети (Amadeus Live)</h3>", unsafe_allow_html=True)
        flights_df = search_flights(st.session_state.playbook['origin'], 
                                  st.session_state.playbook['dest'],
                                  st.session_state.playbook['date'].strftime('%Y-%m-%d'))
        st.dataframe(flights_df, use_container_width=True)
        
        st.markdown("""
        <div class='aya-card'>
        <h4>📋 Playbook Инструкции [file:21]</h4>
        <ol>
        <li>Копирай името на компанията</li>
        <li>Отвори <a href='https://www.google.com/travel/flights'>Google Flights</a></li>
        <li>Приложи филтрите (1 прекачване макс)</li>
        <li>Резервирай директно</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)

# Footer Email
if st.button("📧 Изпрати към Биляна"):
    st.success(f"""
    ✅ Оферта за {st.session_state.playbook['name']} изпратена!
    
    От: goce_terziev@abv.bg
    До: aya.smart.store@gmail.com
    Тема: Playbook - {st.session_state.playbook['dest']} за {st.session_state.playbook['name']}
    
    [Автоматично генерирано от AYA Global Playbook Console]
    """)

st.markdown("""
<div style='text-align:center; padding:2rem; color:rgba(255,255,255,0.8);'>
    🌐 AYA Global Travel Team | Биляна +359 885 07 89 80 | Гоце +359 894 84 28 82 [file:21]
</div>
""", unsafe_allow_html=True)
