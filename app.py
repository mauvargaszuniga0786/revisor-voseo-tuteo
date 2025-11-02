import streamlit as st
import requests
from PIL import Image
import io

OCR_API_KEY = "K88651325788957"  # Tu API Key real

st.title("Revisor Voseo/Tuteo")

uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagen subida", use_column_width=True)

    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()

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
    voseo_palabras = ["vos", "tenés", "hacés", "podés", "sabés", "querés", "pagá"]
    tuteo_palabras = ["tú", "tienes", "haces", "puedes", "sabes", "quieres", "te"]

    texto_lower = detected_text.lower()

    voseo_encontradas = [word for word in voseo_palabras if word in texto_lower]
    tuteo_encontradas = [word for word in tuteo_palabras if word in texto_lower]

    st.subheader("Análisis:")
    if voseo_encontradas or tuteo_encontradas:
        if voseo_encontradas:
            st.write(f"**Palabras VOSEO encontradas:** {', '.join(voseo_encontradas)}")
        if tuteo_encontradas:
            st.write(f"**Palabras TUTEO encontradas:** {', '.join(tuteo_encontradas)}")

        if len(voseo_encontradas) > len(tuteo_encontradas):
            st.success("El texto está mayormente en **VOSEO**.")
        elif len(tuteo_encontradas) > len(voseo_encontradas):
            st.success("El texto está mayormente en **TUTEO**.")
        else:
            st.info("El texto contiene mezcla de voseo y tuteo.")
    else:
        st.warning("El texto parece **NEUTRO** o no contiene indicadores.")
