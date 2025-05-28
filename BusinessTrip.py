import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from io import BytesIO
import requests
import xml.etree.ElementTree as ET
import os
import json

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

# CSS
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
    
    .main-header {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-radius: 0 0 20px 20px;
    }
    
    .section-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
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
        border: 1px solid #6366f1!important;
        background: #8b5cf6!important;
        color: white!important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(99,102,241,0.3)!important;
        background: #6366f1!important;
    }
    
    .dataframe {
        border-radius: 12px!important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05)!important;
    }
    
    .trip-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #6366f1;
    }
    
    .result-card {
        background: #f0f7ff;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #d0e0ff;
    }
    
    .admin-section {
        background: #f9fafb;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e5e7eb;
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

DOMESTIC_ALLOWANCES = {
    "Bakı": 125,
    "Naxçıvan": 100,
    "Gəncə": 95,
    "Sumqayıt": 95,
    "Digər": 90
}

COUNTRIES = {
    "Rusiya Federasiyası": {
        "currency": "USD",
        "cities": {
            "Moskva": {"allowance": 260, "currency": "USD"},
            "Sankt-Peterburq": {"allowance": 260, "currency": "USD"},
            "digər": {"allowance": 170, "currency": "USD"}
        }
    },
    "Türkiyə": {
        "currency": "EUR",
        "cities": {
            "Ankara": {"allowance": 200, "currency": "EUR"},
            "İstanbul": {"allowance": 220, "currency": "EUR"},
            "digər": {"allowance": 180, "currency": "EUR"}
        }
    },
    "Almaniya": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 250, "currency": "EUR"}
        }
    },
    "ABŞ": {
        "currency": "USD",
        "cities": {
            "Nyu-York": {"allowance": 450, "currency": "USD"},
            "digər": {"allowance": 350, "currency": "USD"}
        }
    }
}

# Fayl yoxlamaları
MELUMATLAR_JSON = "melumatlar.json"
if not os.path.exists("ezamiyyet_melumatlari.xlsx"):
    pd.DataFrame(columns=[
        'Tarix', 'Ad', 'Soyad', 'Ata adı', 'Vəzifə', 'Şöbə', 
        'Ezamiyyət növü', 'Ödəniş növü', 'Qonaqlama növü',
        'Marşrut', 'Bilet qiyməti', 'Günlük müavinət', 
        'Başlanğıc tarixi', 'Bitmə tarixi', 'Günlər', 
        'Ümumi məbləğ', 'Məqsəd', 'Valyuta'
    ]).to_excel("ezamiyyet_melumatlari.xlsx", index=False)

