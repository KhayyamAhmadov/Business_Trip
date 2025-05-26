import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from io import BytesIO
import requests
import xml.etree.ElementTree as ET
import os
from bs4 import BeautifulSoup
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
    # ... (COUNTRIES məlumatları eyni qalır)
}

DOMESTIC_ALLOWANCES = {
    "Bakı": 125,
    "Naxçıvan": 100,
    "Gəncə": 95,
    "Sumqayıt": 95,
    "Digər": 90
}

CURRENCY_RATES = {
    "USD": 1.7,
    "EUR": 1.9,
    "GBP": 2.2,
    "JPY": 0.015
}

# Fayl yoxlamaları
if not os.path.exists("countries_data.json"):
    with open('countries_data.json', 'w', encoding='utf-8') as f:
        json.dump(COUNTRIES, f, ensure_ascii=False, indent=4)

if not os.path.exists("currency_rates.xlsx"):
    pd.DataFrame({
        'Valyuta': list(CURRENCY_RATES.keys()),
        'Məzənnə': list(CURRENCY_RATES.values())
    }).to_excel("currency_rates.xlsx", index=False)

if not os.path.exists("ezamiyyet_melumatlari.xlsx"):
    pd.DataFrame(columns=[
        'Tarix', 'Ad', 'Soyad', 'Ata adı', 'Vəzifə', 'Şöbə', 
        'Ezamiyyət növü', 'Ödəniş növü', 'Qonaqlama növü',
        'Marşrut', 'Bilet qiyməti', 'Günlük müavinət', 
        'Başlanğıc tarixi', 'Bitmə tarixi', 'Günlər', 
        'Ümumi məbləğ', 'Məqsəd'
    ]).to_excel("ezamiyyet_melumatlari.xlsx", index=False)

# ============================== FUNKSİYALAR ==============================
def load_trip_data():
    try:
        return pd.read_excel("ezamiyyet_melumatlari.xlsx")
    except FileNotFoundError:
        return pd.DataFrame()

def calculate_days(start_date, end_date):
    return (end_date - start_date).days + 1

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

