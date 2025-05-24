import streamlit as st import pa
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import requests 
from bs4 import BeautifulSoup
import lxml

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
                                  placeholder="Giriş kodunu daxil edin...",
                                  key="login_password_input")
        
        cols = st.columns([1,2,1])
        with cols[1]:
            if st.button("Daxil ol", use_container_width=True, key="main_login_btn"):
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

COUNTRIES = {
    "Türkiyə": 300,
    "Gürcüstan": 250,
    "Almaniya": 600,
    "BƏƏ": 500,
    "Rusiya": 400,
    "İran": 280,
    "İtaliya": 550,
    "Fransa": 580,
    "İngiltərə": 620,
    "ABŞ": 650
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

PAYMENT_TYPES = {
    "Ödənişsiz": 0,
    "10% ödəniş edilməklə": 0.1,
    "Tam ödəniş edilməklə": 1
}

# ============================== FUNKSİYALAR ==============================
def load_trip_data():
    """Ezamiyyət məlumatlarını yükləyir"""
    try:
        if os.path.exists("ezamiyyet_melumatlari.xlsx"):
            df = pd.read_excel("ezamiyyet_melumatlari.xlsx")
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Məlumat yükləmə xətası: {str(e)}")
        return pd.DataFrame()

def check_admin_session():
    if 'admin_session_time' in st.session_state:
        if datetime.now() - st.session_state.admin_session_time > timedelta(minutes=30):
            st.session_state.admin_logged = False
            return False
    return True

def load_system_config():
    try:
        if os.path.exists("system_config.json"):
            with open("system_config.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {}

def write_log(action, details=""):
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "user": "admin"
        }
        
        log_file = "admin_logs.json"
        logs = []
        
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        pass

def load_trip_data():
    """Ezamiyyət məlumatlarını yükləyir"""
    try:
        if os.path.exists("ezamiyyet_melumatlari.xlsx"):
            df = pd.read_excel("ezamiyyet_melumatlari.xlsx")
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Məlumat yükləmə xətası: {str(e)}")
        return pd.DataFrame()

def calculate_domestic_amount(from_city, to_city):
    """Daxili marşrut üçün bilet qiymətini hesablayır"""
    return DOMESTIC_ROUTES.get((from_city, to_city), 70)

def calculate_days(start_date, end_date):
    """İki tarix arasındakı günləri hesablayır"""
    return (end_date - start_date).days + 1

def calculate_total_amount(daily_allowance, days, payment_type, ticket_price=0):
    """Ümumi məbləği hesablayır"""
    return (daily_allowance * days + ticket_price) * PAYMENT_TYPES[payment_type]

def save_trip_data(new_data):
    try:
        if os.path.exists("ezamiyyet_melumatlari.xlsx"):
            df_existing = pd.read_excel("ezamiyyet_melumatlari.xlsx")
            df_combined = pd.concat([df_existing, pd.DataFrame([new_data])], ignore_index=True)
        else:
            df_combined = pd.DataFrame([new_data])
            
        df_combined.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
        return True
    except Exception as e:
        st.error(f"Yadda saxlama xətası: {str(e)}")
        return False

@st.cache_data(ttl=3600)
def get_currency_rates(date=None):
    try:
        if not date:
            date = datetime.now()
        else:
            date = pd.to_datetime(date)
            
        url = f"https://www.cbar.az/currencies/{date.strftime('%d.%m.%Y')}.xml"
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'xml')
        currencies = []
        
        for valute in soup.find_all('Valute'):
            # Ədədi hissəni ayırmaq üçün split() istifadə edirik
            nominal_text = valute.find('Nominal').text.strip()
            nominal = int(nominal_text.split()[0])  # Yalnız birinci hissəni götürürük
            
            currencies.append({
                'Kod': valute['Code'],
                'Valyuta': valute.find('Name').text,
                'Məzənnə': float(valute.find('Value').text.replace(',', '.')),
                'Nominal': nominal
            })
            
        return pd.DataFrame(currencies)
    
    except Exception as e:
        st.error(f"Valyuta məlumatları gətirilərkən xəta: {str(e)}")
        return pd.DataFrame()


def export_data(df, format, start_date, end_date, columns):
    try:
        filtered_df = df[(df['Tarix'] >= start_date) & (df['Tarix'] <= end_date)][columns]
        if format == "Excel (.xlsx)":
            buffer = BytesIO()
            filtered_df.to_excel(buffer, index=False)
            return buffer
        elif format == "CSV (.csv)":
            return filtered_df.to_csv(index=False).encode('utf-8')
        elif format == "JSON (.json)":
            return filtered_df.to_json(orient='records').encode('utf-8')
        return None
    except Exception as e:
        st.error(f"İxrac xətası: {str(e)}")
        return None

def read_uploaded_file(file):
    try:
        if file.name.endswith('.xlsx'):
            return pd.read_excel(file)
        elif file.name.endswith('.csv'):
            return pd.read_csv(file)
        elif file.name.endswith('.json'):
            return pd.read_json(file)
        return None
    except Exception as e:
        st.error(f"Fayl oxuma xətası: {str(e)}")
        return None


