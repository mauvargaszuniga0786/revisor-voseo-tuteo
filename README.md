# Revisor Voseo (CR) / Tuteo (PA) - Streamlit

## Contenido
- `app.py` : aplicación Streamlit principal.
- `requirements.txt` : dependencias.

## Descripción
Esta app permite subir una imagen con texto (afiche, banner) o pegar texto manualmente.
La app intenta extraer texto mediante `pytesseract` y luego analiza si el registro es:
- Voseo (Costa Rica) o
- Tuteo (Panamá)

También detecta coincidencias mixtas y sugiere correcciones según el registro mayoritario.

## Notas importantes sobre OCR / despliegue
- `pytesseract` requiere que el binario Tesseract OCR esté instalado en el servidor:
  - En Ubuntu: `sudo apt-get install tesseract-ocr`
  - En macOS (Homebrew): `brew install tesseract`
- En Streamlit Community Cloud es posible que `tesseract` no esté instalado por defecto. Si el servicio no permite instalar paquetes del sistema, la app mostrará un aviso y podés usar la opción de pegar texto manualmente.
- Si querés OCR sin instalar el binario, considerá servicios externos (APIs) o librerías que empaqueten modelos (por ejemplo `easyocr`, aunque puede requerir muchas dependencias).

## Cómo desplegar en Streamlit Cloud
1. Subí este repositorio a GitHub (archivo ZIP contiene todo).
2. En share.streamlit.io crea una nueva app y conecta tu repo.
3. Asegurate de que `requirements.txt` esté presente; Streamlit instalará las dependencias Python.
4. Si necesitás Tesseract en el servidor, revisá la documentación de Streamlit Cloud para ver si permiten instalar paquetes del sistema o usa un contenedor personalizado si es necesario.

## Ejecutar localmente
1. Crear y activar un virtualenv.
2. `pip install -r requirements.txt`
3. Instalar Tesseract (sistema).
4. `streamlit run app.py`

## Contacto
Proyecto generado automáticamente por ChatGPT para Mauricio. Si querés mejoras (más verbos, reglas, mejor corrección automática o integración con OCR cloud), pedime que lo amplíe.
