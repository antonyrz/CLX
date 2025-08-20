import os
import re
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import tempfile

# Configuración (ajusta según tu sistema)
pytesseract.pytesseract.tesseract_cmd = r'C:/Users/Windows/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'  # Windows
# Para Linux/macOS, asegúrate de tener tesseract instalado y en PATH

def extraer_texto_de_pdf_escaneado(pdf_path):
    # Convertir PDF a imágenes
    images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=1)
    
    if not images:
        return ""
    
    # Procesar la primera página con OCR
    text = pytesseract.image_to_string(images[0], lang='spa')  # 'spa' para español
    
    return text

def extraer_datos(texto):
    # Extraer fecha manteniendo el formato original (d/m/yyyy o dd/mm/yyyy)
    fecha_match = re.search(r'(?i)(fecha\s*[:.]\s*)(\d{1,2}/\d{1,2}/\d{4})', texto)
    fecha = fecha_match.group(2) if fecha_match else "SIN_FECHA"
    
    # Extraer CLIENTE (ajustado para tu caso específico)
    lugar = re.search(r'(?i)(CLIENTE)[:\s]*([^\n]+)', texto)
    lugar = lugar.group(2).strip() if lugar else "SIN_LUGAR"
    lugar = "".join(c for c in lugar if c.isalnum() or c in (' ', '-', '_')).strip()

    # Extraer nombre (ajustado para tu formato)
    nombre_match = re.search(r'(?i)(Sr\.\s*[:.]\s*)([^\n]+)', texto) or \
                 re.search(r'(?i)(.:*[:.]\s*)([^\n]+)', texto)
    nombre = nombre_match.group(2).strip() if nombre_match else "SIN_NOMBRE"
    nombre = "".join(c for c in nombre if c.isalnum() or c in (' ', '-', '_')).strip()

    return fecha, lugar, nombre

def renombrar_pdfs_escaneados(carpeta):
    for archivo in os.listdir(carpeta):
        if archivo.lower().endswith('.pdf'):
            ruta_completa = os.path.join(carpeta, archivo)
            try:
                print(f"\nProcesando: {archivo}")
                
                # Extraer texto
                with open(ruta_completa, 'rb') as f:
                    reader = PdfReader(f)
                    texto = reader.pages[0].extract_text()
                    if not texto or len(texto.strip()) < 20:
                        texto = extraer_texto_de_pdf_escaneado(ruta_completa)
                
                fecha, lugar, nombre = extraer_datos(texto)
                print(f"Datos extraídos - Fecha: {fecha}, Cliente: {lugar}, Nombre: {nombre}")
                
                # Crear nuevo nombre manteniendo el formato original
                nombreSinFormato = f"{fecha} - {lugar} - {nombre}.pdf".strip()
                nuevo_nombre = nombreSinFormato.upper()
                
                # Limpieza segura para nombres de archivo
                nuevo_nombre = "".join(c for c in nuevo_nombre 
                                      if c.isprintable() and c not in {'\\', ':', '*', '?', '"', '<', '>', '|'})
                nuevo_nombre = nuevo_nombre.replace('/', '-')  # Conserva las / en fechas
                
                # Manejar nombres duplicados
                nueva_ruta = os.path.join(carpeta, nuevo_nombre)
                counter = 1
                while os.path.exists(nueva_ruta):
                    nuevo_nombre = f"{fecha} - {lugar} - {nombre.upper()} ({counter}).pdf"
                    nuevo_nombre = "".join(c for c in nuevo_nombre 
                                          if c.isprintable() and c not in {'\\', ':', '*', '?', '"', '<', '>', '|'})
                    nueva_ruta = os.path.join(carpeta, nuevo_nombre)
                    counter += 1
                
                os.rename(ruta_completa, nueva_ruta)
                print(f"✅ Renombrado a: {nuevo_nombre}")
                
            except Exception as e:
                print(f"❌ Error procesando {archivo}: {str(e)}")

# Uso
carpeta_con_pdfs = r'E:/Desktop/Scanner'  # Cambiar por tu ruta
renombrar_pdfs_escaneados(carpeta_con_pdfs)