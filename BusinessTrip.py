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
                    # YENİLİK 1: Dinamik yükləmə
                    countries_data = load_countries_data()
                    try:
                        currency_rates = pd.read_excel("currency_rates.xlsx").set_index('Valyuta')['Məzənnə'].to_dict()
                    except FileNotFoundError:
                        currency_rates = CURRENCY_RATES.copy()
                        st.warning("Valyuta məzənnələri faylı tapılmadı, standart dəyərlər istifadə olunur!")
                    
                    country = st.selectbox("Ölkə", list(countries_data.keys()))
                    
                    if country in countries_data:
                        # YENİLİK 2: Dinamik şəhər siyahısı
                        city_options = [c for c in countries_data[country]['cities'].keys() if c != 'digər']
                        city_options.append("digər")
                        selected_city = st.selectbox("Şəhər", city_options)
                        
                        if selected_city == "digər":
                            base_allowance = countries_data[country]['cities']['digər']['allowance']
                            currency = countries_data[country]['currency']
                        else:
                            base_allowance = countries_data[country]['cities'][selected_city]['allowance']
                            currency = countries_data[country]['currency']
                        
                        # YENİLİK 3: Dinamik valyuta məzənnəsi
                        exchange_rate = currency_rates.get(currency, 1.0)
                        
                        # Ödəniş rejimi seçimi
                        payment_mode = st.selectbox(
                            "Ödəniş rejimi",
                            options=["Adi rejim", "Günlük Normaya 50% əlavə", "Günlük Normaya 30% əlavə"]
                        )
                        
                        # Günlük müavinətin hesablanması (ORİJİNAL VALYUTADA)
                        if payment_mode == "Adi rejim":
                            daily_allowance_foreign = float(base_allowance)
                        elif payment_mode == "Günlük Normaya 50% əlavə":
                            daily_allowance_foreign = float(base_allowance * 1.5)
                        else:
                            daily_allowance_foreign = float(base_allowance * 1.3)
                        
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
                        country_data = countries_data[country]  # COUNTRIES 
                        
                        if selected_city == "digər":
                            base_allowance = country_data['cities']['digər']['allowance']
                            currency = country_data['currency']
                        else:
                            city_data = country_data['cities'][selected_city]
                            base_allowance = city_data['allowance']
                            currency = country_data['currency']
                        
                        exchange_rate = currency_rates.get(currency, 1.0)  # Valyuta məzənnəsi

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
        with tab_currency:
            st.markdown("### Valyuta Məzənnələrinin İdarə Edilməsi")
            currency_df = pd.read_excel("currency_rates.xlsx")
            
            edited_currency = st.data_editor(
                currency_df,
                num_rows="dynamic",
                column_config={
                    "Məzənnə": st.column_config.NumberColumn(
                        "AZN qarşılığı",
                        format="%.4f",
                        min_value=0.0001,
                        default=1.0
                    )
                }
            )
        
            if st.button("💾 Valyuta məzənnələrini saxla"):
                edited_currency.to_excel("currency_rates.xlsx", index=False)
                st.success("Məzənnələr yeniləndi!")



if __name__ == "__main__":
    # Create main data file if not exists
    if not os.path.exists("ezamiyyet_melumatlari.xlsx"):
        pd.DataFrame(columns=[
            'Tarix', 'Ad', 'Soyad', 'Ata adı', 'Vəzifə', 'Şöbə', 
            'Ezamiyyət növü', 'Ödəniş növü', 'Qonaqlama növü',
            'Marşrut', 'Bilet qiyməti', 'Günlük müavinət', 
            'Başlanğıc tarixi', 'Bitmə tarixi', 'Günlər', 
            'Ümumi məbləğ', 'Məqsəd'
        ]).to_excel("ezamiyyet_melumatlari.xlsx", index=False)
    
    # Create currency rates file if not exists
    if not os.path.exists("currency_rates.xlsx"):
        pd.DataFrame({
            'Valyuta': list(CURRENCY_RATES.keys()),
            'Məzənnə': list(CURRENCY_RATES.values())
        }).to_excel("currency_rates.xlsx", index=False)