# ƏSAS İNTERFEYS
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
                    first_name = st.text_input("Ad", key="first_name_input")
                    father_name = st.text_input("Ata adı", key="father_name_input")
                with cols[1]:
                    last_name = st.text_input("Soyad", key="last_name_input")
                    position = st.text_input("Vəzifə", key="position_input")

            with st.expander("🏢 Təşkilat Məlumatları"):
                department = st.selectbox("Şöbə", DEPARTMENTS, key="department_select")

            with st.expander("🧳 Ezamiyyət Detalları"):
                trip_type = st.radio("Növ", ["Ölkə daxili", "Ölkə xarici"], key="trip_type_radio")
                payment_type = st.selectbox("Ödəniş növü", list(PAYMENT_TYPES.keys()), key="payment_type_select")
                
                if trip_type == "Ölkə daxili":
                    cols = st.columns(2)
                    with cols[0]:
                        from_city = st.selectbox("Haradan", CITIES, index=CITIES.index("Bakı"), key="from_city_select")
                    with cols[1]:
                        to_city = st.selectbox("Haraya", [c for c in CITIES if c != from_city], key="to_city_select")
                    ticket_price = calculate_domestic_amount(from_city, to_city)
                    daily_allowance = 70
                    accommodation = "Tətbiq edilmir"
                else:
                    country = st.selectbox("Ölkə", list(COUNTRIES.keys()), key="country_select")
                    payment_mode = st.selectbox(
                        "Ödəniş rejimi",
                        options=["Adi rejim", "Günlük Normaya 50% əlavə", "Günlük Normaya 30% əlavə"],
                        key="payment_mode_select"
                    )
                    accommodation = st.selectbox(
                        "Qonaqlama xərcləri",
                        options=["Adi rejim", "Yalnız yaşayış yeri ilə təmin edir", "Yalnız gündəlik xərcləri təmin edir"],
                        key="accommodation_select"
                    )
                    base_allowance = COUNTRIES[country]
                    if payment_mode == "Adi rejim":
                        daily_allowance = base_allowance
                    elif payment_mode == "Günlük Normaya 50% əlavə":
                        daily_allowance = base_allowance * 1.5
                    else:
                        daily_allowance = base_allowance * 1.3
                    ticket_price = 0
                    from_city = "Bakı"
                    to_city = country

                cols = st.columns(2)
                with cols[0]:
                    start_date = st.date_input("Başlanğıc tarixi", key="start_date_input")
                with cols[1]:
                    end_date = st.date_input("Bitmə tarixi", key="end_date_input")
                
                purpose = st.text_area("Ezamiyyət məqsədi", key="purpose_textarea")

        # Sağ Sütun (Hesablama)
        with col2:
            with st.container():
                st.markdown('<div class="section-header">💰 Hesablama</div>', unsafe_allow_html=True)
                
                if start_date and end_date and end_date >= start_date:
                    trip_days = calculate_days(start_date, end_date)
                    total_amount = calculate_total_amount(daily_allowance, trip_days, payment_type, ticket_price)
                    
                    # Qonaqlama əmsalı
                    if trip_type == "Ölkə xarici":
                        if accommodation == "Yalnız yaşayış yeri ilə təmin edir":
                            total_amount *= 1.4
                            delta_label = "40% artım (Yaşayış)"
                        elif accommodation == "Yalnız gündəlik xərcləri təmin edir":
                            total_amount *= 1.6
                            delta_label = "60% artım (Gündəlik)"
                        else:
                            delta_label = None
                    else:
                        delta_label = None
                    
                    st.metric("📅 Günlük müavinət", f"{daily_allowance} AZN", key="daily_allowance_metric")
                    if trip_type == "Ölkə daxili":
                        st.metric("🚌 Nəqliyyat xərci", f"{ticket_price} AZN", key="ticket_price_metric")
                    st.metric("⏳ Müddət", f"{trip_days} gün", key="trip_days_metric")
                    st.metric(
                        "💳 Ümumi məbləğ", 
                        f"{total_amount:.2f} AZN", 
                        delta=delta_label,
                        delta_color="normal" if delta_label else "off",
                        key="total_amount_metric"
                    )

            if st.button("✅ Yadda Saxla", use_container_width=True, key="save_trip_button"):
                if all([first_name, last_name, start_date, end_date]):
                    trip_data = {
                        "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Ad": first_name,
                        "Soyad": last_name,
                        "Ata adı": father_name,
                        "Vəzifə": position,
                        "Şöbə": department,
                        "Ezamiyyət növü": trip_type,
                        "Ödəniş növü": payment_type,
                        "Qonaqlama növü": accommodation,
                        "Marşrut": f"{from_city} → {to_city}",
                        "Bilet qiyməti": ticket_price,
                        "Günlük müavinət": daily_allowance,
                        "Başlanğıc tarixi": start_date.strftime("%Y-%m-%d"),
                        "Bitmə tarixi": end_date.strftime("%Y-%m-%d"),
                        "Günlər": trip_days,
                        "Ümumi məbləğ": total_amount,
                        "Məqsəd": purpose
                    }
                    if save_trip_data(trip_data):
                        st.success("Məlumatlar yadda saxlandı!")
                else:
                    st.error("Zəhmət olmasa bütün məcburi sahələri doldurun!")


