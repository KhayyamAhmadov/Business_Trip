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
    
    /* ================= INPUT STILLERI ================= */
    .stTextInput input, .stNumberInput input, 
    .stDateInput input, .stSelectbox select, 
    .stTextArea textarea {
        background-color: white !important;
        color: black !important;
        border: 1px solid #ccc !important;
    }
    
    .stTextInput input::placeholder, 
    .stNumberInput input::placeholder, 
    .stTextArea textarea::placeholder {
        color: #666 !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus, 
    .stDateInput input:focus, .stSelectbox select:focus, 
    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
        outline: none !important;
    }
    
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: white !important;
        color: black !important;
    }
    
    .stDateInput input {
        color: black !important;
    }
    
    /* ================= GENEL STILLER ================= */
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


# currency_rates.xlsx faylı üçün nümunə məlumatlar
CURRENCY_RATES = {
    "USD": 1.7,
    "EUR": 1.9,
    "TRY": 0.2,
    "RUB": 0.02,
    "GEL": 0.7
}

DOMESTIC_ALLOWANCES = {
    "Bakı": 125,
    "Naxçıvan": 100,
    "Gəncə": 95,
    "Sumqayıt": 95,
    "Digər": 90
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
    Fetch currency rates from Cbar.az for a specific date and return as DataFrame
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
        st.error(f"Error fetching currency rates: {str(e)}")
        return pd.DataFrame()



MELUMATLAR_JSON = "melumatlar.json"
def load_info_sections():
    """JSON faylından məlumat sektiyalarını yükləyir"""
    try:
        with open(MELUMATLAR_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fayl mövcud deyilsə boş dict qaytarır
        return {}
    except Exception as e:
        st.error(f"Məlumatlar yüklənərkən xəta: {str(e)}")
        return {}

def save_info_sections(sections):
    """Məlumat sektiyalarını JSON faylına saxlayır"""
    try:
        with open(MELUMATLAR_JSON, 'w', encoding='utf-8') as f:
            json.dump(sections, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Məlumatlar saxlanılarkən xəta: {str(e)}")



st.markdown('<div class="main-header"><h1>✈️ Ezamiyyət İdarəetmə Sistemi</h1></div>', unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["📋 Yeni Ezamiyyət", "🔐 Admin Paneli", "📚 Məlumatlar və Qeydlər"])

# YENİ EZAMİYYƏT HISSESI
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
                    # Session state-də səfərləri saxlamaq
                    if 'domestic_trips' not in st.session_state:
                        st.session_state.domestic_trips = []
                    
                    st.subheader("🗂️ Daxili Səfərlər")
                    
                    # Yeni səfər əlavə etmək
                    with st.form("add_domestic_trip"):
                        st.markdown("### ➕ Yeni Səfər Əlavə Et")
                        
                        cols = st.columns(2)
                        with cols[0]:
                            from_city = st.selectbox("Haradan", CITIES, index=CITIES.index("Bakı"))
                            start_date = st.date_input("Başlanğıc tarixi")
                        with cols[1]:
                            to_city = st.selectbox("Haraya", [c for c in CITIES if c != from_city])
                            end_date = st.date_input("Bitmə tarixi")
                        
                        purpose = st.text_area("Səfər məqsədi")

                        # MANUAL NƏQLİYYAT XƏRCİ
                        transport_cost = st.number_input(
                            "🚌 Nəqliyyat xərci (AZN)", 
                            min_value=0.0, 
                            value=0.0,
                            step=10.0,
                            help="Nəqliyyat xərclərini manual daxil edin. Boş buraxılsa 0 qəbul ediləcək"
                        )
                        
                        submitted = st.form_submit_button("➕ Səfər Əlavə Et")
                        
                        if submitted and start_date and end_date and end_date >= start_date:
                            trip_days = (end_date - start_date).days + 1
                            trip_nights = trip_days - 1 if trip_days > 1 else 0
                            domestic_allowances = load_domestic_allowances()
                            daily_allowance = domestic_allowances.get(to_city, domestic_allowances['Digər'])
                            
                            new_trip = {
                                'id': len(st.session_state.domestic_trips) + 1,
                                'from_city': from_city,
                                'to_city': to_city,
                                'start_date': start_date,
                                'end_date': end_date,
                                'purpose': purpose,
                                'trip_days': trip_days,
                                'trip_nights': trip_nights,
                                'ticket_price': transport_cost,
                                'daily_allowance': daily_allowance
                            }
                            
                            st.session_state.domestic_trips.append(new_trip)
                            st.success(f"Səfər əlavə edildi: {from_city} → {to_city}")
                            st.rerun()
                    
                    # Mövcud səfərləri göstər
                    if st.session_state.domestic_trips:
                        st.markdown("### 📋 Əlavə Edilmiş Səfərlər")
                        
                        for i, trip in enumerate(st.session_state.domestic_trips):
                            with st.container(border=True):  # DÜZƏLDİ
                                st.subheader(f"Səfər {trip['id']}: {trip['from_city']} → {trip['to_city']}")
                                col_a, col_b, col_c = st.columns([2, 2, 1])
                                
                                with col_a:
                                    st.write(f"**Tarix:** {trip['start_date']} - {trip['end_date']}")
                                    st.write(f"**Müddət:** {trip['trip_days']} gün")
                                
                                with col_b:
                                    st.write(f"**Günlük müavinət:** {trip['daily_allowance']:.2f} AZN")
                                    st.write(f"**Nəqliyyat:** {trip['ticket_price']:.2f} AZN")
                                
                                with col_c:
                                    if st.button("🗑️", key=f"delete_{i}", help="Səfəri sil"):
                                        st.session_state.domestic_trips.pop(i)
                                        st.rerun()
                                
                                if trip['purpose']:
                                    st.write(f"**Məqsəd:** {trip['purpose']}")
                        
                        # Bütün səfərləri təmizlə
                        if st.button("🗑️ Bütün Səfərləri Təmizlə", type="secondary"):
                            st.session_state.domestic_trips = []
                            st.rerun()
                
                else:  # Ölkə xarici ezamiyyət
                    #  Dinamik yükləmə
                    countries_data = load_countries_data()
                    try:
                        currency_rates = pd.read_excel("currency_rates.xlsx").set_index('Valyuta')['Məzənnə'].to_dict()
                    except FileNotFoundError:
                        currency_rates = CURRENCY_RATES.copy()
                        st.warning("Valyuta məzənnələri faylı tapılmadı, standart dəyərlər istifadə olunur!")
                    
                    country = st.selectbox("Ölkə", list(countries_data.keys()))
                    
                    if country in countries_data:
                        #  Dinamik şəhər siyahısı
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
                    
                    # YENİ: Nəqliyyat xərci valyuta seçimi
                    st.markdown("### 🚀 Nəqliyyat Xərcləri")
                    
                    # Bütün mövcud valyutaları əldə et
                    try:
                        currency_df = get_currency_rates(start_date if start_date else datetime.now().date())
                        if not currency_df.empty:
                            available_currencies = ["AZN"] + currency_df['Valyuta'].tolist()
                            # Təkrarlananları sil və sırala
                            available_currencies = sorted(list(set(available_currencies)))
                        else:
                            available_currencies = ["AZN", currency] if currency and currency != "AZN" else ["AZN"]
                    except:
                        # Əgər scraping xətası varsa, əsas valyutaları göstər
                        available_currencies = ["AZN", "USD", "EUR", "GBP", "RUB", "TRY"]
                        if currency and currency not in available_currencies:
                            available_currencies.append(currency)
                        available_currencies = sorted(available_currencies)
                    
                    transport_currency = st.selectbox(
                        "Nəqliyyat xərci valyutası",
                        options=available_currencies,
                        help="Nəqliyyat xərcini hansı valyutada daxil etmək istəyirsiniz?"
                    )
                    
                    if transport_currency == "AZN":
                        foreign_transport_cost_input = st.number_input(
                            f"✈️ Nəqliyyat xərci (AZN)", 
                            min_value=0.0, 
                            value=0.0,
                            step=50.0,
                            help="Uçaq, qatar və ya digər nəqliyyat xərclərini AZN-lə daxil edin"
                        )
                        # AZN-dən seçilən valyutaya çevir (əsas ezamiyyət valyutası)
                        foreign_transport_cost_azn = foreign_transport_cost_input
                        foreign_transport_cost_foreign = foreign_transport_cost_input / exchange_rate if exchange_rate > 0 else 0
                    else:
                        # Seçilən valyuta üçün məzənnəni əldə et
                        try:
                            if transport_currency == currency:
                                # Əsas ezamiyyət valyutasıdırsa mövcud məzənnəni istifadə et
                                transport_exchange_rate = exchange_rate
                            else:
                                # Digər valyuta üçün məzənnəni tap
                                currency_df = get_currency_rates(start_date if start_date else datetime.now().date())
                                transport_exchange_rate = currency_df.loc[currency_df['Valyuta'] == transport_currency, '1 vahid üçün AZN'].values[0]
                        except:
                            st.error(f"{transport_currency} valyutası üçün məzənnə tapılmadı!")
                            transport_exchange_rate = 1.0
                        
                        foreign_transport_cost_input = st.number_input(
                            f"✈️ Nəqliyyat xərci ({transport_currency})", 
                            min_value=0.0, 
                            value=0.0,
                            step=10.0,
                            help=f"Uçaq, qatar və ya digər nəqliyyat xərclərini {transport_currency}-də daxil edin"
                        )
                        # Seçilən valyutadan AZN-ə çevir
                        foreign_transport_cost_azn = foreign_transport_cost_input * transport_exchange_rate
                        # Əsas ezamiyyət valyutasına çevir
                        foreign_transport_cost_foreign = foreign_transport_cost_azn / exchange_rate if exchange_rate > 0 else 0
                    
                    # Nəqliyyat xərci göstəricisi
                    if foreign_transport_cost_input > 0:
                        cols_transport = st.columns(3)
                        with cols_transport[0]:
                            st.metric("Nəqliyyat (AZN)", f"{foreign_transport_cost_azn:.2f} AZN")
                        with cols_transport[1]:
                            st.metric(f"Nəqliyyat ({currency})", f"{foreign_transport_cost_foreign:.2f} {currency}")
                        with cols_transport[2]:
                            if transport_currency not in ["AZN", currency]:
                                st.metric(f"Daxil edilən ({transport_currency})", f"{foreign_transport_cost_input:.2f} {transport_currency}")
                            else:
                                st.metric("Məzənnə", f"1 {transport_currency} = {transport_exchange_rate:.4f} AZN" if transport_currency != "AZN" else "1 AZN = 1 AZN")



        # Sağ Sütun (Hesablama)
        with col2:
            with st.container():
                st.markdown('<div class="section-header">💰 Hesablama</div>', unsafe_allow_html=True)
                
                if trip_type == "Ölkə daxili":
                    if hasattr(st.session_state, 'domestic_trips') and st.session_state.domestic_trips:
                        # Ümumi hesablamalar
                        total_all_trips = 0
                        total_hotel_cost = 0
                        total_daily_expenses = 0
                        total_ticket_cost = 0
                        total_days = 0
                        
                        st.markdown("### 📊 Səfər Təfərrüatları")
                        
                        # Hər səfər üçün detallı məlumatlar
                        for trip in st.session_state.domestic_trips:
                            # Hər səfər üçün hesablamalar
                            hotel_cost = 0.7 * trip['daily_allowance'] * trip['trip_nights']
                            daily_expenses = 0.3 * trip['daily_allowance'] * trip['trip_days']
                            trip_total = hotel_cost + daily_expenses + trip['ticket_price']
                            
                            # Ümumi məbləğlərə əlavə et
                            total_all_trips += trip_total
                            total_hotel_cost += hotel_cost
                            total_daily_expenses += daily_expenses
                            total_ticket_cost += trip['ticket_price']
                            total_days += trip['trip_days']
                            
                            # Səfər kartı
                            with st.container():
                                st.markdown(f"**🚀 Səfər {trip['id']}:** {trip['from_city']} → {trip['to_city']}")
                                
                                cols_trip = st.columns(2)
                                with cols_trip[0]:
                                    st.metric("📅 Günlük", f"{trip['daily_allowance']:.2f} ₼")
                                    st.metric("🚌 Nəqliyyat", f"{trip['ticket_price']:.2f} ₼")
                                with cols_trip[1]:
                                    st.metric("🏨 Otel", f"{hotel_cost:.2f} ₼")
                                    st.metric("🍽️ Gündəlik", f"{daily_expenses:.2f} ₼")
                                
                                st.metric("💳 Cəmi", f"{trip_total:.2f} ₼", delta=f"{trip['trip_days']} gün")
                                st.divider()
                        
                        # Ümumi məlumatlar
                        st.markdown("### 📈 Ümumi Nəticə")
                        
                        st.metric("🔢 Səfər sayı", f"{len(st.session_state.domestic_trips)}")
                        st.metric("📅 Ümumi günlər", f"{total_days}")
                        
                        cols_summary = st.columns(2)
                        with cols_summary[0]:
                            st.metric("🚌", f"{total_ticket_cost:.2f} ₼")
                            st.metric("🏨", f"{total_hotel_cost:.2f} ₼")
                        with cols_summary[1]:
                            st.metric("🍽️", f"{total_daily_expenses:.2f} ₼")
                        
                        # Ən böyük məbləğ
                        st.metric("💰 ÜMUMI MƏBLƏĞ", f"{total_all_trips:.2f} ₼")
                        
                        # Statistika
                        if len(st.session_state.domestic_trips) > 1:
                            avg_per_trip = total_all_trips / len(st.session_state.domestic_trips)
                            st.info(f"📊 Orta səfər: {avg_per_trip:.2f} ₼")
                    else:
                        st.info("👆 Sol tərəfdən səfər əlavə edin")
                
                elif trip_type == "Ölkə xarici" and start_date and end_date and end_date >= start_date:
                    trip_days = (end_date - start_date).days + 1
                    trip_nights = trip_days - 1 if trip_days > 1 else 0
                    
                    country_data = countries_data[country]  # COUNTRIES 
                    
                    if selected_city == "digər":
                        base_allowance = country_data['cities']['digər']['allowance']
                        currency = country_data['currency']
                    else:
                        city_data = country_data['cities'][selected_city]
                        base_allowance = city_data['allowance']
                        currency = country_data['currency']
                    
                    # tarixe uygun
                    try:
                        # Cbar.az-dan məzənnə məlumatlarını çək
                        currency_df = get_currency_rates(start_date)
                        
                        if currency_df.empty:
                            st.error(f"{start_date.strftime('%d.%m.%Y')} tarixi üçün məzənnə məlumatı tapılmadı!")
                            st.stop()
                            
                        # Valyuta koduna görə məzənnəni seç
                        exchange_rate = currency_df.loc[currency_df['Valyuta'] == currency, '1 vahid üçün AZN'].values[0]
                        
                        # Salam . 
                        exchange_date = start_date.strftime("%d.%m.%Y")
                        
                    except IndexError:
                        st.error(f"{currency} valyutası üçün məzənnə tapılmadı!")
                        st.stop()
                    except Exception as e:
                        st.error(f"Məzənnə alınarkən xəta: {str(e)}")
                        st.stop()

                    
                    # Qonaqlama növünə görə hesablama
                    if accommodation == "Adi Rejim":
                        hotel_cost_foreign = 0.6 * daily_allowance_foreign * trip_nights
                        daily_expenses_foreign = 0.4 * daily_allowance_foreign * trip_days
                        total_amount_foreign = hotel_cost_foreign + daily_expenses_foreign
                    elif accommodation == "Yalnız yaşayış yeri ilə təmin edir":
                        daily_expenses_foreign = daily_allowance_foreign * 0.4 * trip_days
                        hotel_cost_foreign = 0
                        total_amount_foreign = daily_expenses_foreign
                    else:  # "Yalnız gündəlik xərcləri təmin edir"
                        hotel_cost_foreign = daily_allowance_foreign * 0.6 * trip_nights if trip_nights > 0 else 0
                        daily_expenses_foreign = 0
                        total_amount_foreign = hotel_cost_foreign
    
                    # AZN-ə çevir
                    total_amount_azn = total_amount_foreign * exchange_rate
                    hotel_cost_azn = hotel_cost_foreign * exchange_rate
                    daily_expenses_azn = daily_expenses_foreign * exchange_rate

                    # Valyuta məzənnəsi ilə günlük müavinətin AZN-ə çevrilməsi
                    daily_allowance_azn = daily_allowance_foreign * exchange_rate 

                    # YENİ: Nəqliyyat xərcləri (həm valyutada, həm AZN-də)
                    total_with_transport_foreign = total_amount_foreign + foreign_transport_cost_foreign
                    total_with_transport_azn = total_amount_azn + foreign_transport_cost_azn

                    # Göstəricilər ⚙️ YENİLƏNİB - TAM MƏBLƏĞ GÖSTƏR
                    st.metric("📅 Günlük müavinət", 
                             f"{daily_allowance_azn:.2f} AZN", 
                             delta=f"{daily_allowance_foreign:.2f} {currency}")
                    
                    # Adi Rejim üçün hər iki xərc növü ⚙️
                    if accommodation == "Adi Rejim":
                        cols_metrics = st.columns(2)
                        with cols_metrics[0]:
                            st.metric("🏨 Mehmanxana xərcləri", 
                                     f"{hotel_cost_azn:.2f} AZN",
                                     delta=f"{hotel_cost_foreign:.2f} {currency}",
                                     help=f"Günlük müavinətin 60%-i × {trip_nights} gecə")
                        with cols_metrics[1]:
                            st.metric("🍽️ Gündəlik xərclər", 
                                     f"{daily_expenses_azn:.2f} AZN", 
                                     delta=f"{daily_expenses_foreign:.2f} {currency}",
                                     help=f"Günlük müavinətin 40%-i × {trip_days} gün")
                    else:
                        # Digər hallar üçün ⚙️
                        if accommodation == "Yalnız yaşayış yeri ilə təmin edir":
                            st.metric("🍽️ Gündəlik xərclər", 
                                     f"{daily_expenses_azn:.2f} AZN", 
                                     delta=f"{daily_expenses_foreign:.2f} {currency}")
                        elif accommodation == "Yalnız gündəlik xərcləri təmin edir" and trip_nights > 0:
                            st.metric("🏨 Mehmanxana xərcləri", 
                                     f"{hotel_cost_azn:.2f} AZN",
                                     delta=f"{hotel_cost_foreign:.2f} {currency}")
                    
                    # YENİ: Nəqliyyat xərci həm valyutada, həm AZN-də göstər
                    if foreign_transport_cost_input > 0:
                        cols_transport_display = st.columns(2)
                        with cols_transport_display[0]:
                            st.metric("✈️ Nəqliyyat (AZN)", f"{foreign_transport_cost_azn:.2f} AZN")
                        with cols_transport_display[1]:
                            st.metric(f"✈️ Nəqliyyat ({currency})", f"{foreign_transport_cost_foreign:.2f} {currency}")
                    
                    st.metric("⏳ Müddət", f"{trip_days} gün")
                    
                    # YENİ: Həm valyutada, həm AZN-də ümumi məbləğlər
                    cols_total = st.columns(2)
                    with cols_total[0]:
                        st.metric("💳 Ezamiyyət (AZN)", 
                                 f"{total_amount_azn:.2f} AZN",
                                 help="Yalnız ezamiyyət xərcləri")
                    with cols_total[1]:
                        st.metric(f"💳 Ezamiyyət ({currency})", 
                                 f"{total_amount_foreign:.2f} {currency}",
                                 help="Yalnız ezamiyyət xərcləri")
                    
                    # Ümumi məbləğ (ezamiyyət + nəqliyyat)
                    cols_grand_total = st.columns(2)
                    with cols_grand_total[0]:
                        st.metric("💰 ÜMUMI (AZN)", 
                                 f"{total_with_transport_azn:.2f} AZN",
                                 help="Ezamiyyət + nəqliyyat xərci")
                    with cols_grand_total[1]:
                        st.metric(f"💰 ÜMUMI ({currency})", 
                                 f"{total_with_transport_foreign:.2f} {currency}",
                                 help="Ezamiyyət + nəqliyyat xərci")
                    
                    st.info(
                    f"💱 İstifadə edilən məzənnə ({exchange_date}): "
                    f"1 {currency} = {exchange_rate:.4f} AZN"
                    )

                    
                    # Əlavə məlumat  
                    if accommodation == "Adi Rejim":
                        st.caption("ℹ️ Adi Rejim: Günlük müavinətin 60%-i mehmanxana xərclərinə, 40%-i gündəlik xərclərə ayrılır")
                    elif accommodation == "Yalnız yaşayış yeri ilə təmin edir":
                        st.caption("ℹ️ Yalnız gündəlik xərclər ödənilir (günlük müavinətin 40%-i)")
                    elif accommodation == "Yalnız gündəlik xərcləri təmin edir":
                        st.caption("ℹ️ Yalnız mehmanxana xərcləri ödənilir (günlük müavinətin 60%-i × gecə sayı)")

                
        
                # Yadda saxlama düyməsi
                if st.button("✅ Yadda Saxla", use_container_width=True):
                    if all([first_name, last_name]):
                        if trip_type == "Ölkə daxili" and hasattr(st.session_state, 'domestic_trips') and st.session_state.domestic_trips:
                            # Çoxlu səfər üçün yadda saxlama
                            for trip in st.session_state.domestic_trips:
                                # Hər səfər üçün hesablamalar
                                hotel_cost = 0.7 * trip['daily_allowance'] * trip['trip_nights']
                                daily_expenses = 0.3 * trip['daily_allowance'] * trip['trip_days']
                                trip_total = hotel_cost + daily_expenses + trip['ticket_price']
                                
                                trip_data = {
                                    "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "Ad": first_name,
                                    "Soyad": last_name,
                                    "Ata adı": father_name,
                                    "Vəzifə": position,
                                    "Şöbə": department,
                                    "Ezamiyyət növü": trip_type,
                                    "Səfər nömrəsi": f"{trip['id']}/{len(st.session_state.domestic_trips)}",
                                    "Ödəniş rejimi": "Tətbiq edilmir",
                                    "Qonaqlama növü": "Tətbiq edilmir",
                                    "Marşrut": f"{trip['from_city']} → {trip['to_city']}",
                                    "Bilet qiyməti": trip['ticket_price'],
                                    "Günlük müavinət (Valyuta)": f"{trip['daily_allowance']:.2f} AZN",
                                    "Günlük müavinət (AZN)": trip['daily_allowance'],
                                    "Mehmanxana xərcləri": hotel_cost,
                                    "Gündəlik xərclər": daily_expenses,
                                    "Ümumi məbləğ (Valyuta)": f"{trip_total:.2f} AZN",
                                    "Ümumi məbləğ (AZN)": trip_total,
                                    "Valyuta": "AZN",
                                    "Məzənnə": 1.0,
                                    "Başlanğıc tarixi": trip['start_date'].strftime("%Y-%m-%d"),
                                    "Bitmə tarixi": trip['end_date'].strftime("%Y-%m-%d"),
                                    "Günlər": trip['trip_days'],
                                    "Gecələr": trip['trip_nights'],
                                    "Məqsəd": trip['purpose']
                                }
                                
                                save_trip_data(trip_data)
                            
                            st.success(f"{len(st.session_state.domestic_trips)} səfər məlumatları yadda saxlandı!")
                            # Səfərləri təmizlə
                            st.session_state.domestic_trips = []
                            st.rerun()
                            
                        elif trip_type == "Ölkə xarici" and start_date and end_date:
                            # Valyuta məlumatlarını təyin et
                            total_amount_azn = total_amount_foreign * exchange_rate
                            # YENİ: Nəqliyyat xərci də əlavə edilir (həm AZN, həm xarici valyuta)
                            total_with_transport = total_amount_azn + foreign_transport_cost_azn
        
                            trip_data = {
                                "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "Ad": first_name,
                                "Soyad": last_name,
                                "Ata adı": father_name,
                                "Vəzifə": position,
                                "Şöbə": department,
                                "Ezamiyyət növü": trip_type,
                                "Səfər nömrəsi": "1/1",
                                "Ödəniş rejimi": payment_mode,
                                "Qonaqlama növü": accommodation,
                                "Marşrut": f"{country} - {selected_city}",
                                "Bilet qiyməti": foreign_transport_cost_azn,  # AZN-də nəqliyyat xərci
                                "Bilet qiyməti (Valyuta)": f"{foreign_transport_cost_input:.2f} {transport_currency}",  # Daxil edilən valyutada
                                "Nəqliyyat valyutası": transport_currency,  # Daxil edilən valyuta
                                # Valyuta məlumatları
                                "Günlük müavinət (Valyuta)": f"{daily_allowance_foreign:.2f} {currency}",
                                "Günlük müavinət (AZN)": daily_allowance_azn,
                                "Mehmanxana xərcləri": hotel_cost_azn,
                                "Gündəlik xərclər": daily_expenses_azn,
                                "Ümumi məbləğ (Valyuta)": f"{total_with_transport_foreign:.2f} {currency}",  # YENİ: Nəqliyyat daxil
                                "Ümumi məbləğ (AZN)": total_with_transport,  # YENİ: Nəqliyyat xərci daxil
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
                            st.error("Zəhmət olmasa səfər əlavə edin!")
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
        tab_manage, tab_import, tab_settings, tab_currency, tab_info = st.tabs(
            ["📊 Məlumatlar", "📥 İdxal", "⚙️ Parametrlər", "💱 Valyuta Məzənnələri", "📚 Ezamiyyət Qaydaları və Məlumatlar"]
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


        #hdjsahdjsksa
        with tab_info:
            st.markdown("### Məlumat Sektiyalarının İdarə Edilməsi")
            sections = load_info_sections()
            
            # Yeni bölmə əlavə etmə
            st.markdown("#### Yeni Bölmə Əlavə Et")
            new_title = st.text_input("Yeni bölmə başlığı")
            new_content = st.text_area("Yeni bölmə məzmunu", height=200)
            
            if st.button("Yeni bölmə əlavə et"):
                if new_title.strip() and new_content.strip():
                    section_id = f"section_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    sections[section_id] = {
                        "title": new_title.strip(),
                        "content": new_content.strip(),
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    save_info_sections(sections)
                    st.success("Yeni bölmə əlavə edildi!")
                    st.rerun()  # Səhifəni yeniləyir
                else:
                    st.error("Başlıq və məzmun tələb olunur")
            
            # Mövcud bölmələrin redaktəsi
            st.markdown("#### Mövcud Bölmələr")
            if sections:
                for section_id, section_data in sections.items():
                    with st.expander(f"📝 {section_data.get('title', 'Başlıqsız')}", expanded=False):
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
                        
                        cols = st.columns(3)
                        with cols[0]:
                            if st.button("💾 Saxla", key=f"save_{section_id}"):
                                if edited_title.strip():
                                    sections[section_id]['title'] = edited_title.strip()
                                    sections[section_id]['content'] = edited_content.strip()
                                    sections[section_id]['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    save_info_sections(sections)
                                    st.success("Dəyişikliklər yadda saxlanıldı!")
                                    st.rerun()
                                else:
                                    st.error("Başlıq boş ola bilməz")
                        
                        with cols[1]:
                            if st.button("🗑️ Sil", key=f"delete_{section_id}"):
                                # Təsdiq mexanizmi
                                if f"confirm_delete_{section_id}" not in st.session_state:
                                    st.session_state[f"confirm_delete_{section_id}"] = True
                                    st.warning("⚠️ Silmək üçün yenidən basın!")
                                else:
                                    del sections[section_id]
                                    save_info_sections(sections)
                                    st.success("Bölmə silindi!")
                                    # Təsdiq məlumatını təmizlə
                                    if f"confirm_delete_{section_id}" in st.session_state:
                                        del st.session_state[f"confirm_delete_{section_id}"]
                                    st.rerun()
                        
                        with cols[2]:
                            st.caption(f"📅 Yaradılma: {section_data.get('created_at', 'Bilinmir')}")
                            if 'updated_at' in section_data:
                                st.caption(f"🔄 Yenilənmə: {section_data['updated_at']}")
            else:
                st.info("Hələ heç bir bölmə əlavə edilməyib")


# ========================================================================================
# MƏLUMATLAR VƏ QEYDLƏR
with tab3:
    st.markdown("## 📚 Ezamiyyət Qaydaları və Məlumatlar")
    sections = load_info_sections()
    
    if not sections:
        st.info("Hələ heç bir məlumat əlavə edilməyib")
    else:
        # Axtarış funksiyası (opsional)
        search_term = st.text_input("🔍 Məlumatda axtarış edin")
        
        # Məlumatları filter et
        filtered_sections = sections
        if search_term:
            filtered_sections = {
                k: v for k, v in sections.items() 
                if search_term.lower() in v.get('title', '').lower() or 
                   search_term.lower() in v.get('content', '').lower()
            }
        
        # Məlumatları göstər
        if filtered_sections:
            for section_id, section_data in filtered_sections.items():
                with st.expander(f"📌 {section_data.get('title', 'Başlıqsız')}", expanded=False):
                    st.markdown(section_data.get('content', 'Məzmun yoxdur'))
                    st.caption(f"📅 {section_data.get('created_at', 'Tarix bilinmir')}")
        else:
            if search_term:
                st.warning("Axtarış kriteriyasına uyğun məlumat tapılmadı")
            else:
                st.info("Məlumat yoxdur")



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
