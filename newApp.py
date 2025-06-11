import streamlit as st
import requests
import json

# premis 
symptoms_data = {
    "G1": "Poliura (Sering Kencing)",
    "G2": "Mual dan muntah",
    "G3": "Pusing",
    "G4": "Polifagia (Cepat Lapar)",
    "G5": "Keringat berlebihan",
    "G6": "Gelisah",
    "G7": "Mudah lelah",
    "G8": "Polidipsia (Sering haus)",
    "G9": "Gangguan Keseimbangan",
    "G10": "Disfungsi ereksi",
    "G11": "Gemetar",
    "G12": "Pandangan kabur",
    "G13": "Sulit berkonsentrasi",
    "G14": "Gula darah tinggi",
    "G15": "Nafas cepat dan berbau keton",
    "G16": "Penglihatan menurun",
    "G17": "Tampak bercak hitam pada penglihatan",
    "G18": "Nyeri pada mata",
    "G19": "Gatal - gatal",
    "G20": "Hilangnya nafsu makan",
    "G21": "Insomnia",
    "G22": "Lemas",
    "G23": "Penurunan libido",
    "G24": "Sembelit"
}

# data penyakit 
diseases_data = {
    "P1": "Hipoglikemia",
    "P2": "Hiperglikemia",
    "P3": "Ketoasidosis Diabetik",
    "P4": "Retinopati Diabetik",
    "P5": "Nefropati Diabatik",
    "P6": "Neuropati Diabetik"
}

# rule of inference
rules_data = [
    {"conditions": ["G3", "G4", "G5", "G6", "G7", "G11", "G12", "G13"], "disease_code": "P1"},
    {"conditions": ["G4", "G8", "G14"], "disease_code": "P2"},
    {"conditions": ["G1", "G2", "G7", "G8", "G15"], "disease_code": "P3"},
    {"conditions": ["G16", "G17", "G18"], "disease_code": "P4"},
    {"conditions": ["G19", "G20", "G21", "G22"], "disease_code": "P5"},
    {"conditions": ["G5", "G9", "G10", "G23", "G24"], "disease_code": "P6"}
]

def detect_disease_rules(selected_symptom_codes):
    """
    Mendeteksi penyakit berdasarkan gejala yang dipilih dan aturan yang ada (rule-based).
    Args:
        selected_symptom_codes (list): Daftar kode gejala yang dipilih oleh pengguna.
    Returns:
        list: Daftar nama penyakit yang terdeteksi berdasarkan aturan.
    """
    detected_diseases_rules = []
    for rule in rules_data:
        if set(rule["conditions"]).issubset(set(selected_symptom_codes)):
            disease_name = diseases_data.get(rule["disease_code"])
            if disease_name and disease_name not in detected_diseases_rules:
                detected_diseases_rules.append(disease_name)
    return detected_diseases_rules

def get_ai_suggestions(selected_symptom_descriptions_list):
    """
    Menyusun prompt, memanggil LLM (Gemini API), dan mengembalikan responsnya.
    Args:
        selected_symptom_descriptions_list (list): Daftar deskripsi gejala yang dipilih.
    Returns:
        str: Respons dari LLM atau pesan kesalahan.
    """
    if not selected_symptom_descriptions_list:
        return "Tidak ada gejala yang dipilih untuk analisis AI."

    symptoms_text = "\n".join([f"- {desc}" for desc in selected_symptom_descriptions_list])
    prompt = (
        "Anda adalah asisten medis AI. Berdasarkan gejala-gejala berikut yang dialami seseorang:\n\n"
        f"{symptoms_text}\n\n"
        "Mohon berikan beberapa kemungkinan kondisi medis atau penyakit yang mungkin dialami orang tersebut. "
        "Fokus pada kondisi yang mungkin terkait dengan diabetes atau masalah kesehatan umum lainnya. "
        "Untuk setiap saran, berikan penjelasan singkat jika memungkinkan. Format jawaban sebagai daftar bernomor "
        "(misalnya, 1. Nama Kondisi - Penjelasan Singkat). "
        "Ingatlah bahwa informasi ini hanya untuk tujuan pengetahuan dan bukan merupakan diagnosis medis. "
        "Pasien harus selalu berkonsultasi dengan profesional medis untuk diagnosis yang akurat.\n\n"
        "Kemungkinan kondisi:"
    )

    # api call 
    api_key = "AIzaSyDr-0Apfj_a7POuB6ObY8cbkD5SbJn9hB4" 

    if api_key == "none" or not api_key:
        return (
            "**API Key Belum Dikonfigurasi.**\n\n"
            "Untuk menggunakan fitur AI, Anda perlu memasukkan API Key Google Gemini Anda "
            "di dalam kode sumber fungsi `get_ai_suggestions`.\n\n"
            f"Prompt yang akan dikirim:\n```text\n{prompt}\n```"
        )

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}]
        }]
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=45) 
        response.raise_for_status()  
        result = response.json()

        if (result.get("candidates") and
            result["candidates"][0].get("content") and
            result["candidates"][0]["content"].get("parts") and
            result["candidates"][0]["content"]["parts"][0].get("text")):
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            error_detail = f"Struktur respons tidak terduga: {json.dumps(result, indent=2)}"
            return "Gagal mendapatkan respons yang valid dari AI. Struktur respons tidak sesuai."
    except requests.exceptions.Timeout:
        return "Permintaan ke AI melebihi batas waktu (timeout). Coba lagi nanti."
    except requests.exceptions.HTTPError as http_err:
        error_detail = f"Kode Status: {http_err.response.status_code}, Respons: {http_err.response.text}"
        return f"Terjadi kesalahan HTTP saat menghubungi AI: {error_detail}"
    except requests.exceptions.RequestException as e:
        return f"Terjadi kesalahan koneksi saat menghubungi AI: {e}"
    except Exception as e: 
        return f"Terjadi kesalahan yang tidak terduga saat memproses permintaan AI: {e}"


