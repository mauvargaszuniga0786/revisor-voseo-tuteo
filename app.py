import streamlit as st
import requests
from PIL import Image
import io

# Configuración
OCR_API_KEY = "TU_API_KEY_DE_OCRSPACE"  # Obtén una gratis en https://ocr.space/ocrapi

st.title("Revisor Voseo/Tuteo")

uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagen subida", use_column_width=True)

    # Convertir imagen a bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()

    # Llamada a OCR.Space API
    st.write("Procesando texto...")
    response = requests.post(
        "https://api.ocr.space/parse/image",
        files={"file": img_bytes},
        data={"apikey": OCR_API_KEY, "language": "spa"}
    )

    result = response.json()
    detected_text = result.get("ParsedResults", [{}])[0].get("ParsedText", "")

    st.subheader("Texto detectado:")
    st.write(detected_text)

    # --- Análisis voseo/tuteo ---
    voseo_palabras = ["vos", "tenés", "hacés", "podés", "sabés", "querés"]
    tuteo_palabras = ["tú", "tienes", "haces", "puedes", "sabes", "quieres"]

    voseo_count = sum(word in detected_text.lower() for word in voseo_palabras)
    tuteo_count = sum(word in detected_text.lower() for word in tuteo_palabras)

    st.subheader("Análisis:")
    if voseo_count > tuteo_count:
        st.success("El texto está mayormente en **VOSEO**.")
    elif tuteo_count > voseo_count:
        st.success("El texto está mayormente en **TUTEO**.")
    else:
        st.warning("El texto parece **NEUTRO** o no contiene suficientes indicadores.")
