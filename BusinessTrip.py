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
import lxml # lxml importu var, parser olaraq istifadə edək

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
                if access_code == "admin": # Əsas giriş kodu
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
            # Tarix sütunlarını oxuyarkən çevirmək daha yaxşıdır
            date_cols_to_parse = ['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']
            for col in date_cols_to_parse:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Məlumat yükləmə xətası: {str(e)}")
        return pd.DataFrame()

def check_admin_session():
    if 'admin_session_time' in st.session_state:
        if datetime.now() - st.session_state.admin_session_time > timedelta(minutes=30): #Sessiya müddəti
            st.session_state.admin_logged = False
            return False
    return True

def load_system_config():
    try:
        if os.path.exists("system_config.json"):
            with open("system_config.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except: # Ümumi xəta tutma
        pass # Xəta olsa, boş lüğət qaytar
    return {} # Fayl yoxdursa və ya xəta baş verərsə

def save_system_config(config_data):
    """Sistem konfiqurasiyasını JSON faylına yazır."""
    try:
        with open("system_config.json", "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        st.error(f"Sistem konfiqurasiyasını saxlamaq mümkün olmadı: {e}")
        return False

def write_log(action, details=""):
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "user": "admin" # Buranı daha dinamik etmək olar
        }
        
        log_file = "admin_logs.json"
        logs = []
        
        if os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except json.JSONDecodeError: # Fayl boş və ya korlanıbsa
                logs = []

        logs.append(log_entry)
        
        if len(logs) > 1000: # Logların sayını məhdudlaşdır
            logs = logs[-1000:]
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        pass # Log yazma xətası proqramı dayandırmamalıdır

# load_trip_data funksiyası yuxarıda artıq təyin edilib, ikinci təyinatı silirik.

def calculate_domestic_amount(from_city, to_city):
    """Daxili marşrut üçün bilet qiymətini hesablayır"""
    return DOMESTIC_ROUTES.get((from_city, to_city), 70) # Default dəyər

def calculate_days(start_date, end_date):
    """İki tarix arasındakı günləri hesablayır"""
    if isinstance(start_date, datetime) and isinstance(end_date, datetime):
        return (end_date - start_date).days + 1
    elif isinstance(start_date, pd.Timestamp) and isinstance(end_date, pd.Timestamp):
         return (end_date.to_pydatetime().date() - start_date.to_pydatetime().date()).days + 1
    elif hasattr(start_date, 'date') and hasattr(end_date, 'date'): # datetime.date obyektləri üçün
        return (end_date - start_date).days + 1
    else: # Tarix obyektləri düzgün deyilsə
        return 0


def calculate_total_amount(daily_allowance, days, payment_type, ticket_price=0):
    """Ümumi məbləği hesablayır"""
    return (daily_allowance * days + ticket_price) * PAYMENT_TYPES[payment_type]

def save_trip_data(new_data):
    try:
        df_existing = load_trip_data() # Mövcud datanı yükləyirik
        
        # Tarix sütunlarını datetime obyektinə çeviririk (əgər stringdirsə)
        # new_data-dakı tarixlər artıq date obyektləri olmalıdır (st.date_input-dan gəlir)
        # Amma əgər string formatında saxlanılırsa, çevirmək lazımdır
        if isinstance(new_data.get("Başlanğıc tarixi"), str):
            new_data["Başlanğıc tarixi"] = pd.to_datetime(new_data["Başlanğıc tarixi"]).strftime("%Y-%m-%d")
        elif hasattr(new_data.get("Başlanğıc tarixi"), 'strftime'):
            new_data["Başlanğıc tarixi"] = new_data["Başlanğıc tarixi"].strftime("%Y-%m-%d")

        if isinstance(new_data.get("Bitmə tarixi"), str):
            new_data["Bitmə tarixi"] = pd.to_datetime(new_data["Bitmə tarixi"]).strftime("%Y-%m-%d")
        elif hasattr(new_data.get("Bitmə tarixi"), 'strftime'):
            new_data["Bitmə tarixi"] = new_data["Bitmə tarixi"].strftime("%Y-%m-%d")
            
        df_new_row = pd.DataFrame([new_data])

        if not df_existing.empty:
            df_combined = pd.concat([df_existing, df_new_row], ignore_index=True)
        else:
            df_combined = df_new_row
            
        df_combined.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
        return True
    except Exception as e:
        st.error(f"Yadda saxlama xətası: {str(e)}")
        return False

@st.cache_data(ttl=3600)
def get_currency_rates(date=None):
    try:
        if not date:
            target_date = datetime.now()
        else:
            # Gələn 'date' streamlit tərəfindən datetime.date ola bilər
            if isinstance(date, pd.Timestamp):
                target_date = date.to_pydatetime()
            elif not isinstance(date, datetime):
                 target_date = datetime.combine(date, datetime.min.time())
            else:
                target_date = date

        url = f"https://www.cbar.az/currencies/{target_date.strftime('%d.%m.%Y')}.xml"
        response = requests.get(url)
        response.raise_for_status() # HTTP xətalarını yoxla

        soup = BeautifulSoup(response.content, 'lxml-xml') # lxml-xml parser istifadə edirik
        currencies = []

        for valute in soup.find_all('Valute'):
            nominal_text = valute.find('Nominal').text.strip()
            try:
                nominal = int(nominal_text.split()[0])
            except (ValueError, IndexError):
                nominal = 1 # Əgər nominal parse edilə bilmirsə, default 1 götürək

            currencies.append({
                'Kod': valute['Code'],
                'Valyuta': valute.find('Name').text,
                'Məzənnə': float(valute.find('Value').text.replace(',', '.')),
                'Nominal': nominal
            })

        return pd.DataFrame(currencies)

    except requests.exceptions.RequestException as e:
        st.error(f"Valyuta məlumatları gətirilərkən şəbəkə xətası: {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Valyuta məlumatları gətirilərkən ümumi xəta: {str(e)}")
        return pd.DataFrame()


def export_data_general(df_to_export, format_type): # Bu funksiya birbaşa istifadə olunmur, amma kodda var
    """Verilmiş DataFrame-i göstərilən formatda ixrac edir."""
    try:
        if format_type == "Excel (.xlsx)":
            buffer = BytesIO()
            df_to_export.to_excel(buffer, index=False)
            buffer.seek(0)
            return buffer, f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif format_type == "CSV (.csv)":
            csv_data = df_to_export.to_csv(index=False).encode('utf-8')
            return BytesIO(csv_data), f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv"
        elif format_type == "JSON (.json)":
            json_data = df_to_export.to_json(orient='records').encode('utf-8')
            return BytesIO(json_data), f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "application/json"
        return None, None, None
    except Exception as e:
        st.error(f"İxrac xətası: {str(e)}")
        return None, None, None

def read_uploaded_file(file):
    try:
        if file.name.endswith('.xlsx'):
            return pd.read_excel(file)
        elif file.name.endswith('.csv'):
            return pd.read_csv(file)
        elif file.name.endswith('.json'):
            return pd.read_json(file)
        st.error("Dəstəklənməyən fayl formatı.")
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
                cols_person = st.columns(2) # Ad dəyişikliyi
                with cols_person[0]:
                    first_name = st.text_input("Ad", key="first_name_input")
                    father_name = st.text_input("Ata adı", key="father_name_input")
                with cols_person[1]:
                    last_name = st.text_input("Soyad", key="last_name_input")
                    position = st.text_input("Vəzifə", key="position_input")

            with st.expander("🏢 Təşkilat Məlumatları"):
                department = st.selectbox("Şöbə", DEPARTMENTS, key="department_select")

            with st.expander("🧳 Ezamiyyət Detalları"):
                trip_type = st.radio("Növ", ["Ölkə daxili", "Ölkə xarici"], key="trip_type_radio")
                payment_type = st.selectbox("Ödəniş növü", list(PAYMENT_TYPES.keys()), key="payment_type_select")

                # Bu dəyişənlərə ilkin qiymət mənimsədək
                from_city_val = "Bakı"
                to_city_val = CITIES[1] if len(CITIES) > 1 and CITIES[0] == "Bakı" else (CITIES[0] if CITIES else "")

                if trip_type == "Ölkə daxili":
                    cols_trip_details = st.columns(2) # Ad dəyişikliyi
                    with cols_trip_details[0]:
                        from_city_val = st.selectbox("Haradan", CITIES, index=CITIES.index("Bakı") if "Bakı" in CITIES else 0, key="from_city_select")
                    with cols_trip_details[1]:
                        available_to_cities = [c for c in CITIES if c != from_city_val]
                        if not available_to_cities and CITIES: # Əgər from_city bütün şəhərləri əhatə edirsə və ya tək şəhərdirsə
                           available_to_cities = CITIES # Fallback
                        to_city_val = st.selectbox("Haraya", available_to_cities, key="to_city_select")
                    
                    ticket_price = calculate_domestic_amount(from_city_val, to_city_val)
                    daily_allowance = 70
                    accommodation = "Tətbiq edilmir"
                else: # Ölkə xarici
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
                    base_allowance = COUNTRIES.get(country, 0) # Ölkə tapılmazsa default 0
                    if payment_mode == "Adi rejim":
                        daily_allowance = base_allowance
                    elif payment_mode == "Günlük Normaya 50% əlavə":
                        daily_allowance = base_allowance * 1.5
                    else: # Günlük Normaya 30% əlavə
                        daily_allowance = base_allowance * 1.3
                    ticket_price = 0 # Xarici ezamiyyətlər üçün bilet ayrıca hesablanmır (ümumi məbləğə daxil deyil)
                    from_city_val = "Bakı"
                    to_city_val = country # 'to_city' olaraq ölkəni saxlayaq

                cols_dates = st.columns(2) # Ad dəyişikliyi
                with cols_dates[0]:
                    start_date = st.date_input("Başlanğıc tarixi", value=datetime.now().date(), key="start_date_input")
                with cols_dates[1]:
                    end_date = st.date_input("Bitmə tarixi", value=datetime.now().date() + timedelta(days=1), key="end_date_input")

                purpose = st.text_area("Ezamiyyət məqsədi", key="purpose_textarea")

        # Sağ Sütun (Hesablama)
        with col2:
            with st.container():
                st.markdown('<div class="section-header">💰 Hesablama</div>', unsafe_allow_html=True)

                trip_days = 0
                total_amount = 0
                delta_label = None

                if start_date and end_date and end_date >= start_date:
                    trip_days = calculate_days(start_date, end_date)
                    total_amount_raw = calculate_total_amount(daily_allowance, trip_days, payment_type, ticket_price if trip_type == "Ölkə daxili" else 0)
                    
                    total_amount = total_amount_raw # İlkin dəyər
                    # Qonaqlama əmsalı
                    if trip_type == "Ölkə xarici":
                        if accommodation == "Yalnız yaşayış yeri ilə təmin edir":
                            # Qanunvericiliyə görə: yaşayış yeri təmin edilirsə, günlük normanın 40%-i ödənilir
                            # Amma kodda 1.4-ə vurulur, yəni 40% artım. Bu məntiq saxlanılır.
                            total_amount = total_amount_raw * 1.4 # Yalnız gündəlik xərclər 40% artırılır (əgər məntiq belədirsə)
                                                                # Və ya, əgər yaşayış yeri ödənilirsə, gündəlik xərclərə 40% əlavə edilir.
                                                                # Bu hissə dəqiqləşdirilməlidir. Mövcud kodun məntiqi ilə gedirəm.
                            delta_label = "40% artım (Yaşayış)"
                        elif accommodation == "Yalnız gündəlik xərcləri təmin edir":
                            # Qanunvericiliyə görə: gündəlik xərclər təmin edilirsə, normanın 60%-i otel xərci ödənilir.
                            # Kodda 1.6-ya vurulur, yəni 60% artım. Bu məntiq saxlanılır.
                            total_amount = total_amount_raw * 1.6
                            delta_label = "60% artım (Gündəlik)"
                        # else: Adi rejim, dəyişiklik yoxdur

                st.metric("📅 Günlük müavinət", f"{daily_allowance} AZN", key="daily_allowance_metric")
                if trip_type == "Ölkə daxili":
                    st.metric("🚌 Nəqliyyat xərci", f"{ticket_price} AZN", key="ticket_price_metric")
                st.metric("⏳ Müddət", f"{trip_days} gün", key="trip_days_metric")
                st.metric(
                    "💳 Ümumi məbləğ",
                    f"{total_amount:.2f} AZN",
                    delta=delta_label if delta_label else None, # None göndərmək daha doğrudur
                    delta_color="normal" if delta_label else "off",
                    key="total_amount_metric"
                )

            if st.button("✅ Yadda Saxla", use_container_width=True, key="save_trip_button"):
                if all([first_name, last_name, position, department, start_date, end_date]):
                    if end_date < start_date:
                        st.error("Bitmə tarixi başlanğıc tarixindən əvvəl ola bilməz!")
                    else:
                        trip_data = {
                            "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Ad": first_name,
                            "Soyad": last_name,
                            "Ata adı": father_name,
                            "Vəzifə": position,
                            "Şöbə": department,
                            "Ezamiyyət növü": trip_type,
                            "Ödəniş növü": payment_type,
                            "Qonaqlama növü": accommodation if trip_type == "Ölkə xarici" else "Tətbiq edilmir",
                            "Marşrut": f"{from_city_val} → {to_city_val}",
                            "Bilet qiyməti": ticket_price if trip_type == "Ölkə daxili" else 0,
                            "Günlük müavinət": daily_allowance,
                            "Başlanğıc tarixi": start_date, # Artıq date obyektidir
                            "Bitmə tarixi": end_date,     # Artıq date obyektidir
                            "Günlər": trip_days,
                            "Ümumi məbləğ": total_amount,
                            "Məqsəd": purpose
                        }
                        if save_trip_data(trip_data):
                            st.success("Məlumatlar yadda saxlandı!")
                            # Formanı təmizləmək üçün inputların dəyərlərini sıfırlaya bilərik (əgər lazımdırsa)
                            # st.experimental_rerun() # və ya rerun etmək olar
                        else:
                            st.error("Məlumatları yadda saxlayarkən xəta baş verdi.")
                else:
                    st.error("Zəhmət olmasa bütün məcburi sahələri doldurun (Ad, Soyad, Vəzifə, Şöbə, Tarixlər)!")


# ========== VALYUTA MƏZƏNNƏSİ HISSƏSİ ==========
with st.expander("💱 Valyuta Məzənnələri (Cbar.az)", expanded=True):
    selected_date_currency = st.date_input( # Ayrı key
        "Məzənnə tarixini seçin",
        value=datetime.now().date(),
        max_value=datetime.now().date(),
        format="DD.MM.YYYY",
        key="currency_date_picker"
    )

    if st.button("🔄 Yenilə", help="Son məzənnələri yüklə", key="refresh_currency_btn"):
        st.cache_data.clear() # Cache-i təmizləyirik
        # st.rerun() # Səhifəni yenidən yükləyərək cache-dən təmiz datanı almaq üçün

    try:
        currency_df = get_currency_rates(selected_date_currency)

        if not currency_df.empty:
            st.markdown("""
            <style>
                .light-card {
                    background: rgba(129, 131, 244, 0.1);
                    border: 1px solid rgba(129, 131, 244, 0.2);
                    border-radius: 8px;
                    padding: 0.8rem;
                    margin: 0.3rem;
                    flex: 1 1 30%; /* Daha yaxşı responsive üçün */
                    min-width: 200px; /* Minimum en */
                    transition: all 0.3s ease;
                }
                .light-card:hover {
                    background: rgba(129, 131, 244, 0.15);
                    transform: translateY(-2px); /* Kiçik hover effekti */
                }
                .light-header {
                    color: #8183f4 !important;
                    font-size: 1.1rem !important;
                    font-weight: bold; /* Qalın şrift */
                    margin: 0 !important;
                }
                .light-rate {
                    color: #a78bfa !important;
                    font-size: 1rem !important;
                    font-weight: bold; /* Qalın şrift */
                    margin: 0 !important;
                }
                .currency-desc {
                    color: #777 !important;
                    font-size: 0.75rem !important;
                    margin: 0 !important;
                }
            </style>
            """, unsafe_allow_html=True)

            # Sütun sayını dinamik etmək və ya daha çox məlumat göstərmək
            # st.dataframe(currency_df, use_container_width=True) # Alternativ olaraq cədvəl
            
            cols_currency_display = st.columns(3) # Daha yaxşı görünüm üçün
            currency_groups = [currency_df.iloc[i::len(cols_currency_display)] for i in range(len(cols_currency_display))]


            for idx, col_group in enumerate(currency_groups):
                with cols_currency_display[idx]:
                    for _, row in col_group.iterrows():
                        rate = row['Məzənnə'] / row['Nominal'] if row['Nominal'] != 0 else row['Məzənnə']
                        st.markdown(f"""
                        <div class="light-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <p class="light-header">{row['Kod']}</p>
                                    <p class="currency-desc">{row['Valyuta']}</p>
                                </div>
                                <div style="text-align: right;">
                                    <p class="light-rate">{rate:.4f}</p>
                                    <p class="currency-desc">1 {row['Kod']} = {rate:.4f} AZN</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.warning(f"{selected_date_currency.strftime('%d.%m.%Y')} üçün məzənnə məlumatı tapılmadı.")

    except Exception as e:
        st.error(f"Məzənnə yüklənərkən xəta: {str(e)}")


# Admin Panel hissəsi
with tab2:
    if 'admin_logged' not in st.session_state:
        st.session_state.admin_logged = False
    if 'admin_session_time' not in st.session_state:
        st.session_state.admin_session_time = datetime.now()

    if st.session_state.admin_logged:
        if not check_admin_session(): # check_admin_session funksiyasını çağırırıq
            st.warning("Sessiya müddəti bitdi. Yenidən giriş edin.")
            st.session_state.admin_logged = False # Sessiyanı bitir
            st.rerun() # Səhifəni yeniləyib giriş formasına qaytarır

    if not st.session_state.admin_logged:
        st.warning("🔐 Admin paneli üçün giriş tələb olunur")
        with st.container():
            col_login1, col_login2, col_login3 = st.columns([1, 2, 1])
            with col_login2:
                with st.form("admin_login_form"):
                    admin_user = st.text_input("👤 İstifadəçi adı", placeholder="admin", key="admin_user_input")
                    admin_pass = st.text_input("🔒 Şifrə", type="password", placeholder="••••••••", key="admin_pass_input")
                    submitted = st.form_submit_button("🚀 Giriş Et", use_container_width=True)
                    if submitted:
                        if admin_user == "admin" and admin_pass == "admin123": # Admin giriş məlumatları
                            st.session_state.admin_logged = True
                            st.session_state.admin_session_time = datetime.now()
                            st.rerun()
                        else:
                            st.error("❌ Yanlış giriş məlumatları!")
        st.stop() # Giriş edilməyibsə, qalan kodu icra etmə


    # Admin Panel Ana Səhifəsi (əgər giriş edilibsə)
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

    col_header1, col_header2, col_header3 = st.columns([2,1,1])
    with col_header1: st.info(f"👋 Xoş gəlmisiniz, Admin! Sessiya başlama: {st.session_state.admin_session_time.strftime('%H:%M:%S')}")
    with col_header2:
        if st.button("🔄 Sessiyanı Yenilə", key="refresh_admin_session_btn"): # Unikal key
            st.session_state.admin_session_time = datetime.now()
            st.success("Sessiya yeniləndi!")
            st.rerun()
    with col_header3:
        if st.button("🚪 Çıxış Et", type="secondary", key="admin_logout_btn"): # Unikal key
            st.session_state.admin_logged = False
            # Digər sessiya dəyişənlərini də təmizləmək olar
            if 'admin_session_time' in st.session_state:
                del st.session_state['admin_session_time']
            st.rerun()

    admin_tabs = st.tabs([
        "📊 Dashboard",
        "🗂️ Məlumatlar",
        "📥 İdxal/İxrac",
        "👥 İstifadəçilər",
        "🔧 Alətlər"
    ])

    # 1. DASHBOARD TAB
    with admin_tabs[0]:
        st.markdown("### 📊 Dashboard və Analitika")
        try:
            df_dashboard = load_trip_data()

            if not df_dashboard.empty:
                # Tarix sütunlarını datetime formatına çevir (əgər hələ çevrilməyibsə)
                if 'Tarix' in df_dashboard.columns:
                    df_dashboard['Tarix'] = pd.to_datetime(df_dashboard['Tarix'], errors='coerce')
                if 'Başlanğıc tarixi' in df_dashboard.columns:
                    df_dashboard['Başlanğıc tarixi'] = pd.to_datetime(df_dashboard['Başlanğıc tarixi'], errors='coerce')

                # Rəqəmsal sütunları düzəlt
                numeric_cols_dash = ['Ümumi məbləğ', 'Günlük müavinət', 'Bilet qiyməti', 'Günlər']
                for col in numeric_cols_dash:
                    if col in df_dashboard.columns:
                        df_dashboard[col] = pd.to_numeric(df_dashboard[col], errors='coerce').fillna(0)

                # --- Əsas Dashboard Qrafikləri ---
                st.markdown("#### 📅 Zaman üzrə Trendlər və Paylanmalar")
                dash_col1, dash_col2 = st.columns(2)

                with dash_col1:
                    st.markdown("##### 📈 Xərclərin Zaman üzrə Dəyişimi")
                    date_col_selector = 'Başlanğıc tarixi' if 'Başlanğıc tarixi' in df_dashboard.columns and not df_dashboard['Başlanğıc tarixi'].isnull().all() else 'Tarix'
                    
                    if date_col_selector not in df_dashboard.columns or df_dashboard[date_col_selector].isnull().all():
                        st.warning(f"'{date_col_selector}' sütunu tapılmadı və ya tamamilə boşdur. Trend analizi mümkün deyil.")
                    else:
                        df_dashboard[date_col_selector] = pd.to_datetime(df_dashboard[date_col_selector], errors='coerce')
                        df_trend = df_dashboard.dropna(subset=[date_col_selector, 'Ümumi məbləğ'])

                        min_date_trend = df_trend[date_col_selector].min().date() if not df_trend.empty else datetime.now().date() - timedelta(days=30)
                        max_date_trend = df_trend[date_col_selector].max().date() if not df_trend.empty else datetime.now().date()

                        selected_dates_trend = st.date_input(
                            "Trend üçün tarix aralığını seçin",
                            value=(min_date_trend, max_date_trend) if not df_trend.empty else (datetime.now().date() - timedelta(days=30), datetime.now().date()),
                            min_value=min_date_trend,
                            max_value=max_date_trend,
                            key="dashboard_date_range_trend"
                        )
                        if len(selected_dates_trend) == 2:
                            filtered_df_trend = df_trend[
                                (df_trend[date_col_selector].dt.normalize() >= pd.to_datetime(selected_dates_trend[0])) &
                                (df_trend[date_col_selector].dt.normalize() <= pd.to_datetime(selected_dates_trend[1]))
                            ]
                            if not filtered_df_trend.empty:
                                weekly_data_trend = filtered_df_trend.set_index(date_col_selector).resample('W')['Ümumi məbləğ'].sum().reset_index()
                                fig_trend = px.line(
                                    weekly_data_trend, x=date_col_selector, y='Ümumi məbləğ',
                                    title='Həftəlik Xərc Trendləri', markers=True, line_shape='spline', template='plotly_white'
                                )
                                fig_trend.update_traces(line=dict(width=3, color='#6366f1'), marker=dict(size=8, color='#8b5cf6'))
                                fig_trend.update_layout(hoverlabel=dict(bgcolor="white", font_size=12), xaxis_title='', yaxis_title='Ümumi Xərc (AZN)')
                                st.plotly_chart(fig_trend, use_container_width=True)
                            else:
                                st.info("Seçilmiş tarix aralığında trend üçün məlumat yoxdur.")
                        else:
                            st.warning("Trend üçün düzgün tarix aralığı seçin.")


                with dash_col2:
                    if 'Şöbə' in df_dashboard.columns and 'Ümumi məbləğ' in df_dashboard.columns:
                        st.markdown("##### 🌳 Şöbə Xərcləri (Treemap)")
                        fig_treemap = px.treemap(
                            df_dashboard.dropna(subset=['Şöbə', 'Ümumi məbləğ']),
                            path=['Şöbə'], values='Ümumi məbləğ', color='Ümumi məbləğ',
                            color_continuous_scale='Blues',
                            hover_data=['Ezamiyyət növü', 'Günlər'] if 'Ezamiyyət növü' in df_dashboard.columns and 'Günlər' in df_dashboard.columns else None
                        )
                        fig_treemap.update_layout(margin=dict(t=30, l=0, r=0, b=0), height=500)
                        fig_treemap.update_traces(textinfo='label+value+percent parent', texttemplate='<b>%{label}</b><br>%{value:.2f} AZN<br>(%{percentParent:.1%})')
                        st.plotly_chart(fig_treemap, use_container_width=True)
                    else:
                        st.warning("Treemap üçün 'Şöbə' və ya 'Ümumi məbləğ' sütunları mövcud deyil.")

                if date_col_selector in df_dashboard.columns and 'Ümumi məbləğ' in df_dashboard.columns and not df_dashboard[date_col_selector].isnull().all():
                    st.markdown("##### 🔥 Aylıq Aktivlik Xəritəsi (Heatmap)")
                    heatmap_df = df_dashboard.copy()
                    heatmap_df = heatmap_df.dropna(subset=[date_col_selector, 'Ümumi məbləğ'])
                    
                    # Ensure date_col_selector is datetime
                    heatmap_df[date_col_selector] = pd.to_datetime(heatmap_df[date_col_selector])

                    heatmap_df['Ay'] = heatmap_df[date_col_selector].dt.strftime('%B') # Ay adları
                    heatmap_df['Həftənin Günü'] = heatmap_df[date_col_selector].dt.strftime('%A') # Gün adları
                    
                    # Düzgün sıralama üçün
                    month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    
                    heatmap_df['Ay'] = pd.Categorical(heatmap_df['Ay'], categories=month_order, ordered=True)
                    heatmap_df['Həftənin Günü'] = pd.Categorical(heatmap_df['Həftənin Günü'], categories=day_order, ordered=True)

                    if not heatmap_df.empty:
                        fig_heatmap = px.density_heatmap(
                            heatmap_df, x='Həftənin Günü', y='Ay', z='Ümumi məbləğ',
                            histfunc='sum', color_continuous_scale='YlGnBu',
                            category_orders={"Həftənin Günü": day_order, "Ay": month_order}
                        )
                        fig_heatmap.update_layout(xaxis_title='', yaxis_title='', coloraxis_colorbar=dict(title='Ümumi Xərc'))
                        st.plotly_chart(fig_heatmap, use_container_width=True)
                    else:
                        st.info("Heatmap üçün məlumat yoxdur.")
                else:
                    st.warning("Heatmap üçün kifayət qədər məlumat (tarix və ümumi məbləğ) yoxdur.")


                # --- Detallı Analitika ---
                st.markdown("---")
                st.markdown("#### 🔬 Ətraflı Analiz")

                if 'Ümumi məbləğ' in df_dashboard.columns and 'Günlər' in df_dashboard.columns and \
                   'Günlük müavinət' in df_dashboard.columns and 'Ezamiyyət növü' in df_dashboard.columns:
                    
                    st.markdown("##### 🔍 Çoxölçülü Analiz (Scatter Matrix)")
                    scatter_cols = ['Ümumi məbləğ', 'Günlər', 'Günlük müavinət']
                    # Bilet qiyməti də əlavə oluna bilər, amma çox vaxt 0 olduğu üçün qrafiki poza bilər
                    # if 'Bilet qiyməti' in df_dashboard.columns: scatter_cols.append('Bilet qiyməti')

                    # Seçilmiş sütunların mövcudluğunu yoxla
                    valid_scatter_cols = [col for col in scatter_cols if col in df_dashboard.columns and df_dashboard[col].nunique() > 1]

                    if len(valid_scatter_cols) >= 2:
                        fig_scatter_matrix = px.scatter_matrix(
                            df_dashboard, dimensions=valid_scatter_cols, color='Ezamiyyət növü',
                            hover_name='Marşrut' if 'Marşrut' in df_dashboard.columns else None,
                            title='Parametrler Arası Əlaqələr'
                        )
                        fig_scatter_matrix.update_traces(diagonal_visible=False, showupperhalf=False, marker=dict(size=4, opacity=0.6))
                        st.plotly_chart(fig_scatter_matrix, use_container_width=True)
                    else:
                        st.warning("Scatter matrix üçün kifayət qədər (ən azı 2) dəyişkən rəqəmsal sütun tapılmadı.")

                    st.markdown("##### 📦 Xərc Paylanması (Box Plot)")
                    box_col1, box_col2 = st.columns([1, 3])
                    with box_col1:
                        group_by_box = st.selectbox(
                            "Qruplaşdırma (Box Plot)",
                            [col for col in ['Ezamiyyət növü', 'Şöbə', 'Ödəniş növü'] if col in df_dashboard.columns],
                            key="boxplot_group_by"
                        )
                        log_scale_box = st.checkbox("Loqarifmik miqyas (Box Plot)", key="boxplot_log_scale")
                    
                    if group_by_box:
                        with box_col2:
                            fig_box = px.box(
                                df_dashboard, x=group_by_box, y='Ümumi məbləğ', color=group_by_box,
                                points="all", hover_data=['Ad', 'Soyad'] if 'Ad' in df_dashboard.columns and 'Soyad' in df_dashboard.columns else None,
                                log_y=log_scale_box
                            )
                            fig_box.update_layout(showlegend=False, xaxis_title='', yaxis_title='Ümumi Xərc (AZN)')
                            st.plotly_chart(fig_box, use_container_width=True)
                    else:
                        st.warning("Box plot üçün qruplaşdırma sütunu tapılmadı.")
                else:
                    st.info("Detallı analiz üçün bəzi əsas sütunlar ('Ümumi məbləğ', 'Günlər', 'Günlük müavinət', 'Ezamiyyət növü') çatışmır.")

                # Coğrafi xəritə üçün daha çox məlumat və ya API inteqrasiyası tələb oluna bilər.
                # Sadə bir nümunə olaraq saxlanılıb.
                if 'Marşrut' in df_dashboard.columns and 'Ümumi məbləğ' in df_dashboard.columns:
                    st.markdown("##### 🌍 Coğrafi Xərc Xəritəsi (Nümunə)")
                    # Bu hissə real geokordinatlarla zənginləşdirilməlidir.
                    # Hazırki CITIES listindən istifadə edərək sadə bir demo:
                    geo_data_list = []
                    # Nümunə koordinatlar (dəqiqləşdirilməlidir və ya API-dən alınmalıdır)
                    city_coords = {
                        "Bakı": {"lat": 40.3777, "lon": 49.8920}, "Gəncə": {"lat": 40.6828, "lon": 46.3606},
                        "Sumqayıt": {"lat": 40.5897, "lon": 49.6686}, "Lənkəran": {"lat": 38.7539, "lon": 48.8475},
                        "Şəki": {"lat": 41.1919, "lon": 47.1725}, "Naxçıvan": {"lat": 39.2089, "lon": 45.4123}
                        # ... digər şəhərlər
                    }
                    for city, coords in city_coords.items():
                        total_cost_for_city = df_dashboard[df_dashboard['Marşrut'].str.contains(city, na=False)]['Ümumi məbləğ'].sum()
                        if total_cost_for_city > 0:
                             geo_data_list.append({'Şəhər': city, 'Lat': coords['lat'], 'Lon': coords['lon'], 'Ümumi Xərc': total_cost_for_city})
                    
                    if geo_data_list:
                        geo_df_display = pd.DataFrame(geo_data_list)
                        fig_geo = px.scatter_geo(
                            geo_df_display, lat='Lat', lon='Lon', size='Ümumi Xərc',
                            hover_name='Şəhər', projection='natural earth', title='Şəhərlər üzrə Xərclər (Nümunə)'
                        )
                        fig_geo.update_geos(resolution=50, showcountries=True, countrycolor="RebeccaPurple", landcolor="LightGreen", showland=True)
                        st.plotly_chart(fig_geo, use_container_width=True)
                    else:
                        st.info("Coğrafi xəritə üçün məlumat (koordinatlı şəhərlər üzrə xərclər) tapılmadı.")
                else:
                    st.warning("Coğrafi analiz üçün 'Marşrut' və 'Ümumi məbləğ' sütunları tələb olunur.")

            else: # df_dashboard.empty
                st.warning("📭 Dashboard üçün heç bir ezamiyyət qeydiyyatı yoxdur.")
        except Exception as e:
            st.error(f"❌ Dashboard yüklənərkən xəta: {str(e)}")
            st.exception(e) # Daha detallı xəta məlumatı üçün

    # 2. MƏLUMAT İDARƏETMƏSİ TAB
    with admin_tabs[1]:
        st.markdown("### 🗂️ Məlumatların İdarə Edilməsi")
        try:
            df_manage = load_trip_data()

            if not df_manage.empty:
                # Tarix sütunları artıq load_trip_data-da çevrilir

                st.markdown("#### 🔍 Filtr və Axtarış")
                m_col1, m_col2, m_col3 = st.columns(3)
                
                with m_col1:
                    date_filter_manage = st.selectbox(
                        "📅 Tarix filtri",
                        ["Hamısı", "Son 7 gün", "Son 30 gün", "Son 3 ay", "Bu il", "Seçilmiş aralıq"],
                        key="manage_date_filter"
                    )
                    start_date_manage, end_date_manage = None, None
                    if date_filter_manage == "Seçilmiş aralıq":
                        start_date_manage = st.date_input("Başlanğıc tarixi (Filtr)", value=datetime.now().date() - timedelta(days=30), key="manage_start_date")
                        end_date_manage = st.date_input("Bitmə tarixi (Filtr)", value=datetime.now().date(), key="manage_end_date")

                with m_col2:
                    selected_dept_manage = "Hamısı"
                    if 'Şöbə' in df_manage.columns:
                        departments_manage = ["Hamısı"] + sorted(list(df_manage['Şöbə'].dropna().unique()))
                        selected_dept_manage = st.selectbox("🏢 Şöbə filtri", departments_manage, key="manage_dept_filter")

                with m_col3:
                    selected_type_manage = "Hamısı"
                    if 'Ezamiyyət növü' in df_manage.columns:
                        trip_types_manage = ["Hamısı"] + list(df_manage['Ezamiyyət növü'].dropna().unique())
                        selected_type_manage = st.selectbox("✈️ Ezamiyyət növü", trip_types_manage, key="manage_type_filter")

                search_term_manage = st.text_input("🔎 Ad, Soyad və ya Vəzifə üzrə axtarış", key="manage_search_term")

                filtered_df_manage = df_manage.copy()

                # Tarix filtri
                date_col_for_filter = 'Tarix' # Əsas qeyd tarixi
                if date_col_for_filter in filtered_df_manage.columns:
                    filtered_df_manage[date_col_for_filter] = pd.to_datetime(filtered_df_manage[date_col_for_filter], errors='coerce')
                    if date_filter_manage != "Hamısı":
                        now_manage = pd.to_datetime(datetime.now())
                        if date_filter_manage == "Seçilmiş aralıq" and start_date_manage and end_date_manage:
                             filtered_df_manage = filtered_df_manage[
                                (filtered_df_manage[date_col_for_filter].dt.normalize() >= pd.to_datetime(start_date_manage)) &
                                (filtered_df_manage[date_col_for_filter].dt.normalize() <= pd.to_datetime(end_date_manage))
                            ]
                        elif date_filter_manage == "Son 7 gün": cutoff = now_manage - timedelta(days=7)
                        elif date_filter_manage == "Son 30 gün": cutoff = now_manage - timedelta(days=30)
                        elif date_filter_manage == "Son 3 ay": cutoff = now_manage - timedelta(days=90)
                        elif date_filter_manage == "Bu il": cutoff = datetime(now_manage.year, 1, 1)
                        else: cutoff = None # "Hamısı" üçün

                        if date_filter_manage != "Seçilmiş aralıq" and cutoff:
                             filtered_df_manage = filtered_df_manage[filtered_df_manage[date_col_for_filter] >= cutoff]
                
                if selected_dept_manage != "Hamısı" and 'Şöbə' in filtered_df_manage.columns:
                    filtered_df_manage = filtered_df_manage[filtered_df_manage['Şöbə'] == selected_dept_manage]
                if selected_type_manage != "Hamısı" and 'Ezamiyyət növü' in filtered_df_manage.columns:
                    filtered_df_manage = filtered_df_manage[filtered_df_manage['Ezamiyyət növü'] == selected_type_manage]

                if search_term_manage:
                    search_mask = pd.Series([False] * len(filtered_df_manage))
                    for col_search in ['Ad', 'Soyad', 'Vəzifə']:
                        if col_search in filtered_df_manage.columns:
                            search_mask |= filtered_df_manage[col_search].astype(str).str.contains(search_term_manage, case=False, na=False)
                    filtered_df_manage = filtered_df_manage[search_mask]
                
                st.markdown(f"#### 📊 Nəticələr ({len(filtered_df_manage)} qeyd)")
                if not filtered_df_manage.empty:
                    column_config_manage = {}
                    date_cols_in_df = ['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']
                    num_cols_in_df = ['Ümumi məbləğ', 'Günlük müavinət', 'Bilet qiyməti', 'Günlər']

                    for col in filtered_df_manage.columns:
                        if col in date_cols_in_df:
                            column_config_manage[col] = st.column_config.DateColumn( # DateColumn istifadə edək
                                col, format="DD.MM.YYYY" # Saat olmadan
                            )
                        elif col in num_cols_in_df:
                            column_config_manage[col] = st.column_config.NumberColumn(
                                col, format="%.2f AZN" if "məbləğ" in col or "qiymət" in col else "%.0f"
                            )
                    
                    # data_editor-a ötürülən df-in indeksini saxlayaq
                    filtered_df_manage_indexed = filtered_df_manage.copy()
                    # st.data_editor orijinal indeksi qoruyur əgər DataFrame-də varsa.
                    # load_trip_data() RangeIndex qaytara bilər. Bu halda problem yoxdur.
                    
                    edited_df_manage = st.data_editor(
                        filtered_df_manage_indexed,
                        column_config=column_config_manage,
                        use_container_width=True,
                        height=600,
                        key="admin_data_editor",
                        num_rows="dynamic" # Sətir əlavə etmə/silmə imkanı
                    )

                    if st.button("💾 Dəyişiklikləri Saxla", type="primary", key="save_edited_data_btn"):
                        try:
                            # `edited_df_manage` redaktə edilmiş datadır.
                            # Orijinal `df_manage` faylını yeniləmək üçün:
                            # Əgər sətirlər silinib və ya əlavə edilibsə, tam əvəzləmə daha asandır.
                            # Əgər yalnız mövcud sətirlər redaktə edilibsə, indeks üzrə update etmək olar.
                            # `num_rows="dynamic"` olduğu üçün, `edited_df_manage` birbaşa `df_manage`-in yerinə keçə bilər
                            # ancaq bu, filtrdən kənar datanı itirər.
                            # Daha doğru yanaşma: `edited_df_manage`-dəki dəyişiklikləri orijinal `df_manage`-ə tətbiq etmək
                            # və sonra tam `df_manage`-i saxlamaq.
                            
                            # Bu, mürəkkəb ola bilər. Sadə həll:
                            # 1. `edited_df_manage` `filtered_df_manage_indexed`-in son vəziyyətidir.
                            # 2. Orijinal `df_manage`-dən `filtered_df_manage_indexed`-in indekslərini tapıb silirik.
                            # 3. Sonra `edited_df_manage`-i (yeni/dəyişmiş sətirlərlə) `df_manage`-ə birləşdiririk.

                            # Daha asan, amma potensial olaraq bütün faylı redaktə edilmiş filterlənmiş data ilə əvəz edən:
                            # df_manage.loc[edited_df_manage.index] = edited_df_manage # Bu, indekslər uyğun gələrsə işləyir
                            
                            # Ən etibarlı yol, əgər `num_rows="dynamic"` istifadə olunursa,
                            # bütün data faylını `edited_df_manage` ilə əvəz etməkdir,
                            # amma bu yalnız o zaman düzgündür ki, filterləmə yalnız göstərmək üçündür,
                            # və redaktə bütün dataya tətbiq olunmalıdır (filterdən asılı olmayaraq).
                            # Bu ssenaridə, filterlənmiş datanı redaktə edib, həmin filterlənmiş hissəni əsas datada yeniləmək lazımdır.
                            # `st.data_editor` orijinal DataFrame-in slice-ı üzərində işləmir, kopya yaradır.

                            # Həll: Dəyişən sətirləri indekslərinə görə ana DataFrame-də yeniləyək
                            # Bu, `num_rows="dynamic"` ilə bir az qəlizləşir.
                            # Əgər yalnız mövcud sətirlər dəyişibsə:
                            df_manage.update(edited_df_manage) 
                            # Ancaq `num_rows="dynamic"` ilə yeni sətirlər əlavə edilibsə və ya silinibsə,
                            # `update` kifayət etməyəcək. Bu halda, `edited_df_manage`-i bütün faylın yerinə yazmaq olar,
                            # amma bu, yalnız redaktə olunan hissənin deyil, bütün faylın dəyişdirilməsi deməkdir.
                            # Bu demo üçün, əgər filter aktivdirsə, yalnız filterlənmiş hissənin
                            # redaktə edilib saxlanması məntiqi pozar.
                            # Ona görə də, bütün `df_manage` faylını `load_trip_data` ilə yenidən yükləyib,
                            # `edited_df_manage`-dəki dəyişiklikləri tətbiq edib, sonra hamısını saxlamaq daha doğru olardı.
                            # Və ya, `st.data_editor`-a bütün `df_manage`-i vermək.

                            # Kompromis: Edited_df-i əsas df-in yerinə qoyuruq, amma bu yalnız
                            # filterlənmiş datanın saxlanması deməkdir.
                            # Ən yaxşısı bütün df-i göstərib redaktə etmək və ya daha mürəkkəb update logic.
                            # Hal-hazırda, əgər filter yoxdursa, bütün df-i edited_df ilə əvəz edəcək.
                            # Əgər filter varsa, yalnız filterlənmiş hissəni göstərir və redaktə edir.
                            # "Dəyişiklikləri Saxla" bütün faylı yeniləməlidir.
                            # Bu, `edited_df_manage`in indekslərini istifadə edərək ana `df_main` faylını yeniləməyi tələb edir.

                            current_main_df = load_trip_data() # Ən son datanı al
                            # edited_df_manage `filtered_df_manage`in redaktə olunmuş versiyasıdır.
                            # Onun indeksləri `filtered_df_manage`in indeksləri ilə eynidir.
                            # Bu indekslər `current_main_df`-dəki orijinal indekslərdir.
                            for index_val in edited_df_manage.index:
                                if index_val in current_main_df.index: # Əgər sətir silinməyibsə
                                    current_main_df.loc[index_val] = edited_df_manage.loc[index_val]
                                else: # Sətir yeni əlavə edilibsə (bu, data_editor-un birbaşa qabiliyyəti deyil)
                                      # num_rows="dynamic" ilə yeni sətirlər əlavə edildikdə, onların indeksi fərqli ola bilər.
                                      # Bu halda, sadəcə edited_df_manage-i tamamilə yazmaq (əgər filter yoxdursa) və ya
                                      # daha mürəkkəb birləşdirmə lazımdır.
                                      # Bu demo üçün, update etməklə kifayətlənək, bu, yeni sətir əlavə etməni dəstəkləməyəcək.
                                      # Əgər num_rows="dynamic" həqiqətən yeni sətir əlavə edirsə, onda edited_df_manage tam fayl olmalıdır.
                                      # Streamlitin sənədlərinə görə, `num_rows="dynamic"` redaktə edilən DataFrame-i qaytarır,
                                      # ona görə də onu birbaşa saxlamaq olar, amma bu filterləməni nəzərə almaz.
                                      # Filterləmə varsa, bu hissə çətinləşir.
                                      # Tutaq ki, `num_rows="dynamic"` olmadan yalnız dəyərlər dəyişir:
                                      pass # Yeni sətir əlavə etmə bu sadə update ilə işləməyəcək.
                            
                            # Ən sadə yanaşma: editor-a bütün datanı verin, filterləməni UI-da edin, amma saxla düyməsi bütün datanı saxlasın.
                            # Yaxud, filterlənmiş datanı saxla:
                            # Bu, filterlənmiş datanın bütün faylın yerinə yazılması deməkdir, bu da səhvdir.
                            
                            # Düzgün yanaşma:
                            # 1. Orijinal tam datanı yüklə (df_manage).
                            # 2. `edited_df_manage` (bu, filterlənmiş və redaktə edilmişdir) içindəki dəyişiklikləri
                            #    `df_manage`-in müvafiq sətirlərinə tətbiq et.
                            #    Əgər `edited_df_manage` orijinal `df_manage`-in slice-nın indekslərini qoruyursa:
                            df_manage.update(edited_df_manage) # Bu, eyni indeksli sətirləri yeniləyəcək.
                            # Yeni sətirlər əlavə edilibsə və ya silinibsə, bu daha mürəkkəbdir.
                            # `st.data_editor` ilə `num_rows="dynamic"` istifadə edərkən,
                            # qaytarılan DataFrame tamamilə yenidir.
                            # Bu halda, əgər filter varsa, bu məntiq düzgün işləməyəcək.
                            # Filter olmadan (bütün datanı göstərəndə) `edited_df_manage`-i birbaşa saxlamaq olar.
                            
                            # Kompromis: Əgər filter yoxdursa, bütün datanı `edited_df_manage` ilə əvəz et.
                            if not (date_filter_manage != "Hamısı" or \
                                    (selected_dept_manage != "Hamısı" and 'Şöbə' in df_manage.columns) or \
                                    (selected_type_manage != "Hamısı" and 'Ezamiyyət növü' in df_manage.columns) or \
                                    search_term_manage):
                                df_to_save = edited_df_manage
                            else:
                                # Filter varsa, dəyişiklikləri ana df-ə tətbiq etmək lazımdır.
                                # Bu, edited_df_manage-in indekslərinin filtered_df_manage-in indeksləri ilə eyni olmasına əsaslanır.
                                # Və filtered_df_manage-in indeksləri df_manage-dəki orijinal indekslərdir.
                                base_df_for_update = load_trip_data() # Həmişə təmiz datadan başla
                                
                                # Silinmiş sətirləri emal et:
                                # `filtered_df_manage` (editordan əvvəlki) ilə `edited_df_manage` (editordan sonrakı) müqayisə et.
                                # Əgər bir indeks `filtered_df_manage`-də var, amma `edited_df_manage`-də yoxdursa, o silinib.
                                original_indices_in_filtered_view = filtered_df_manage_indexed.index
                                current_indices_in_edited_view = edited_df_manage.index
                                
                                rows_to_delete_indices = original_indices_in_filtered_view.difference(current_indices_in_edited_view)
                                if not rows_to_delete_indices.empty:
                                    base_df_for_update = base_df_for_update.drop(index=rows_to_delete_indices)

                                # Yenilənmiş və yeni əlavə edilmiş sətirləri emal et:
                                base_df_for_update = pd.concat([
                                    base_df_for_update[~base_df_for_update.index.isin(original_indices_in_filtered_view)], # filterdən kənar orijinal sətirlər
                                    edited_df_manage # redaktə edilmiş/yeni sətirlər (indeksləri qorunmalıdır)
                                ]).sort_index()
                                df_to_save = base_df_for_update.reset_index(drop=True) # İndeksi sıfırla

                            # Tarix sütunlarını string formatına çevirərək saxlamaq (Excel üçün daha yaxşı)
                            for col_date_save in date_cols_in_df:
                                if col_date_save in df_to_save.columns:
                                    df_to_save[col_date_save] = pd.to_datetime(df_to_save[col_date_save], errors='coerce').dt.strftime('%Y-%m-%d')

                            df_to_save.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                            st.success("✅ Dəyişikliklər saxlanıldı!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Saxlama xətası: {str(e)}")
                            st.exception(e)
                else:
                    st.info("🔍 Filtrə uyğun qeyd tapılmadı.")
            else:
                st.warning("📭 Hələ heç bir məlumat yoxdur.")
        except Exception as e:
            st.error(f"❌ Məlumat idarəetməsi xətası: {str(e)}")
            st.exception(e)

    # 3. İDXAL/İXRAC TAB
    with admin_tabs[2]:
        st.markdown("### 📥 Məlumat İdxal/İxrac Mərkəzi")
        io_col1, io_col2 = st.columns(2)

        with io_col1: # İXRAC
            st.markdown("#### 📤 İxrac Seçimləri")
            try:
                df_export_base = load_trip_data()
                if not df_export_base.empty:
                    export_format_type = st.selectbox(
                        "📄 Fayl formatı", ["Excel (.xlsx)", "CSV (.csv)"], key="export_format_select"
                    )
                    st.markdown("##### 📅 Tarix Aralığı (İxrac)")
                    exp_date_col1, exp_date_col2 = st.columns(2)
                    with exp_date_col1:
                        export_start_date = st.date_input("Başlanğıc tarixi", value=df_export_base['Tarix'].min().date() if 'Tarix' in df_export_base and not df_export_base['Tarix'].empty else datetime.now().date() - timedelta(days=30), key="export_start_date")
                    with exp_date_col2:
                        export_end_date = st.date_input("Bitmə tarixi", value=df_export_base['Tarix'].max().date() if 'Tarix' in df_export_base and not df_export_base['Tarix'].empty else datetime.now().date(), key="export_end_date")

                    # İxrac üçün df-i filterlə
                    df_to_export_filtered = df_export_base.copy()
                    if 'Tarix' in df_to_export_filtered:
                         df_to_export_filtered['Tarix'] = pd.to_datetime(df_to_export_filtered['Tarix'])
                         df_to_export_filtered = df_to_export_filtered[
                            (df_to_export_filtered['Tarix'].dt.normalize() >= pd.to_datetime(export_start_date)) &
                            (df_to_export_filtered['Tarix'].dt.normalize() <= pd.to_datetime(export_end_date))
                        ]

                    if st.button("📤 İxrac Et", type="primary", use_container_width=True, key="export_data_btn"):
                        if export_start_date > export_end_date:
                            st.error("❌ Başlanğıc tarixi bitmə tarixindən böyük ola bilməz!")
                        elif df_to_export_filtered.empty:
                            st.warning("Seçilmiş tarix aralığında ixrac üçün məlumat yoxdur.")
                        else:
                            with st.spinner("İxrac edilir..."):
                                file_buffer, file_name, mime_type = None, None, None
                                if export_format_type == "Excel (.xlsx)":
                                    buffer = BytesIO()
                                    df_to_export_filtered.to_excel(buffer, index=False, engine='openpyxl')
                                    file_buffer = buffer.getvalue()
                                    file_name = f"ezamiyyetler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                elif export_format_type == "CSV (.csv)":
                                    csv_data = df_to_export_filtered.to_csv(index=False).encode('utf-8')
                                    file_buffer = csv_data
                                    file_name = f"ezamiyyetler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                                    mime_type = "text/csv"
                                
                                if file_buffer and file_name and mime_type:
                                    st.download_button(
                                        label=f"📥 {export_format_type} Faylını Yüklə",
                                        data=file_buffer,
                                        file_name=file_name,
                                        mime=mime_type
                                    )
                                    st.success("Fayl ixrac üçün hazırdır!")
                else:
                    st.info("📝 İxrac üçün məlumat yoxdur.")
            except Exception as e:
                st.error(f"❌ İxrac xətası: {str(e)}")
                st.exception(e)

        with io_col2: # İDXAL
            st.markdown("#### 📥 İdxal Seçimləri")
            uploaded_file_import = st.file_uploader(
                "📎 Fayl seçin (Excel və ya CSV)", type=['xlsx', 'csv'], key="import_file_uploader"
            )
            if uploaded_file_import:
                try:
                    new_df_import = read_uploaded_file(uploaded_file_import) # Funksiyanı istifadə edirik
                    if new_df_import is not None:
                        st.markdown("##### 👀 İdxal Əvvəli Nəzər")
                        imp_stat_col1, imp_stat_col2 = st.columns(2)
                        with imp_stat_col1: st.metric("📊 Qeyd sayı", len(new_df_import))
                        with imp_stat_col2: st.metric("📈 Sütun sayı", len(new_df_import.columns))
                        st.dataframe(new_df_import.head(5), use_container_width=True)

                        import_mode_select = st.radio(
                            "İdxal rejimi", ["Əlavə et", "Əvəzlə"], key="import_mode_radio",
                            help="Əlavə et: Mövcud məlumatlarla birləşdir\nƏvəzlə: Mövcud məlumatları sil və yenilərini əlavə et"
                        )
                        if st.button("📥 İdxal Et", type="primary", use_container_width=True, key="import_data_btn"):
                            with st.spinner("İdxal edilir..."):
                                try:
                                    # Tarix sütunlarını düzgün formatda idxal etmək üçün
                                    date_cols_to_parse_import = ['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']
                                    for col in date_cols_to_parse_import:
                                        if col in new_df_import.columns:
                                            new_df_import[col] = pd.to_datetime(new_df_import[col], errors='coerce')
                                    
                                    if import_mode_select == "Əvəzlə":
                                        new_df_import.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                                    else: # Əlavə et
                                        existing_df_import = load_trip_data()
                                        combined_df_import = pd.concat([existing_df_import, new_df_import], ignore_index=True).drop_duplicates(keep='last')
                                        combined_df_import.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                                    st.success("✅ İdxal uğurla tamamlandı!")
                                    st.balloons()
                                    st.info("🔄 Dəyişikliklərin görünməsi üçün səhifəni və ya tabı yeniləyin (və ya F5).")
                                    st.rerun() # Yenidən başlatma
                                except Exception as e_import_save:
                                    st.error(f"❌ İdxal zamanı yadda saxlama xətası: {str(e_import_save)}")
                                    st.exception(e_import_save)
                except Exception as e_read_file:
                    st.error(f"❌ Fayl oxuma xətası: {str(e_read_file)}")
                    st.exception(e_read_file)

    # 4. İSTİFADƏÇİ İDARƏETMƏSİ TAB
    with admin_tabs[3]:
        st.markdown("### 👥 İstifadəçi Statistikaları")
        try:
            df_users = load_trip_data()
            if not df_users.empty and 'Ad' in df_users.columns and 'Soyad' in df_users.columns and 'Ümumi məbləğ' in df_users.columns:
                df_users['Ümumi məbləğ'] = pd.to_numeric(df_users['Ümumi məbləğ'], errors='coerce').fillna(0)
                
                user_stats_df = df_users.groupby(['Ad', 'Soyad'], as_index=False).agg(
                    Ümumi_Xərc=('Ümumi məbləğ', 'sum'),
                    Ezamiyyət_Sayı=('Ümumi məbləğ', 'count')
                )
                user_stats_df['Orta_Xərc'] = user_stats_df['Ümumi_Xərc'] / user_stats_df['Ezamiyyət_Sayı']
                user_stats_df = user_stats_df.sort_values('Ümumi_Xərc', ascending=False).reset_index(drop=True)
                
                user_col1, user_col2 = st.columns([2,1])
                with user_col1:
                    st.markdown("#### 📊 Bütün İstifadəçilər üzrə Statistikalar")
                    formatted_stats_display = user_stats_df.copy()
                    formatted_stats_display['Ümumi_Xərc'] = formatted_stats_display['Ümumi_Xərc'].map('{:.2f} AZN'.format)
                    formatted_stats_display['Orta_Xərc'] = formatted_stats_display['Orta_Xərc'].map('{:.2f} AZN'.format)
                    st.dataframe(formatted_stats_display, use_container_width=True)
                
                with user_col2:
                    st.markdown("#### 📈 Top 5 İstifadəçi (Xərcə görə)")
                    top_users_display = user_stats_df.head(5)
                    if not top_users_display.empty:
                        fig_top_users = px.bar(
                            top_users_display,
                            y=[f"{ad} {soyad}" for ad, soyad in zip(top_users_display['Ad'], top_users_display['Soyad'])],
                            x='Ümumi_Xərc',
                            orientation='h', title="Ən Çox Xərc Edən 5 İstifadəçi"
                        )
                        fig_top_users.update_layout(height=350, showlegend=False, yaxis_title="İstifadəçi", xaxis_title="Ümumi Xərc (AZN)")
                        st.plotly_chart(fig_top_users, use_container_width=True)
                    else:
                        st.info("Top istifadəçi məlumatı yoxdur.")
            else:
                st.info("👤 İstifadəçi statistikaları üçün kifayət qədər məlumat ('Ad', 'Soyad', 'Ümumi məbləğ') yoxdur.")
        except Exception as e_users:
            st.error(f"❌ İstifadəçi statistikaları xətası: {str(e_users)}")
            st.exception(e_users)

    # 5. SİSTEM ALƏTLƏRİ TAB
    with admin_tabs[4]:
        st.markdown("### 🔧 Sistem Alətləri")
        tool_col1, tool_col2 = st.columns(2)

        with tool_col1:
            st.markdown("#### 🧹 Məlumat Təmizliyi")
            if st.button("🗑️ Dublikatları Sil (Bütün sütunlar üzrə)", use_container_width=True, key="deduplicate_btn"):
                try:
                    df_tools = load_trip_data()
                    if not df_tools.empty:
                        initial_count = len(df_tools)
                        df_clean = df_tools.drop_duplicates(keep='first') # İlkini saxla, qalanlarını sil
                        final_count = len(df_clean)
                        if initial_count > final_count:
                            df_clean.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                            st.success(f"✅ {initial_count - final_count} dublikat qeyd silindi!")
                            st.rerun()
                        else:
                            st.info("ℹ️ Dublikat qeyd tapılmadı.")
                    else:
                        st.info("ℹ️ Təmizləmək üçün məlumat yoxdur.")
                except Exception as e_dedup:
                    st.error(f"❌ Dublikat silmə xətası: {str(e_dedup)}")

            if st.button("🧽 Tamamilə Boş Sətirləri Sil", use_container_width=True, key="dropna_btn"):
                try:
                    df_tools_na = load_trip_data()
                    if not df_tools_na.empty:
                        initial_count_na = len(df_tools_na)
                        df_clean_na = df_tools_na.dropna(how='all') # Bütün sütunları NaN olan sətirləri sil
                        final_count_na = len(df_clean_na)
                        if initial_count_na > final_count_na:
                            df_clean_na.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                            st.success(f"✅ {initial_count_na - final_count_na} tamamilə boş qeyd silindi!")
                            st.rerun()
                        else:
                            st.info("ℹ️ Tamamilə boş qeyd tapılmadı.")
                    else:
                        st.info("ℹ️ Təmizləmək üçün məlumat yoxdur.")
                except Exception as e_dropna:
                    st.error(f"❌ Boş qeyd silmə xətası: {str(e_dropna)}")
        
        with tool_col2:
            st.markdown("#### 💾 Backup İdarəetməsi")
            if st.button("📦 Yedək Nüsxə Yarat (Backup)", use_container_width=True, key="backup_btn"):
                try:
                    df_backup = load_trip_data()
                    if not df_backup.empty:
                        backup_dir = "backups"
                        os.makedirs(backup_dir, exist_ok=True)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        backup_filename = os.path.join(backup_dir, f"backup_ezamiyyetler_{timestamp}.xlsx")
                        df_backup.to_excel(backup_filename, index=False)
                        st.success(f"✅ Yedək nüsxə yaradıldı: {backup_filename}")
                    else:
                        st.info("ℹ️ Yedək nüsxə yaratmaq üçün məlumat yoxdur.")
                except Exception as e_backup:
                    st.error(f"❌ Yedək nüsxə yaratma xətası: {str(e_backup)}")

            st.markdown("#### 📊 Sistem Statistikaları")
            if st.button("📈 Statistikaları Göstər", use_container_width=True, key="sys_stats_btn"):
                try:
                    df_sys_stats = load_trip_data()
                    if not df_sys_stats.empty:
                        total_records = len(df_sys_stats)
                        total_amount_stats = 0
                        if 'Ümumi məbləğ' in df_sys_stats.columns:
                            total_amount_stats = pd.to_numeric(df_sys_stats['Ümumi məbləğ'], errors='coerce').sum()
                        
                        avg_amount_stats = (total_amount_stats / total_records) if total_records > 0 else 0
                        
                        st.markdown(f"""
                        - **Cəmi qeyd sayı:** {total_records}
                        - **Cəmi xərc (AZN):** {total_amount_stats:.2f}
                        - **Orta xərc (AZN):** {avg_amount_stats:.2f}
                        """)
                        if 'Tarix' in df_sys_stats.columns and not df_sys_stats['Tarix'].empty:
                             df_sys_stats['Tarix'] = pd.to_datetime(df_sys_stats['Tarix'], errors='coerce')
                             st.markdown(f"- **İlk qeyd tarixi:** {df_sys_stats['Tarix'].min().strftime('%d.%m.%Y') if not df_sys_stats['Tarix'].dropna().empty else 'Məlumat yoxdur'}")
                             st.markdown(f"- **Son qeyd tarixi:** {df_sys_stats['Tarix'].max().strftime('%d.%m.%Y') if not df_sys_stats['Tarix'].dropna().empty else 'Məlumat yoxdur'}")
                    else:
                        st.info("ℹ️ Statistika üçün məlumat yoxdur.")
                except Exception as e_sys_stats:
                    st.error(f"❌ Sistem statistikaları xətası: {str(e_sys_stats)}")
