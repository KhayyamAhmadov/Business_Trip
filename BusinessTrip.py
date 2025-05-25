import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from io import BytesIO
import requests
import xml.etree.ElementTree as ET
import os
from bs4 import BeautifulSoup
import plotly 
import openpyxl


# 1. İLK STREAMLIT ƏMRİ OLMALIDIR!
st.set_page_config(
    page_title="Ezamiyyət İdarəetmə Sistemi",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. GİRİŞ MƏNTİQİ
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Giriş üçün CSS
st.markdown("""
<style>
    .login-box {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 15px;
        box-shadow: 0 0 20px rgba(0,0,0,0.1);
        max-width: 500px;
        margin: 5rem auto;
    }
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-box .stTextInput {
        width: 30%;
        margin: 0 auto;
    }
    .stTextInput input {
        background-color: rgba(255,255,255,0.2)!important;
        color: white!important;
        border: 1px solid rgba(255,255,255,0.3)!important;
        border-radius: 8px!important;
        padding: 8px 12px!important;
        font-size: 14px!important;
    }
    .stTextInput input::placeholder {
        color: rgba(255,255,255,0.7)!important;
    }
</style>
""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    with st.container():
        st.markdown('<div class="login-box"><div class="login-header"><h2>🔐 Sistemə Giriş</h2></div>', unsafe_allow_html=True)
        
        access_code = st.text_input("Giriş kodu", type="password", 
                                  label_visibility="collapsed", 
                                  placeholder="Giriş kodunu daxil edin...")
        
        cols = st.columns([1,2,1])
        with cols[1]:
            if st.button("Daxil ol", use_container_width=True):
                if access_code == "admin":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Yanlış giriş kodu!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 3. ƏSAS TƏRTİBAT VƏ PROQRAM MƏNTİQİ
st.markdown("""
<style>
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --background-color: #ffffff;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-radius: 0 0 20px 20px;
    }
    
    .section-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white!important;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: none;
    }
    
    .stButton>button {
        border-radius: 8px!important;
        padding: 0.5rem 1.5rem!important;
        transition: all 0.3s ease!important;
        border: 1px solid var(--primary-color)!important;
        background: var(--secondary-color)!important;
        color: white!important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(99,102,241,0.3)!important;
        background: var(--primary-color)!important;
    }
    
    .dataframe {
        border-radius: 12px!important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05)!important;
    }
