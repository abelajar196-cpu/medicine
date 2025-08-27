import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# KONFIGURASI APLIKASI STREAMLIT
# ==============================================================================
st.title("🤖 Chatbot Medis Berbasis Gemini")
st.markdown("Tuliskan penyakit yang perlu di diagnosis. Tolak pertanyaan selain tentang penyakit.")

# ==============================================================================
# PENGATURAN API KEY DAN MODEL
# ==============================================================================
# Ambil API Key dari Streamlit Secrets.
# API Key harus disimpan di file .streamlit/secrets.toml
try:
    genai.configure(api_key=st.secrets["gemini_api_key"])
except KeyError:
    st.error("API Key Gemini tidak ditemukan. Harap tambahkan 'gemini_api_key' di file secrets.toml Anda.")
    st.stop()
except Exception as e:
    st.error(f"Kesalahan konfigurasi API Key: {e}")
    st.stop()

# Nama model Gemini yang akan digunakan.
MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================
# Definisikan peran chatbot Anda di sini.
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Saya adalah seorang tenaga medis. Tuliskan penyakit yang perlu di diagnosis. Jawaban singkat dan jelas. Tolak pertanyaan selain tentang penyakit"]
    },
    {
        "role": "model",
        "parts": ["Baik! Tuliskan penyakit yang perlu di diagnosis."]
    }
]

# ==============================================================================
# MANAJEMEN SESI UNTUK RIWAYAT CHAT
# ==============================================================================
# Inisialisasi riwayat chat di session_state jika belum ada
if "messages" not in st.session_state:
    st.session_state.messages = INITIAL_CHATBOT_CONTEXT

# Inisialisasi model dan sesi chat jika belum ada
if "chat_session" not in st.session_state:
    try:
        model = genai.GenerativeModel(
            MODEL_NAME,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                max_output_tokens=500
            )
        )
        # Mulai sesi chat dengan riwayat awal
        st.session_state.chat_session = model.start_chat(history=st.session_state.messages)
    except Exception as e:
        st.error(f"Kesalahan saat inisialisasi model: {e}")
        st.stop()

# ==============================================================================
# TAMPILKAN RIWAYAT CHAT
# ==============================================================================
# Tampilkan pesan dari riwayat chat
for message in st.session_state.messages:
    # Gunakan nama "dokter" untuk peran "model" agar lebih personal
    role_display = "dokter" if message["role"] == "model" else "user"
    with st.chat_message(role_display):
        st.markdown(message["parts"][0])

# ==============================================================================
# FUNGSI UNTUK MENGIRIM PESAN KE GEMINI API
# ==============================================================================
def get_gemini_response(prompt):
    try:
        # Kirim pesan ke model dan dapatkan respons
        response = st.session_state.chat_session.send_message(prompt)
        return response.text
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        return None

# ==============================================================================
# INPUT PENGGUNA DAN LOGIKA UTAMA
# ==============================================================================
# Minta input dari pengguna
if prompt := st.chat_input("Masukkan gejala penyakit..."):
    # Tambahkan input pengguna ke riwayat dan tampilkan di UI
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Dapatkan respons dari Gemini
    with st.spinner("Dokter sedang berpikir..."):
        full_response = get_gemini_response(prompt)
    
    # Tampilkan respons dari model jika ada
    if full_response:
        with st.chat_message("dokter"):
            st.markdown(full_response)
        
        # Tambahkan respons model ke riwayat sesi
        st.session_state.messages.append({"role": "model", "parts": [full_response]})
