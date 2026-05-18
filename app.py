import streamlit as st
import google.generativeai as genai
import PyPDF2
import io
import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="CV Analiz Aracı", page_icon="📄", layout="centered")

st.title("📄 Ücretsiz CV Analiz Aracı")
st.markdown("CV'nizi yükleyin, yapay zeka ücretsiz analiz etsin.")

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)


dosya = st.file_uploader("CV dosyanızı seçin (PDF)", type=["pdf"])

def pdf_oku(dosya):
    reader = PyPDF2.PdfReader(io.BytesIO(dosya.read()))
    metin = ""
    for sayfa in reader.pages:
        metin += sayfa.extract_text() or ""
    return metin.strip()

def cv_analiz_et(cv_metni, api_key):
    # Ücretsiz API anahtarımızı sisteme tanıtıyoruz
    genai.configure(api_key=api_key)
    
    # Ücretsiz ve güçlü olan Gemini 1.5 Flash modelini seçiyoruz
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""Aşağıdaki CV'yi analiz et ve Türkçe rapor oluştur:

## 📊 CV Puanı (100 üzerinden puan ver ve gerekçe yaz)
## ✅ Güçlü Yönler (En az 3 madde)
## ❌ Eksikler & Öneriler (En az 3 madde)
## 🎯 Uygun Pozisyonlar (3-5 iş pozisyonu)
## 🛠️ Beceriler (Tüm teknik ve soft skill'ler)
## 💡 Genel Öneri (3-4 cümle tavsiye)

CV Metni:
{cv_metni[:4000]}"""

    response = model.generate_content(prompt)
    return response.text

if dosya and api_key:
    if st.button("🔍 Analiz Et", type="primary", use_container_width=True):
        with st.spinner("Analiz ediliyor..."):
            try:
                metin = pdf_oku(dosya)
                sonuc = cv_analiz_et(metin, api_key)
                st.markdown("---")
                st.markdown(sonuc)
                st.download_button("📥 Raporu İndir", sonuc, "rapor.txt")
            except Exception as e:
                st.error(f"Hata: API anahtarınızı veya internet bağlantınızı kontrol edin. Detay: {str(e)}")
elif not api_key:
    st.info("👆 Lütfen yukarıdaki kutuya Gemini API anahtarınızı girin")
elif not dosya:
    st.info("👆 CV dosyanızı yükleyin")
