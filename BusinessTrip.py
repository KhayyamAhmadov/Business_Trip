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
    "Rusiya Federasiyası": {
        "currency": "USD",
        "cities": {
            "Moskva": {"allowance": 260, "currency": "USD"},
            "Sankt-Peterburq": {"allowance": 260, "currency": "USD"},
            "digər": {"allowance": 170, "currency": "USD"}
        }
    },
    "Tacikistan": {
        "currency": "USD",
        "cities": {
            "Düşənbə": {"allowance": 165, "currency": "USD"},
            "digər": {"allowance": 140, "currency": "USD"}
        }
    },
    "Özbəkistan": {
        "currency": "USD",
        "cities": {
            "Daşkənd": {"allowance": 180, "currency": "USD"},
            "digər": {"allowance": 140, "currency": "USD"}
        }
    },
    "Belarus": {
        "currency": "USD",
        "cities": {
            "Minsk": {"allowance": 180, "currency": "USD"},
            "digər": {"allowance": 140, "currency": "USD"}
        }
    },
    "Ukrayna": {
        "currency": "USD",
        "cities": {
            "Kiyev": {"allowance": 210, "currency": "USD"},
            "digər": {"allowance": 160, "currency": "USD"}
        }
    },
    "Moldova": {
        "currency": "USD",
        "cities": {
            "Kişineu": {"allowance": 150, "currency": "USD"},
            "digər": {"allowance": 150, "currency": "USD"}
        }
    },
    "Qazaxıstan": {
        "currency": "USD",
        "cities": {
            "Almatı": {"allowance": 200, "currency": "USD"},
            "Astana": {"allowance": 200, "currency": "USD"},
            "digər": {"allowance": 150, "currency": "USD"}
        }
    },
    "Qırğızıstan": {
        "currency": "USD",
        "cities": {
            "Bişkek": {"allowance": 160, "currency": "USD"},
            "digər": {"allowance": 130, "currency": "USD"}
        }
    },
    "Gürcüstan": {
        "currency": "USD",
        "cities": {
            "Tbilisi": {"allowance": 200, "currency": "USD"},
            "digər": {"allowance": 155, "currency": "USD"}
        }
    },
    "Türkmənistan": {
        "currency": "USD",
        "cities": {
            "Aşqabad": {"allowance": 150, "currency": "USD"},
            "digər": {"allowance": 125, "currency": "USD"}
        }
    },
    "Latviya": {
        "currency": "EUR",
        "cities": {
            "Riqa": {"allowance": 180, "currency": "EUR"},
            "digər": {"allowance": 150, "currency": "EUR"}
        }
    },
    "Litva": {
        "currency": "EUR",
        "cities": {
            "Vilnüs": {"allowance": 180, "currency": "EUR"},
            "digər": {"allowance": 150, "currency": "EUR"}
        }
    },
    "Estoniya": {
        "currency": "EUR",
        "cities": {
            "Tallin": {"allowance": 180, "currency": "EUR"},
            "digər": {"allowance": 150, "currency": "EUR"}
        }
    },
    "Böyük Britaniya": {
        "currency": "GBP",
        "cities": {
            "London": {"allowance": 280, "currency": "GBP"},
            "digər": {"allowance": 250, "currency": "GBP"}
        }
    },
    "Lixtenşteyn": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 250, "currency": "EUR"}
        }
    },
    "Avstriya": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 250, "currency": "EUR"}
        }
    },
    "Almaniya": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 250, "currency": "EUR"}
        }
    },
    "Belçika": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 250, "currency": "EUR"}
        }
    },
    "İrlandiya": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 250, "currency": "EUR"}
        }
    },
    "Monako": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 250, "currency": "EUR"}
        }
    },
    "Norveç": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 280, "currency": "EUR"}
        }
    },
    "Niderland": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 270, "currency": "EUR"}
        }
    },
    "San-Marino": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 240, "currency": "EUR"}
        }
    },
    "Fransa": {
        "currency": "EUR",
        "cities": {
            "Paris": {"allowance": 300, "currency": "EUR"},
            "digər": {"allowance": 250, "currency": "EUR"}
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
    "İtaliya": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 250, "currency": "EUR"}
        }
    },
    "Xorvatiya": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 250, "currency": "EUR"}
        }
    },
    "Bosniya və Herseqovina": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 200, "currency": "EUR"}
        }
    },
    "Danimarka": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 250, "currency": "EUR"}
        }
    },
    "İsveçrə": {
        "currency": "EUR",
        "cities": {
            "Bern": {"allowance": 330, "currency": "EUR"},
            "Cenevrə": {"allowance": 330, "currency": "EUR"},
            "Sürix": {"allowance": 330, "currency": "EUR"},
            "digər": {"allowance": 310, "currency": "EUR"}
        }
    },
    "Lüksemburq": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 290, "currency": "EUR"}
        }
    },
    "Makedoniya": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 190, "currency": "EUR"}
        }
    },
    "Kipr": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 200, "currency": "EUR"}
        }
    },
    "Macarıstan": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 200, "currency": "EUR"}
        }
    },
    "Malta": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 230, "currency": "EUR"}
        }
    },
    "Portuqaliya": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 250, "currency": "EUR"}
        }
    },
    "Slovakiya": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 200, "currency": "EUR"}
        }
    },
    "Finlandiya": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 250, "currency": "EUR"}
        }
    },
    "Çexiya": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 200, "currency": "EUR"}
        }
    },
    "Serbiya": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 200, "currency": "EUR"}
        }
    },
    "Monteneqro": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 200, "currency": "EUR"}
        }
    },
    "Andorra": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 200, "currency": "EUR"}
        }
    },
    "Albaniya": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 180, "currency": "EUR"}
        }
    },
    "Yunanıstan": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 230, "currency": "EUR"}
        }
    },
    "İslandiya": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 250, "currency": "EUR"}
        }
    },
    "İspaniya": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 260, "currency": "EUR"}
        }
    },
    "Polşa": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 220, "currency": "EUR"}
        }
    },
    "İsveç": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 300, "currency": "EUR"}
        }
    },
    "Bolqarıstan": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 185, "currency": "EUR"}
        }
    },
    "Rumıniya": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 220, "currency": "EUR"}
        }
    },
    "Sloveniya": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 220, "currency": "EUR"}
        }
    },
    "ABŞ": {
        "currency": "USD",
        "cities": {
            "Nyu-York": {"allowance": 450, "currency": "USD"},
            "digər": {"allowance": 350, "currency": "USD"}
        }
    },
    "Argentina": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 220, "currency": "USD"}
        }
    },
    "Braziliya": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 250, "currency": "USD"}
        }
    },
    "Kanada": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 300, "currency": "USD"}
        }
    },
    "Meksika": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 220, "currency": "USD"}
        }
    },
    "Amerika qitəsi üzrə digər ölkələr": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 200, "currency": "USD"}
        }
    },
    "Bəhreyn": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 220, "currency": "USD"}
        }
    },
    "Səudiyyə Ərəbistanı": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 250, "currency": "USD"}
        }
    },
    "Birləşmiş Ərəb Əmirlikləri": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 280, "currency": "USD"}
        }
    },
    "İordaniya": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 180, "currency": "USD"}
        }
    },
    "İran": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 160, "currency": "USD"}
        }
    },
    "Qətər": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 250, "currency": "USD"}
        }
    },
    "Küveyt": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 220, "currency": "USD"}
        }
    },
    "Oman": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 220, "currency": "USD"}
        }
    },
    "Suriya": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 200, "currency": "USD"}
        }
    },
    "İraq": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 190, "currency": "USD"}
        }
    },
    "İsrail": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 250, "currency": "USD"}
        }
    },
    "Fələstin": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 200, "currency": "USD"}
        }
    },
    "Livan": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 200, "currency": "USD"}
        }
    },
    "Liviya": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 200, "currency": "USD"}
        }
    },
    "Bruney": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 190, "currency": "USD"}
        }
    },
    "Yəmən": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 190, "currency": "USD"}
        }
    },
    "Əlcəzair": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 190, "currency": "USD"}
        }
    },
    "Mərakeş": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 200, "currency": "USD"}
        }
    },
    "Misir": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 220, "currency": "USD"}
        }
    },
    "Tunis": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 180, "currency": "USD"}
        }
    },
    "Seneqal": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 200, "currency": "USD"}
        }
    },
    "Cənubi Afrika Respublikası": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 200, "currency": "USD"}
        }
    },
    "Afrika qitəsi üzrə digər ölkələr": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 180, "currency": "USD"}
        }
    },
    "Çin Xalq Respublikası": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 250, "currency": "USD"}
        }
    },
    "Sinqapur": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 320, "currency": "USD"}
        }
    },
    "Tailand": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 220, "currency": "USD"}
        }
    },
    "Malayziya": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 220, "currency": "USD"}
        }
    },
    "Şri-Lanka": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 180, "currency": "USD"}
        }
    },
    "Hindistan": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 180, "currency": "USD"}
        }
    },
    "Nepal": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 180, "currency": "USD"}
        }
    },
    "Banqladeş": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 170, "currency": "USD"}
        }
    },
    "Pakistan": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 200, "currency": "USD"}
        }
    },
    "Butan": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 145, "currency": "USD"}
        }
    },
    "Myanma": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 155, "currency": "USD"}
        }
    },
    "Monqolustan": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 180, "currency": "USD"}
        }
    },
    "Laos": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 170, "currency": "USD"}
        }
    },
    "Vyetnam": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 180, "currency": "USD"}
        }
    },
    "İndoneziya": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 220, "currency": "USD"}
        }
    },
    "Əfqanıstan": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 180, "currency": "USD"}
        }
    },
    "Kamboca": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 180, "currency": "USD"}
        }
    },
    "Mali": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 200, "currency": "USD"}
        }
    },
    "Maldiv adaları": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 200, "currency": "USD"}
        }
    },
    "Hibraltar": {
        "currency": "EUR",
        "cities": {
            "digər": {"allowance": 180, "currency": "EUR"}
        }
    },
    "Koreya Xalq Demokratik Respublikası (KXDR)": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 230, "currency": "USD"}
        }
    },
    "Koreya Respublikası": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 250, "currency": "USD"}
        }
    },
    "Yaponiya": {
        "currency": "JPY",
        "cities": {
            "digər": {"allowance": 40000, "currency": "JPY"}
        }
    },
    "Filippin": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 220, "currency": "USD"}
        }
    },
    "Yeni Zelandiya": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 250, "currency": "USD"}
        }
    },
    "Avstraliya və Okeaniya": {
        "currency": "USD",
        "cities": {
            "digər": {"allowance": 270, "currency": "USD"}
        }
    }
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

