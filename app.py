import streamlit as st
import requests
from PIL import Image
import io
import re
import chardet

# 🔑 Clave del servicio OCR
OCR_API_KEY = "K88651325788957"

# --- FUNCIONES ---

def limpiar_texto(texto):
    """Limpia el texto de caracteres no deseados y lo pasa a minúsculas."""
    texto = texto.lower()
    texto = re.sub(r'[^a-záéíóúñ\s]', '', texto)
    return texto

def analizar_texto(texto):
    """Analiza el texto buscando indicadores de voseo o tuteo."""
    texto_limpio = limpiar_texto(texto)
    voseo_palabras = ["vos", "tenés", "hacés", "podés", "sabés", "querés", "pagá", "vení", "andá", "decí", "seguí"]
    tuteo_palabras = ["tú", "tienes", "haces", "puedes", "sabes", "quieres", "te", "dime", "ven", "haz", "anda"]
    voseo_encontradas = [word for word in voseo_palabras if word in texto_limpio]
    tuteo_encontradas = [word for word in tuteo_palabras if word in texto_limpio]
    return voseo_encontradas, tuteo_encontradas

# --- INTERFAZ PRINCIPAL ---

st.title("🗣️ Revisor de Voseo y Tuteo")
st.write("Subí una imagen o un archivo de texto para detectar si está en voseo o tuteo.")

opcion = st.radio("Selecciona el tipo de archivo:", ["Imagen", "Texto (.txt)"])

# --- OPCIÓN IMAGEN ---
if opcion == "Imagen":
    uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="📸 Imagen subida", use_column_width=True)

        # Convertir imagen a bytes
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes = img_bytes.getvalue()

        st.write("🔍 Procesando imagen con OCR...")
        response = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": img_bytes},
            data={"apikey": OCR_API_KEY, "language": "spa"}
        )

        result = response.json()
        detected_text = result.get("ParsedResults", [{}])[0].get("ParsedText", "")

        st.subheader("📝 Texto detectado:")
        st.write(detected_text if detected_text.strip() else "No se detectó texto.")

        voseo_encontradas, tuteo_encontradas = analizar_texto(detected_text)

# --- OPCIÓN TEXTO (.TXT) ---
elif opcion == "Texto (.txt)":
    uploaded_text = st.file_uploader("Sube un archivo .txt", type=["txt"])
    if uploaded_text is not None:
        raw_data = uploaded_text.read()

        # Detectar codificación del archivo
        detected = chardet.detect(raw_data)
        encoding = detected.get("encoding", "utf-8") or "utf-8"
        st.write(f"📄 Codificación detectada: `{encoding}`")

        # Intentar decodificar con tolerancia a errores
        try:
            texto = raw_data.decode(encoding)
        except UnicodeDecodeError:
            try:
                texto = raw_data.decode("utf-8", errors="replace")
            except Exception:
                texto = raw_data.decode("latin-1", errors="replace")

        st.subheader("📝 Texto cargado:")
        st.write(texto if texto.strip() else "El archivo está vacío o no contiene texto legible.")

        voseo_encontradas, tuteo_encontradas = analizar_texto(texto)

# --- RESULTADOS DE ANÁLISIS ---
if (opcion == "Imagen" and 'detected_text' in locals()) or (opcion == "Texto (.txt)" and 'texto' in locals()):
    st.subheader("📊 Análisis:")
    if voseo_encontradas or tuteo_encontradas:
        st.write("**Palabras encontradas:**")
        if voseo_encontradas:
            st.write(f"- VOSEO: {', '.join(voseo_encontradas)}")
        if tuteo_encontradas:
            st.write(f"- TUTEO: {', '.join(tuteo_encontradas)}")

        if len(voseo_encontradas) > len(tuteo_encontradas):
            st.success("✅ El texto está mayormente en **VOSEO**.")
        elif len(tuteo_encontradas) > len(voseo_encontradas):
            st.success("✅ El texto está mayormente en **TUTEO**.")
        else:
            st.info("⚖️ El texto contiene una mezcla equilibrada de voseo y tuteo.")
    else:
        st.warning("🔎 El texto parece **NEUTRO** o no contiene indicadores claros.")