# ========== VALYUTA MƏZƏNNƏSİ HISSƏSİ ==========
with st.expander("💱 Valyuta Məzənnələri (Cbar.az)", expanded=True):
    selected_date = st.date_input(
        "Məzənnə tarixini seçin",
        value=datetime.now().date(),
        max_value=datetime.now().date(),
        format="DD.MM.YYYY"
    )
    
    if st.button("🔄 Yenilə", help="Son məzənnələri yüklə"):
        st.cache_data.clear()

    try:
        currency_df = get_currency_rates(selected_date)
        
        if not currency_df.empty:
            # Açıq rəng palitrası
            st.markdown("""
            <style>
                .light-card {
                    background: rgba(129, 131, 244, 0.1);
                    border: 1px solid rgba(129, 131, 244, 0.2);
                    border-radius: 8px;
                    padding: 0.8rem;
                    margin: 0.3rem;
                    flex: 1 1 30%;
                    transition: all 0.3s ease;
                }
                .light-card:hover {
                    background: rgba(129, 131, 244, 0.15);
                }
                .light-header {
                    color: #8183f4 !important;
                    font-size: 1.1rem !important;
                    margin: 0 !important;
                }
                .light-rate {
                    color: #a78bfa !important;
                    font-size: 1rem !important;
                    margin: 0 !important;
                }
                .currency-desc {
                    color: #777 !important;
                    font-size: 0.75rem !important;
                    margin: 0 !important;
                }
            </style>
            """, unsafe_allow_html=True)

            cols = st.columns(3)
            currency_groups = [currency_df[i::3] for i in range(3)]

            for idx, col in enumerate(cols):
                with col:
                    for _, row in currency_groups[idx].iterrows():
                        rate = row['Məzənnə'] / row['Nominal']
                        st.markdown(f"""
                        <div class="light-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <p class="light-header">{row['Kod']}</p>
                                    <p class="currency-desc">{row['Valyuta']}</p>
                                </div>
                                <div style="text-align: right;">
                                    <p class="light-rate">{rate:.4f}</p>
                                    <p class="currency-desc">1 {row['Kod']}</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.warning(f"{selected_date.strftime('%d.%m.%Y')} üçün məlumat yoxdur")
            
    except Exception as e:
        st.error(f"Məzənnə yüklənərkən xəta: {str(e)}")

# Admin Panel hissəsi
with tab2:
    # Admin sessiya idarəetməsi
    if 'admin_logged' not in st.session_state:
        st.session_state.admin_logged = False
    
    if 'admin_session_time' not in st.session_state:
        st.session_state.admin_session_time = datetime.now()

    # Sessiya müddəti yoxlanışı (30 dəqiqə)
    if st.session_state.admin_logged:
        time_diff = datetime.now() - st.session_state.admin_session_time
        if time_diff > timedelta(minutes=30):
            st.session_state.admin_logged = False
            st.warning("Sessiya müddəti bitdi. Yenidən giriş edin.")

    # Admin Panel məzmunu
    if st.session_state.admin_logged:
        # Header və Navigation
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        ">
            <h1 style="color: white; text-align: center; margin: 0;">
                ⚙️ Admin İdarəetmə Paneli
            </h1>
            <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 0.5rem 0 0 0;">
                Ezamiyyət sisteminin tam idarəetməsi
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Session info və çıxış
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.info(f"👋 Xoş gəlmisiniz, Admin! Sessiya: {st.session_state.admin_session_time.strftime('%H:%M')}")
        with col2:
            if st.button("🔄 Sessiya Yenilə"):
                st.session_state.admin_session_time = datetime.now()
                st.success("Sessiya yeniləndi!")
        with col3:
            if st.button("🚪 Çıxış Et", type="secondary"):
                st.session_state.admin_logged = False
                st.rerun()

        # Ana tab bölməsi
        admin_tabs = st.tabs([
            "📊 Dashboard", 
            "🗂️ Məlumat İdarəetməsi", 
            "📥 İdxal/İxrac", 
            "👥 İstifadəçi İdarəetməsi",
            "🔧 Sistem Alətləri"
        ])

        # 1. DASHBOARD TAB
        with admin_tabs[0]:
            # Dashboard content here
            pass

        # 2. DATA MANAGEMENT TAB
        with admin_tabs[1]:
            # Data management content here
            pass

        # 3. IMPORT/EXPORT TAB
        with admin_tabs[2]:
            # Import/export content here
            pass

        # 4. USER MANAGEMENT TAB
        with admin_tabs[3]:
            # User management content here
            pass

        # 5. SYSTEM TOOLS TAB
        with admin_tabs[4]:
            # System tools content here
            pass

    else:
        st.warning("🔐 Admin paneli üçün giriş tələb olunur")
        
        # Admin giriş forması
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form("admin_login_form"):
                    admin_user = st.text_input("👤 İstifadəçi adı", placeholder="admin")
                    admin_pass = st.text_input("🔒 Şifrə", type="password", placeholder="••••••••")
                    
                    submitted = st.form_submit_button("🚀 Giriş Et", use_container_width=True)
                    
                    if submitted:
                        if admin_user == "admin" and admin_pass == "admin123":
                            st.session_state.admin_logged = True
                            st.session_state.admin_session_time = datetime.now()
                            st.rerun()
                        else:
                            st.error("❌ Yanlış giriş məlumatları!")

        st.stop()

    # Admin Panel Ana Səhifə
    if st.session_state.admin_logged:
        # Header və Navigation
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        ">
            <h1 style="color: white; text-align: center; margin: 0;">
                ⚙️ Admin İdarəetmə Paneli
            </h1>
            <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 0.5rem 0 0 0;">
                Ezamiyyət sisteminin tam idarəetməsi
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Session info və çıxış
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.info(f"👋 Xoş gəlmisiniz, Admin! Sessiya: {st.session_state.admin_session_time.strftime('%H:%M')}")
        with col2:
            if st.button("🔄 Sessiya Yenilə"):
                st.session_state.admin_session_time = datetime.now()
                st.success("Sessiya yeniləndi!")
        with col3:
            if st.button("🚪 Çıxış Et", type="secondary"):
                st.session_state.admin_logged = False
                st.rerun()

        # Ana tab bölməsi
        admin_tabs = st.tabs([
            "📊 Dashboard", 
            "🗂️ Məlumat İdarəetməsi", 
            "📥 İdxal/İxrac", 
            "👥 İstifadəçi İdarəetməsi",
            "🔧 Sistem Alətləri"
        ])


# 1. DASHBOARD TAB
with admin_tabs[0]:
    try:
        df = load_trip_data()
        
        if not df.empty:
            # Tarixi sütunları düzəlt
            if 'Tarix' in df.columns:
                df['Tarix'] = pd.to_datetime(df['Tarix'], errors='coerce')
            if 'Başlanğıc tarixi' in df.columns:
                df['Başlanğıc tarixi'] = pd.to_datetime(df['Başlanğıc tarixi'], errors='coerce')
            
            # Rəqəmsal sütunları düzəlt
            numeric_cols = ['Ümumi məbləğ', 'Günlük müavinət', 'Bilet qiyməti']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Əsas metrikalar
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                # Interaktiv tarix seçimi ilə trend analizi
                st.markdown("### 📈 Xərclərin Zaman üzrə Dəyişimi")
                
                date_col = 'Başlanğıc tarixi' if 'Başlanğıc tarixi' in df.columns else 'Tarix'
                df[date_col] = pd.to_datetime(df[date_col])
                
                # Tarix aralığı seçimi
                min_date = df[date_col].min().date()
                max_date = df[date_col].max().date()
                selected_dates = st.date_input(
                    "Tarix aralığını seçin",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )

                
                # Filtrə görə məlumat
                filtered_df = df[
                    (df[date_col].dt.date >= selected_dates[0]) & 
                    (df[date_col].dt.date <= selected_dates[1])
                ]
                
                # Xərc trendləri
                weekly_data = filtered_df.set_index(date_col).resample('W')['Ümumi məbləğ'].sum().reset_index()
                fig = px.line(
                    weekly_data,
                    x=date_col,
                    y='Ümumi məbləğ',
                    title='Həftəlik Xərc Trendləri',
                    markers=True,
                    line_shape='spline',
                    template='plotly_white'
                )

                fig.update_traces(
                    line=dict(width=3, color='#6366f1'),
                    marker=dict(size=8, color='#8b5cf6')
                )
                fig.update_layout(
                    hoverlabel=dict(bgcolor="white", font_size=12),
                    xaxis_title='',
                    yaxis_title='Ümumi Xərc (AZN)'
                )
                st.plotly_chart(fig, use_container_width=True)

            
                # Rəqəmsal olmayan sütunları sil
                numeric_df = filtered_df.select_dtypes(include=['number'])
                if not numeric_df.empty:
                    weekly_data = numeric_df.resample('W', on=date_col).sum().reset_index()
                else:
                    st.warning("Hesablama üçün rəqəmsal məlumat yoxdur")


            with col2:
                # Şöbələr üzrə interaktiv treemap
                st.markdown("### 🌳 Şöbə Xərcləri")
                
                fig = px.treemap(
                    df,
                    path=['Şöbə'],
                    values='Ümumi məbləğ',
                    color='Ümumi məbləğ',
                    color_continuous_scale='Blues',
                    hover_data=['Ezamiyyət növü', 'Günlər']
                )
                fig.update_layout(
                    margin=dict(t=30, l=0, r=0, b=0),
                    height=500
                )
                fig.update_traces(
                    textinfo='label+value+percent parent',
                    texttemplate='<b>%{label}</b><br>%{value:.2f} AZN<br>(%{percentParent:.1%})'
                )
                st.plotly_chart(fig, use_container_width=True)

            # Yeni interaktiv heatmap
            st.markdown("### 🔥 Aylıq Aktivlik Xəritəsi")
            
            heatmap_df = df.copy()
            heatmap_df['Ay'] = heatmap_df[date_col].dt.month_name()
            heatmap_df['Həftənin Günü'] = heatmap_df[date_col].dt.day_name()
            heatmap_df['Həftə'] = heatmap_df[date_col].dt.isocalendar().week
            
            fig = px.density_heatmap(
                heatmap_df,
                x='Həftənin Günü',
                y='Ay',
                z='Ümumi məbləğ',
                histfunc='sum',
                color_continuous_scale='YlGnBu',
                category_orders={
                    "Həftənin Günü": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    "Ay": ["January", "February", "March", "April", "May", "June", 
                           "July", "August", "September", "October", "November", "December"]
                }
            )
            fig.update_layout(
                xaxis_title='',
                yaxis_title='',
                coloraxis_colorbar=dict(title='Ümumi Xərc')
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("📭 Hələ heç bir ezamiyyət qeydiyyatı yoxdur")
            
    except Exception as e:
        st.error(f"❌ Dashboard yüklənərkən xəta: {str(e)}")

# 2. ANALİTİKA TAB yeniləməsi
with admin_tabs[2]:
    st.markdown("### 📈 Detallı Analitika və Hesabatlar")
    
    try:
        df = load_trip_data()
        
        if not df.empty:
            # Yeni interaktiv scatter matrix
            st.markdown("#### 🔍 Çoxölçülü Analiz")
            
            numeric_cols = ['Ümumi məbləğ', 'Günlər', 'Günlük müavinət', 'Bilet qiyməti']
            selected_cols = st.multiselect(
                "Analiz üçün sütunları seçin",
                numeric_cols,
                default=numeric_cols[:3]
            )
            
            if len(selected_cols) >= 2:
                fig = px.scatter_matrix(
                    df,
                    dimensions=selected_cols,
                    color='Ezamiyyət növü',
                    hover_name='Marşrut',
                    title='Parametr Arası Əlaqələr'
                )
                fig.update_traces(
                    diagonal_visible=False,
                    showupperhalf=False,
                    marker=dict(size=4, opacity=0.6)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Minimum 2 ədəd rəqəmsal sütun seçin")

            # Dinamik filtrlənə bilən box plot
            st.markdown("#### 📦 Xərc Paylanması")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                group_by = st.selectbox(
                    "Qruplaşdırma üçün sütun",
                    ['Ezamiyyət növü', 'Şöbə', 'Ödəniş növü']
                )
                log_scale = st.checkbox("Loqarifmik miqyas")
                
            with col2:
                fig = px.box(
                    df,
                    x=group_by,
                    y='Ümumi məbləğ',
                    color=group_by,
                    points="all",
                    hover_data=['Ad', 'Soyad'],
                    log_y=log_scale
                )
                fig.update_layout(
                    showlegend=False,
                    xaxis_title='',
                    yaxis_title='Ümumi Xərc (AZN)'
                )
                st.plotly_chart(fig, use_container_width=True)

            # Dinamik map vizualizasiyası (əlavə məlumat tələb edir)
            st.markdown("#### 🌍 Coğrafi Xərc Xəritəsi")
            
            # Geokoordinatlar üçün nümunə məlumat (əlavə edilməlidir)
            geo_df = pd.DataFrame({
                'Şəhər': ['Bakı', 'Gəncə', 'Sumqayıt'],
                'Lat': [40.4093, 40.6828, 40.5897],
                'Lon': [49.8671, 46.3606, 49.6686],
                'Ümumi Xərc': [df[df['Marşrut'].str.contains(city)]['Ümumi məbləğ'].sum() 
                              for city in ['Bakı', 'Gəncə', 'Sumqayıt']]
            })
            
            fig = px.scatter_geo(
                geo_df,
                lat='Lat',
                lon='Lon',
                size='Ümumi Xərc',
                hover_name='Şəhər',
                projection='natural earth',
                title='Şəhərlər üzrə xərclər'
            )
            fig.update_geos(
                resolution=50,
                showcountries=True,
                countrycolor="Black"
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("📊 Analiz üçün məlumat yoxdur")
            
    except Exception as e:
        st.error(f"❌ Analitika xətası: {str(e)}")

# 2. MƏLUMAT İDARƏETMƏSİ TAB hissəsindəki kodu aşağıdakı kimi düzəldin:

with admin_tabs[1]:
    st.markdown("### 🗂️ Məlumatların İdarə Edilməsi")
    
    try:
        df = load_trip_data()
        
        if not df.empty:
            # Tarix sütunlarını avtomatik çevir
            date_columns = ['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')

            # Filtr və axtarış seçimləri
            st.markdown("#### 🔍 Filtr və Axtarış")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                date_filter = st.selectbox(
                    "📅 Tarix filtri",
                    ["Hamısı", "Son 7 gün", "Son 30 gün", "Son 3 ay", "Bu il", "Seçilmiş aralıq"]
                )
                
                if date_filter == "Seçilmiş aralıq":
                    start_date = st.date_input("Başlanğıc tarixi")
                    end_date = st.date_input("Bitmə tarixi")
            
            with col2:
                if 'Şöbə' in df.columns:
                    departments = ["Hamısı"] + sorted(df['Şöbə'].unique().tolist())
                    selected_dept = st.selectbox("🏢 Şöbə filtri", departments)
            
            with col3:
                if 'Ezamiyyət növü' in df.columns:
                    trip_types = ["Hamısı"] + df['Ezamiyyət növü'].unique().tolist()
                    selected_type = st.selectbox("✈️ Ezamiyyət növü", trip_types)
            
            search_term = st.text_input("🔎 Ad və ya soyad üzrə axtarış")

            # Filtirləmə məntiqi
            filtered_df = df.copy()
            if date_filter != "Hamısı" and 'Tarix' in df.columns:
                if date_filter == "Seçilmiş aralıq":
                    filtered_df = filtered_df[
                        (filtered_df['Tarix'].dt.date >= start_date) & 
                        (filtered_df['Tarix'].dt.date <= end_date)
                    ]
                else:
                    now = datetime.now()
                    if date_filter == "Son 7 gün":
                        cutoff = now - timedelta(days=7)
                    elif date_filter == "Son 30 gün":
                        cutoff = now - timedelta(days=30)
                    elif date_filter == "Son 3 ay":
                        cutoff = now - timedelta(days=90)
                    elif date_filter == "Bu il":
                        cutoff = datetime(now.year, 1, 1)
                    filtered_df = filtered_df[filtered_df['Tarix'] >= cutoff]

            if selected_dept != "Hamısı" and 'Şöbə' in df.columns:
                filtered_df = filtered_df[filtered_df['Şöbə'] == selected_dept]

            if selected_type != "Hamısı" and 'Ezamiyyət növü' in df.columns:
                filtered_df = filtered_df[filtered_df['Ezamiyyət növü'] == selected_type]

            if search_term:
                mask = filtered_df['Ad'].str.contains(search_term, case=False, na=False) | filtered_df['Soyad'].str.contains(search_term, case=False, na=False)
                filtered_df = filtered_df[mask]

                    
                    edited_df = st.data_editor(
                        display_df,
                        column_config=column_config,
                        use_container_width=True,
                        height=600,
                        key="admin_data_editor"
                    )
                    
                    # Dəyişiklikləri saxla
                    if st.button("💾 Dəyişiklikləri Saxla", type="primary"):
                        try:
                            # Tarix sütunlarını formatla
                            for col in date_columns:
                                if col in edited_df.columns:
                                    edited_df[col] = pd.to_datetime(edited_df[col], errors='coerce')
                            
                            # Əsas dataframe-i yenilə
                            df.update(edited_df)
                            
                            # Faylı saxla
                            df.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                            st.success("✅ Dəyişikliklər saxlanıldı!")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Saxlama xətası: {str(e)}")
                
                else:
                    st.warning("Zəhmət olmasa göstəriləcək sütunları seçin")
            
            else:
                st.info("🔍 Filtrə uyğun qeyd tapılmadı")
        
        else:
            st.warning("📭 Hələ heç bir məlumat yoxdur")
            
    except Exception as e:
        st.error(f"❌ Məlumat idarəetməsi xətası: {str(e)}")       
        
# 4. İDXAL/İXRAC TAB
        with admin_tabs[3]:
            st.markdown("### 📥 Məlumat İdxal/İxrac Mərkəzi")
            
            col1, col2 = st.columns(2)
            
            # İXRAC BÖLÜMÜ
            with col1:
                st.markdown("#### 📤 İxrac Seçimləri")
                
                try:
                    df = load_trip_data()
                    
                    if not df.empty:
                        # Format seçimi
                        export_format = st.selectbox(
                            "📄 Fayl formatı",
                            ["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"],
                            help="İxrac ediləcək fayl formatını seçin"
                        )
                        
                        # Tarix aralığı seçimi
                        st.markdown("##### 📅 Tarix Aralığı")
                        col_a, col_b = st.columns(2)
                        with col_a:
                            start_date = st.date_input(
                                "Başlanğıc tarixi", 
                                value=datetime.now() - timedelta(days=30),
                                help="İxrac ediləcək məlumatların başlanğıc tarixi"
                            )
                        with col_b:
                            end_date = st.date_input(
                                "Bitmə tarixi", 
                                value=datetime.now(),
                                help="İxrac ediləcək məlumatların bitmə tarixi"
                            )
                        
                        # Sütun seçimi
                        st.markdown("##### 📊 Sütun Seçimi")
                        all_columns = df.columns.tolist()
                        selected_cols = st.multiselect(
                            "İxrac ediləcək sütunlar",
                            all_columns,
                            default=all_columns,
                            help="İxrac ediləcək sütunları seçin"
                        )
                        
                        # Filtrlər
                        st.markdown("##### 🔍 Əlavə Filtrlər")
                        if 'Şöbə' in df.columns:
                            departments = df['Şöbə'].unique().tolist()
                            selected_depts = st.multiselect(
                                "Şöbə filtri",
                                departments,
                                default=departments,
                                help="Müəyyən şöbələri seçin"
                            )
                        
                        # İxrac düyməsi
                        if st.button("📤 İxrac Et", type="primary", use_container_width=True):
                            if not selected_cols:
                                st.error("❌ Ən azı bir sütun seçin!")
                            elif start_date > end_date:
                                st.error("❌ Başlanğıc tarixi bitmə tarixindən böyük ola bilməz!")
                            else:
                                with st.spinner("İxrac edilir..."):
                                    success = export_data(df, export_format, start_date, end_date, 
                                                       selected_cols, selected_depts if 'Şöbə' in df.columns else None)
                                    if success:
                                        st.balloons()
                    else:
                        st.info("📝 İxrac üçün məlumat yoxdur")
                        st.markdown("İlk öncə məlumat əlavə edin və ya idxal edin.")
                
                except Exception as e:
                    st.error(f"❌ İxrac xətası: {str(e)}")
                    with st.expander("🔍 Xəta təfərrüatları"):
                        st.code(str(e))
            
            # İDXAL BÖLÜMÜ
            with col2:
                st.markdown("#### 📥 İdxal Seçimləri")
                
                uploaded_file = st.file_uploader(
                    "📎 Fayl seçin",
                    type=['xlsx', 'csv', 'json'],
                    help="Excel (.xlsx), CSV (.csv) və ya JSON (.json) formatında faylları idxal edə bilərsiniz"
                )
                
                if uploaded_file is not None:
                    try:
                        # Fayl məlumatları
                        file_details = {
                            "Fayl adı": uploaded_file.name,
                            "Fayl ölçüsü": f"{uploaded_file.size / 1024:.2f} KB",
                            "Fayl tipi": uploaded_file.type
                        }
                        
                        with st.expander("📋 Fayl məlumatları"):
                            for key, value in file_details.items():
                                st.write(f"**{key}:** {value}")
                        
                        # Faylı oxu
                        new_df = read_uploaded_file(uploaded_file)
                        
                        if new_df is not None:
                            # Məlumat nəzərə alınması
                            st.markdown("##### 👀 İdxal Əvvəli Nəzər")
                            
                            # Məlumat statistikaları
                            col_x, col_y, col_z = st.columns(3)
                            with col_x:
                                st.metric("📊 Qeyd sayı", len(new_df))
                            with col_y:
                                st.metric("📈 Sütun sayı", len(new_df.columns))
                            with col_z:
                                st.metric("💾 Ölçü", f"{new_df.memory_usage().sum() / 1024:.1f} KB")
                            
                            # Məlumat nümunəsi
                            st.dataframe(new_df.head(10), use_container_width=True)
                            
                            # Sütun məlumatları
                            with st.expander("📊 Sütun təfərrüatları"):
                                for col in new_df.columns:
                                    null_count = new_df[col].isnull().sum()
                                    data_type = str(new_df[col].dtype)
                                    st.write(f"**{col}:** {data_type} - {null_count} boş qeyd")
                            
                            # İdxal seçimləri
                            st.markdown("##### ⚙️ İdxal Seçimləri")
                            import_mode = st.radio(
                                "İdxal rejimi",
                                ["Əlavə et", "Əvəzlə", "Birləşdir"],
                                help="Əlavə et: Mövcud məlumatlarla birləşdir\n"
                                     "Əvəzlə: Mövcud məlumatları sil və yenilərini əlavə et\n"
                                     "Birləşdir: Dublikatları birləşdir"
                            )
                            
                            # Məlumat validasiyası seçimi
                            validate_data = st.checkbox(
                                "Məlumat validasiyası et",
                                value=True,
                                help="İdxal zamanı məlumat keyfiyyətini yoxla"
                            )
                            
                            # İdxal düyməsi
                            if st.button("📥 İdxal Et", type="primary", use_container_width=True):
                                with st.spinner("İdxal edilir..."):
                                    success = import_data(new_df, import_mode, validate_data)
                                    if success:
                                        st.balloons()
                                        st.info("🔄 Dəyişikliklərin görünməsi üçün səhifəni yeniləyin")
                    
                    except Exception as e:
                        st.error(f"❌ Fayl oxuma xətası: {str(e)}")
                        with st.expander("🔍 Xəta təfərrüatları"):
                            st.code(str(e))

        # 5. SİSTEM PARAMETRLƏRİ TAB
        with admin_tabs[4]:
            st.markdown("### ⚙️ Sistem Konfiqurasiyası")
            
            # Mövcud konfiqurasiya yüklə
            current_config = load_system_config()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎨 İnterfeys Parametrləri")
                
                # Tema seçimi
                theme_color = st.selectbox(
                    "🎨 Tema rəngi",
                    ["Mavi", "Yaşıl", "Qırmızı", "Bənövşəyi", "Qara"],
                    index=["Mavi", "Yaşıl", "Qırmızı", "Bənövşəyi", "Qara"].index(current_config.get("theme_color", "Mavi"))
                )
                
                # Dil seçimi
                language = st.selectbox(
                    "🌐 Sistem dili",
                    ["Azərbaycan", "English", "Русский"],
                    index=["Azərbaycan", "English", "Русский"].index(current_config.get("language", "Azərbaycan"))
                )
                
                # Valyuta
                currency = st.selectbox(
                    "💰 Valyuta",
                    ["AZN", "USD", "EUR", "TRY"],
                    index=["AZN", "USD", "EUR", "TRY"].index(current_config.get("currency", "AZN"))
                )
                
                # Tarix formatı
                date_format = st.selectbox(
                    "📅 Tarix formatı",
                    ["DD.MM.YYYY", "MM/DD/YYYY", "YYYY-MM-DD"],
                    index=["DD.MM.YYYY", "MM/DD/YYYY", "YYYY-MM-DD"].index(current_config.get("date_format", "DD.MM.YYYY"))
                )
                
                # Zaman formatı
                time_format = st.selectbox(
                    "🕐 Zaman formatı",
                    ["24 saat", "12 saat"],
                    index=["24 saat", "12 saat"].index(current_config.get("time_format", "24 saat"))
                )
            
            with col2:
                st.markdown("#### 📊 Məlumat Parametrləri")
                
                # Səhifə başına qeyd sayı
                records_per_page = st.slider(
                    "📄 Səhifə başına qeyd sayı",
                    min_value=10,
                    max_value=100,
                    value=current_config.get("records_per_page", 20),
                    step=5
                )
                
                # Avtomatik backup
                auto_backup = st.checkbox(
                    "💾 Avtomatik backup",
                    value=current_config.get("auto_backup", True)
                )
                
                if auto_backup:
                    backup_frequency = st.selectbox(
                        "🔄 Backup tezliyi",
                        ["Gündəlik", "Həftəlik", "Aylıq"],
                        index=["Gündəlik", "Həftəlik", "Aylıq"].index(current_config.get("backup_frequency", "Həftəlik"))
                    )
                    
                    backup_location = st.text_input(
                        "📂 Backup qovluğu",
                        value=current_config.get("backup_location", "./backups/"),
                        help="Backup fayllarının saxlanacağı qovluq"
                    )
                
                # Məlumat saxlama müddəti
                data_retention = st.slider(
                    "📦 Məlumat saxlama müddəti (ay)",
                    min_value=6,
                    max_value=120,
                    value=current_config.get("data_retention", 24),
                    step=6
                )
                
                # Performans parametrləri
                st.markdown("##### ⚡ Performans")
                
                cache_enabled = st.checkbox(
                    "🗄️ Cache aktiv",
                    value=current_config.get("cache_enabled", True),
                    help="Məlumat yaddaşa alınaraq sürət artırılır"
                )
                
                if cache_enabled:
                    cache_duration = st.slider(
                        "Cache müddəti (dəqiqə)",
                        min_value=1,
                        max_value=60,
                        value=current_config.get("cache_duration", 15)
                    )
            
            # Bildiriş parametrləri
            st.markdown("#### 🔔 Bildiriş Parametrləri")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("##### 📧 Email")
                email_notifications = st.checkbox(
                    "Email bildirişləri",
                    value=current_config.get("email_notifications", True)
                )
                if email_notifications:
                    admin_email = st.text_input(
                        "Admin email",
                        value=current_config.get("admin_email", "admin@company.com")
                    )
                    email_frequency = st.selectbox(
                        "Email tezliyi",
                        ["Dərhal", "Gündəlik", "Həftəlik"],
                        index=["Dərhal", "Gündəlik", "Həftəlik"].index(current_config.get("email_frequency", "Gündəlik"))
                    )
            
            with col2:
                st.markdown("##### 📱 SMS")
                sms_notifications = st.checkbox(
                    "SMS bildirişləri",
                    value=current_config.get("sms_notifications", False)
                )
                if sms_notifications:
                    admin_phone = st.text_input(
                        "Admin telefon",
                        value=current_config.get("admin_phone", "+994xxxxxxxxx")
                    )
                    sms_provider = st.selectbox(
                        "SMS provayderi",
                        ["Azercell", "Bakcell", "Nar"],
                        index=["Azercell", "Bakcell", "Nar"].index(current_config.get("sms_provider", "Azercell"))
                    )
            
            with col3:
                st.markdown("##### 🔔 Sistem")
                system_notifications = st.checkbox(
                    "Sistem bildirişləri",
                    value=current_config.get("system_notifications", True)
                )
                if system_notifications:
                    notification_sound = st.checkbox(
                        "Bildiriş səsi",
                        value=current_config.get("notification_sound", True)
                    )
                    notification_popup = st.checkbox(
                        "Popup bildirişlər",
                        value=current_config.get("notification_popup", True)
                    )
            
            # Təhlükəsizlik parametrləri
            st.markdown("#### 🔒 Təhlükəsizlik Parametrləri")
            
            col1, col2 = st.columns(2)
            
            with col1:
                session_timeout = st.slider(
                    "🕐 Sessiya müddəti (dəqiqə)",
                    min_value=15,
                    max_value=480,
                    value=current_config.get("session_timeout", 120)
                )
                
                max_login_attempts = st.slider(
                    "🔐 Maksimum giriş cəhdi",
                    min_value=3,
                    max_value=10,
                    value=current_config.get("max_login_attempts", 5)
                )
            
            with col2:
                password_complexity = st.checkbox(
                    "🔑 Şifrə mürəkkəbliyi",
                    value=current_config.get("password_complexity", True)
                )
                
                two_factor_auth = st.checkbox(
                    "📱 İki faktorlu autentifikasiya",
                    value=current_config.get("two_factor_auth", False)
                )
            
            # Parametrləri saxla
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if st.button("💾 Parametrləri Saxla", type="primary", use_container_width=True):
                    config_data = {
                        "theme_color": theme_color,
                        "language": language,
                        "currency": currency,
                        "date_format": date_format,
                        "time_format": time_format,
                        "records_per_page": records_per_page,
                        "auto_backup": auto_backup,
                        "backup_frequency": backup_frequency if auto_backup else None,
                        "backup_location": backup_location if auto_backup else None,
                        "data_retention": data_retention,
                        "cache_enabled": cache_enabled,
                        "cache_duration": cache_duration if cache_enabled else None,
                        "email_notifications": email_notifications,
                        "admin_email": admin_email if email_notifications else None,
                        "email_frequency": email_frequency if email_notifications else None,
                        "sms_notifications": sms_notifications,
                        "admin_phone": admin_phone if sms_notifications else None,
                        "sms_provider": sms_provider if sms_notifications else None,
                        "system_notifications": system_notifications,
                        "notification_sound": notification_sound if system_notifications else None,
                        "notification_popup": notification_popup if system_notifications else None,
                        "session_timeout": session_timeout,
                        "max_login_attempts": max_login_attempts,
                        "password_complexity": password_complexity,
                        "two_factor_auth": two_factor_auth,
                        "last_updated": datetime.now().isoformat()
                    }
                    
                    if save_system_config(config_data):
                        st.success("✅ Sistem parametrləri uğurla saxlanıldı!")
                        st.info("🔄 Bəzi dəyişikliklər səhifə yenilənəndən sonra tətbiq olunacaq")
                    else:
                        st.error("❌ Parametrləri saxlamaq mümkün olmadı!")

        # 6. İSTİFADƏÇİ İDARƏETMƏSİ TAB
        with admin_tabs[5]:
            st.markdown("### 👥 İstifadəçi İdarəetməsi")
            
            # Mevcut istifadəçi statistikaları
            try:
                df = load_trip_data()
                
                if not df.empty and 'Ad' in df.columns:
                    user_stats = df.groupby(['Ad', 'Soyad']).agg({
                        'Ümumi məbləğ': ['sum', 'count', 'mean'],
                        'Tarix': 'max'
                    }).round(2) if 'Tarix' in df.columns else df.groupby(['Ad', 'Soyad']).agg({
                        'Ümumi məbləğ': ['sum', 'count', 'mean']
                    }).round(2)
                    
                    user_stats.columns = ['Ümumi Xərc', 'Ezamiyyət Sayı', 'Orta Xərc'] + (['Son Ezamiyyət'] if 'Tarix' in df.columns else [])
                    user_stats = user_stats.sort_values('Ümumi Xərc', ascending=False)
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("#### 📊 İstifadəçi Statistikaları")
                        st.dataframe(
                            user_stats.style.format({
                                'Ümumi Xərc': '{:.2f} AZN',
                                'Orta Xərc': '{:.2f} AZN'
                            }),
                            use_container_width=True
                        )
                    
                    with col2:
                        st.markdown("#### 📈 Top İstifadəçilər")
                        top_users = user_stats.head(10)
                        fig = px.bar(
                            x=top_users['Ümumi Xərc'],
                            y=[f"{idx[0]} {idx[1]}" for idx in top_users.index],
                            orientation='h',
                            title="Ən Çox Xərc Edən İstifadəçilər"
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                
                else:
                    st.info("👤 Hələ qeydiyyatlı istifadəçi yoxdur")
                    
            except Exception as e:
                st.error(f"❌ İstifadəçi statistikaları xətası: {str(e)}")
            
            # İstifadəçi idarəetmə alətləri
            st.markdown("#### 🔧 İstifadəçi Alətləri")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📧 Bildiriş Göndər"):
                    st.info("📨 Kütləvi bildiriş funksionallığı əlavə ediləcək")
            
            with col2:
                if st.button("📊 Həftəlik Hesabat"):
                    st.info("📈 Avtomatik hesabat funksionallığı əlavə ediləcək")
            
            with col3:
                if st.button("🔄 Məlumat Sinxronizasiyası"):
                    st.info("🔗 Xarici sistemlərlə sinxronizasiya əlavə ediləcək")

# Admin Panel Ana Səhifə
# Admin Panel Ana Səhifə
if st.session_state.admin_logged:
    # Header və Navigation
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    ">
        <h1 style="color: white; text-align: center; margin: 0;">
            ⚙️ Admin İdarəetmə Paneli
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Session info və çıxış
    col1, col2, col3 = st.columns([2,1,1])
    with col1: st.info(f"👋 Admin: {st.session_state.admin_session_time.strftime('%H:%M')}")
    with col2: 
        if st.button("🔄 Yenilə"): 
            st.session_state.admin_session_time = datetime.now()
            st.rerun()
    with col3: 
        if st.button("🚪 Çıxış"):
            st.session_state.admin_logged = False
            st.rerun()

    # Yenilənmiş Admin Tabs
    admin_tabs = st.tabs([
        "📊 Dashboard",
        "🗂️ Məlumatlar",
        "📥 İdxal/İxrac", 
        "👥 İstifadəçilər",
        "🔧 Alətlər"
    ])

    # 1. DASHBOARD TAB
    with admin_tabs[0]:
        # Dashboard məzmunu əvvəlki kimi qalır
        pass

    # 2. MƏLUMAT İDARƏETMƏSİ TAB
with admin_tabs[1]:
    st.markdown("### 🗂️ Məlumatların İdarə Edilməsi")
    
    try:
        df = load_trip_data()
        
        if not df.empty:
            # Tarix sütunlarını avtomatik çevir
            date_columns = ['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')

            # Filtr və axtarış seçimləri
            st.markdown("#### 🔍 Filtr və Axtarış")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                date_filter = st.selectbox(
                    "📅 Tarix filtri",
                    ["Hamısı", "Son 7 gün", "Son 30 gün", "Son 3 ay", "Bu il"]
                )
            
            with col2:
                if 'Şöbə' in df.columns:
                    departments = ["Hamısı"] + sorted(df['Şöbə'].unique().tolist())
                    selected_dept = st.selectbox("🏢 Şöbə filtri", departments)
                else:
                    selected_dept = "Hamısı"
            
            with col3:
                if 'Ezamiyyət növü' in df.columns:
                    trip_types = ["Hamısı"] + df['Ezamiyyət növü'].unique().tolist()
                    selected_type = st.selectbox("✈️ Ezamiyyət növü", trip_types)
                else:
                    selected_type = "Hamısı"
            
            search_term = st.text_input("🔎 Ad və ya soyad üzrə axtarış")

            # Filtirləmə məntiqi
            filtered_df = df.copy()
            
            # Tarix filtri
            if date_filter != "Hamısı" and 'Tarix' in df.columns:
                now = datetime.now()
                if date_filter == "Son 7 gün":
                    cutoff = now - timedelta(days=7)
                elif date_filter == "Son 30 gün":
                    cutoff = now - timedelta(days=30)
                elif date_filter == "Son 3 ay":
                    cutoff = now - timedelta(days=90)
                elif date_filter == "Bu il":
                    cutoff = datetime(now.year, 1, 1)
                filtered_df = filtered_df[filtered_df['Tarix'] >= cutoff]

            # Şöbə filtri
            if selected_dept != "Hamısı" and 'Şöbə' in df.columns:
                filtered_df = filtered_df[filtered_df['Şöbə'] == selected_dept]

            # Ezamiyyət növü filtri
            if selected_type != "Hamısı" and 'Ezamiyyət növü' in df.columns:
                filtered_df = filtered_df[filtered_df['Ezamiyyət növü'] == selected_type]

            # Axtarış filtri
            if search_term and 'Ad' in filtered_df.columns and 'Soyad' in filtered_df.columns:
                mask = (filtered_df['Ad'].str.contains(search_term, case=False, na=False) | 
                       filtered_df['Soyad'].str.contains(search_term, case=False, na=False))
                filtered_df = filtered_df[mask]

            # Nəticələr
            st.markdown(f"#### 📊 Nəticələr ({len(filtered_df)} qeyd)")
            
            if len(filtered_df) > 0:
                # Sütun konfiqurasiyası
                column_config = {}
                for col in filtered_df.columns:
                    if col in date_columns:
                        column_config[col] = st.column_config.DatetimeColumn(
                            col,
                            format="DD.MM.YYYY HH:mm" if col == 'Tarix' else "DD.MM.YYYY"
                        )
                    elif col in ['Ümumi məbləğ', 'Günlük müavinət', 'Bilet qiyməti']:
                        column_config[col] = st.column_config.NumberColumn(
                            col,
                            format="%.2f AZN"
                        )
                
                edited_df = st.data_editor(
                    filtered_df,
                    column_config=column_config,
                    use_container_width=True,
                    height=600,
                    key="admin_data_editor"
                )
                
                # Dəyişiklikləri saxla
                if st.button("💾 Dəyişiklikləri Saxla", type="primary"):
                    try:
                        # Tarix sütunlarını formatla
                        for col in date_columns:
                            if col in edited_df.columns:
                                edited_df[col] = pd.to_datetime(edited_df[col], errors='coerce')
                        
                        # Əsas dataframe-i yenilə
                        df.update(edited_df)
                        
                        # Faylı saxla
                        df.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                        st.success("✅ Dəyişikliklər saxlanıldı!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Saxlama xətası: {str(e)}")
            
            else:
                st.info("🔍 Filtrə uyğun qeyd tapılmadı")
        
        else:
            st.warning("📭 Hələ heç bir məlumat yoxdur")
            
    except Exception as e:
        st.error(f"❌ Məlumat idarəetməsi xətası: {str(e)}")

    # 3. İDXAL/İXRAC TAB
with admin_tabs[2]:  # İDXAL/İXRAC TAB
    st.markdown("### 📥 Məlumat İdxal/İxrac Mərkəzi")
    
    col1, col2 = st.columns(2)
    
    # İXRAC BÖLÜMÜ
    with col1:
        st.markdown("#### 📤 İxrac Seçimləri")
        
        try:
            df = load_trip_data()
            
            if not df.empty:
                # Format seçimi
                export_format = st.selectbox(
                    "📄 Fayl formatı",
                    ["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"]
                )
                
                # Tarix aralığı seçimi
                st.markdown("##### 📅 Tarix Aralığı")
                col_a, col_b = st.columns(2)
                with col_a:
                    start_date = st.date_input(
                        "Başlanğıc tarixi", 
                        value=datetime.now() - timedelta(days=30)
                    )
                with col_b:
                    end_date = st.date_input(
                        "Bitmə tarixi", 
                        value=datetime.now()
                    )
                
                # İxrac düyməsi
                if st.button("📤 İxrac Et", type="primary", use_container_width=True):
                    if start_date > end_date:
                        st.error("❌ Başlanğıc tarixi bitmə tarixindən böyük ola bilməz!")
                    else:
                        with st.spinner("İxrac edilir..."):
                            # İxrac məntiqini əlavə edin
                            if export_format == "Excel (.xlsx)":
                                buffer = BytesIO()
                                df.to_excel(buffer, index=False)
                                st.download_button(
                                    label="📥 Excel Faylını Yüklə",
                                    data=buffer.getvalue(),
                                    file_name=f"ezamiyyetler_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                            elif export_format == "CSV (.csv)":
                                csv = df.to_csv(index=False)
                                st.download_button(
                                    label="📥 CSV Faylını Yüklə",
                                    data=csv,
                                    file_name=f"ezamiyyetler_{datetime.now().strftime('%Y%m%d')}.csv",
                                    mime="text/csv"
                                )
            else:
                st.info("📝 İxrac üçün məlumat yoxdur")
                
        except Exception as e:
            st.error(f"❌ İxrac xətası: {str(e)}")
    
    # İDXAL BÖLÜMÜ
    with col2:
        st.markdown("#### 📥 İdxal Seçimləri")
        
        uploaded_file = st.file_uploader(
            "📎 Fayl seçin",
            type=['xlsx', 'csv'],
            help="Excel (.xlsx) və ya CSV (.csv) formatında faylları idxal edə bilərsiniz"
        )
        
        if uploaded_file is not None:
            try:
                # Faylı oxu
                if uploaded_file.name.endswith('.xlsx'):
                    new_df = pd.read_excel(uploaded_file)
                else:
                    new_df = pd.read_csv(uploaded_file)
                
                # Məlumat nəzərə alınması
                st.markdown("##### 👀 İdxal Əvvəli Nəzər")
                
                # Məlumat statistikaları
                col_x, col_y = st.columns(2)
                with col_x:
                    st.metric("📊 Qeyd sayı", len(new_df))
                with col_y:
                    st.metric("📈 Sütun sayı", len(new_df.columns))
                
                # Məlumat nümunəsi
                st.dataframe(new_df.head(5), use_container_width=True)
                
                # İdxal seçimləri
                st.markdown("##### ⚙️ İdxal Seçimləri")
                import_mode = st.radio(
                    "İdxal rejimi",
                    ["Əlavə et", "Əvəzlə"],
                    help="Əlavə et: Mövcud məlumatlarla birləşdir\nƏvəzlə: Mövcud məlumatları sil və yenilərini əlavə et"
                )
                
                # İdxal düyməsi
                if st.button("📥 İdxal Et", type="primary", use_container_width=True):
                    with st.spinner("İdxal edilir..."):
                        try:
                            if import_mode == "Əvəzlə":
                                # Köhnə məlumatları əvəzlə
                                new_df.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                            else:
                                # Mövcud məlumatlarla birləşdir
                                existing_df = load_trip_data()
                                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                                combined_df.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                            
                            st.success("✅ İdxal uğurla tamamlandı!")
                            st.balloons()
                            st.info("🔄 Dəyişikliklərin görünməsi üçün səhifəni yeniləyin")
                            
                        except Exception as e:
                            st.error(f"❌ İdxal xətası: {str(e)}")
        
            except Exception as e:
                st.error(f"❌ Fayl oxuma xətası: {str(e)}")

    # 4. İSTİFADƏÇİ İDARƏETMƏSİ TAB
with admin_tabs[3]:  # İSTİFADƏÇİ İDARƏETMƏSİ TAB
    st.markdown("### 👥 İstifadəçi İdarəetməsi")
    
    try:
        df = load_trip_data()
        
        if not df.empty and 'Ad' in df.columns and 'Soyad' in df.columns:
            # İstifadəçi statistikaları
            user_stats = df.groupby(['Ad', 'Soyad']).agg({
                'Ümumi məbləğ': ['sum', 'count', 'mean']
            }).round(2)
            
            user_stats.columns = ['Ümumi Xərc', 'Ezamiyyət Sayı', 'Orta Xərc']
            user_stats = user_stats.sort_values('Ümumi Xərc', ascending=False)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### 📊 İstifadəçi Statistikaları")
                
                # Format edilmiş cədvəl
                formatted_stats = user_stats.copy()
                formatted_stats['Ümumi Xərc'] = formatted_stats['Ümumi Xərc'].apply(lambda x: f"{x:.2f} AZN")
                formatted_stats['Orta Xərc'] = formatted_stats['Orta Xərc'].apply(lambda x: f"{x:.2f} AZN")
                
                st.dataframe(formatted_stats, use_container_width=True)
            
            with col2:
                st.markdown("#### 📈 Top İstifadəçilər")
                top_users = user_stats.head(5)
                
                # Bar chart
                import plotly.express as px
                fig = px.bar(
                    x=top_users['Ümumi Xərc'],
                    y=[f"{idx[0]} {idx[1]}" for idx in top_users.index],
                    orientation='h',
                    title="Ən Çox Xərc Edən İstifadəçilər"
                )
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("👤 Hələ qeydiyyatlı istifadəçi yoxdur")
            
    except Exception as e:
        st.error(f"❌ İstifadəçi statistikaları xətası: {str(e)}")

    # 5. SİSTEM ALƏTLƏRİ TAB
with admin_tabs[4]:  # SİSTEM ALƏTLƏRİ TAB
    st.markdown("### 🔧 Sistem Alətləri")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🧹 Məlumat Təmizliyi")
        
        if st.button("🗑️ Dublikatları Sil", use_container_width=True):
            try:
                df = load_trip_data()
                initial_count = len(df)
                df_clean = df.drop_duplicates()
                final_count = len(df_clean)
                
                if initial_count > final_count:
                    df_clean.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                    st.success(f"✅ {initial_count - final_count} dublikat qeyd silindi!")
                else:
                    st.info("ℹ️ Dublikat qeyd tapılmadı")
                    
            except Exception as e:
                st.error(f"❌ Xəta: {str(e)}")
                
        if st.button("🧽 Boş Qeydləri Sil", use_container_width=True):
            try:
                df = load_trip_data()
                initial_count = len(df)
                df_clean = df.dropna(how='all')  # Tamamilə boş sətirləri sil
                final_count = len(df_clean)
                
                if initial_count > final_count:
                    df_clean.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                    st.success(f"✅ {initial_count - final_count} boş qeyd silindi!")
                else:
                    st.info("ℹ️ Boş qeyd tapılmadı")
                    
            except Exception as e:
                st.error(f"❌ Xəta: {str(e)}")
    
    with col2:
        st.markdown("#### 💾 Backup İdarəetməsi")
        
        if st.button("📦 Backup Yarat", use_container_width=True):
            try:
                df = load_trip_data()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"backup_ezamiyyetler_{timestamp}.xlsx"
                
                # Backup qovluğu yarat
                import os
                os.makedirs("backups", exist_ok=True)
                
                # Backup faylını saxla
                df.to_excel(f"backups/{backup_filename}", index=False)
                st.success(f"✅ Backup yaradıldı: {backup_filename}")
                
            except Exception as e:
                st.error(f"❌ Backup xətası: {str(e)}")
        
        if st.button("📊 Sistem Statistikaları", use_container_width=True):
            try:
                df = load_trip_data()
                
                # Sistem statistikaları
                total_records = len(df)
                total_amount = df['Ümumi məbləğ'].sum() if 'Ümumi məbləğ' in df.columns else 0
                
                st.info(f"""
                📊 **Sistem Statistikaları:**
                - Cəmi qeyd sayı: {total_records}
                - Cəmi xərc: {total_amount:.2f} AZN
                - Orta xərc: {total_amount/total_records if total_records > 0 else 0:.2f} AZN
                """)
                
            except Exception as e:
                st.error(f"❌ Statistika xətası: {str(e)}")