# Fayl yoxlamaları ən başda
if not os.path.exists("countries_data.json"):
    with open('countries_data.json', 'w', encoding='utf-8') as f:
        json.dump(COUNTRIES, f, ensure_ascii=False, indent=4)

# Valyuta məzənnələri faylı
if not os.path.exists("currency_rates.xlsx"):
    pd.DataFrame({
        'Valyuta': list(CURRENCY_RATES.keys()),
        'Məzənnə': list(CURRENCY_RATES.values())
    }).to_excel("currency_rates.xlsx", index=False)

# Əsas məlumatlar faylı
if not os.path.exists("ezamiyyet_melumatlari.xlsx"):
    pd.DataFrame(columns=[
        'Tarix', 'Ad', 'Soyad', 'Ata adı', 'Vəzifə', 'Şöbə', 
        'Ezamiyyət növü', 'Ödəniş növü', 'Qonaqlama növü',
        'Marşrut', 'Bilet qiyməti', 'Günlük müavinət', 
        'Başlanğıc tarixi', 'Bitmə tarixi', 'Günlər', 
        'Ümumi məbləğ', 'Məqsəd'
    ]).to_excel("ezamiyyet_melumatlari.xlsx", index=False)


MELUMATLAR_JSON = "melumatlar.json"
# Fayl yoxlamaları (əvvəlki yoxlamalara əlavə)
if not os.path.exists(MELUMATLAR_JSON):
    with open(MELUMATLAR_JSON, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=4)


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