def load_countries_data():
    try:
        with open('countries_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        with open('countries_data.json', 'w', encoding='utf-8') as f:
            json.dump(COUNTRIES, f, ensure_ascii=False, indent=4)
        return COUNTRIES

def save_countries_data(data):
    with open('countries_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

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

# ============================== ƏSAS İNTERFEYS ==============================
st.markdown('<div class="main-header"><h1>✈️ Ezamiyyət İdarəetmə Sistemi</h1></div>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📋 Yeni Ezamiyyət", "🔐 Admin Paneli"])

with tab1:
    with st.container():
        col1, col2 = st.columns([2, 1], gap="large")
        
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
                    if 'trips' not in st.session_state:
                        st.session_state.trips = []
                    
                    with st.container(border=True):
                        cols = st.columns(2)
                        with cols[0]:
                            from_city = st.selectbox("Haradan", CITIES, index=CITIES.index("Bakı"))
                        with cols[1]:
                            to_city = st.selectbox("Haraya", [c for c in CITIES if c != from_city])
                        
                        cols_dates = st.columns(2)
                        with cols_dates[0]:
                            start_date = st.date_input("Başlanğıc tarixi")
                        with cols_dates[1]:
                            end_date = st.date_input("Bitmə tarixi")
                        
                        ticket_price = st.number_input("Nəqliyyat xərci (AZN)", min_value=0.0, value=0.0)
                        
                        cols_buttons = st.columns([3,1])
                        with cols_buttons[0]:
                            if st.button("➕ Yeni sefer əlavə et", use_container_width=True):
                                st.session_state.trips.append({
                                    'from': from_city,
                                    'to': to_city,
                                    'start': start_date,
                                    'end': end_date,
                                    'price': ticket_price
                                })
                                st.rerun()
                        with cols_buttons[1]:
                            if st.button("➖ Son seferi sil", use_container_width=True, type="secondary"):
                                if st.session_state.trips:
                                    st.session_state.trips.pop()
                                    st.rerun()
                        
                    if st.session_state.trips:
                        st.markdown("**Əlavə edilmiş seferlər:**")
                        for i, trip in enumerate(st.session_state.trips, 1):
                            st.write(f"{i}. {trip['from']} → {trip['to']} | "
                                    f"{trip['start']} - {trip['end']} | "
                                    f"Nəqliyyat: {trip['price']} AZN")

                else:
                    countries_data = load_countries_data()
                    country = st.selectbox("Ölkə", list(countries_data.keys()))
                    
                    if country in countries_data:
                        city_options = [c for c in countries_data[country]['cities'].keys() if c != 'digər']
                        city_options.append("digər")
                        selected_city = st.selectbox("Şəhər", city_options)
                        
                        cols = st.columns(2)
                        with cols[0]:
                            start_date = st.date_input("Başlanğıc tarixi")
                        with cols[1]:
                            end_date = st.date_input("Bitmə tarixi")
                        
                        purpose = st.text_area("Ezamiyyət məqsədi")

        with col2:
            with st.container():
                st.markdown('<div class="section-header">💰 Hesablama</div>', unsafe_allow_html=True)
                
                if trip_type == "Ölkə daxili":
                    domestic_allowances = load_domestic_allowances()
                    
                    if st.session_state.trips:
                        total_amount = 0
                        total_transport = 0
                        total_days = 0
                        
                        for trip in st.session_state.trips:
                            # Müavinət təyini YALNIZ 'to_city' əsasında
                            daily_allowance = domestic_allowances.get(
                                trip['to'], 
                                domestic_allowances.get('Digər', 90)
                            )
                            
                            days = (trip['end'] - trip['start']).days + 1
                            total_days += days
                            
                            hotel_cost = 0.7 * daily_allowance * (days-1)
                            daily_expenses = 0.3 * daily_allowance * days
                            trip_total = hotel_cost + daily_expenses + trip['price']
                            total_amount += trip_total
                            total_transport += trip['price']
        
                            with st.expander(f"Sefer {trip['from']}→{trip['to']}"):
                                st.metric("Hədəf şəhər", trip['to'])
                                st.metric("Günlük müavinət", f"{daily_allowance} AZN")
                                st.metric("Günlər", days)
                                st.metric("Mehmanxana xərcləri", f"{hotel_cost:.2f} AZN")
                                st.metric("Gündəlik xərclər", f"{daily_expenses:.2f} AZN")
                                st.metric("Nəqliyyat xərci", f"{trip['price']:.2f} AZN")
                                st.metric("Sefer ümumi", f"{trip_total:.2f} AZN")
        
                        st.divider()
                        cols_total = st.columns(2)
                        with cols_total[0]:
                            st.metric("Ümumi Günlər", total_days)
                            st.metric("Ümumi Nəqliyyat Xərcləri", f"{total_transport:.2f} AZN")
                        with cols_total[1]:
                            st.metric("Ümumi Məbləğ", f"{total_amount:.2f} AZN")
                    
                    else:
                        st.warning("Ən azı bir sefer əlavə edin!")
                    
                if st.button("✅ Yadda Saxla", use_container_width=True):
                    if all([first_name, last_name]):
                        if trip_type == "Ölkə daxili" and st.session_state.trips:
                            for trip in st.session_state.trips:
                                days = (trip['end'] - trip['start']).days + 1
                                trip_data = {
                                    "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "Ad": first_name,
                                    "Soyad": last_name,
                                    "Ata adı": father_name,
                                    "Vəzifə": position,
                                    "Şöbə": department,
                                    "Ezamiyyət növü": trip_type,
                                    "Marşrut": f"{trip['from']} → {trip['to']}",
                                    "Bilet qiyməti": trip['price'],
                                    "Günlük müavinət": domestic_allowances.get(trip['to'], 90),
                                    "Başlanğıc tarixi": trip['start'].strftime("%Y-%m-%d"),
                                    "Bitmə tarixi": trip['end'].strftime("%Y-%m-%d"),
                                    "Günlər": days,
                                    "Ümumi məbləğ": 0.7*domestic_allowances.get(trip['to'], 90)*(days-1) + 0.3*domestic_allowances.get(trip['to'], 90)*days + trip['price'],
                                    "Məqsəd": purpose
                                }
                                save_trip_data(trip_data)
                            st.success("Məlumatlar yadda saxlandı!")
                            st.session_state.trips = []
                            st.rerun()


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
        

        # Parametrlər sekmesi
        # Parametrlər sekmesi
        with tab_settings:
            # Ölkə məlumatlarını yüklə
            countries_data = load_countries_data()  # ƏSAS DÜZƏLİŞ
            
            st.markdown("### 🛠️ Sistem Parametrləri")
            
            # Ölkə və məbləğlərin redaktə edilməsi
            with st.expander("🌍 Beynəlxalq Ezamiyyət Parametrləri", expanded=True):
                st.markdown("### Ölkə və Şəhər İdarəetməsi")
                
                # Yeni ölkə əlavə etmə
                cols = st.columns([3, 2, 1])
                with cols[0]:
                    new_country = st.text_input("Yeni ölkə adı", key="new_country_name")
                with cols[1]:
                    new_currency = st.selectbox("Valyuta", list(CURRENCY_RATES.keys()), key="new_country_currency")
                with cols[2]:
                    if st.button("➕ Ölkə əlavə et", key="add_new_country"):
                        if new_country.strip() and new_country not in countries_data:
                            countries_data[new_country] = {
                                "currency": new_currency,
                                "cities": {"digər": {"allowance": 100, "currency": new_currency}}}
                            save_countries_data(countries_data)
                            st.rerun()

                # Ölkə seçimi
                selected_country = st.selectbox(
                    "Redaktə ediləcək ölkəni seçin",
                    list(countries_data.keys()),
                    key="country_selector"
                )

                # Seçilmiş ölkənin redaktəsi
                if selected_country:
                    country = countries_data[selected_country]
                    
                    # Valyuta yeniləmə
                    new_currency = st.selectbox(
                        "Ölkə valyutası",
                        list(CURRENCY_RATES.keys()),
                        index=list(CURRENCY_RATES.keys()).index(country['currency']),
                        key=f"currency_{selected_country}"
                    )
                    if new_currency != country['currency']:
                        country['currency'] = new_currency
                        # Bütün şəhərlərin valyutasını yenilə
                        for city in country['cities']:
                            country['cities'][city]['currency'] = new_currency
                        save_countries_data(countries_data)
                        st.rerun()

                    # Şəhər idarəetmə
                    st.markdown("### Şəhərlər")
                    cols = st.columns([3, 2, 1])
                    with cols[0]:
                        new_city = st.text_input("Yeni şəhər adı", key=f"new_city_{selected_country}")
                    with cols[1]:
                        new_allowance = st.number_input("Gündəlik müavinət", min_value=0, value=100, 
                                                    key=f"new_allowance_{selected_country}")
                    with cols[2]:
                        if st.button("Əlavə et", key=f"add_city_{selected_country}") and new_city:
                            country['cities'][new_city] = {
                                "allowance": new_allowance,
                                "currency": country['currency']
                            }
                            save_countries_data(countries_data)
                            st.rerun()

                    # Mövcud şəhərlərin redaktəsi
                    for city in list(country['cities'].keys()):
                        cols = st.columns([3, 2, 1])
                        with cols[0]:
                            st.write(f"🏙️ {city}")
                        with cols[1]:
                            new_allowance = st.number_input(
                                "Müavinət",
                                value=country['cities'][city]['allowance'],
                                key=f"allowance_{selected_country}_{city}"
                            )
                            if new_allowance != country['cities'][city]['allowance']:
                                country['cities'][city]['allowance'] = new_allowance
                                save_countries_data(countries_data)
                                st.rerun()
                        with cols[2]:
                            if city != 'digər' and st.button("🗑️", key=f"delete_{selected_country}_{city}"):
                                del country['cities'][city]
                                save_countries_data(countries_data)
                                st.rerun()

            # Yeni hisse
            with st.expander("🏙️ Daxili Ezamiyyət Müavinətləri (Ətraflı)", expanded=True):
                st.markdown("""
                **İstifadə qaydası:**
                1. Yeni şəhər əlavə etmək üçün sol sahədən ad daxil edin
                2. Müvafiq müavinət məbləğini AZN ilə təyin edin
                3. "Əlavə et" düyməsinə basın
                4. Mövcud şəhərlərin məbləğlərini dəyişdirmək üçün sütunlarda redaktə edin
                5. "Digər" kateqoriyası üçün standart dəyəri təyin edin
                """)
                
                # Yeni şəhər əlavə etmə paneli
                cols = st.columns([2, 1, 1])
                with cols[0]:
                    new_city = st.text_input("Şəhər adı", key="new_city")
                with cols[1]:
                    new_city_allowance = st.number_input("Müavinət (AZN)", 
                                                       min_value=0, 
                                                       value=90, 
                                                       step=5,
                                                       key="new_city_allowance")
                with cols[2]:
                    if st.button("Əlavə et", key="add_new_city"):
                        try:
                            allowances = load_domestic_allowances()
                            # Əgər fayl korrupsiya olubsa
                            if not isinstance(allowances, dict):
                                st.warning("Müavinət məlumatları yenidən yaradılır...")
                                allowances = {'Digər': 90}
                            
                            if new_city and new_city not in allowances:
                                allowances[new_city] = new_city_allowance
                                save_domestic_allowances(allowances)
                                st.success(f"{new_city} üçün {new_city_allowance} AZN müavinət təyin edildi!")
                                st.rerun()
                            else:
                                st.error("Zəhmət olmasa unikal şəhər adı daxil edin!")
                        except Exception as e:
                            st.error(f"Xəta baş verdi: {str(e)}")
            
                # Mövcud məlumatların yüklənməsi
                try:
                    allowances = load_domestic_allowances()
                    # Əgər faylda 'Digər' yoxdursa
                    if 'Digər' not in allowances:
                        allowances['Digər'] = 90
                        save_domestic_allowances(allowances)
                except Exception as e:
                    st.error(f"Müavinət məlumatları yüklənmədi: {str(e)}")
                    allowances = {'Digər': 90}
                    save_domestic_allowances(allowances)
            
                # Digər kateqoriyası üçün tənzimləmə
                other_allowance = allowances.get('Digər', 90)
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
            
                # Mövcud şəhərlərin idarə edilməsi
                st.markdown("### 📋 Mövcud Şəhər Müavinətləri")
                try:
                    # DataFrame yaratmaq
                    df = pd.DataFrame({
                        'Şəhər': allowances.keys(),
                        'Müavinət (AZN)': allowances.values()
                    })
                    
                    # Data Editor ilə redaktə
                    edited_df = st.data_editor(
                        df,
                        column_config={
                            "Şəhər": st.column_config.TextColumn(
                                width="medium",
                                disabled=True
                            ),
                            "Müavinət (AZN)": st.column_config.NumberColumn(
                                min_value=0,
                                step=5,
                                format="%d AZN"
                            )
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    if st.button("💾 Bütün dəyişiklikləri saxla", key="save_all_changes"):
                        new_allowances = pd.Series(
                            edited_df['Müavinət (AZN)'].values, 
                            index=edited_df['Şəhər']
                        ).to_dict()
                        save_domestic_allowances(new_allowances)
                        st.success("Bütün dəyişikliklər uğurla yadda saxlanıldı!")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Cədvəl yaradılarkən xəta: {str(e)}")            
                
                
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
        with tab_currency:
            st.markdown("## Cbar.az Valyuta Məzənnələri")
            
            # Tarix seçimi
            selected_date = st.date_input(
                "Tarix seçin",
                datetime.now(),
                max_value=datetime.now(),
                format="DD.MM.YYYY"
            )
            
            # Məlumatları yüklə
            df_currency = get_currency_rates(selected_date)
            
            if not df_currency.empty:
                # Tələb olunan sütunların yoxlanılması
                required_columns = ['Valyuta', 'Ad', 'Nominal', 'Məzənnə', '1 vahid üçün AZN']
                if not all(col in df_currency.columns for col in required_columns):
                    st.error("Məlumatlar düzgün formatda deyil!")
                    st.stop()
                
                # Çeşidləmə parametrləri
                cols = st.columns([3,2])
                with cols[0]:
                    sort_by = st.selectbox(
                        "Çeşidləmə üçün sütun",
                        options=df_currency.columns,
                        index=0  # Default olaraq 'Valyuta' sütunu
                    )
                with cols[1]:
                    ascending = st.checkbox("Artan sıra", True)
                
                try:
                    # Çeşidləmə əməliyyatı
                    df_sorted = df_currency.sort_values(sort_by, ascending=ascending)
                    
                    # Cədvəlin göstərilməsi
                    st.markdown("### Bütün Valyuta Məzənnələri")
                    st.dataframe(
                        df_sorted,
                        use_container_width=True,
                        height=600,
                        column_config={
                            "1 vahid üçün AZN": st.column_config.NumberColumn(
                                format="%.4f AZN"
                            )
                        }
                    )
                    
                except KeyError as e:
                    st.error(f"Çeşidləmə xətası: {e} sütunu mövcud deyil")
                    st.stop()

                
                # Statistik məlumatlar
                st.markdown("### Statistik Məlumatlar")
                cols_stats = st.columns(3)
                cols_stats[0].metric(
                    "Ən yüksək məzənnə",
                    f"{df_currency['1 vahid üçün AZN'].max():.4f} AZN"
                )
                cols_stats[1].metric(
                    "Ən aşağı məzənnə",
                    f"{df_currency['1 vahid üçün AZN'].min():.4f} AZN"
                )
                cols_stats[2].metric(
                    "Orta məzənnə",
                    f"{df_currency['1 vahid üçün AZN'].mean():.4f} AZN"
                )
                
                # İxrac funksionallığı
                st.markdown("### İxrac Seçimləri")
                csv = df_currency.to_csv(index=False).encode('utf-8-sig')
                excel_buffer = BytesIO()
                df_currency.to_excel(excel_buffer, index=False)
                
                cols_export = st.columns(2)
                cols_export[0].download_button(
                    "CSV olaraq yüklə",
                    data=csv,
                    file_name=f"valyuta_mezenneleri_{selected_date.strftime('%d%m%Y')}.csv",
                    mime="text/csv"
                )
                cols_export[1].download_button(
                    "Excel olaraq yüklə",
                    data=excel_buffer.getvalue(),
                    file_name=f"valyuta_mezenneleri_{selected_date.strftime('%d%m%Y')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            else:
                st.warning("Seçilmiş tarix üçün məlumat tapılmadı!")    



if __name__ == "__main__":
    if not os.path.exists("ezamiyyet_melumatlari.xlsx"):
        pd.DataFrame(columns=[
            'Tarix', 'Ad', 'Soyad', 'Ata adı', 'Vəzifə', 'Şöbə', 
            'Ezamiyyət növü', 'Marşrut', 'Bilet qiyməti', 
            'Günlük müavinət', 'Başlanğıc tarixi', 'Bitmə tarixi', 
            'Günlər', 'Ümumi məbləğ', 'Məqsəd'
        ]).to_excel("ezamiyyet_melumatlari.xlsx", index=False)

    # # Köhnə valyuta faylını sil
    # if os.path.exists("currency_rates.xlsx"):
    #     os.remove("currency_rates.xlsx")
