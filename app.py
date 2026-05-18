import streamlit as st
from google import genai
import PyPDF2
import io

st.set_page_config(page_title="CV Analiz Aracı", page_icon="📄", layout="centered")

st.title("📄 Ücretsiz CV Analiz Aracı")
st.markdown("CV'nizi yükleyin, yapay zeka ücretsiz analiz etsin.")

# 1. Anahtarı Streamlit Secrets kasasından alıp yeni modern Client'ı başlatıyoruz
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

dosya = st.file_uploader("CV dosyanızı seçin (PDF)", type=["pdf"])

def pdf_oku(dosya):
    reader = PyPDF2.PdfReader(io.BytesIO(dosya.read()))
    metin = ""
    for sayfa in reader.pages:
        metin += sayfa.extract_text() or ""
    return metin.strip()

def cv_analiz_et(cv_metni):
    prompt = f"""Aşağıdaki CV'yi analiz et ve Türkçe rapor oluştur:

## 📊 CV Puanı (100 üzerinden puan ver ve gerekçe yaz)
## ✅ Güçlü Yönler (En az 3 madde)
## ❌ Eksikler & Öneriler (En az 3 madde)
## 🎯 Uygun Pozisyonlar (3-5 iş pozisyonu)
## 🛠️ Beceriler (Tüm teknik ve soft skill'ler)
## 💡 Genel Öneri (3-4 cümle tavsiye)

CV Metni:
{cv_metni[:4000]}"""

    # Yeni Google-GenAI kütüphanesi standart çağrısı
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt,
    )
    return response.text

# Ekrandaki buton basma kontrolleri
if dosya:
    if st.button("🔍 Analiz Et", type="primary", use_container_width=True):
        with st.spinner("Analiz ediliyor..."):
            try:
                metin = pdf_oku(dosya)
                sonuc = cv_analiz_et(metin)
                st.markdown("---")
                st.markdown(sonuc)
                st.download_button("📥 Raporu İndir", sonuc, "rapor.txt")
            except Exception as e:
                st.error(f"Hata: API anahtarınızı veya internet bağlantınızı kontrol edin. Detay: {str(e)}")
else:
    st.info("👆 CV dosyanızı yükleyin")