def load_countries_data():
    try:
        with open('countries_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Default məlumatları yadda saxla
        with open('countries_data.json', 'w', encoding='utf-8') as f:
            json.dump(COUNTRIES, f, ensure_ascii=False, indent=4)
        return COUNTRIES

def save_countries_data(data):
    with open('countries_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@st.cache_data(ttl=3600)
def get_currency_rates(date):
    """
    Cbar.az-dan konkret tarix üçün valyuta məzənnələrini çəkərək DataFrame qaytarır
    """
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
    country_data = countries_data[country]
    
    # Gün və gecə sayının hesablanması
    trip_days = (end_date - start_date).days + 1
    trip_nights = max(trip_days - 1, 0)
    
    # Məzənnənin alınması
    try:
        currency_df = get_currency_rates(start_date)
        if currency_df.empty:
            st.error("Valyuta məlumatları yoxdur!")
            return None
            
        exchange_rate = currency_df.loc[
            currency_df['Valyuta'] == country_data['currency'], 
            '1 vahid üçün AZN'
        ].values[0]
        
    except IndexError:
        st.error(f"{country_data['currency']} valyutası tapılmadı!")
        return None
    except Exception as e:
        st.error(f"Məzənnə xətası: {str(e)}")
        return None

    # Əsas müavinətin təyin edilməsi
    if city == "digər":
        base_allowance = country_data['cities']['digər']['allowance']
    else:
        base_allowance = country_data['cities'][city]['allowance']
    
    # Ödəniş rejimi
    payment_multiplier = 1.0
    if payment_mode == "Günlük Normaya 50% əlavə":
        payment_multiplier = 1.5
    elif payment_mode == "Günlük Normaya 30% əlavə":
        payment_multiplier = 1.3
    
    daily_allowance = base_allowance * payment_multiplier
    
    # Qonaqlama növü
    hotel_ratio = 0.6
    daily_ratio = 0.4
    if accommodation == "Yalnız yaşayış yeri ilə təmin edir":
        hotel_ratio = 0.0
        daily_ratio = 1.0
    elif accommodation == "Yalnız gündəlik xərcləri təmin edir":
        hotel_ratio = 1.0
        daily_ratio = 0.0
    
    # Ümumi məbləğin hesablanması
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


st.markdown('<div class="main-header"><h1>✈️ Ezamiyyət İdarəetmə Sistemi</h1></div>', unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["📋 Yeni Ezamiyyət", "🔐 Admin Paneli", "📋 Məlumatlar və Qeydlər",])

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

            with st.expander("🏢 Təşkilat Məlumatları", expanded=True):
                department = st.selectbox("Şöbə", DEPARTMENTS)

            with st.expander("🧳 Ezamiyyət Detalları", expanded=True):
                trip_type = st.radio("Növ", ["Ölkə daxili", "Ölkə xarici"])
                
                if trip_type == "Ölkə daxili":
                    if 'trips' not in st.session_state:
                        st.session_state.trips = []
                    
                    # Yeni səfər əlavə etmə interfeysi
                    cols = st.columns([3,1])
                    with cols[0]:
                        st.subheader("Səfər Planı")
                    with cols[1]:
                        if st.button("➕ Yeni səfər əlavə et"):
                            st.session_state.trips.append({
                                'from_city': 'Bakı',
                                'to_city': 'Bakı',
                                'start_date': datetime.now().date(),
                                'end_date': datetime.now().date(),
                                'ticket_price': 0
                            })
                    
                    # Səfərlərin siyahısı
                    for i, trip in enumerate(st.session_state.trips):
                        with st.expander(f"Səfər #{i+1}", expanded=True):
                            cols = st.columns([2,2,2,2,1])
                            with cols[0]:
                                trip['from_city'] = st.selectbox(
                                    f"Haradan #{i+1}", 
                                    CITIES,
                                    key=f'from_{i}'
                                )
                            with cols[1]:
                                trip['to_city'] = st.selectbox(
                                    f"Haraya #{i+1}", 
                                    [c for c in CITIES if c != trip['from_city']],
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
                            
                            if st.button(f"Səfəri sil #{i+1}", key=f'del_{i}'):
                                del st.session_state.trips[i]
                                st.rerun()
                
                    # Hesablama hissəsi
                    if st.session_state.trips:
                        total_days = 0
                        total_hotel = 0
                        total_daily = 0
                        total_transport = 0
                        daily_allowances = []
                        
                        # Tarixləri sırala və üst-üstə düşən günləri tənzimlə
                        sorted_trips = sorted(st.session_state.trips, key=lambda x: x['start_date'])
                        prev_end = None
                        
                        for trip in sorted_trips:
                            days = (trip['end_date'] - trip['start_date']).days + 1
                            
                            # Üst-üstə düşən günləri çıx
                            if prev_end and trip['start_date'] <= prev_end:
                                overlap = (prev_end - trip['start_date']).days + 1
                                days = max(0, days - overlap)
                            
                            allowance = DOMESTIC_ALLOWANCES.get(
                                trip['to_city'], 
                                DOMESTIC_ALLOWANCES['Digər']
                            )
                            
                            hotel_cost = allowance * 0.7 * max(days-1, 0)
                            daily_cost = allowance * 0.3 * days
                            total_transport += trip['ticket_price']
                            total_days += days
                            total_hotel += hotel_cost
                            total_daily += daily_cost
                            
                            prev_end = trip['end_date']
                            
                            daily_allowances.append({
                                'Şəhər': trip['to_city'],
                                'Günlər': days,
                                'Gecələr': max(days-1, 0),
                                'Müavinət': allowance,
                                'Mehmanxana': hotel_cost,
                                'Gündəlik': daily_cost,
                                'Ümumi': hotel_cost + daily_cost
                            })
                
                        # Nəticələrin göstərilməsi
                        st.subheader("Hesablama Nəticələri")
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Ümumi Günlər", total_days)
                        col2.metric("Ümumi Gecələr", max(total_days-1, 0))
                        col3.metric("Ümumi Nəqliyyat", f"{total_transport} AZN")
                        
                        cols = st.columns(2)
                        cols[0].metric("Ümumi Mehmanxana Xərcləri", f"{total_hotel:.2f} AZN")
                        cols[1].metric("Ümumi Gündəlik Xərclər", f"{total_daily:.2f} AZN")
                        
                        st.metric("📈 Ümumi Məbləğ", f"{total_hotel + total_daily + total_transport:.2f} AZN")
                        
                        # Detal cədvəli
                        df_details = pd.DataFrame(daily_allowances)
                        st.dataframe(
                            df_details,
                            column_config={
                                "Şəhər": "Hədəf şəhər",
                                "Günlər": st.column_config.NumberColumn(format="%d gün"),
                                "Gecələr": st.column_config.NumberColumn(format="%d gecə"),
                                "Müavinət": st.column_config.NumberColumn(format="%.2f AZN/gün"),
                                "Mehmanxana": st.column_config.NumberColumn(format="%.2f AZN"),
                                "Gündəlik": st.column_config.NumberColumn(format="%.2f AZN"),
                                "Ümumi": st.column_config.NumberColumn(format="%.2f AZN")
                            },
                            hide_index=True
                        )
                    else:
                        st.warning("Ən azı bir səfər əlavə edin!")
                else:  # Ölkə xarici ezamiyyət
                    countries_data = load_countries_data()
                    country = st.selectbox("Ölkə", list(countries_data.keys()))
                    
                    if country in countries_data:
                        city_options = [c for c in countries_data[country]['cities'].keys() if c != 'digər']
                        city_options.append("digər")
                        selected_city = st.selectbox("Şəhər", city_options)
                        
                        payment_mode = st.selectbox(
                            "Ödəniş rejimi",
                            options=["Adi rejim", "Günlük Normaya 50% əlavə", "Günlük Normaya 30% əlavə"]
                        )
                        
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
                        
                        if start_date and end_date and start_date <= end_date:
                            result = calculate_international_trip(
                                country, selected_city, payment_mode, 
                                accommodation, start_date, end_date
                            )
                            
                            st.subheader("Hesablama Nəticələri")
                            
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
                            
                            st.metric("💳 Ümumi məbləğ", 
                                     f"{result['total_foreign']:.2f} {result['currency']} / {result['total_azn']:.2f} AZN")
                            
                            if accommodation == "Adi Rejim":
                                st.info("Adi Rejim: Günlük müavinətin 60%-i mehmanxana xərclərinə, 40%-i gündəlik xərclərə ayrılır")
                            elif accommodation == "Yalnız yaşayış yeri ilə təmin edir":
                                st.info("Yalnız gündəlik xərclər ödənilir (günlük müavinətin 40%-i)")
                            elif accommodation == "Yalnız gündəlik xərcləri təmin edir":
                                st.info("Yalnız mehmanxana xərcləri ödənilir (günlük müavinətin 60%-i × gecə sayı)")
                        else:
                            st.error("Bitmə tarixi başlanğıc tarixindən əvvəl ola bilməz!")


        # Sağ Sütun (Hesablama)
        with col2:
            if trip_type == "Ölkə daxili":
                if st.session_state.trips:
                    total_days = 0
                    total_amount = 0
                    total_transport = 0
                    daily_allowances = []
                    
                    # Tarixləri sırala və üst-üstə düşən günləri tənzimlə
                    sorted_trips = sorted(st.session_state.trips, key=lambda x: x['start_date'])
                    prev_end = None
                    
                    for i, trip in enumerate(sorted_trips):
                        days = (trip['end_date'] - trip['start_date']).days + 1
                        if prev_end and trip['start_date'] <= prev_end:
                            overlap = (prev_end - trip['start_date']).days + 1
                            days = max(0, days - overlap)

                        # hdsajdhsajdkha
                        domestic_allowances = load_domestic_allowances()  # <-- ƏLAVƏ EDİN
                        allowance = domestic_allowances.get(  # <-- ƏVVƏLKI DOMESTIC_ALLOWANCES əvəz edin
                            trip['to_city'], 
                            domestic_allowances['Digər']
                        )
                        
                        trip_amount = allowance * days
                        total_amount += trip_amount
                        total_transport += trip['ticket_price']
                        total_days += days
                        
                        prev_end = trip['end_date']
                    
                    st.markdown('<div class="section-header">💰 Hesablama</div>', unsafe_allow_html=True)
                    
                    # Səfər detalları
                    with st.expander("📑 Səfər Detalları", expanded=True):
                        for i, trip in enumerate(sorted_trips):
                            days = (trip['end_date'] - trip['start_date']).days + 1
                            allowance = domestic_allowances.get(trip['to_city'], domestic_allowances['Digər'])
                            st.write(f"""
                            **Səfər #{i+1}**  
                            🚩 {trip['from_city']} → {trip['to_city']}  
                            📅 {trip['start_date'].strftime('%d.%m.%Y')} - {trip['end_date'].strftime('%d.%m.%Y')}  
                            🕒 {days} gün | 🚌 {trip['ticket_price']} AZN  
                            💰 Gündəlik: {allowance} AZN × {days} = {allowance*days} AZN
                            """)
                    
                    # Ümumi statistikalar
                    st.metric("⏳ Ümumi müddət", f"{total_days} gün")
                    st.metric("🚌 Ümumi nəqliyyat", f"{total_transport} AZN")
                    st.metric("💳 Ümumi müavinət", f"{total_amount} AZN")
                    st.metric("📈 Ümumi məbləğ", f"{total_amount + total_transport} AZN")
                else:
                    st.warning("Ən azı bir səfər əlavə edin!")
            
            else:  # Ölkə xarici ezamiyyət
                country_data = COUNTRIES[country]
                trip_days = (end_date - start_date).days + 1
                trip_nights = trip_days - 1 if trip_days > 0 else 0
                
                try:
                    currency_df = get_currency_rates(start_date)
                    if currency_df.empty:
                        st.error("Valyuta məzənnələri alına bilmədi!")
                        st.stop()
                    
                    exchange_rate = currency_df.loc[
                        currency_df['Valyuta'] == country_data['currency'], 
                        '1 vahid üçün AZN'
                    ].values[0]
                    
                except Exception as e:
                    st.error(f"Məzənnə alınarkən xəta: {str(e)}")
                    exchange_rate = 1.0
                
                # Gündəlik müavinət hesablamaları
                if selected_city == "digər":
                    base_allowance = country_data['cities']['digər']['allowance']
                else:
                    base_allowance = country_data['cities'][selected_city]['allowance']
                
                # Ödəniş rejimi
                if payment_mode == "Günlük Normaya 50% əlavə":
                    daily_allowance_foreign = base_allowance * 1.5
                elif payment_mode == "Günlük Normaya 30% əlavə":
                    daily_allowance_foreign = base_allowance * 1.3
                else:
                    daily_allowance_foreign = base_allowance
                
                # Qonaqlama növü
                if accommodation == "Adi Rejim":
                    hotel_ratio = 0.6
                    daily_ratio = 0.4
                elif accommodation == "Yalnız yaşayış yeri ilə təmin edir":
                    hotel_ratio = 0.0
                    daily_ratio = 0.4
                else:
                    hotel_ratio = 0.6
                    daily_ratio = 0.0
                
                # Ümumi məbləğ hesablamaları
                total_foreign = (
                    (daily_allowance_foreign * daily_ratio * trip_days) +
                    (daily_allowance_foreign * hotel_ratio * trip_nights)
                )
                total_azn = total_foreign * exchange_rate
                
                # Göstəricilər
                st.markdown('<div class="section-header">💰 Hesablama</div>', unsafe_allow_html=True)
                cols = st.columns(2)
                cols[0].metric("💵 Gündəlik müavinət", 
                              f"{daily_allowance_foreign:.2f} {country_data['currency']}")
                cols[1].metric("🔢 Məzənnə", 
                              f"1 {country_data['currency']} = {exchange_rate:.4f} AZN")
                
                st.metric("📅 Ümumi müddət", f"{trip_days} gün ({trip_nights} gecə)")
                
                cost_cols = st.columns(2)
                cost_cols[0].metric("🏨 Yaşayış xərcləri", 
                                   f"{(daily_allowance_foreign * hotel_ratio * trip_nights):.2f} {country_data['currency']}")
                cost_cols[1].metric("🍽️ Gündəlik xərclər", 
                                   f"{(daily_allowance_foreign * daily_ratio * trip_days):.2f} {country_data['currency']}")
                
                st.metric("💳 Ümumi məbləğ", 
                         f"{total_foreign:.2f} {country_data['currency']} / {total_azn:.2f} AZN")
                        
                # Əlavə məlumat  
                if accommodation == "Adi Rejim":
                    st.caption("ℹ️ Adi Rejim: Günlük müavinətin 60%-i mehmanxana xərclərinə, 40%-i gündəlik xərclərə ayrılır")
                elif accommodation == "Yalnız yaşayış yeri ilə təmin edir":
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
                            if 'result' not in locals():
                                st.error("Zəhmət olmasa əvvəlcə tarixləri düzgün daxil edin!")
                                return

                            # fdasfsadf
                            total_azn = result['total_azn']
                            daily_allowance_foreign = result['daily_allowance']
                            currency = result['currency']
                            exchange_rate = result['exchange_rate']
                            total_foreign = result['total_foreign']


        
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
                            "Günlük müavinət (AZN)": daily_allowance_foreign * exchange_rate,
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
                    fig = px.scatter(df, x='Başlanğıc tarixi', y='Ümumi məbləğ', 
                                    color='Şöbə', size='Günlər',
                                    title='Səfərlərin Zaman Qrafiki')
                    st.plotly_chart(fig, use_container_width=True)


                # Məlumat cədvəli
                with st.expander("🔍 Bütün Qeydlər", expanded=True):
                    column_config = {
                        'Tarix': st.column_config.DatetimeColumn(format="DD.MM.YYYY HH:mm"),
                        'Ad': st.column_config.TextColumn("Ad"),
                        'Soyad': st.column_config.TextColumn("Soyad"),
                        'Ata adı': st.column_config.TextColumn("Ata adı"),
                        'Vəzifə': st.column_config.TextColumn("Vəzifə"),
                        'Şöbə': st.column_config.TextColumn("Şöbə"),
                        'Ezamiyyət növü': st.column_config.TextColumn("Növ"),
                        'Ödəniş rejimi': st.column_config.TextColumn("Ödəniş rejimi"),
                        'Qonaqlama növü': st.column_config.TextColumn("Qonaqlama növü"),
                        'Marşrut': st.column_config.TextColumn(width="medium"),
                        'Bilet qiyməti': st.column_config.NumberColumn(format="%.2f AZN"),
                        'Günlük müavinət (Valyuta)': st.column_config.TextColumn("Gündəlik müavinət (Valyuta)"),
                        'Günlük müavinət (AZN)': st.column_config.NumberColumn(format="%.2f AZN"),
                        'Ümumi məbləğ (Valyuta)': st.column_config.TextColumn("Ümumi məbləğ (Valyuta)"),
                        'Ümumi məbləğ (AZN)': st.column_config.NumberColumn(format="%.2f AZN"),
                        'Valyuta': st.column_config.TextColumn("Valyuta"),
                        'Məzənnə': st.column_config.NumberColumn(format="%.4f"),
                        'Başlanğıc tarixi': st.column_config.DateColumn(format="DD.MM.YYYY"),
                        'Bitmə tarixi': st.column_config.DateColumn(format="DD.MM.YYYY"),
                        'Günlər': st.column_config.NumberColumn(format="%d"),
                        'Gecələr': st.column_config.NumberColumn(format="%d"),
                        'Məqsəd': st.column_config.TextColumn("Məqsəd")
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


        # YENİ YAZILAR İDARƏETMƏ SEKMESİ
        with tab_texts:
            st.markdown('<div class="section-header">📝 Məlumatların İdarə Edilməsi</div>', unsafe_allow_html=True)
            
            try:
                with open(MELUMATLAR_JSON, 'r', encoding='utf-8') as f:
                    sections = json.load(f)
            except Exception as e:
                st.error(f"Fayl oxuma xətası: {str(e)}")
                sections = {}
    
            # Yeni bölmə əlavə et
            with st.expander("➕ Yeni Bölmə Əlavə Et", expanded=True):
                new_title = st.text_input("Başlıq", key="new_section_title")
                new_content = st.text_area("Məzmun (Markdown dəstəklənir)", height=300, key="new_section_content")
                
                if st.button("Yadda Saxla", key="save_new_section"):
                    if new_title.strip():
                        new_id = f"section_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        sections[new_id] = {
                            "title": new_title,
                            "content": new_content,
                            "created_at": datetime.now().isoformat()
                        }
                        with open(MELUMATLAR_JSON, 'w', encoding='utf-8') as f:
                            json.dump(sections, f, ensure_ascii=False, indent=4)
                        st.success("Yeni bölmə əlavə edildi!")
                        st.rerun()
                    else:
                        st.error("Başlıq daxil edilməlidir!")
    
            # Mövcud bölmələrin redaktəsi
            st.markdown("### 📋 Mövcud Bölmələr")
            if not sections:
                st.info("Hələ heç bir bölmə yoxdur")
            else:
                for section_id in list(sections.keys()):
                    section_data = sections[section_id]
                    with st.expander(f"✏️ {section_data.get('title', 'Başlıqsız')}", expanded=False):
                        edited_title = st.text_input(
                            "Başlıq", 
                            value=section_data.get('title', ''),
                            key=f"title_{section_id}"
                        )
                        edited_content = st.text_area(
                            "Məzmun", 
                            value=section_data.get('content', ''),
                            height=300,
                            key=f"content_{section_id}"
                        )
                        
                        cols = st.columns([4,1,1])
                        with cols[0]:
                            if st.button("💾 Saxla", key=f"save_{section_id}"):
                                sections[section_id]['title'] = edited_title
                                sections[section_id]['content'] = edited_content
                                with open(MELUMATLAR_JSON, 'w', encoding='utf-8') as f:
                                    json.dump(sections, f, ensure_ascii=False, indent=4)
                                st.success("Dəyişikliklər yadda saxlanıldı!")
                        with cols[1]:
                            if st.button("🗑️ Sil", key=f"delete_{section_id}"):
                                del sections[section_id]
                                with open(MELUMATLAR_JSON, 'w', encoding='utf-8') as f:
                                    json.dump(sections, f, ensure_ascii=False, indent=4)
                                st.success("Bölmə silindi!")
                                st.rerun()
                        with cols[2]:
                            created_at = section_data.get('created_at', 'Tarix bilinmir')
                            st.caption(f"Yaradılma tarixi: {created_at[:10]}")
    
            new_other = st.number_input(
                "Digər parametr", 
                key="unique_key_for_texts_tab"  # Unikalliq
            )


# ====================================================================================================
with tab3:
    st.markdown('<div class="section-header">📋 Məlumatlar və Qeydlər</div>', unsafe_allow_html=True)
    
    try:
        with open(MELUMATLAR_JSON, 'r', encoding='utf-8') as f:
            sections = json.load(f)
            
            if not sections:
                st.info("Hələ heç bir məlumat əlavə edilməyib")
            else:
                for section_id, section_data in sections.items():
                    with st.expander(f"📌 {section_data.get('title', 'Başlıqsız')}", expanded=True):
                        st.markdown(section_data.get('content', ''))
    except Exception as e:
        st.error(f"Məlumatlar yüklənərkən xəta: {str(e)}")



if __name__ == "__main__":
    # İlkin fayl yoxlamaları
    if not os.path.exists("ezamiyyet_melumatlari.xlsx"):
        pd.DataFrame(columns=[
            'Tarix', 'Ad', 'Soyad', 'Ata adı', 'Vəzifə', 'Şöbə', 
            'Ezamiyyət növü', 'Ödəniş növü', 'Qonaqlama növü',
            'Marşrut', 'Bilet qiyməti', 'Günlük müavinət', 
            'Başlanğıc tarixi', 'Bitmə tarixi', 'Günlər', 
            'Ümumi məbləğ', 'Məqsəd'
        ]).to_excel("ezamiyyet_melumatlari.xlsx", index=False)
    
    # Köhnə valyuta faylını sil
    if os.path.exists("currency_rates.xlsx"):
        os.remove("currency_rates.xlsx")
