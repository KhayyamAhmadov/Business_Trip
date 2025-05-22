import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Ezamiyyət hesablayıcı", page_icon="✈️")

st.title(" Ezamiyyət Məlumat Forması")

sobeler = [
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

seherler = [
    "Abşeron", "Ağcabədi", "Ağdam", "Ağdaş", "Ağdərə", "Ağstafa", "Ağsu", "Astara", "Bakı",
    "Babək (Naxçıvan MR)", "Balakən", "Bərdə", "Beyləqan", "Biləsuvar", "Cəbrayıl", "Cəlilabad",
    "Culfa (Naxçıvan MR)", "Daşkəsən", "Füzuli", "Gədəbəy", "Gəncə", "Goranboy", "Göyçay",
    "Göygöl", "Hacıqabul", "Xaçmaz", "Xankəndi", "Xızı", "Xocalı", "Xocavənd", "İmişli",
    "İsmayıllı", "Kəlbəcər", "Kəngərli (Naxçıvan MR)", "Kürdəmir", "Laçın", "Lənkəran",
    "Lerik", "Masallı", "Mingəçevir", "Naftalan", "Neftçala", "Naxçıvan", "Oğuz",
    "Ordubad (Naxçıvan MR)", "Qəbələ", "Qax", "Qazax", "Qobustan", "Quba", "Qubadlı",
    "Qusar", "Saatlı", "Sabirabad", "Sədərək (Naxçıvan MR)", "Salyan", "Samux", "Şabran",
    "Şahbuz (Naxçıvan MR)", "Şamaxı", "Şəki", "Şəmkir", "Şərur (Naxçıvan MR)", "Şirvan",
    "Şuşa", "Sumqayıt", "Tərtər", "Tovuz", "Ucar", "Yardımlı", "Yevlax", "Zaqatala",
    "Zəngilan", "Zərdab"
]

st.subheader(" Şəxsi məlumatlar")
ad = st.text_input("Ad")
soyad = st.text_input("Soyad")
ata_adi = st.text_input("Ata adı")

st.subheader(" Şöbə seçimi")
sobe = st.selectbox("Hansə şöbədə işləyirsiniz?", sobeler)

st.subheader(" Ezamiyyət növü")
ezam_tip = st.radio("Ezamiyyət ölkə daxili, yoxsa ölkə xaricidir?", ["Ölkə daxili", "Ölkə xarici"])

destination = ""
mebleg = 0

if ezam_tip == "Ölkə daxili":
    st.subheader(" Marşrut seçimi")
    hardan = st.selectbox("Haradan ezam olunursunuz?", seherler, index=seherler.index("Bakı"))
    haraya_secim = [s for s in seherler if s != hardan]
    haraya = st.selectbox("Haraya ezam olunursunuz?", haraya_secim)

    # Məbləğləri marşrutlara görə müəyyən edək (nümunə üçün bəzi əsas marşrutlar)
    amount_map = {
        ("Bakı", "Gəncə"): 100,
        ("Bakı", "Şəki"): 90,
        ("Bakı", "Lənkəran"): 80,
        ("Bakı", "Sumqayıt"): 50,
    }

    # Güzəştlər əks istiqamət üçün də işləsin deyə
    mebleg = amount_map.get((hardan, haraya)) or amount_map.get((haraya, hardan)) or 0

    destination = f"{hardan} - {haraya}"

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
    mebleg = amount_map.get(destination, 0)

st.subheader(" Ezamiyyət dövrü")
baslama_tarixi = st.date_input("Başlanğıc tarixi")
bitme_tarixi = st.date_input("Bitmə tarixi")

if st.button(" Ödəniləcək məbləği göstər və yadda saxla"):
    if not (ad and soyad and ata_adi):
        st.error("Zəhmət olmasa, ad, soyad və ata adını daxil edin!")
    elif bitme_tarixi < baslama_tarixi:
        st.error("Bitmə tarixi başlanğıc tarixindən kiçik ola bilməz!")
    else:
        indiki_vaxt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success(f" {ad} {soyad} {ata_adi} üçün ezamiyyət məbləği: **{mebleg} AZN**")
        st.info(f" Məlumat daxil edilmə vaxtı: {indiki_vaxt}")

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
        st.info(" Məlumat uğurla yadda saxlanıldı.")


# admin girisi hissesi 
st.subheader("Admin bölməsi")

admin_username = st.text_input("Admin istifadəçi adı daxil edin")
admin_password = st.text_input("Admin şifrəni daxil edin", type="password")

if admin_username == "admin" and admin_password == "admin":
    try:
        df_admin = pd.read_csv("ezamiyyet_melumatlari.csv")
        st.dataframe(df_admin)
    
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_admin.to_excel(writer, index=False, sheet_name='Ezamiyyet')
        processed_data = output.getvalue()
    
        st.download_button(
            label="Excel faylını yüklə",
            data=processed_data,
            file_name="ezamiyyet_melumatlari.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except FileNotFoundError:
        st.warning("Hələ heç bir məlumat daxil edilməyib.")

else:
    if admin_username or admin_password:
        st.error("İstifadəçi adı və ya şifrə yalnışdır!")