</style>
""", unsafe_allow_html=True)

# ============================== SABİTLƏR ==============================
DEPARTMENTS = [
    "Statistika işlərinin əlaqələndirilməsi və strateji planlaşdırma şöbəsi",
    "Keyfiyyətin idarə edilməsi və metaməlumatlar şöbəsi",
    "Milli hesablar və makroiqtisadi göstəricilər statistikası şöbəsi",
    "Kənd təsərrüfatı statistikası şöbəsi",
    "Sənaye və tikinti statistikası şöbəsi",
    "Energetika və ətraf mühit statistikası şöbəsi",
    "Ticarət statistikası şöbəsi",
    "Sosial statistika şöbəsi",
    "Xidmət statistikası şöbəsi",
    "Əmək statistikası şöbəsi",
    "Qiymət statistikası şöbəsi",
    "Əhali statistikası şöbəsi",
    "Həyat keyfiyyətinin statistikası şöbəsi",
    "Dayanıqlı inkişaf statistikası şöbəsi",
    "İnformasiya texnologiyaları şöbəsi",
    "İnformasiya və ictimaiyyətlə əlaqələr şöbəsi",
    "Beynəlxalq əlaqələr şöbəsi",
    "İnsan resursları və hüquq şöbəsi",
    "Maliyyə və təsərrüfat şöbəsi",
    "Ümumi şöbə",
    "Rejim və məxfi kargüzarlıq şöbəsi",
    "Elmi - Tədqiqat və Statistik İnnovasiyalar Mərkəzi",
    "Yerli statistika orqanları"
]

CITIES = [
    "Abşeron", "Ağcabədi", "Ağdam", "Ağdaş", "Ağdərə", "Ağstafa", "Ağsu", "Astara", "Bakı",
    "Babək (Naxçıvan MR)", "Balakən", "Bərdə", "Beyləqan", "Biləsuvar", "Cəbrayıl", "Cəlilabad",
    "Culfa (Naxçıvan MR)", "Daşkəsən", "Füzuli", "Gədəbəy", "Gəncə", "Goranboy", "Göyçay",
    "Göygöl", "Hacıqabul", "Xaçmaz", "Xankəndi", "Xızı", "Xocalı", "Xocavənd", "İmişli",
    "İsmayıllı", "Kəlbəcər", "Kəngərli (Naxçıvan MR)", "Kürdəmir", "Laçın", "Lənkəran",
    "Lerik", "Masallı", "Mingəçevir", "Naftalan", "Neftçala", "Naxçıvan", "Oğuz", "Siyəzən",
    "Ordubad (Naxçıvan MR)", "Qəbələ", "Qax", "Qazax", "Qobustan", "Quba", "Qubadlı",
    "Qusar", "Saatlı", "Sabirabad", "Sədərək (Naxçıvan MR)", "Salyan", "Samux", "Şabran",
    "Şahbuz (Naxçıvan MR)", "Şamaxı", "Şəki", "Şəmkir", "Şərur (Naxçıvan MR)", "Şirvan",
    "Şuşa", "Sumqayıt", "Tərtər", "Tovuz", "Ucar", "Yardımlı", "Yevlax", "Zaqatala",
    "Zəngilan", "Zərdab", "Nabran", "Xudat"
]

# COUNTRIES = {
#     "Türkiyə": 300,
#     "Gürcüstan": 250,
#     "Almaniya": 600,
#     "BƏƏ": 500,
#     "Rusiya": 400,
#     "İran": 280,
#     "İtaliya": 550,
#     "Fransa": 580,
#     "İngiltərə": 620,
#     "ABŞ": 650
# }

# COUNTRY_CITIES = {
#     "Türkiyə": ["İstanbul", "Ankara", "İzmir", "Antalya", "Bursa", "Digər"],
#     "Gürcüstan": ["Tbilisi", "Batumi", "Kutaisi", "Zugdidi", "Digər"],
#     "Almaniya": ["Berlin", "Münhen", "Frankfurt", "Hamburg", "Digər"],
#     "BƏƏ": ["Dubai", "Abu Dabi", "Şarqah", "Əcman", "Digər"],
#     "Rusiya": ["Moskva", "Sankt-Peterburq", "Kazan", "Soçi", "Digər"],
#     "İran": ["Təbriz", "Tehran", "İsfahan", "Məşhəd", "Digər"],
#     "İtaliya": ["Roma", "Milan", "Venesiya", "Florensiya", "Digər"],
#     "Fransa": ["Paris", "Marsel", "Lion", "Nitsa", "Digər"],
#     "İngiltərə": ["London", "Manchester", "Birmingem", "Liverpul", "Digər"],
#     "ABŞ": ["Nyu York", "Los Anceles", "Çikaqo", "Mayami", "Digər"]
# }

COUNTRIES = {
    "Türkiyə": {
        "currency": "TRY",
        "cities": {
            "İstanbul": {"allowance": 300, "currency": "TRY"},
            "Ankara": {"allowance": 280, "currency": "TRY"}
        }
    },
    "Almaniya": {
        "currency": "EUR",
        "cities": {
            "Berlin": {"allowance": 600, "currency": "EUR"},
            "Frankfurt": {"allowance": 650, "currency": "EUR"}
        }
    }
}


DOMESTIC_ROUTES = {
    ("Bakı", "Ağcabədi"): 10.50,
    ("Bakı", "Ağdam"): 13.50,
    ("Bakı", "Ağdaş"): 10.30,
    ("Bakı", "Astara"): 10.40,
    ("Bakı", "Şuşa"): 28.90,
    ("Bakı", "Balakən"): 17.30,
    ("Bakı", "Beyləqan"): 10.00,
    ("Bakı", "Bərdə"): 11.60,
    ("Bakı", "Biləsuvar"): 6.50,
    ("Bakı", "Cəlilabad"): 7.10,
    ("Bakı", "Füzuli"): 10.80,
    ("Bakı", "Gədəbəy"): 16.50,
    ("Bakı", "Gəncə"): 13.10,
    ("Bakı", "Goranboy"): 9.40,
    ("Bakı", "Göyçay"): 9.20,
    ("Bakı", "Göygöl"): 13.50,
    ("Bakı", "İmişli"): 8.10,
    ("Bakı", "İsmayıllı"): 7.00,
    ("Bakı", "Kürdəmir"): 7.10,
    ("Bakı", "Lənkəran"): 8.80,
    ("Bakı", "Masallı"): 7.90,
    ("Bakı", "Mingəçevir"): 11.40,
    ("Bakı", "Naftalan"): 12.20,
    ("Bakı", "Oğuz"): 13.10,
    ("Bakı", "Qax"): 14.60,
    ("Bakı", "Qazax"): 17.60,
    ("Bakı", "Qəbələ"): 11.50,
    ("Bakı", "Quba"): 5.90,
    ("Bakı", "Qusar"): 6.40,
    ("Bakı", "Saatlı"): 7.10,
    ("Bakı", "Sabirabad"): 6.10,
    ("Bakı", "Şəki"): 13.20,
    ("Bakı", "Şəmkir"): 15.00,
    ("Bakı", "Siyəzən"): 3.60,
    ("Bakı", "Tərtər"): 12.20,
    ("Bakı", "Tovuz"): 16.40,
    ("Bakı", "Ucar"): 8.90,
    ("Bakı", "Xaçmaz"): 5.50,
    ("Bakı", "Nabran"): 7.20,
    ("Bakı", "Xudat"): 6.30,
    ("Bakı", "Zaqatala"): 15.60,
    ("Bakı", "Zərdab"): 9.30
}

DOMESTIC_ALLOWANCES = {
    "Bakı": 125,
    "Naxçıvan": 100,
    "Gəncə": 95,
    "Sumqayıt": 95,
    "Digər": 90
}

# currency_rates.xlsx faylı üçün nümunə məlumatlar
CURRENCY_RATES = {
    "USD": 1.7,
    "EUR": 1.9,
    "TRY": 0.2,
    "RUB": 0.02,
    "GEL": 0.7
}



# ============================== FUNKSİYALAR ==============================
def load_trip_data():
    try:
        return pd.read_excel("ezamiyyet_melumatlari.xlsx")
    except FileNotFoundError:
        return pd.DataFrame()

def calculate_domestic_amount(from_city, to_city):
    return DOMESTIC_ROUTES.get((from_city, to_city), 70)

def calculate_days(start_date, end_date):
    return (end_date - start_date).days + 1

def calculate_total_amount(daily_allowance, days, payment_type, ticket_price=0):
    return (daily_allowance * days + ticket_price) * PAYMENT_TYPES[payment_type]

def save_trip_data(data):
    try:
        df_new = pd.DataFrame([data])
        try:
            df_existing = pd.read_excel("ezamiyyet_melumatlari.xlsx")
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        except FileNotFoundError:
            df_combined = df_new
        df_combined.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
        return True
    except Exception as e:
        st.error(f"Xəta: {str(e)}")
        return False

def load_domestic_allowances():
    try:
        df = pd.read_excel("domestic_allowances.xlsx")
        return df.set_index('Şəhər')['Müavinət'].to_dict()
    except FileNotFoundError:
        df = pd.DataFrame({
            'Şəhər': ['Bakı', 'Naxçıvan', 'Gəncə', 'Sumqayıt', 'Digər'],
            'Müavinət': [125, 100, 95, 95, 90]
        })
        df.to_excel("domestic_allowances.xlsx", index=False)
        return df.set_index('Şəhər')['Müavinət'].to_dict()

def save_domestic_allowances(data):
    df = pd.DataFrame({
        'Şəhər': data.keys(),
        'Müavinət': data.values()
    })
    df.to_excel("domestic_allowances.xlsx", index=False)

def scrape_currency_rates():
    try:
        url = "https://www.cbar.az/currency/rates"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        currencies = {}
        table = soup.find('table', {'class': 'table'})
        for row in table.find_all('tr')[1:]:  # Başlığı atlayaq
            cols = row.find_all('td')
            if len(cols) >= 3:
                code = cols[1].text.strip()
                rate = float(cols[2].text.strip())
                currencies[code] = rate
        return currencies
    except Exception as e:
        st.error(f"Valyuta məzənnələri yüklənərkən xəta: {str(e)}")
        return {}

# COUNTRIES konfiqurasiyasinin dinamiklesmesi 
def load_countries_config():
    try:
        df = pd.read_excel("countries_config.xlsx")
        countries = {}
        for _, row in df.iterrows():
            countries[row['Ölkə']] = {
                "currency": row['Valyuta'],
                "cities": eval(row['Şəhərlər'])  # Dict olaraq saxlayaq
            }
        return countries
    except FileNotFoundError:
        return {}

def save_countries_config(countries):
    data = []
    for country, info in countries.items():
        data.append({
            'Ölkə': country,
            'Valyuta': info['currency'],
            'Şəhərlər': str(info['cities'])
        })
    pd.DataFrame(data).to_excel("countries_config.xlsx", index=False)


def get_exchange_rate(currency_code):
    try:
        df = pd.read_excel("currency_rates.xlsx")
        rate = df[df['Kod'] == currency_code]['Məzənnə'].values[0]
        return float(rate)
    except:
        return 1.0  # Əgər məzənnə tapılmasa

# Xarici ezamiyyət hesablamalarında
exchange_rate = get_exchange_rate(currency)



st.markdown('<div class="main-header"><h1>✈️ Ezamiyyət İdarəetmə Sistemi</h1></div>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📋 Yeni Ezamiyyət", "🔐 Admin Paneli"])

# YENİ EZAMİYYƏT HISSESI
with tab1:
    with st.container():
        col1, col2 = st.columns([2, 1], gap="large")
        
        # Sol Sütun
        with col1:
            with st.expander("👤 Şəxsi Məlumatlar", expanded=True):
                cols = st.columns(2)
                with cols[0]:
                    first_name = st.text_input("Ad")
                    father_name = st.text_input("Ata adı")
                with cols[1]:
                    last_name = st.text_input("Soyad")
                    position = st.text_input("Vəzifə")

            with st.expander("🏢 Təşkilat Məlumatları"):
                department = st.selectbox("Şöbə", DEPARTMENTS)

            with st.expander("🧳 Ezamiyyət Detalları"):
                trip_type = st.radio("Növ", ["Ölkə daxili", "Ölkə xarici"])
                
                if trip_type == "Ölkə daxili":
                    cols = st.columns(2)
                    with cols[0]:
                        from_city = st.selectbox("Haradan", CITIES, index=CITIES.index("Bakı"))
                    with cols[1]:
                        to_city = st.selectbox("Haraya", [c for c in CITIES if c != from_city])
                    ticket_price = calculate_domestic_amount(from_city, to_city)
                    domestic_allowances = load_domestic_allowances()
                    daily_allowance = domestic_allowances.get(to_city, domestic_allowances['Digər'])
                else:  # Ölkə xarici ezamiyyət
                    country = st.selectbox("Ölkə", list(COUNTRIES.keys()))
                    
                    if country in COUNTRIES:
                        city_options = list(COUNTRIES[country]['cities'].keys()) + ["Digər"]
                        selected_city = st.selectbox("Şəhər", city_options)
                        
                        if selected_city == "Digər":
                            base_allowance = 500  # Default value
                            currency = COUNTRIES[country]['currency']
                        else:
                            city_data = COUNTRIES[country]['cities'][selected_city]
                            base_allowance = city_data['allowance']
                            currency = city_data['currency']
                        
                        # Ödəniş rejimi seçimi
                        payment_mode = st.selectbox(
                            "Ödəniş rejimi",
                            options=["Adi rejim", "Günlük Normaya 50% əlavə", "Günlük Normaya 30% əlavə"]
                        )
                        
                        # Günlük müavinətin hesablanması (ORİJİNAL VALYUTADA)
                        if payment_mode == "Adi rejim":
                            daily_allowance = float(base_allowance)
                        elif payment_mode == "Günlük Normaya 50% əlavə":
                            daily_allowance = float(base_allowance * 1.5)
                        else:
                            daily_allowance = float(base_allowance * 1.3)
                        
                        # Qonaqlama növünün seçimi
                        accommodation = st.radio(
                            "Qonaqlama növü",
                            options=[
                                "Adi Rejim",
                                "Yalnız yaşayış yeri ilə təmin edir", 
                                "Yalnız gündəlik xərcləri təmin edir"
                            ]
                        )


                cols = st.columns(2)
                with cols[0]:
                    start_date = st.date_input("Başlanğıc tarixi")
                with cols[1]:
                    end_date = st.date_input("Bitmə tarixi")
                
                purpose = st.text_area("Ezamiyyət məqsədi")

        # Sağ Sütun (Hesablama)
        with col2:
            with st.container():
                st.markdown('<div class="section-header">💰 Hesablama</div>', unsafe_allow_html=True)
                
                if start_date and end_date and end_date >= start_date:
                    trip_days = (end_date - start_date).days + 1
                    trip_nights = trip_days - 1 if trip_days > 1 else 0
        
                    if trip_type == "Ölkə daxili":
                        # Daxili ezamiyyət hesablamaları
                        hotel_cost = 0.7 * daily_allowance * trip_nights
                        daily_expenses = 0.3 * daily_allowance * trip_days
                        total_amount = hotel_cost + daily_expenses + ticket_price
        
                        # Göstəricilər
                        st.metric("📅 Günlük müavinət", f"{daily_allowance:.2f} AZN")
                        st.metric("🚌 Nəqliyyat xərci", f"{ticket_price:.2f} AZN")
                        st.metric("🏨 Mehmanxana xərcləri", f"{hotel_cost:.2f} AZN")
                        st.metric("🍽️ Gündəlik xərclər", f"{daily_expenses:.2f} AZN")
                        st.metric("⏳ Müddət", f"{trip_days} gün")
                        st.metric("💳 Ümumi məbləğ", f"{total_amount:.2f} AZN")
                        
                    else:  # Xarici ezamiyyət hesablamaları
                        country_data = COUNTRIES[country]
                        if selected_city == "Digər":
                            base_allowance = 500  # Default value
                            currency = country_data['currency']
                        else:
                            city_data = country_data['cities'][selected_city]
                            base_allowance = city_data['allowance']
                            currency = city_data['currency']
                        
                        exchange_rate = CURRENCY_RATES.get(currency, 1.0)
                        
                        # Ödəniş rejimi əsasında günlük müavinəti hesabla (orijinal valyutada)
                        if payment_mode == "Adi rejim":
                            daily_allowance_foreign = float(base_allowance)
                        elif payment_mode == "Günlük Normaya 50% əlavə":
                            daily_allowance_foreign = float(base_allowance * 1.5)
                        else:  # 30% əlavə
                            daily_allowance_foreign = float(base_allowance * 1.3)
                        
                        # AZN-də günlük müavinət
                        daily_allowance_azn = daily_allowance_foreign * exchange_rate
                        
                        # Qonaqlama növünə görə hesablama
                        if accommodation == "Adi Rejim":
                            total_amount_foreign = daily_allowance_foreign * trip_days
                            hotel_cost_foreign = 0
                            daily_expenses_foreign = daily_allowance_foreign * trip_days
                            
                        elif accommodation == "Yalnız yaşayış yeri ilə təmin edir":
                            # Yalnız gündəlik xərclər ödənilir (40%)
                            daily_expenses_foreign = daily_allowance_foreign * 0.4 * trip_days
                            hotel_cost_foreign = 0
                            total_amount_foreign = daily_expenses_foreign
                            
                        else:  # "Yalnız gündəlik xərcləri təmin edir"
                            # Yalnız mehmanxana xərcləri ödənilir (60%)
                            if trip_nights > 0:
                                hotel_cost_foreign = daily_allowance_foreign * 0.6 * trip_nights
                            else:
                                hotel_cost_foreign = 0
                            daily_expenses_foreign = 0
                            total_amount_foreign = hotel_cost_foreign
        
                        # AZN-ə çevir
                        total_amount_azn = total_amount_foreign * exchange_rate
                        hotel_cost_azn = hotel_cost_foreign * exchange_rate
                        daily_expenses_azn = daily_expenses_foreign * exchange_rate
                        
                        # Göstəricilər
                        st.metric("📅 Günlük müavinət", 
                                 f"{daily_allowance_azn:.2f} AZN", 
                                 delta=f"{daily_allowance_foreign:.2f} {currency}")
                        
                        if accommodation == "Yalnız yaşayış yeri ilə təmin edir":
                            st.metric("🍽️ Gündəlik xərclər", 
                                     f"{daily_expenses_azn:.2f} AZN", 
                                     delta=f"{daily_expenses_foreign:.2f} {currency}")
                        elif accommodation == "Yalnız gündəlik xərcləri təmin edir" and trip_nights > 0:
                            st.metric("🏨 Mehmanxana xərcləri", 
                                     f"{hotel_cost_azn:.2f} AZN",
                                     delta=f"{hotel_cost_foreign:.2f} {currency}")
                        elif accommodation == "Adi Rejim":
                            st.metric("🍽️ Ümumi gündəlik", 
                                     f"{daily_expenses_azn:.2f} AZN", 
                                     delta=f"{daily_expenses_foreign:.2f} {currency}")
                        
                        st.metric("⏳ Müddət", f"{trip_days} gün")
                        st.metric("💳 Ümumi məbləğ", 
                                 f"{total_amount_azn:.2f} AZN", 
                                 delta=f"{total_amount_foreign:.2f} {currency}",
                                 help="Delta orijinal valyutada məbləği göstərir")
                        st.info(f"💱 Cari məzənnə: 1 {currency} = {exchange_rate:.4f} AZN")
                        
                        # Əlavə məlumat
                        if accommodation == "Yalnız yaşayış yeri ilə təmin edir":
                            st.caption("ℹ️ Yalnız gündəlik xərclər ödənilir (günlük müavinətin 40%-i)")
                        elif accommodation == "Yalnız gündəlik xərcləri təmin edir":
                            st.caption("ℹ️ Yalnız mehmanxana xərcləri ödənilir (günlük müavinətin 60%-i × gecə sayı)")
                
        
                # Yadda saxlama düyməsi
                if st.button("✅ Yadda Saxla", use_container_width=True):
                    if all([first_name, last_name, start_date, end_date]):
                        # Valyuta məlumatlarını təyin et
                        if trip_type == "Ölkə daxili":
                            currency = "AZN"
                            exchange_rate = 1.0
                            daily_allowance_foreign = daily_allowance
                            total_amount_foreign = total_amount
                            total_amount_azn = total_amount
                        else:
                            # Xarici ezamiyyət üçün yuxarıda hesablanmış dəyərləri istifadə et
                            total_amount_azn = total_amount_foreign * exchange_rate
        
                        trip_data = {
                            "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Ad": first_name,
                            "Soyad": last_name,
                            "Ata adı": father_name,
                            "Vəzifə": position,
                            "Şöbə": department,
                            "Ezamiyyət növü": trip_type,
                            "Ödəniş rejimi": payment_mode if trip_type == "Ölkə xarici" else "Tətbiq edilmir",
                            "Qonaqlama növü": accommodation if trip_type == "Ölkə xarici" else "Tətbiq edilmir",
                            "Marşrut": f"{from_city} → {to_city}" if trip_type == "Ölkə daxili" else f"{country} - {selected_city}",
                            "Bilet qiyməti": ticket_price if trip_type == "Ölkə daxili" else 0,
                            # Valyuta məlumatları
                            "Günlük müavinət (Valyuta)": f"{daily_allowance_foreign:.2f} {currency}",
                            "Günlük müavinət (AZN)": daily_allowance_azn if trip_type == "Ölkə xarici" else daily_allowance,
                            "Ümumi məbləğ (Valyuta)": f"{total_amount_foreign:.2f} {currency}",
                            "Ümumi məbləğ (AZN)": total_amount_azn,
                            "Valyuta": currency,
                            "Məzənnə": exchange_rate,
                            "Başlanğıc tarixi": start_date.strftime("%Y-%m-%d"),
                            "Bitmə tarixi": end_date.strftime("%Y-%m-%d"),
                            "Günlər": trip_days,
                            "Gecələr": trip_nights,
                            "Məqsəd": purpose
                        }
                        
                        if save_trip_data(trip_data):
                            st.success("Məlumatlar yadda saxlandı!")
                            # Formanı təmizlə (isteğe bağlı)
                            st.rerun()
                    else:
                        st.error("Zəhmət olmasa bütün məcburi sahələri doldurun!")


# ============================== ADMIN PANELİ ==============================
with tab2:
    # Admin giriş statusunun yoxlanılması
    if 'admin_logged' not in st.session_state:
        st.session_state.admin_logged = False

    # Giriş edilməyibsə
    if not st.session_state.admin_logged:
        with st.container():
            st.markdown('<div class="login-box"><div class="login-header"><h2>🔐 Admin Girişi</h2></div>', unsafe_allow_html=True)
            
            cols = st.columns(2)
            with cols[0]:
                admin_user = st.text_input("İstifadəçi adı", key="admin_user")
            with cols[1]:
                admin_pass = st.text_input("Şifrə", type="password", key="admin_pass")
            
            if st.button("Giriş et", key="admin_login_btn"):
                if admin_user == "admin" and admin_pass == "admin123":
                    st.session_state.admin_logged = True
                    st.rerun()
                else:
                    st.error("Yanlış giriş məlumatları!")
            
            st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # Giriş edildikdə
    if st.session_state.admin_logged:
        st.markdown('<div class="main-header"><h1>⚙️ Admin İdarəetmə Paneli</h1></div>', unsafe_allow_html=True)
        
        # Çıxış düyməsi
        if st.button("🚪 Çıxış", key="logout_btn"):
            st.session_state.admin_logged = False
            st.rerun()
        
        # Sekmələrin yaradılması
        tab_manage, tab_import, tab_settings, tab_currency = st.tabs(
            ["📊 Məlumatlar", "📥 İdxal", "⚙️ Parametrlər", "💱 Valyuta Məzənnələri"]
        )
        
        # Məlumatlar sekmesi
        with tab_manage:
            try:
                df = load_trip_data()
                if not df.empty:
                    # Sütun tip konvertasiyaları
                    datetime_cols = ['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']
                    numeric_cols = ['Ümumi məbləğ', 'Günlük müavinət', 'Bilet qiyməti', 'Günlər']
                    
                    for col in datetime_cols:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], errors='coerce')
                    
                    for col in numeric_cols:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                            if col == 'Günlər':
                                df[col] = df[col].astype('Int64')
                    
                    df = df.sort_values("Tarix", ascending=False)
                    
            except Exception as e:
                st.error(f"Məlumatlar yüklənərkən xəta: {str(e)}")
                df = pd.DataFrame()

            if not df.empty:
                # Statistik kartlar
                cols = st.columns(4)
                with cols[0]:
                    st.metric("Ümumi Ezamiyyət", len(df))
                with cols[1]:
                    st.metric("Ümumi Xərclər", f"{df['Ümumi məbləğ'].sum():.2f} AZN")
                with cols[2]:
                    st.metric("Orta Müddət", f"{df['Günlər'].mean():.1f} gün")
                with cols[3]:
                    st.metric("Aktiv İstifadəçilər", df['Ad'].nunique())

                # Qrafiklər
                cols = st.columns(2)
                with cols[0]:
                    fig = px.pie(df, names='Ezamiyyət növü', title='Ezamiyyət Növlərinin Payı',
                                color_discrete_sequence=px.colors.sequential.RdBu)
                    st.plotly_chart(fig, use_container_width=True)
                
                with cols[1]:
                    department_stats = df.groupby('Şöbə')['Ümumi məbləğ'].sum().nlargest(10)
                    fig = px.bar(department_stats, 
                                title='Top 10 Xərc Edən Şöbə',
                                labels={'value': 'Məbləğ (AZN)', 'index': 'Şöbə'},
                                color=department_stats.values,
                                color_continuous_scale='Bluered')
                    st.plotly_chart(fig, use_container_width=True)

                # Məlumat cədvəli
                with st.expander("🔍 Bütün Qeydlər", expanded=True):
                    column_config = {
                        'Tarix': st.column_config.DatetimeColumn(format="DD.MM.YYYY HH:mm"),
                        'Başlanğıc tarixi': st.column_config.DateColumn(format="YYYY-MM-DD"),
                        'Bitmə tarixi': st.column_config.DateColumn(format="YYYY-MM-DD"),
                        'Ümumi məbləğ': st.column_config.NumberColumn(format="%.2f AZN"),
                        'Günlük müavinət': st.column_config.NumberColumn(format="%.2f AZN"),
                        'Bilet qiyməti': st.column_config.NumberColumn(format="%.2f AZN"),
                        'Günlər': st.column_config.NumberColumn(format="%.0f")
                    }
                    
                    edited_df = st.data_editor(
                        df,
                        column_config=column_config,
                        use_container_width=True,
                        height=600,
                        num_rows="fixed",
                        hide_index=True,
                        key="main_data_editor"
                    )

                    # Silinmə əməliyyatı
                    display_options = [f"{row['Ad']} {row['Soyad']} - {row['Marşrut']} ({row['Tarix'].date() if pd.notnull(row['Tarix']) else 'N/A'})" 
                                      for _, row in df.iterrows()]
                    
                    selected_indices = st.multiselect(
                        "Silinəcək qeydləri seçin",
                        options=df.index.tolist(),
                        format_func=lambda x: display_options[x]
                    )
                    
                    if st.button("🗑️ Seçilmiş qeydləri sil", type="secondary"):
                        try:
                            df = df.drop(selected_indices)
                            df.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                            st.success(f"{len(selected_indices)} qeyd silindi!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Silinmə xətası: {str(e)}")

                # İxrac funksiyaları
                try:
                    csv_df = df.fillna('').astype(str)
                    csv = csv_df.to_csv(index=False).encode('utf-8')
                    
                    st.download_button(
                        "📊 CSV ixrac et",
                        data=csv,
                        file_name=f"ezamiyyet_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    excel_data = buffer.getvalue()
                    
                    st.download_button(
                        "📊 Excel ixrac et",
                        data=excel_data,
                        file_name=f"ezamiyyet_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"İxrac xətası: {str(e)}")
            else:
                st.warning("Hələ heç bir məlumat yoxdur")

        # İdxal sekmesi
        with tab_import:
            st.markdown("### Excel Fayl İdxalı")
            st.info("""
            **Tələblər:**
            1. Eyni adlı sütunlar avtomatik uyğunlaşdırılacaq
            2. Tarixlər YYYY-MM-DD formatında olmalıdır
            3. Rəqəmsal dəyərlər AZN ilə olmalıdır
            """)
            
            uploaded_file = st.file_uploader("Fayl seçin", type=["xlsx", "xls", "csv"])
            
            if uploaded_file is not None:
                try:
                    # Faylın yüklənməsi
                    if uploaded_file.name.endswith('.csv'):
                        df_import = pd.read_csv(uploaded_file)
                    else:
                        df_import = pd.read_excel(uploaded_file)
                    
                    # Avtomatik sütun uyğunlaşdırması
                    existing_columns = [
                        'Tarix', 'Ad', 'Soyad', 'Ata adı', 'Vəzifə', 'Şöbə', 
                        'Ezamiyyət növü', 'Ödəniş növü', 'Qonaqlama növü', 'Marşrut',
                        'Bilet qiyməti', 'Günlük müavinət', 'Başlanğıc tarixi',
                        'Bitmə tarixi', 'Günlər', 'Ümumi məbləğ', 'Məqsəd'
                    ]
                    
                    # Sütunları filtrlə
                    matched_columns = [col for col in df_import.columns if col in existing_columns]
                    df_mapped = df_import[matched_columns].copy()
                    
                    # Tarix konvertasiyaları
                    date_columns = ['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']
                    for col in date_columns:
                        if col in df_mapped.columns:
                            df_mapped[col] = pd.to_datetime(df_mapped[col], errors='coerce')
                    
                    # Rəqəmsal dəyərlərin konvertasiyası
                    numeric_columns = ['Bilet qiyməti', 'Günlük müavinət', 'Günlər', 'Ümumi məbləğ']
                    for col in numeric_columns:
                        if col in df_mapped.columns:
                            df_mapped[col] = pd.to_numeric(df_mapped[col], errors='coerce')
                    
                    # Önizləmə
                    with st.expander("📋 İdxal önizləməsi (İlk 10 qeyd)", expanded=False):
                        st.dataframe(df_mapped.head(10)) 
        
                    if st.button("✅ Təsdiqlə və Yüklə"):
                        # Mövcud məlumatlarla birləşdir
                        try:
                            df_existing = pd.read_excel("ezamiyyet_melumatlari.xlsx")
                            df_combined = pd.concat([df_existing, df_mapped], ignore_index=True)
                        except FileNotFoundError:
                            df_combined = df_mapped
                        
                        # Faylı yenilə
                        df_combined.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                        st.success(f"✅ {len(df_mapped)} qeyd uğurla idxal edildi!")
                        st.rerun()
        
                except Exception as e:
                    st.error(f"Xəta: {str(e)}")
        

        # Parametrler tabi 
        with tab_settings:
            st.markdown("### 🛠️ Sistem Parametrləri")
            
            # Valyuta məzənnələri bölməsi
            with st.expander("💱 Valyuta Məzənnələri", expanded=True):
                # Skreyp et butonu
                if st.button("🔄 Məzənnələri CBAR-dan yenilə"):
                    scraped_rates = scrape_currency_rates()
                    if scraped_rates:
                        save_currency_rates(scraped_rates)
                        st.success(f"{len(scraped_rates)} valyuta uğurla yeniləndi!")
                
                # Valyuta redaktə paneli
                try:
                    currency_rates = load_currency_rates()
                    df_currency = pd.DataFrame({
                        'Kod': currency_rates.keys(),
                        'Məzənnə': currency_rates.values()
                    })
                    
                    edited_currency = st.data_editor(
                        df_currency,
                        num_rows="dynamic",
                        column_config={
                            "Kod": st.column_config.TextColumn(
                                "Valyuta Kodu (3 hərf)",
                                max_chars=3,
                                validate="^[A-Z]{3}$",
                                required=True
                            ),
                            "Məzənnə": st.column_config.NumberColumn(
                                "AZN qarşılığı",
                                min_value=0.0001,
                                format="%.4f",
                                required=True
                            )
                        }
                    )
                    
                    if st.button("💾 Valyuta dəyişikliklərini saxla"):
                        new_rates = edited_currency.set_index('Kod')['Məzənnə'].to_dict()
                        save_currency_rates(new_rates)
                        st.success("Valyuta məzənnələri yeniləndi!")
                        
                except Exception as e:
                    st.error(f"Valyuta məzənnələri yüklənərkən xəta: {str(e)}")
        
            # Ölkə və şəhər idarəetmə bölməsi
            with st.expander("🌍 Beynəlxalq Ezamiyyət Parametrləri", expanded=True):
                COUNTRIES = load_countries_config()
                CURRENCY_OPTIONS = list(load_currency_rates().keys())
                
                # Yeni ölkə əlavə etmə
                cols = st.columns([3, 2, 1])
                with cols[0]:
                    new_country_name = st.text_input("Yeni ölkə adı")
                with cols[1]:
                    new_country_currency = st.selectbox(
                        "Valyuta seçin",
                        options=CURRENCY_OPTIONS,
                        index=0 if not CURRENCY_OPTIONS else None
                    )
                with cols[2]:
                    if st.button("➕ Ölkə əlavə et"):
                        if new_country_name and new_country_name not in COUNTRIES:
                            COUNTRIES[new_country_name] = {
                                "currency": new_country_currency,
                                "cities": {}
                            }
                            save_countries_config(COUNTRIES)
                            st.rerun()
        
                # Ölkə seçimi və redaktə
                selected_country = st.selectbox(
                    "Redaktə ediləcək ölkə",
                    options=list(COUNTRIES.keys()),
                    index=0 if COUNTRIES else None
                )
        
                if selected_country:
                    country_data = COUNTRIES[selected_country]
                    
                    # Ölkə əsas valyutasını redaktə
                    new_currency = st.selectbox(
                        "Ölkə valyutasını dəyişdir",
                        options=CURRENCY_OPTIONS,
                        index=CURRENCY_OPTIONS.index(country_data['currency']) if country_data['currency'] in CURRENCY_OPTIONS else 0
                    )
                    if new_currency != country_data['currency']:
                        country_data['currency'] = new_currency
                        save_countries_config(COUNTRIES)
                        st.rerun()
        
                    # Şəhər idarəetmə
                    st.markdown("### Şəhər Konfiqurasiyası")
                    
                    # Yeni şəhər əlavə etmə
                    cols = st.columns([3, 2, 2, 1])
                    with cols[0]:
                        new_city_name = st.text_input("Yeni şəhər adı")
                    with cols[1]:
                        new_city_allowance = st.number_input("Günlük müavinət", min_value=0)
                    with cols[2]:
                        new_city_currency = st.selectbox(
                            "Valyuta seçin",
                            options=CURRENCY_OPTIONS,
                            index=CURRENCY_OPTIONS.index(country_data['currency']) if country_data['currency'] in CURRENCY_OPTIONS else 0
                        )
                    with cols[3]:
                        if st.button("➕ Şəhər əlavə et"):
                            if new_city_name:
                                country_data['cities'][new_city_name] = {
                                    "allowance": new_city_allowance,
                                    "currency": new_city_currency
                                }
                                save_countries_config(COUNTRIES)
                                st.rerun()
        
                    # Mövcud şəhərlərin redaktəsi
                    for city in list(country_data['cities'].keys()):
                        st.markdown(f"#### {city}")
                        cols = st.columns([2, 2, 1])
                        with cols[0]:
                            new_allowance = st.number_input(
                                "Günlük müavinət",
                                value=country_data['cities'][city]['allowance'],
                                key=f"allowance_{city}"
                            )
                        with cols[1]:
                            new_currency = st.selectbox(
                                "Valyuta",
                                options=CURRENCY_OPTIONS,
                                index=CURRENCY_OPTIONS.index(country_data['cities'][city]['currency']) if country_data['cities'][city]['currency'] in CURRENCY_OPTIONS else 0,
                                key=f"currency_{city}"
                            )
                        with cols[2]:
                            if st.button("🗑️ Sil", key=f"delete_{city}"):
                                del country_data['cities'][city]
                                save_countries_config(COUNTRIES)
                                st.rerun()
        
                        if new_allowance != country_data['cities'][city]['allowance'] or new_currency != country_data['cities'][city]['currency']:
                            country_data['cities'][city]['allowance'] = new_allowance
                            country_data['cities'][city]['currency'] = new_currency
                            save_countries_config(COUNTRIES)
                            st.rerun()


            
                        # Yeni əlavə edilən hissə
            with st.expander("🏙️ Daxili Ezamiyyət Müavinətləri (Ətraflı)", expanded=True):
                st.markdown("""
                **Təlimat:**
                - Mövcud şəhərlərin müavinətlərini dəyişə bilərsiniz
                - Yeni şəhərlər əlavə edə bilərsiniz
                - "Digər" kateqoriyası siyahıda olmayan bütün şəhərlər üçün əsas götürülür
                """)
                
                # Yeni şəhər əlavə etmə paneli
                st.markdown("### ➕ Yeni Şəhər Əlavə Et")
                cols = st.columns([2, 1, 1])
                with cols[0]:
                    new_city = st.text_input("Şəhər adı", key="new_city")
                with cols[1]:
                    new_city_allowance = st.number_input("Müavinət (AZN)", min_value=0, value=90, key="new_city_allowance")
                with cols[2]:
                    if st.button("Əlavə et", key="add_new_city"):
                        allowances = load_domestic_allowances()
                        if new_city and new_city not in allowances:
                            allowances[new_city] = new_city_allowance
                            save_domestic_allowances(allowances)
                            st.success(f"{new_city} əlavə edildi!")
                            st.rerun()
                        else:
                            st.error("Zəhmət olmasa etibarlı şəhər adı daxil edin!")

                # Mövcud şəhərlərin idarə edilməsi
                st.markdown("### 📋 Mövcud Şəhər Müavinətləri")
                allowances = load_domestic_allowances()
                
                # Default 'Digər' sütununu qorumaq üçün
                other_allowance = allowances.get('Digər', 90)
                
                # Şəhərləri düzəlt
                cities = [city for city in allowances if city != 'Digər']
                cities.sort()
                
                for city in cities:
                    cols = st.columns([3, 2, 1])
                    with cols[0]:
                        st.write(f"🏙️ {city}")
                    with cols[1]:
                        new_allowance = st.number_input(
                            "Müavinət",
                            min_value=0,
                            value=int(allowances[city]),
                            key=f"allowance_{city}"
                        )
                    with cols[2]:
                        if city != 'Digər' and st.button("🗑️", key=f"del_{city}"):
                            del allowances[city]
                            save_domestic_allowances(allowances)
                            st.rerun()
                    
                    if new_allowance != allowances[city]:
                        allowances[city] = new_allowance
                        save_domestic_allowances(allowances)
                        st.rerun()

                # Digər kateqoriyası üçün
                st.markdown("### 🔄 Digər Şəhərlər")
                new_other = st.number_input(
                    "Digər şəhərlər üçün müavinət (AZN)",
                    min_value=0,
                    value=int(other_allowance),
                    key="other_allowance"
                )
                if new_other != other_allowance:
                    allowances['Digər'] = new_other
                    save_domestic_allowances(allowances)
                    st.rerun()


            # Daxili marşrutların redaktə edilməsi
            with st.expander("🚌 Daxili Marşrut Parametrləri"):
                st.markdown("#### Daxili Marşrut Qiymətləri")
                
                # Yeni marşrut əlavə etmə
                cols = st.columns([1, 1, 1, 1])
                with cols[0]:
                    route_from = st.selectbox("Haradan", CITIES, key="route_from")
                with cols[1]:
                    route_to = st.selectbox("Haraya", [c for c in CITIES if c != route_from], key="route_to")
                with cols[2]:
                    route_price = st.number_input("Qiymət (AZN)", min_value=0.0, value=10.0, step=0.5)
                with cols[3]:
                    if st.button("➕ Marşrut əlavə et"):
                        DOMESTIC_ROUTES[(route_from, route_to)] = route_price
                        st.success(f"{route_from} → {route_to} marşrutu əlavə edildi!")
                        st.rerun()
                
                # Mövcud marşrutları göstər
                route_df = pd.DataFrame([
                    {"Haradan": k[0], "Haraya": k[1], "Qiymət": v} 
                    for k, v in DOMESTIC_ROUTES.items()
                ])
                
                if not route_df.empty:
                    edited_routes = st.data_editor(
                        route_df,
                        use_container_width=True,
                        num_rows="dynamic",
                        column_config={
                            "Qiymət": st.column_config.NumberColumn(
                                "Qiymət (AZN)",
                                min_value=0,
                                max_value=100,
                                step=0.5,
                                format="%.2f AZN"
                            )
                        }
                    )
                    
                    if st.button("💾 Marşrut dəyişikliklərini saxla"):
                        # Yenilənmiş marşrutları saxla
                        new_routes = {}
                        for _, row in edited_routes.iterrows():
                            new_routes[(row['Haradan'], row['Haraya'])] = row['Qiymət']
                        DOMESTIC_ROUTES.clear()
                        DOMESTIC_ROUTES.update(new_routes)
                        st.success("Marşrut məlumatları yeniləndi!")

            # Sistem məlumatları
            # In the "Sistem Məlumatları" section under tab_settings:
            with st.expander("📊 Sistem Məlumatları"):
                st.markdown("#### Ümumi Statistikalar")
                
                try:
                    df = pd.read_excel("ezamiyyet_melumatlari.xlsx")
                    
                    # Convert Tarix column to datetime
                    if not df.empty:
                        df['Tarix'] = pd.to_datetime(df['Tarix'], errors='coerce')
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Toplam Qeydlər", len(df))
                    with col2:
                        if not df.empty and 'Tarix' in df.columns:
                            last_date = df['Tarix'].max()
                            display_date = last_date.strftime("%Y-%m-%d") if not pd.isnull(last_date) else "Yoxdur"
                        else:
                            display_date = "Yoxdur"
                        st.metric("Ən Son Qeyd", display_date)
                    with col3:
                        st.metric("Fayl Ölçüsü", f"{len(df) * 0.5:.1f} KB" if not df.empty else "0 KB")
                    
                    # Sistem təmizliyi
                    st.markdown("#### 🗑️ Sistem Təmizliyi")
                    if st.button("⚠️ Bütün məlumatları sil", type="secondary"):
                        if st.checkbox("Təsdiq edirəm ki, bütün məlumatları silmək istəyirəm"):
                            try:
                                import os
                                if os.path.exists("ezamiyyet_melumatlari.xlsx"):
                                    os.remove("ezamiyyet_melumatlari.xlsx")
                                st.success("Bütün məlumatlar silindi!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Silinmə zamanı xəta: {str(e)}")
                
                except FileNotFoundError:
                    st.info("Hələ heç bir məlumat faylı yaradılmayıb")

        # valyuta 
        # Admin panelində Currency tab-ını elave olunur
        with tab_currency:
            st.markdown("### Valyuta Məzənnələrinin İdarə Edilməsi")
            
            # Valyutaları skreyp et
            if st.button("🔄 Valyuta məzənnələrini yenilə"):
                scraped_rates = scrape_currency_rates()
                if scraped_rates:
                    df_currency = pd.DataFrame({
                        'Valyuta': scraped_rates.keys(),
                        'Kod': scraped_rates.keys(),
                        'Məzənnə': scraped_rates.values()
                    })
                    df_currency.to_excel("currency_rates.xlsx", index=False)
                    st.success("Valyuta məzənnələri uğurla yeniləndi!")
            
            try:
                df_currency = pd.read_excel("currency_rates.xlsx")
            except FileNotFoundError:
                df_currency = pd.DataFrame(columns=['Valyuta', 'Kod', 'Məzənnə'])
            
            edited_currency = st.data_editor(
                df_currency,
                num_rows="dynamic",
                column_config={
                    "Məzənnə": st.column_config.NumberColumn(
                        "AZN qarşılığı",
                        format="%.4f",
                        min_value=0.0001,
                    ),
                    "Kod": st.column_config.TextColumn(
                        "Valyuta Kodu (3 hərf)",
                        max_chars=3,
                        validate="^[A-Z]{3}$",
                    )
                }
            )
            
            if st.button("💾 Valyuta məzənnələrini saxla"):
                edited_currency.to_excel("currency_rates.xlsx", index=False)
                st.success("Məzənnələr yeniləndi!")
            
            # Cari məzənnələrin göstərilməsi
            with st.expander("📊 Cari Valyuta Məzənnələri"):
                try:
                    current_rates = pd.read_excel("currency_rates.xlsx")
                    st.dataframe(current_rates, hide_index=True)
                except FileNotFoundError:
                    st.warning("Valyuta məzənnələri faylı tapılmadı")


if __name__ == "__main__":
    if not os.path.exists("ezamiyyet_melumatlari.xlsx"):
        pd.DataFrame(columns=[
            'Tarix', 'Ad', 'Soyad', 'Ata adı', 'Vəzifə', 'Şöbə', 
            'Ezamiyyət növü', 'Ödəniş növü', 'Qonaqlama növü',
            'Marşrut', 'Bilet qiyməti', 'Günlük müavinət', 
            'Başlanğıc tarixi', 'Bitmə tarixi', 'Günlər', 
            'Ümumi məbləğ', 'Məqsəd'
        ]).to_excel("ezamiyyet_melumatlari.xlsx", index=False)
