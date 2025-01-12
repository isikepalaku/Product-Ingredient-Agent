import streamlit as st
import os
from PIL import Image
from io import BytesIO
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.tavily import TavilyTools
from tempfile import NamedTemporaryFile
from constants import SYSTEM_PROMPT, INSTRUCTIONS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

tavily_api_key = os.getenv('TAVILY_API_KEY')
google_api_key = os.getenv('GOOGLE_API_KEY')

if not tavily_api_key or not google_api_key:
    st.error("Pastikan TAVILY_API_KEY dan GOOGLE_API_KEY telah diatur dalam file .env Anda")
    st.stop()

MAX_IMAGE_WIDTH = 800

def resize_image_for_display(image_file):
    if isinstance(image_file, str):
        img = Image.open(image_file)
    else:
        img = Image.open(image_file)
        image_file.seek(0)
    
    aspect_ratio = img.height / img.width
    new_height = int(MAX_IMAGE_WIDTH * aspect_ratio)
    img = img.resize((MAX_IMAGE_WIDTH, new_height), Image.Resampling.LANCZOS)
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

@st.cache_resource
def get_agent():
    return Agent(
        model=Gemini(id="gemini-2.0-flash-exp"),
        system_prompt=SYSTEM_PROMPT,
        instructions=INSTRUCTIONS,
        tools=[TavilyTools(api_key=tavily_api_key)],
        markdown=True,
    )

def analyze_image(image_path):
    agent = get_agent()
    with st.spinner('Melakukan analisis forensik...'):
        response = agent.run(
            "Lakukan analisis forensik lengkap pada gambar ini dengan fokus pada:\n"
            "1. Identifikasi dan analisis semua objek\n"
            "2. Metadata dan karakteristik teknis gambar\n"
            "3. Jika ada sidik jari, berikan formula Henry Classification\n"
            "4. Transkripsi dan analisis teks atau tulisan tangan\n"
            "Berikan analisis terstruktur dalam Bahasa Indonesia.",
            images=[image_path],
        )
        st.markdown(response.content)

def save_uploaded_file(uploaded_file):
    with NamedTemporaryFile(dir='.', suffix='.jpg', delete=False) as f:
        f.write(uploaded_file.getbuffer())
        return f.name

def main():
    st.title("🔍 Penganalisis Forensik Digital")
    st.markdown("""
    Alat ini menyediakan analisis komprehensif untuk:
    - Identifikasi dan analisis objek dalam gambar
    - Analisis metadata dan teknis
    - Formula sidik jari (Henry Classification)
    - Transkripsi dan analisis teks/tulisan tangan
    """)
    
    tab_upload, tab_camera = st.tabs([
        "📤 Unggah Gambar", 
        "📸 Ambil Gambar"
    ])
    
    with tab_upload:
        uploaded_file = st.file_uploader(
            "Unggah gambar untuk analisis", 
            type=["jpg", "jpeg", "png"],
            help="Unggah gambar yang jelas untuk analisis forensik"
        )
        if uploaded_file:
            resized_image = resize_image_for_display(uploaded_file)
            st.image(resized_image, caption="Gambar yang Diunggah", use_container_width=True)
            if st.button("🔍 Analisis Gambar", key="analyze_upload"):
                temp_path = save_uploaded_file(uploaded_file)
                analyze_image(temp_path)
                os.unlink(temp_path)
    
    with tab_camera:
        camera_photo = st.camera_input("Ambil foto untuk analisis")
        if camera_photo:
            resized_image = resize_image_for_display(camera_photo)
            st.image(resized_image, caption="Gambar yang Diambil", use_container_width=True)
            if st.button("🔍 Analisis Gambar", key="analyze_camera"):
                temp_path = save_uploaded_file(camera_photo)
                analyze_image(temp_path)
                os.unlink(temp_path)

if __name__ == "__main__":
    st.set_page_config(
        page_title="Penganalisis Forensik Digital",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    main()