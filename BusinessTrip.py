import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import requests

# Telegram parametrləri
TELEGRAM_BOT_TOKEN = "SENIN_BOT_TOKENIN"
TELEGRAM_CHAT_ID = "SENIN_CHAT_ID"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            return True
        else:
            st.warning(f"Telegram mesajı göndərilə bilmədi. Status kodu: {response.status_code}")
            return False
    except Exception as e:
        st.warning(f"Telegram mesajı göndərərkən xəta: {e}")
        return False

# Email göndərmə funksiyası (SMTP parametrləri dəyişdirilməlidir)
def send_email(receiver_email, subject, body, attachment=None, attachment_name=None):
    sender_email = "sənin_emailin@example.com"
    sender_password = "sənin_email_password"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, "plain"))

    if attachment and attachment_name:
        part = MIMEApplication(attachment.getvalue(), Name=attachment_name)
        part['Content-Disposition'] = f'attachment; filename="{attachment_name}"'
        msg.attach(part)

    try:
        with smtplib.SMTP_SSL('smtp.example.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Email göndərilərkən xəta baş verdi: {e}")
        return False


st.set_page_config(page_title="Ezamiyyət hesablayıcı", page_icon="✈️")

st.title("✈️ Ezamiyyət Məlumat Forması")

# Şəxsi məlumatlar
st.subheader("👤 Şəxsi məlumatlar")
ad = st.text_input("Ad")
soyad = st.text_input("Soyad")
ata_adi = st.text_input("Ata adı")
email = st.text_input("Email ünvanı (nəticə bu ünvana göndəriləcək)")

# Şöbə seçimi
st.subheader("🏢 Şöbə seçimi")
sobe = st.selectbox("Hansə şöbədə işləyirsiniz?", [
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
])

# Vəzifə seçimi
st.subheader("💼 Vəzifə seçimi")
vezife = st.selectbox("Vəzifəniz", [
    "Kiçik mütəxəssis",
    "Mütəxəssis",
    "Baş mütəxəssis",
    "Şöbə müdiri",
    "Baş mütəxəssis köməkçisi",
    "Müdir müavini"
])

# Ezamiyyət tipi
st.subheader("🧳 Ezamiyyət növü")
ezam_tip = st.radio("Ezamiyyət ölkə daxili, yoxsa ölkə xaricidir?", ["Ölkə daxili", "Ölkə xarici"])

# Hara gedir?
destination = ""
if ezam_tip == "Ölkə daxili":
    destination = st.selectbox("Hara ezam olunursunuz?", [
        "Bakı - Gəncə", "Bakı - Şəki", "Bakı - Lənkəran", "Bakı - Sumqayıt"
    ])
    amount_map = {
        "Bakı - Gəncə": 100,
        "Bakı - Şəki": 90,
        "Bakı - Lənkəran": 80,
        "Bakı - Sumqayıt": 50,
    }
else:
    destination = st.selectbox("Hansı ölkəyə ezam olunursunuz?", [
        "Türkiyə", "Gürcüstan", "Almaniya", "BƏƏ", "Rusiya"
    ])
    amount_map = {
        "Türkiyə": 300,
        "Gürcüstan": 250,
        "Almaniya": 600,
        "BƏƏ": 500,
        "Rusiya": 400,
    }

# Ezamiyyətin başlanğıc və son tarixləri
st.subheader("📅 Ezamiyyət dövrü")
baslama_tarixi = st.date_input("Başlanğıc tarixi")
bitme_tarixi = st.date_input("Bitmə tarixi")

mebleg = amount_map.get(destination, 0)

if st.button("💰 Ödəniləcək məbləği göstər və yadda saxla"):
    if not (ad and soyad and ata_adi and email):
        st.error("Zəhmət olmasa, ad, soyad, ata adı və email daxil edin!")
    elif bitme_tarixi < baslama_tarixi:
        st.error("Bitmə tarixi başlanğıc tarixindən kiçik ola bilməz!")
    else:
        indiki_vaxt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"👤 {ad} {soyad} {ata_adi} üçün ezamiyyət məbləği: **{mebleg} AZN**")
        st.info(f"🕒 Məlumat daxil edilmə vaxtı: {indiki_vaxt}")

        new_data = {
            "Tarix": [indiki_vaxt],
            "Ad": [ad],
            "Soyad": [soyad],
            "Ata adı": [ata_adi],
            "Email": [email],
            "Şöbə": [sobe],
            "Vəzifə": [vezife],
            "Ezamiyyət növü": [ezam_tip],
            "Yön": [destination],
            "Başlanğıc tarixi": [baslama_tarixi.strftime("%Y-%m-%d")],
            "Bitmə tarixi": [bitme_tarixi.strftime("%Y-%m-%d")],
            "Məbləğ": [mebleg]
        }
        df_new = pd.DataFrame(new_data)

        try:
            df_existing = pd.read_csv("ezamiyyet_melumatlari.csv")
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        except FileNotFoundError:
            df_combined = df_new

        df_combined.to_csv("ezamiyyet_melumatlari.csv", index=False)
        st.info("📁 Məlumat uğurla yadda saxlanıldı!")

        # Excel faylı hazırla
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_new.to_excel(writer, index=False, sheet_name='Ezamiyyət')
            writer.save()
        output.seek(0)

        fayl_adi = f"{ad}_{soyad}_ezamiyyet.xlsx"

        email_subject = "Ezamiyyət Məlumatlarınız"
        email_body = f"""
Salam {ad} {soyad},

Sizin üçün aşağıdakı ezamiyyət məbləği hesablanmışdır:

Məbləğ: {mebleg} AZN
Ezamiyyət növü: {ezam_tip}
Yön: {destination}
Dövr: {baslama_tarixi.strftime('%Y-%m-%d')} - {bitme_tarixi.strftime('%Y-%m-%d')}

Hörmətlə,
Ezamiyyət Hesablayıcı
"""

        email_gonderildi = send_email(email, email_subject, email_body, attachment=output, attachment_name=fayl_adi)

        if email_gonderildi:
            st.success(f"{email} ünvanına email göndərildi!")
        else:
            st.error("Email göndərilə bilmədi!")

        # Telegrama bildiriş
        telegram_message = (
            f"<b>Yeni ezamiyyət məlumatı daxil edildi</b>\n"
            f"👤 İstifadəçi: {ad} {soyad}\n"
            f"📧 Email: {email}\n"
            f"🏢 Şöbə: {sobe}\n"
            f"💼 Vəzifə: {vezife}\n"
            f"🧳 Ezamiyyət növü: {ezam_tip}\n"
            f"➡️ Yön: {destination}\n"
            f"📅 Dövr: {baslama_tarixi.strftime('%Y-%m-%d')} - {bitme_tarixi.strftime('%Y-%m-%d')}\n"
            f"💰 Məbləğ: {mebleg} AZN"
        )
        send_telegram_message(telegram_message)

# Admin üçün məlumatların göstərilməsi
with st.expander("📊 Girişləri göstər (admin görünüşü)"):
    try:
        df = pd.read_csv("ezamiyyet_melumatlari.csv")
        st.dataframe(df)
    except FileNotFoundError:
        st.info("Hələ məlumat bazası boşdur.")
