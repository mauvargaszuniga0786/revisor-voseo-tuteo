import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import re

st.set_page_config(page_title="Revisor Voseo (CR) / Tuteo (PA)", layout="wide")

st.title("🗣️ Revisor: Voseo costarricense y Tuteo panameño")
st.markdown("""Sube una imagen con texto (afiche, post, banner) o pega texto para que el sistema:
1. Extraiga el texto (OCR) - usa pytesseract si está disponible.
2. Detecte si el texto está mayoritariamente en voseo (Costa Rica) o tuteo (Panamá).
3. Informe palabras mezcladas o formas inconsistentes y proponga correcciones.
""")

col1, col2 = st.columns([1,1])

with col1:
    st.header("1) Entrada")
    input_mode = st.radio("Modo de entrada:", ("Subir imagen (OCR)", "Pegar texto manualmente"))
    uploaded_image = None
    text_input = ""

    if input_mode == "Subir imagen (OCR)":
        uploaded_file = st.file_uploader("Subí una imagen (PNG/JPG).", type=["png","jpg","jpeg"])
        if uploaded_file:
            uploaded_image = Image.open(uploaded_file).convert("RGB")
    else:
        text_input = st.text_area("Pega el texto aquí:", height=250)

    st.write("Registro objetivo: voseo costarricense (análisis) y tuteo panameño (detección).")
    show_boxes = st.checkbox("Mostrar imagen con palabras resaltadas (si usás imagen)", value=True)

with col2:
    st.header("2) Resultados")
    result_area = st.empty()

# --- Lexicons (sample focused on common forms) ---
voseo_forms = {
    "vos":"vos",
    "hablás":"hablar",
    "tenés":"tener",
    "vivís":"vivir",
    "venís":"venir",
    "podés":"poder",
    "sabés":"saber",
    "querés":"querer",
    "decís":"decir",
    "hacés":"hacer",
    "ponés":"poner",
    "salís":"salir",
    "dormís":"dormir",
    "entendés":"entender",
    "pedís":"pedir",
    "comés":"comer",
    "llamás":"llamar",
    "pagás":"pagar",
    "usás":"usar",
    "mirás":"mirar",
    "pensás":"pensar",
    "volvés":"volver",
    "sentís":"sentir",
    "asegurate":"asegurate",
    "contame":"contar"
}

tuteo_forms = {
    "tú":"tú",
    "hablas":"hablar",
    "tienes":"tener",
    "vives":"vivir",
    "vienes":"venir",
    "puedes":"poder",
    "sabes":"saber",
    "quieres":"querer",
    "dices":"decir",
    "haces":"hacer",
    "pones":"poner",
    "sales":"salir",
    "duermes":"dormir",
    "entiendes":"entender",
    "pides":"pedir",
    "comes":"comer",
    "llamas":"llamar",
    "pagas":"pagar",
    "usas":"usar",
    "miras":"mirar",
    "piensas":"pensar",
    "vuelves":"volver",
    "sientes":"sentir",
    "asegúrate":"asegúrate",
    "cuéntame":"cuéntame"
}

suggestion_map = {
    "hablas":"hablás", "tienes":"tenés", "vives":"vivís", "vienes":"venís", "puedes":"podés",
    "sabes":"sabés", "quieres":"querés", "dices":"decís", "haces":"hacés", "pones":"ponés",
    "sales":"salís", "duermes":"dormís", "entiendes":"entendés", "pides":"pedís", "comes":"comés",
    "llamas":"llamás", "pagas":"pagás", "usas":"usás", "miras":"mirás", "piensas":"pensás",
    "vuelves":"volvés", "sientes":"sentís", "asegúrate":"asegurate", "cuéntame":"contame",
    "hablás":"hablas", "tenés":"tienes", "vivís":"vives", "venís":"venies", "podés":"puedes",
    "sabés":"sabes", "querés":"quieres", "decís":"dices", "hacés":"haces", "ponés":"pones",
    "salís":"sales", "dormís":"duermes", "entendés":"entiendes", "pedís":"pides", "comés":"comes",
    "llamás":"llamas", "pagás":"pagas", "usás":"usas", "mirás":"miras", "pensás":"piensas",
    "volvés":"vuelves", "sentís":"sientes", "asegurate":"asegúrate", "contame":"cuéntame"
}

def norm(w):
    return re.sub(r"[^\wáéíóúüñ]", "", w.lower())

ocr_available = True
try:
    import pytesseract
    from pytesseract import Output
except Exception as e:
    ocr_available = False

extracted_text = ""
boxes = []