if not os.path.exists(MELUMATLAR_JSON):
    with open(MELUMATLAR_JSON, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

# ============================== FUNKSİYALAR ==============================
def load_trip_data():
    try:
        return pd.read_excel("ezamiyyet_melumatlari.xlsx")
    except FileNotFoundError:
        return pd.DataFrame()

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
    return DOMESTIC_ALLOWANCES

def load_countries_data():
    return COUNTRIES

@st.cache_data(ttl=3600)
def get_currency_rates(date):
    try:
        formatted_date = date.strftime("%d.%m.%Y")
        url = f"https://cbar.az/currencies/{formatted_date}.xml"
        response = requests.get(url)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        currencies = []
        for val_type in root.findall('.//ValType'):
            if val_type.get('Type') == 'Xarici valyutalar':
                for valute in val_type.findall('Valute'):
                    code = valute.get('Code')
                    name = valute.find('Name').text
                    nominal = valute.find('Nominal').text
                    value = valute.find('Value').text
                    currencies.append({
                        'Valyuta': code,
                        'Ad': name,
                        'Nominal': int(nominal),
                        'Məzənnə': float(value.replace(',', '.'))
                    })
        
        df = pd.DataFrame(currencies)
        if not df.empty:
            df['1 vahid üçün AZN'] = df['Məzənnə'] / df['Nominal']
        return df.sort_values('Valyuta')
    
    except Exception as e:
        st.error(f"Məzənnələr alınarkən xəta: {str(e)}")
        return pd.DataFrame()

def calculate_international_trip(country, city, payment_mode, accommodation, start_date, end_date):
    countries_data = load_countries_data()
    
    try:
        country_data = countries_data[country]
    except KeyError:
        st.error(f"{country} ölkəsi siyahıda yoxdur!")
        return None

    try:
        trip_days = (end_date - start_date).days + 1
        trip_nights = max(trip_days - 1, 0)
    except TypeError:
        st.error("Tarixlər düzgün daxil edilməyib!")
        return None

    try:
        currency_df = get_currency_rates(start_date)
        exchange_rate = currency_df.loc[
            currency_df['Valyuta'] == country_data['currency'], 
            '1 vahid üçün AZN'
        ].values[0]
    except (IndexError, AttributeError):
        st.error(f"{country_data['currency']} valyutası tapılmadı!")
        return None

    city_data = country_data['cities'].get(city, country_data['cities']['digər'])
    base_allowance = city_data['allowance']

    payment_multiplier = 1.0
    if payment_mode == "Günlük Normaya 50% əlavə":
        payment_multiplier = 1.5
    elif payment_mode == "Günlük Normaya 30% əlavə":
        payment_multiplier = 1.3

    daily_allowance = base_allowance * payment_multiplier

    hotel_ratio = 0.6 
    daily_ratio = 0.4
    if accommodation == "Yalnız yaşayış yeri ilə təmin edir":
        hotel_ratio = 0.0
        daily_ratio = 1.0
    elif accommodation == "Yalnız gündəlik xərcləri təmin edir":
        hotel_ratio = 1.0
        daily_ratio = 0.0

    hotel_cost = daily_allowance * hotel_ratio * trip_nights
    daily_cost = daily_allowance * daily_ratio * trip_days
    total_foreign = hotel_cost + daily_cost
    total_azn = total_foreign * exchange_rate

    return {
        'currency': country_data['currency'],
        'exchange_rate': exchange_rate,
        'daily_allowance': daily_allowance,
        'trip_days': trip_days,
        'trip_nights': trip_nights,
        'hotel_cost': hotel_cost,
        'daily_cost': daily_cost,
        'total_foreign': total_foreign,
        'total_azn': total_azn
    }

def load_info_sections():
    try:
        with open(MELUMATLAR_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Məlumatlar yüklənərkən xəta: {str(e)}")
        return {}

def save_info_sections(sections):
    with open(MELUMATLAR_JSON, 'w', encoding='utf-8') as f:
        json.dump(sections, f, ensure_ascii=False, indent=4)

# ============================== ƏSAS TƏRTİB ==============================
st.markdown('<div class="main-header"><h1>✈️ Ezamiyyət İdarəetmə Sistemi</h1></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📋 Yeni Ezamiyyət", "🔐 Admin Paneli", "📚 Məlumatlar və Qeydlər"])

# YENİ EZAMİYYƏT HISSESI
with tab1:
    st.markdown("## 📋 Yeni Ezamiyyət Qeydi")
    
    with st.form("new_trip_form"):
        col1, col2 = st.columns([1, 1], gap="large")
        
        # Sol Sütun - Ümumi Məlumatlar
        with col1:
            st.markdown("### 👤 Şəxsi Məlumatlar")
            cols = st.columns(2)
            with cols[0]:
                first_name = st.text_input("Ad*", key="first_name")
                father_name = st.text_input("Ata adı", key="father_name")
            with cols[1]:
                last_name = st.text_input("Soyad*", key="last_name")
                position = st.text_input("Vəzifə*", key="position")
            
            st.markdown("### 🏢 Təşkilat Məlumatları")
            department = st.selectbox("Şöbə*", DEPARTMENTS, key="department")
            
            st.markdown("### 🧳 Ezamiyyət Detalları")
            trip_type = st.radio("Ezamiyyət növü*", ["Ölkə daxili", "Ölkə xarici"], key="trip_type", horizontal=True)
            
            purpose = st.text_area("Ezamiyyət məqsədi*", 
                                 placeholder="Ezamiyyətin məqsədini qeyd edin...",
                                 key="purpose")
    
        # Sağ Sütun - Ezamiyyət Detalları və Hesablama
        with col2:
            if trip_type == "Ölkə daxili":
                st.markdown("### 🚌 Ölkə Daxili Səfər Planı")
                
                if 'trips' not in st.session_state:
                    st.session_state.trips = []
                
                if st.button("➕ Yeni səfər əlavə et", key="add_domestic_trip"):
                    st.session_state.trips.append({
                        'from_city': 'Bakı',
                        'to_city': 'Bakı',
                        'start_date': datetime.now().date(),
                        'end_date': datetime.now().date(),
                        'ticket_price': 0
                    })
                
                # SƏFƏR SİYAHISI
                for i, trip in enumerate(st.session_state.trips):
                    with st.container():
                        st.markdown(f"<div class='trip-card'><b>Səfər #{i+1}</b></div>", unsafe_allow_html=True)
                        cols = st.columns([2, 2, 2, 2, 1])
                        with cols[0]:
                            trip['from_city'] = st.selectbox(
                                f"Haradan #{i+1}", 
                                CITIES,
                                index=CITIES.index(trip['from_city']),
                                key=f'from_{i}'
                            )
                        with cols[1]:
                            trip['to_city'] = st.selectbox(
                                f"Haraya #{i+1}", 
                                [c for c in CITIES if c != trip['from_city']],
                                index=0,
                                key=f'to_{i}'
                            )
                        with cols[2]:
                            trip['start_date'] = st.date_input(
                                f"Başlanğıc #{i+1}", 
                                value=trip['start_date'],
                                key=f'start_{i}'
                            )
                        with cols[3]:
                            trip['end_date'] = st.date_input(
                                f"Bitmə #{i+1}", 
                                value=trip['end_date'],
                                min_value=trip['start_date'],
                                key=f'end_{i}'
                            )
                        with cols[4]:
                            trip['ticket_price'] = st.number_input(
                                "Nəqliyyat xərci (AZN)",
                                min_value=0,
                                value=trip['ticket_price'],
                                key=f'ticket_{i}'
                            )
                        
                        if st.button(f"❌ Səfəri sil #{i+1}", key=f'del_{i}'):
                            del st.session_state.trips[i]
                            st.rerun()
                
                # HESABLAMA NƏTİCƏLƏRİ
                if st.session_state.trips:
                    st.markdown("### 📊 Hesablama Nəticələri")
                    total_days = 0
                    total_amount = 0
                    total_transport = 0
                    daily_allowances = []
                    
                    sorted_trips = sorted(st.session_state.trips, key=lambda x: x['start_date'])
                    prev_end = None
                    
                    for trip in sorted_trips:
                        days = (trip['end_date'] - trip['start_date']).days + 1
                        
                        if prev_end and trip['start_date'] <= prev_end:
                            overlap = (prev_end - trip['start_date']).days + 1
                            days = max(0, days - overlap)
                        
                        allowance = DOMESTIC_ALLOWANCES.get(
                            trip['to_city'], 
                            DOMESTIC_ALLOWANCES['Digər']
                        )
                        
                        trip_amount = allowance * days
                        total_amount += trip_amount
                        total_transport += trip['ticket_price']
                        total_days += days
                        
                        prev_end = trip['end_date']
                        
                        daily_allowances.append({
                            'Şəhər': trip['to_city'],
                            'Günlər': days,
                            'Gündəlik müavinət (AZN)': allowance,
                            'Ümumi müavinət (AZN)': trip_amount
                        })
                    
                    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                    cols = st.columns(3)
                    cols[0].metric("Ümumi Günlər", total_days)
                    cols[1].metric("Ümumi Nəqliyyat", f"{total_transport} AZN")
                    cols[2].metric("Ümumi Müavinət", f"{total_amount} AZN")
                    st.metric("**Ümumi Məbləğ**", f"{total_amount + total_transport} AZN")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    df_details = pd.DataFrame(daily_allowances)
                    st.dataframe(
                        df_details,
                        column_config={
                            "Şəhər": "Hədəf şəhər",
                            "Günlər": st.column_config.NumberColumn(format="%d gün"),
                            "Gündəlik müavinət (AZN)": st.column_config.NumberColumn(format="%.2f AZN"),
                            "Ümumi müavinət (AZN)": st.column_config.NumberColumn(format="%.2f AZN")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.info("Ən azı bir səfər əlavə edin")
            
            else:  # Ölkə xarici ezamiyyət
                st.markdown("### 🌍 Ölkə Xarici Ezamiyyət Detalları")
                
                countries_data = load_countries_data()
                country = st.selectbox("Ölkə*", list(countries_data.keys()), key="country")
                
                if country in countries_data:
                    city_options = [c for c in countries_data[country]['cities'].keys() if c != 'digər']
                    city_options.append("digər")
                    selected_city = st.selectbox("Şəhər*", city_options, key="city")
                    
                    payment_mode = st.selectbox(
                        "Ödəniş rejimi*",
                        options=["Adi rejim", "Günlük Normaya 50% əlavə", "Günlük Normaya 30% əlavə"],
                        key="payment_mode"
                    )
                    
                    accommodation = st.radio(
                        "Qonaqlama növü*",
                        options=[
                            "Adi Rejim",
                            "Yalnız yaşayış yeri ilə təmin edir", 
                            "Yalnız gündəlik xərcləri təmin edir"
                        ],
                        key="accommodation"
                    )
            
                    cols = st.columns(2)
                    with cols[0]:
                        start_date = st.date_input("Başlanğıc tarixi*", key="start_date")
                    with cols[1]:
                        end_date = st.date_input("Bitmə tarixi*", key="end_date", min_value=start_date)
                
                # HESABLAMA NƏTİCƏLƏRİ
                if start_date and end_date:
                    result = calculate_international_trip(
                        country, selected_city, payment_mode, 
                        accommodation, start_date, end_date
                    )
                    
                    if result:
                        st.markdown("### 📊 Hesablama Nəticələri")
                        
                        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                        cols = st.columns(2)
                        cols[0].metric("Gündəlik Müavinət", 
                                      f"{result['daily_allowance']:.2f} {result['currency']}")
                        cols[1].metric("Məzənnə", 
                                      f"1 {result['currency']} = {result['exchange_rate']:.4f} AZN")
                        
                        cols = st.columns(3)
                        cols[0].metric("Ümumi Günlər", result['trip_days'])
                        cols[1].metric("Ümumi Gecələr", result['trip_nights'])
                        cols[2].metric("Valyuta Cəmi", 
                                      f"{result['total_foreign']:.2f} {result['currency']}")
                        
                        cols = st.columns(2)
                        cols[0].metric("Mehmanxana Xərcləri", 
                                      f"{result['hotel_cost']:.2f} {result['currency']}")
                        cols[1].metric("Gündəlik Xərclər", 
                                      f"{result['daily_cost']:.2f} {result['currency']}")
                        
                        st.metric("**Ümumi məbləğ**", 
                                 f"{result['total_foreign']:.2f} {result['currency']} / {result['total_azn']:.2f} AZN")
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        if accommodation == "Adi Rejim":
                            st.info("Adi Rejim: Günlük müavinətin 60%-i mehmanxana xərclərinə, 40%-i gündəlik xərclərə ayrılır")
        
        # Formun aşağı hissəsi - Yadda Saxla düyməsi
        submitted = st.form_submit_button("✅ Yadda Saxla", type="primary", use_container_width=True)
        if submitted:
            if not all([first_name, last_name, position, department, purpose]):
                st.error("Zəhmət olmasa bütün məcburi sahələri doldurun (* ilə işarələnmiş)")
            elif trip_type == "Ölkə daxili" and not st.session_state.trips:
                st.error("Ən azı bir səfər əlavə edin")
            elif trip_type == "Ölkə xarici" and (start_date > end_date):
                st.error("Tarixləri düzgün daxil edin")
            else:
                trip_data = {
                    "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Ad": first_name,
                    "Soyad": last_name,
                    "Ata adı": father_name,
                    "Vəzifə": position,
                    "Şöbə": department,
                    "Ezamiyyət növü": trip_type,
                    "Məqsəd": purpose
                }
                
                if trip_type == "Ölkə daxili":
                    routes = []
                    total_amount = 0
                    total_transport = 0
                    for trip in st.session_state.trips:
                        routes.append(f"{trip['from_city']} → {trip['to_city']}")
                        allowance = DOMESTIC_ALLOWANCES.get(trip['to_city'], DOMESTIC_ALLOWANCES['Digər'])
                        days = (trip['end_date'] - trip['start_date']).days + 1
                        total_amount += allowance * days
                        total_transport += trip['ticket_price']
                    
                    trip_data.update({
                        "Marşrut": ", ".join(routes),
                        "Bilet qiyməti": total_transport,
                        "Günlük müavinət": total_amount,
                        "Ümumi məbləğ": total_amount + total_transport,
                        "Başlanğıc tarixi": min([trip['start_date'] for trip in st.session_state.trips]).strftime("%Y-%m-%d"),
                        "Bitmə tarixi": max([trip['end_date'] for trip in st.session_state.trips]).strftime("%Y-%m-%d"),
                        "Günlər": sum([(trip['end_date'] - trip['start_date']).days + 1 for trip in st.session_state.trips]),
                        "Valyuta": "AZN"
                    })
                else:
                    trip_data.update({
                        "Ödəniş növü": payment_mode,
                        "Qonaqlama növü": accommodation,
                        "Marşrut": f"{country} - {selected_city}",
                        "Bilet qiyməti": 0,
                        "Günlük müavinət": result['daily_allowance'],
                        "Ümumi məbləğ": result['total_azn'],
                        "Başlanğıc tarixi": start_date.strftime("%Y-%m-%d"),
                        "Bitmə tarixi": end_date.strftime("%Y-%m-%d"),
                        "Günlər": result['trip_days'],
                        "Valyuta": result['currency']
                    })
                
                if save_trip_data(trip_data):
                    st.success("Məlumatlar uğurla yadda saxlandı!")
                    if trip_type == "Ölkə daxili":
                        st.session_state.trips = []
                else:
                    st.error("Məlumatlar saxlanılarkən xəta baş verdi")

# ADMIN PANELİ
with tab2:
    if 'admin_logged' not in st.session_state:
        st.session_state.admin_logged = False

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
    else:
        st.markdown('<div class="main-header"><h1>⚙️ Admin İdarəetmə Paneli</h1></div>', unsafe_allow_html=True)
        
        if st.button("🚪 Çıxış", key="logout_btn"):
            st.session_state.admin_logged = False
            st.rerun()
        
        tab_manage, tab_settings, tab_info = st.tabs(["📊 Məlumatların İdarəsi", "⚙️ Parametrlər", "📝 Məlumatların Redaktəsi"])
        
        with tab_manage:
            st.markdown("### Bütün Ezamiyyət Qeydləri")
            df = load_trip_data()
            
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                
                # İxrac funksiyaları
                st.markdown("### İxrac Seçimləri")
                csv = df.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    "📊 CSV ixrac et",
                    data=csv,
                    file_name=f"ezamiyyet_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("Hələ heç bir məlumat yoxdur")
        
        with tab_settings:
            st.markdown("### Ölkə Daxili Parametrlər")
            allowances = load_domestic_allowances()
            
            for city, allowance in allowances.items():
                new_value = st.number_input(
                    f"{city} üçün gündəlik müavinət (AZN)",
                    min_value=0,
                    value=allowance,
                    key=f"allowance_{city}"
                )
                allowances[city] = new_value
            
            if st.button("Parametrləri yenilə"):
                st.success("Parametrlər uğurla yeniləndi")
            
            st.markdown("### Ölkə Xarici Parametrlər")
            countries = load_countries_data()
            selected_country = st.selectbox("Ölkə seçin", list(countries.keys()))
            
            if selected_country:
                country_data = countries[selected_country]
                new_currency = st.selectbox("Valyuta", ["USD", "EUR", "GBP"], 
                                          index=["USD", "EUR", "GBP"].index(country_data['currency']))
                
                st.markdown("#### Şəhər Müavinətləri")
                for city, data in country_data['cities'].items():
                    new_allowance = st.number_input(
                        f"{city} üçün gündəlik müavinət",
                        min_value=0,
                        value=data['allowance'],
                        key=f"city_{selected_country}_{city}"
                    )
                    country_data['cities'][city]['allowance'] = new_allowance
                
                if st.button("Ölkə məlumatlarını yenilə"):
                    countries[selected_country] = country_data
                    st.success("Məlumatlar uğurla yeniləndi")
        
        with tab_info:
            st.markdown("### Məlumat Sektiyalarının İdarə Edilməsi")
            sections = load_info_sections()
            
            new_title = st.text_input("Yeni bölmə başlığı")
            new_content = st.text_area("Yeni bölmə məzmunu", height=200)
            
            if st.button("Yeni bölmə əlavə et"):
                if new_title.strip() and new_content.strip():
                    section_id = f"section_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    sections[section_id] = {
                        "title": new_title,
                        "content": new_content,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    save_info_sections(sections)
                    st.success("Yeni bölmə əlavə edildi!")
                else:
                    st.error("Başlıq və məzmun tələb olunur")
            
            st.markdown("### Mövcud Bölmələr")
            for section_id, section_data in sections.items():
                with st.expander(section_data['title'], expanded=False):
                    edited_title = st.text_input("Başlıq", value=section_data['title'], key=f"title_{section_id}")
                    edited_content = st.text_area("Məzmun", value=section_data['content'], height=300, key=f"content_{section_id}")
                    
                    cols = st.columns(3)
                    with cols[0]:
                        if st.button("💾 Saxla", key=f"save_{section_id}"):
                            sections[section_id]['title'] = edited_title
                            sections[section_id]['content'] = edited_content
                            save_info_sections(sections)
                            st.success("Dəyişikliklər yadda saxlanıldı!")
                    with cols[1]:
                        if st.button("🗑️ Sil", key=f"delete_{section_id}"):
                            del sections[section_id]
                            save_info_sections(sections)
                            st.success("Bölmə silindi!")
                            st.rerun()
                    with cols[2]:
                        st.caption(f"Yaradılma tarixi: {section_data['created_at']}")

# MƏLUMATLAR VƏ QEYDLƏR
with tab3:
    st.markdown("## 📚 Ezamiyyət Qaydaları və Məlumatlar")
    sections = load_info_sections()
    
    if not sections:
        st.info("Hələ heç bir məlumat əlavə edilməyib")
    else:
        for section_id, section_data in sections.items():
            with st.expander(f"📌 {section_data.get('title', 'Başlıqsız')}", expanded=True):
                st.markdown(section_data.get('content', ''))
