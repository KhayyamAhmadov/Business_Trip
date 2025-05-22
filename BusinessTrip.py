import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Ezamiyyət hesablayıcı", page_icon="✈️")

st.title("✈️ Ezamiyyət Məlumat Forması")

# İstifadəçi məlumatları
st.subheader("👤 Şəxsi məlumatlar")
ad = st.text_input("Ad")
soyad = st.text_input("Soyad")
ata_adi = st.text_input("Ata adı")

# Şöbə seçimi
st.subheader("🏢 Şöbə seçimi")
sobe = st.selectbox("Hansə şöbədə işləyirsiniz?", [
    "Maliyyə", "İT", "HR", "Satış", "Marketinq"
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
    if not (ad and soyad and ata_adi):
        st.error("Zəhmət olmasa, ad, soyad və ata adı daxil edin!")
    elif bitme_tarixi < baslama_tarixi:
        st.error("Bitmə tarixi başlanğıc tarixindən kiçik ola bilməz!")
    else:
        indiki_vaxt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"👤 {ad} {soyad} {ata_adi} üçün ezamiyyət məbləği: **{mebleg} AZN**")
        st.info(f"🕒 Məlumat daxil edilmə vaxtı: {indiki_vaxt}")

        # Məlumatı CSV-ə əlavə et
        new_data = {
            "Tarix": [indiki_vaxt],
            "Ad": [ad],
            "Soyad": [soyad],
            "Ata adı": [ata_adi],
            "Şöbə": [sobe],
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

# Excel faylının yüklənməsi üçün ayrıca bölmə
st.subheader("📥 Excel faylını yüklə")

if st.button("Excel faylını hazırla və yüklə"):
    if not (ad and soyad and ata_adi):
        st.error("Excel faylı yaratmaq üçün əvvəlcə ad, soyad və ata adını daxil edin!")
    else:
        data = {
            "Ad": [ad],
            "Soyad": [soyad],
            "Ata adı": [ata_adi],
            "Şöbə": [sobe],
            "Ezamiyyət növü": [ezam_tip],
            "Yön": [destination],
            "Başlanğıc tarixi": [baslama_tarixi.strftime("%Y-%m-%d")],
            "Bitmə tarixi": [bitme_tarixi.strftime("%Y-%m-%d")],
            "Məbləğ (AZN)": [mebleg]
        }
        df = pd.DataFrame(data)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Ezamiyyət')
            writer.save()
        output.seek(0)

        fayl_adi = f"{ad}_{soyad}.xlsx"

        st.download_button(
            label="Excel faylını yüklə",
            data=output,
            file_name=fayl_adi,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Admin üçün məlumatların göstərilməsi
with st.expander("📊 Girişləri göstər (admin görünüşü)"):
    try:
        df = pd.read_csv("ezamiyyet_melumatlari.csv")
        st.dataframe(df)
    except FileNotFoundError:
        st.warning("Heç bir qeyd yoxdur.")