if 'uploaded_image' in globals() and uploaded_image is not None:
    if not ocr_available:
        st.warning("OCR (pytesseract) no disponible en este entorno. Podés pegar el texto manualmente como alternativa.")
        st.image(uploaded_image, use_column_width=True)
        st.stop()
    else:
        try:
            import numpy as np
            data = pytesseract.image_to_data(uploaded_image, output_type=Output.DICT, lang='spa')
            extracted_text = pytesseract.image_to_string(uploaded_image, lang='spa')
            n = len(data['text'])
            for i in range(n):
                word = data['text'][i]
                if word.strip() == "":
                    continue
                left = data['left'][i]
                top = data['top'][i]
                width = data['width'][i]
                height = data['height'][i]
                boxes.append({"word": word, "left": left, "top": top, "w": width, "h": height})
        except Exception as e:
            st.error("Error al ejecutar OCR: " + str(e))
            st.stop()
else:
    extracted_text = globals().get('text_input', "")

words = re.findall(r"\b[\wáéíóúüñ']+\b", extracted_text, flags=re.IGNORECASE) if extracted_text else []
words_norm = [norm(w) for w in words]

voseo_hits = []
tuteo_hits = []
other_hits = []

for w, wn in zip(words, words_norm):
    if wn in voseo_forms:
        voseo_hits.append((w, wn))
    elif wn in tuteo_forms:
        tuteo_hits.append((w, wn))
    else:
        other_hits.append((w, wn))

vcount = len(voseo_hits)
tcount = len(tuteo_hits)
total_detected = vcount + tcount

if total_detected == 0:
    majority = "none"
elif vcount > tcount:
    majority = "voseo"
elif tcount > vcount:
    majority = "tuteo"
else:
    majority = "mixed"

suggestions = []
if majority == "voseo":
    for original, wn in tuteo_hits:
        if wn in suggestion_map:
            suggestions.append((original, suggestion_map.get(wn, "")))
elif majority == "tuteo":
    for original, wn in voseo_hits:
        if wn in suggestion_map:
            suggestions.append((original, suggestion_map.get(wn, "")))
else:
    for original, wn in voseo_hits + tuteo_hits:
        if wn in suggestion_map:
            suggestions.append((original, suggestion_map.get(wn, "")))

with result_area.container():
    st.subheader("Texto extraído:")
    st.code(extracted_text if extracted_text.strip() else "—")

    st.subheader("Análisis:")
    if majority == "none":
        st.info("No se detectaron formas típicas de voseo o tuteo. Podés revisar manualmente.")
    elif majority == "voseo":
        st.success(f"El texto está mayoritariamente en voseo (Costa Rica). (voseo={vcount}, tuteo={tcount})")
    elif majority == "tuteo":
        st.success(f"El texto está mayoritariamente en tuteo (Panamá). (tuteo={tcount}, voseo={vcount})")
    elif majority == "mixed":
        st.warning(f"El texto parece mixto (voseo={vcount}, tuteo={tcount}).")

    if suggestions:
        st.subheader("Sugerencias de corrección (según registro mayoritario):")
        for orig, sug in suggestions:
            st.write(f"• **{orig}**  →  **{sug}**")

    st.subheader("Detalles por palabra:")
    st.write(f"Voseo detectado ({vcount}): " + ", ".join([w for w,_ in voseo_hits]) if voseo_hits else "Voseo detectado: —")
    st.write(f"Tuteo detectado ({tcount}): " + ", ".join([w for w,_ in tuteo_hits]) if tuteo_hits else "Tuteo detectado: —")

if 'uploaded_image' in globals() and uploaded_image is not None and show_boxes:
    img_draw = uploaded_image.copy()
    draw = ImageDraw.Draw(img_draw)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 14)
    except:
        font = None

    for b in boxes:
        wn = norm(b['word'])
        x1, y1 = b['left'], b['top']
        x2, y2 = x1 + b['w'], y1 + b['h']

        color = None
        label = b['word']
        if wn in voseo_forms:
            if majority == "tuteo":
                color = (255, 80, 80)
            else:
                color = (80, 200, 120)
        elif wn in tuteo_forms:
            if majority == "voseo":
                color = (255, 80, 80)
            else:
                color = (80, 200, 120)
        else:
            color = (200, 200, 200)

        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
        if font:
            draw.rectangle([x1, y1 - 18, x1 + 200, y1], fill=(0,0,0))
            draw.text((x1+2, y1-16), label, fill=(255,255,255), font=font)

    st.subheader("Imagen con palabras resaltadas:")
    st.image(img_draw, use_column_width=True)

st.markdown("---")
st.caption("Nota: Para que OCR funcione correctamente en despliegue (Streamlit Cloud), es probable que necesites instalar el binario de Tesseract en el entorno del servidor o usar una alternativa de OCR. En caso de que OCR no funcione, podés pegar el texto manualmente.")
st.markdown("README incluido en el proyecto descargable con instrucciones para desplegar en Streamlit Cloud y/o localmente.")