def main():
    """
    Fungsi utama untuk menjalankan aplikasi Streamlit.
    """
    st.set_page_config(page_title="Deteksi Dini Diabetes", layout="wide")
    st.title("🩺 Program Deteksi Dini Penyakit Terkait Diabetes")
    st.markdown("""
    Aplikasi ini membantu melakukan deteksi dini beberapa penyakit terkait diabetes berdasarkan gejala yang Anda alami. 
    Pilih gejala-gejala di bawah ini, lalu klik tombol "Deteksi Penyakit". 
    """)

    st.header("Pilih Gejala yang Anda Alami:")

    selected_symptoms_codes = []
    
    sorted_symptom_keys = sorted(symptoms_data.keys())
    
    num_columns = 3 
    columns = st.columns(num_columns)
    
    for i, symptom_code in enumerate(sorted_symptom_keys):
        symptom_name = symptoms_data[symptom_code]
        with columns[i % num_columns]:
            if st.checkbox(f"**{symptom_code}**: {symptom_name}", key=symptom_code):
                selected_symptoms_codes.append(symptom_code)

    st.markdown("---") 

    if st.button("Deteksi Penyakit Dengan Rule of Inference", type="primary", use_container_width=True):
        if not selected_symptoms_codes:
            st.warning("Mohon pilih minimal satu gejala untuk melakukan deteksi.")
        else:
            st.subheader("Gejala yang Dipilih:")
            cols_gejala = st.columns(3)
            for idx, code in enumerate(selected_symptoms_codes):
                 cols_gejala[idx % 3].info(f"{code}: {symptoms_data[code]}")

            diagnosed_diseases_rules = detect_disease_rules(selected_symptoms_codes)
            
            st.markdown("---")
            st.subheader("Hasil Deteksi Berdasarkan Rule of Inference:")
            if diagnosed_diseases_rules:
                for disease in diagnosed_diseases_rules:
                    st.success(f"Berdasarkan gejala yang dipilih dan aturan yang ada, Anda kemungkinan menderita: **{disease}**")
            else:
                st.info("Tidak ada penyakit spesifik yang terdeteksi berdasarkan kombinasi gejala yang Anda pilih dari aturan yang tersedia.")
                st.markdown("Jika Anda merasa khawatir dengan kondisi kesehatan Anda, sebaiknya tetap berkonsultasi dengan dokter.")
    
    st.markdown("---")

    with st.expander("Saran Tambahan", expanded=False):
        st.markdown("""
        Fitur ini menggunakan LLM untuk memberikan kemungkinan kondisi lain berdasarkan
        kombinasi gejala yang Anda pilih 
        """)
        if st.button("Analisis dengan LLM", use_container_width=True):
            if not selected_symptoms_codes:
                st.warning("Mohon pilih minimal satu gejala untuk analisis berbasis LLM")
            else:
                st.subheader("Gejala yang Dipilih untuk LLM Analysis:")
                # menampilkan kembali gejala yang dipilih agar dapat dibaca LLM
                cols_gejala_ai = st.columns(3)
                for idx, code in enumerate(selected_symptoms_codes):
                    cols_gejala_ai[idx % 3].info(f"{code}: {symptoms_data[code]}")

                selected_symptom_descriptions = [symptoms_data[code] for code in selected_symptoms_codes]
                
                with st.spinner("Sedang menganalisis gejala dengan AI... Mohon tunggu."):
                    ai_response = get_ai_suggestions(selected_symptom_descriptions)
                
                st.markdown("---")
                st.subheader("LLM Response")
                st.markdown(ai_response, unsafe_allow_html=True) # unsafe_allow_html untuk render markdown 

    st.markdown("---")
    st.caption(" Kelompok 6 ")

if __name__ == "__main__":
    main()
