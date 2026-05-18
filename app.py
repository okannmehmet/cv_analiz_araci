import streamlit as st
import requests
import PyPDF2
import io
import json

# 📊 GOOGLE ANALYTICS AYARI
ANALYTICS_ID = "G-0NQHLF7DMY"

# Google Analytics izleme kodunu görünmez bir şekilde siteye gömen HTML
analytics_html = f"""
<script async src="https://www.googletagmanager.com/gtag/js?id={ANALYTICS_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{ANALYTICS_ID}');
</script>
"""
# Sayacı siteye enjekte ediyoruz
st.components.v1.html(analytics_html, height=0, width=0)

st.set_page_config(page_title="CV Analiz Aracı", page_icon="📄", layout="centered")

st.title("📄 Ücretsiz CV Analiz Aracı")
st.markdown("CV'nizi yükleyin, yapay zeka ücretsiz analiz etsin.")

# Secrets kasasından anahtarı alıyoruz
api_key = st.secrets["GEMINI_API_KEY"]

dosya = st.file_uploader("CV dosyanızı seçin (PDF)", type=["pdf"])

def pdf_oku(dosya):
    reader = PyPDF2.PdfReader(io.BytesIO(dosya.read()))
    metin = ""
    for sayfa in reader.pages:
        metin += sayfa.extract_text() or ""
    return metin.strip()

def cv_analiz_et(cv_metni, key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    prompt = f"""Aşağıdaki CV'yi çok dikkatli bir şekilde analiz et ve Türkçe detaylı bir kariyer raporu oluştur. 

Kritik Not: PDF dönüştürme esnasında harfler arasında oluşabilecek istemsiz boşlukları (Örn: M echatronics, m ehm tokann gibi) veya PDF okuma kaynaklı karakter kaymalarını kesinlikle dikkate alma, bunları adayın yazım hatası olarak yorumlama. Tarihleri mantıklı bir süzgeçten geçir; 'Devam ediyor' veya yakın tarihli/mevcut süreçleri 'gelecek tarihli yalan beyan' olarak algılama, güncel durum olarak değerlendir. Daha yapıcı, profesyonel ve adayı geliştirmeye odaklı bir puanlama yap.

## 📊 CV Puanı (100 üzerinden adil bir puan ver ve kısa gerekçe yaz)
## ✅ Güçlü Yönler (En az 3 madde)
## ❌ Eksikler & Öneriler (Geliştirilmesi gereken alanlar, net tavsiyeler)
## 🎯 Uygun Pozisyonlar (Adayın çalışabileceği 3-5 iş pozisyonu)
## 🛠️ Beceriler (Teknik ve soft skill'ler)
## 💡 Genel Öneri (Gelecek vizyonu için 3-4 cümle tavsiye)

CV Metni:
{cv_metni[:4000]}"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        response_json = response.json()
        return response_json['candidates'][0]['content']['parts'][0]['text']
    else:
        url_alt = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={key}"
        response_alt = requests.post(url_alt, headers=headers, json=payload)
        if response_alt.status_code == 200:
            response_json = response_alt.json()
            return response_json['candidates'][0]['content']['parts'][0]['text']
        else:
            raise Exception(f"Google API Hatası (Kod {response_alt.status_code}): {response_alt.text}")

# Ekrandaki buton basma kontrolleri
if dosya:
    if st.button("🔍 Analiz Et", type="primary", use_container_width=True):
        with st.spinner("Analiz ediliyor..."):
            try:
                metin = pdf_oku(dosya)
                sonuc = cv_analiz_et(metin, api_key)
                st.markdown("---")
                st.markdown(sonuc)
                st.download_button("📥 Raporu İndir", sonuc, "rapor.txt")
            except Exception as e:
                st.error(f"Hata: Sistem yanıt vermedi. Detay: {str(e)}")
else:
    st.info("👆 CV dosyanızı yükleyin")
