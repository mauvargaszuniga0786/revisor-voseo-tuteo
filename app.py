import streamlit as st
import requests
from PIL import Image
import io
import re

# Configuración API OCR
OCR_API_KEY = "K88651325788957"  # Sustituye con tu API Key real

def limpiar_texto(texto):
    # Convertir a minúsculas y eliminar caracteres no alfabéticos (manteniendo tildes y espacios)
    texto = texto.lower()
    texto = re.sub(r'[^a-záéíóúñ\s]', '', texto)
    return texto

def analizar_texto(texto):
    texto_limpio = limpiar_texto(texto)

    voseo_palabras = ["vos", "tenés", "hacés", "podés", "sabés", "querés", "pagá", "vení", "andá"]
    tuteo_palabras = ["tú", "tienes", "haces", "puedes", "sabes", "quieres", "te"]

    voseo_encontradas = [word for word in voseo_palabras if word in texto_limpio]
    tuteo_encontradas = [word for word in tuteo_palabras if word in texto_limpio]

    return voseo_encontradas, tuteo_encontradas

st.title("Revisor Voseo/Tuteo")

opcion = st.radio("Selecciona el tipo de archivo:", ["Imagen", "Texto (.txt)"])

if opcion == "Imagen":
    uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagen subida", use_column_width=True)

        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes = img_bytes.getvalue()

        st.write("Procesando imagen con OCR...")
        response = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": img_bytes},
            data={"apikey": OCR_API_KEY, "language": "spa"}
        )

        result = response.json()
        detected_text = result.get("ParsedResults", [{}])[0].get("ParsedText", "")

        st.subheader("Texto detectado:")
        st.write(detected_text)

        voseo_encontradas, tuteo_encontradas = analizar_texto(detected_text)

elif opcion == "Texto (.txt)":
    uploaded_text = st.file_uploader("Sube un archivo .txt", type=["txt"])
    if uploaded_text is not None:
        texto = uploaded_text.read().decode("utf-8")
        st.subheader("Texto cargado:")
        st.write(texto)

        voseo_encontradas, tuteo_encontradas = analizar_texto(texto)

# Mostrar análisis si hay resultados
if (opcion == "Imagen" and 'detected_text' in locals()) or (opcion == "Texto (.txt)" and 'texto' in locals()):
    st.subheader("Análisis:")
    if voseo_encontradas or tuteo_encontradas:
        st.write("**Palabras encontradas:**")
        if voseo_encontradas:
            st.write(f"- VOSEO: {', '.join(voseo_encontradas)}")
        if tuteo_encontradas:
            st.write(f"- TUTEO: {', '.join(tuteo_encontradas)}")

        if len(voseo_encontradas) > len(tuteo_encontradas):
            st.success("El texto está mayormente en **VOSEO**.")
        elif len(tuteo_encontradas) > len(voseo_encontradas):
            st.success("El texto está mayormente en **TUTEO**.")
        else:
            st.info("El texto contiene mezcla de voseo y tuteo.")
    else:
        st.warning("El texto parece **NEUTRO** o no contiene indicadores.")
