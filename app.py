import streamlit as st
import easyocr
from PIL import Image
import tempfile
import os

# Configuración de la página
st.set_page_config(page_title="Revisor: Voseo y Tuteo", layout="wide")

st.title("🧐 Revisor: Voseo costarricense y Tuteo panameño")
st.write("Sube una imagen con texto (afiche, post, banner) y el sistema hará lo siguiente:")
st.markdown("""
1. Extrae el texto (OCR).
2. Detecta si el texto usa mayoritariamente el voseo (Costa Rica) o el tuteo (Panamá).
3. Informa palabras anómalas o formas inconsistentes y sugiere correcciones.
""")

# Entrada de imagen
st.header("1) Entrada")
modo = st.radio("Modo de entrada:", ["Subir imagen (OCR)", "Pegar texto manualmente"])

texto_extraido = ""

if modo == "Subir imagen (OCR)":
    imagen = st.file_uploader("Sube una imagen (PNG/JPG)", type=["png", "jpg", "jpeg"])
    if imagen:
        # Guardar imagen temporalmente
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, imagen.name)
        with open(temp_path, "wb") as f:
            f.write(imagen.read())

        st.image(Image.open(temp_path), caption="Imagen cargada", use_column_width=True)

        # OCR con EasyOCR
        st.info("Procesando OCR...")
        reader = easyocr.Reader(['es'])  # idioma español
        result = reader.readtext(temp_path)
        texto_extraido = " ".join([res[1] for res in result])

elif modo == "Pegar texto manualmente":
    texto_extraido = st.text_area("Pega el texto aquí:")

# Mostrar resultados
st.header("2) Resultados")
st.subheader("Texto extraído:")
st.write(texto_extraido if texto_extraido else "-")

# Análisis de voseo/tuteo
def analizar_voseo_tuteo(texto):
    voseo_palabras = ["vos", "tenés", "hacés", "podés", "querés"]
    tuteo_palabras = ["tú", "tienes", "haces", "puedes", "quieres"]

    voseo_detectado = any(p in texto.lower() for p in voseo_palabras)
    tuteo_detectado = any(p in texto.lower() for p in tuteo_palabras)

    return voseo_detectado, tuteo_detectado

if texto_extraido:
    voseo, tuteo = analizar_voseo_tuteo(texto_extraido)
    st.subheader("Análisis:")
    if voseo and not tuteo:
        st.success("Se detecta voseo costarricense.")
    elif tuteo and not voseo:
        st.success("Se detecta tuteo panameño.")
    elif voseo and tuteo:
        st.warning("Texto mixto: contiene voseo y tuteo.")
    else:
        st.info("No se detectaron formas típicas de voseo o tuteo. Podés revisar manualmente.")

    st.subheader("Detalles por palabra:")
    st.write(f"Voseo detectado: {'Sí' if voseo else 'No'}")
    st.write(f"Tuteo detectado: {'Sí' if tuteo else 'No'}")
