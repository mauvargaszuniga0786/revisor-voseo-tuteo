import streamlit as st
import easyocr
from PIL import Image
import numpy as np

# Título de la aplicación
st.title("Revisor Voseo/Tuteo")

# Subir imagen
uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Mostrar imagen subida
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagen subida", use_column_width=True)

    # Convertir imagen a array para EasyOCR
    img_array = np.array(image)

    # Inicializar EasyOCR en CPU (evita error CUDA)
    reader = easyocr.Reader(['es'], gpu=False)

    # Extraer texto
    st.write("Procesando texto...")
    result = reader.readtext(img_array)

    # Unir todo el texto detectado
    detected_text = " ".join([res[1] for res in result])

    # Mostrar texto detectado
    st.subheader("Texto detectado:")
    st.write(detected_text)

    # --- Análisis de voseo/tuteo ---
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
``
