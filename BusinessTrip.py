import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from io import BytesIO
import requests
import xml.etree.ElementTree as ET
import os
from bs4 import BeautifulSoup


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

COUNTRY_CITIES = {
    "Türkiyə": ["İstanbul", "Ankara", "İzmir", "Antalya", "Bursa", "Digər"],
    "Gürcüstan": ["Tbilisi", "Batumi", "Kutaisi", "Zugdidi", "Digər"],
    "Almaniya": ["Berlin", "Münhen", "Frankfurt", "Hamburg", "Digər"],
    "BƏƏ": ["Dubai", "Abu Dabi", "Şarqah", "Əcman", "Digər"],
    "Rusiya": ["Moskva", "Sankt-Peterburq", "Kazan", "Soçi", "Digər"],
    "İran": ["Təbriz", "Tehran", "İsfahan", "Məşhəd", "Digər"],
    "İtaliya": ["Roma", "Milan", "Venesiya", "Florensiya", "Digər"],
    "Fransa": ["Paris", "Marsel", "Lion", "Nitsa", "Digər"],
    "İngiltərə": ["London", "Manchester", "Birmingem", "Liverpul", "Digər"],
    "ABŞ": ["Nyu York", "Los Anceles", "Çikaqo", "Mayami", "Digər"]
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


@st.cache_data(ttl=3600)
def get_currency_rates(date):
    try:
        formatted_date = date.strftime("%Y%m%d")
        url = f"https://www.cbar.az/currencies/{formatted_date}.xml"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        currencies = []
        for val_type in root.findall('.//ValType'):
            for valute in val_type.findall('Valute'):
                currency_data = {
                    'Kod': valute.get('Code'),
                    'Valyuta': valute.find('Name').text,
                    'Miqdar': float(valute.find('Nominal').text),
                    'Kurs (AZN)': float(valute.find('Value').text.replace(',', '.'))
                }
                currency_data['1 vahid üçün'] = currency_data['Kurs (AZN)'] / currency_data['Miqdar']
                currencies.append(currency_data)
        
        return pd.DataFrame(currencies)
    
    except Exception as e:
        st.error(f"API xətası: {str(e)}")
        return pd.DataFrame()
        
def get_historical_rates(currency, start_date, end_date):
    """Seçilmiş tarix aralığı üçün tarixçə məlumatları"""
    dates = pd.date_range(start=start_date, end=end_date)
    rates = []
    
    for date in dates:
        df = get_currency_rates(date)
        if not df.empty and currency in df['Valyuta'].values:
            rate = df[df['Valyuta'] == currency]['1 vahid üçün'].values[0]
            rates.append({"Tarix": date.date(), "Kurs": rate})
    
    return pd.DataFrame(rates)


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
                    first_name = st.text_input("Ad")
                    father_name = st.text_input("Ata adı")
                with cols[1]:
                    last_name = st.text_input("Soyad")
                    position = st.text_input("Vəzifə")

            with st.expander("🏢 Təşkilat Məlumatları"):
                department = st.selectbox("Şöbə", DEPARTMENTS)

            with st.expander("🧳 Ezamiyyət Detalları"):
                trip_type = st.radio("Növ", ["Ölkə daxili", "Ölkə xarici"])
                payment_type = st.selectbox("Ödəniş növü", list(PAYMENT_TYPES.keys()))
                
                if trip_type == "Ölkə daxili":
                    cols = st.columns(2)
                    with cols[0]:
                        from_city = st.selectbox("Haradan", CITIES, index=CITIES.index("Bakı"))
                    with cols[1]:
                        to_city = st.selectbox("Haraya", [c for c in CITIES if c != from_city])
                    ticket_price = calculate_domestic_amount(from_city, to_city)
                    daily_allowance = 70
                else:
                    country = st.selectbox("Ölkə", list(COUNTRIES.keys()))
                    # Yeni əlavə edilən şəhər seçimi
                    city_options = COUNTRY_CITIES.get(country, ["Digər"])
                    selected_city = st.selectbox("Şəhər", city_options)
                    
                    payment_mode = st.selectbox(
                        "Ödəniş rejimi",
                        options=["Adi rejim", "Günlük Normaya 50% əlavə", "Günlük Normaya 30% əlavə"]
                    )
                    accommodation = st.selectbox(
                        "Qonaqlama xərcləri",
                        options=["Adi rejim", "Yalnız yaşayış yeri ilə təmin edir", "Yalnız gündəlik xərcləri təmin edir"]
                    )
                    base_allowance = COUNTRIES[country]
                    if payment_mode == "Adi rejim":
                        daily_allowance = base_allowance
                    elif payment_mode == "Günlük Normaya 50% əlavə":
                        daily_allowance = base_allowance * 1.5
                    else:
                        daily_allowance = base_allowance * 1.3
                    ticket_price = 0

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
                    
                    st.metric("📅 Günlük müavinət", f"{daily_allowance} AZN")
                    if trip_type == "Ölkə daxili":
                        st.metric("🚌 Nəqliyyat xərci", f"{ticket_price} AZN")
                    st.metric("⏳ Müddət", f"{trip_days} gün")
                    st.metric(
                        "💳 Ümumi məbləğ", 
                        f"{total_amount:.2f} AZN", 
                        delta=delta_label,
                        delta_color="normal" if delta_label else "off"
                    )

            if st.button("✅ Yadda Saxla", use_container_width=True):
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
                        "Qonaqlama növü": accommodation if trip_type == "Ölkə xarici" else "Tətbiq edilmir",
                        # Şəhər məlumatı əlavə edildi
                        "Marşrut": f"{from_city} → {to_city}" if trip_type == "Ölkə daxili" else f"{country} - {selected_city}",
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
            **Dəstəklənən formatlar:**
            - .xlsx, .xls, .csv
            **Tələblər:**
            1. Fayl aşağıdakı sütunları ehtiva etməlidir:
               - Ad, Soyad, Başlanğıc tarixi, Bitmə tarixi
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
                    
                    # Sütun uyğunlaşdırmaları
                    st.markdown("### Sütun Uyğunlaşdırmaları")
                    column_mapping = {}
                    tələb_olunan_sütunlar = ['Ad', 'Soyad', 'Başlanğıc tarixi', 'Bitmə tarixi', 'Ümumi məbləğ']
                    
                    for sütun in tələb_olunan_sütunlar:
                        seçim = st.selectbox(
                            f"{sütun} sütununu seçin",
                            options=["--Seçin--"] + list(df_import.columns),
                            key=f"map_{sütun}"
                        )
                        column_mapping[sütun] = seçim if seçim != "--Seçin--" else None
                    
                    # Validasiya
                    if st.button("✅ Təsdiqlə və Yüklə"):
                        çatışmayanlar = [k for k,v in column_mapping.items() if not v]
                        if çatışmayanlar:
                            st.error(f"Zəruri sütunlar seçilməyib: {', '.join(çatışmayanlar)}")
                        else:
                            # Mapping işləmi
                            df_mapped = df_import.rename(columns={v: k for k, v in column_mapping.items() if v})
                            
                            # Məlumatları mövcud faylə əlavə et
                            try:
                                df_existing = pd.read_excel("ezamiyyet_melumatlari.xlsx")
                                df_combined = pd.concat([df_existing, df_mapped], ignore_index=True)
                            except FileNotFoundError:
                                df_combined = df_mapped
                            
                            df_combined.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                            st.success(f"✅ {len(df_mapped)} qeyd uğurla idxal edildi!")
                            st.rerun()
                    
                    # Önizləmə
                    if st.checkbox("📋 Məlumat önizləməsi"):
                        st.dataframe(df_import.head(10), use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Fayl oxunarkən xəta: {str(e)}")


        
                # VALYUTA MƏZƏNNƏLƏRİ SEKME MƏZMUNU
        with tab_currency:
            st.markdown("## Valyuta Məzənnələrinin İdarəetmə Paneli")
            
            # Tarix seçimi və məzənnə yükləmə
            cols = st.columns([2,1,1])
            with cols[0]:
                selected_date = st.date_input(
                    "Məzənnə tarixi",
                    datetime.today(),
                    key="admin_currency_date"
                )
                
            with cols[1]:
                if st.button("📥 Məzənnələri yüklə"):
                    with st.spinner("Məzənnə məlumatları yüklənir..."):
                        st.session_state.currency_data = get_currency_rates(selected_date)
            
            with cols[2]:
                if st.button("🔄 Cari məzənnələri yenilə"):
                    with st.spinner("Cari məzənnələr yenilənir..."):
                        st.session_state.currency_data = get_currency_rates(datetime.today())
            
            # Məzənnə cədvəli
            if 'currency_data' in st.session_state:
                if not st.session_state.currency_data.empty:
                    df = st.session_state.currency_data
                    
                    # Formatlanmış cədvəl
                    st.dataframe(
                        df[['Valyuta', 'Kod', 'Miqdar', '1 vahid üçün']],
                        column_config={
                            "Valyuta": "Valyuta",
                            "Kod": "ISO Kod",
                            "Miqdar": "Vahid",
                            "1 vahid üçün": st.column_config.NumberColumn(
                                "Məzənnə",
                                help="1 vahid üçün AZN ekvivalenti",
                                format="%.4f AZN"
                            )
                        },
                        use_container_width=True,
                        height=400
                    )
                    
                    # Tarixçə analizi
                    st.markdown("---")
                    st.markdown("### Tarixçə Analizi")
                    
                    cols_hist = st.columns(3)
                    with cols_hist[0]:
                        currency = st.selectbox(
                            "Valyuta seçin",
                            options=df['Valyuta'].unique(),
                            index=0
                        )
                    with cols_hist[1]:
                        start_date_hist = st.date_input(
                            "Başlanğıc tarixi",
                            datetime.today() - timedelta(days=30),  # Düzəliş edildi
                            key="start_date"
                        )
                    with cols_hist[2]:
                        end_date_hist = st.date_input(
                            "Bitmə tarixi",
                            datetime.today(),
                            key="end_date"
                        )
                    
                    if st.button("📈 Tarixçəni yüklə"):
                        historical_data = get_historical_rates(currency, start_date_hist, end_date_hist)
                        
                        if not historical_data.empty:
                            fig = px.line(
                                historical_data,
                                x='Tarix',
                                y='Kurs',
                                title=f"{currency} məzənnəsi üçün tarixçə ({start_date_hist} - {end_date_hist})",
                                markers=True
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Statistik məlumatlar
                            stats = historical_data['Kurs'].describe()
                            cols_stats = st.columns(3)
                            cols_stats[0].metric("Maksimum", f"{stats['max']:.4f} AZN")
                            cols_stats[1].metric("Minimum", f"{stats['min']:.4f} AZN")
                            cols_stats[2].metric("Ortalama", f"{stats['mean']:.4f} AZN")
                        else:
                            st.warning("Seçilmiş aralıqda məlumat tapılmadı!")
                else:
                    st.warning("Məzənnə məlumatı tapılmadı!")
            else:
                st.info("Məzənnələri görmək üçün tarix seçib 'Yüklə' düyməsini basın")

        

        # Parametrlər sekmesi
        with tab_settings:
            st.markdown("### 🛠️ Sistem Parametrləri")
            
            # Ölkə və məbləğlərin redaktə edilməsi
            with st.expander("🌍 Beynəlxalq Ezamiyyət Parametrləri", expanded=True):
                st.markdown("#### Mövcud Ölkələr və Günlük Müavinətlər")
                
                # Yeni ölkə əlavə etmə
                cols = st.columns([2, 1, 1])
                with cols[0]:
                    new_country = st.text_input("Yeni ölkə adı")
                with cols[1]:
                    new_allowance = st.number_input("Günlük müavinət (AZN)", min_value=0, value=300)
                with cols[2]:
                    if st.button("➕ Əlavə et"):
                        if new_country and new_country not in COUNTRIES:
                            COUNTRIES[new_country] = new_allowance
                            st.success(f"{new_country} əlavə edildi!")
                            st.rerun()
                
                # Mövcud ölkələri göstər və redaktə et
                for country, allowance in COUNTRIES.items():
                    cols = st.columns([2, 1, 1])
                    with cols[0]:
                        st.write(f"🌍 {country}")
                    with cols[1]:
                        new_val = st.number_input(f"Müavinət", value=allowance, key=f"country_{country}")
                        if new_val != allowance:
                            COUNTRIES[country] = new_val
                    with cols[2]:
                        if st.button("🗑️", key=f"del_{country}"):
                            del COUNTRIES[country]
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
            with st.expander("📊 Sistem Məlumatları"):
                st.markdown("#### Ümumi Statistikalar")
                
                try:
                    df = pd.read_excel("ezamiyyet_melumatlari.xlsx")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Toplam Qeydlər", len(df))
                    with col2:
                        st.metric("Ən Son Qeyd", df['Tarix'].max() if not df.empty else "Yoxdur")
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

if __name__ == "__main__":
    if not os.path.exists("ezamiyyet_melumatlari.xlsx"):
        pd.DataFrame(columns=[
            'Tarix', 'Ad', 'Soyad', 'Ata adı', 'Vəzifə', 'Şöbə', 
            'Ezamiyyət növü', 'Ödəniş növü', 'Qonaqlama növü',
            'Marşrut', 'Bilet qiyməti', 'Günlük müavinət', 
            'Başlanğıc tarixi', 'Bitmə tarixi', 'Günlər', 
            'Ümumi məbləğ', 'Məqsəd'
        ]).to_excel("ezamiyyet_melumatlari.xlsx", index=False)
