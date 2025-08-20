"""
ORGANIZADOR AUTOMÁTICO DE PDFS CON INTEGRACIÓN TRELLO

Este script realiza dos funciones principales:
1. Organiza archivos PDF en carpetas específicas basándose en su nombre
2. Marca items correspondientes en Trello como completados

Autor: Asistente AI
Fecha: 2025
"""

import os
import shutil
import re
import requests
from datetime import datetime

# ================= CONFIGURACIÓN =================
# 🔧 ESTA SECCIÓN ES DONDE DEBES CONFIGURAR TUS PROPIAS RUTAS Y CREDENCIALES

# Credenciales de Trello (obtener desde https://trello.com/power-ups/admin)
TRELLO_API_KEY = '42787586eee516566278d073c147d0a6'  # Tu clave API de Trello
TRELLO_TOKEN = 'ATTA12214504dfa0e26f448ea4cfa62b9965aa4f0173461637b794192feea6f39d782E0B66A6'  # Tu token de Trello
NOMBRE_TABLERO_TRELLO = 'RECEPCIÓN DESPACHOS'  # Nombre exacto de tu tablero en Trello

# Rutas de carpetas (ajusta estas rutas según tu sistema)
CARPETA_PDFS = r'E:/Desktop/Scanner'  # Carpeta donde se encuentran los PDFs escaneados
RUTA_BASE = r"\\10.10.53.21\Logistica\COMPARTIDA LOGISTICA\DESPACHO TIENDAS"  # Ruta base de la red donde se guardarán los PDFs

# ================= FUNCIONES DE TRELLO =================
# 🤖 ESTAS FUNCIONES SE ENCARGAN DE LA COMUNICACIÓN CON TRELLO

def obtener_id_tablero_por_nombre(nombre_tablero):
    """
    Busca un tablero en Trello por su nombre y devuelve su ID único
    
    Parámetros:
    nombre_tablero (str): El nombre del tablero que quieres encontrar
    
    Retorna:
    str: El ID del tablero si se encuentra, None si no existe
    """
    # Construye la URL para obtener todos los tableros del usuario
    url = f"https://api.trello.com/1/members/me/boards?key={TRELLO_API_KEY}&token={TRELLO_TOKEN}"
    
    # Hace la solicitud a la API de Trello
    response = requests.get(url)
    
    # Si la solicitud fue exitosa (código 200)
    if response.status_code == 200:
        boards = response.json()  # Convierte la respuesta a formato JSON
        
        # Busca entre todos los tableros
        for board in boards:
            # Compara los nombres (ignorando mayúsculas/minúsculas)
            if nombre_tablero.upper() in board['name'].upper():
                return board['id']  # Devuelve el ID del tablero encontrado
    
    # Si no encuentra el tablero o hay error
    return None

def obtener_listas_tablero(tablero_id):
    """
    Obtiene todas las listas de un tablero específico de Trello
    
    Parámetros:
    tablero_id (str): El ID del tablero del cual obtener las listas
    
    Retorna:
    list: Una lista de todas las listas en el tablero, o lista vacía si hay error
    """
    # Construye la URL para obtener las listas del tablero
    url = f"https://api.trello.com/1/boards/{tablero_id}/lists?key={TRELLO_API_KEY}&token={TRELLO_TOKEN}"
    
    # Hace la solicitud a la API
    response = requests.get(url)
    
    # Si la solicitud fue exitosa, devuelve las listas
    if response.status_code == 200:
        return response.json()
    
    # Si hay error, devuelve lista vacía
    return []

def obtener_tarjetas_lista(lista_id):
    """
    Obtiene todas las tarjetas de una lista específica de Trello
    
    Parámetros:
    lista_id (str): El ID de la lista de la cual obtener las tarjetas
    
    Retorna:
    list: Lista de tarjetas en la lista especificada
    """
    # Construye la URL para obtener las tarjetas de la lista
    url = f"https://api.trello.com/1/lists/{lista_id}/cards?key={TRELLO_API_KEY}&token={TRELLO_TOKEN}"
    
    # Hace la solicitud
    response = requests.get(url)
    
    # Si es exitosa, devuelve las tarjetas
    if response.status_code == 200:
        return response.json()
    
    # Si hay error, devuelve lista vacía
    return []

def obtener_checklists_tarjeta(tarjeta_id):
    """
    Obtiene todos los checklists de una tarjeta específica de Trello
    
    Parámetros:
    tarjeta_id (str): El ID de la tarjeta de la cual obtener los checklists
    
    Retorna:
    list: Lista de checklists en la tarjeta
    """
    # Construye la URL para obtener los checklists de la tarjeta
    url = f"https://api.trello.com/1/cards/{tarjeta_id}/checklists?key={TRELLO_API_KEY}&token={TRELLO_TOKEN}"
    
    # Hace la solicitud
    response = requests.get(url)
    
    # Si es exitosa, devuelve los checklists
    if response.status_code == 200:
        return response.json()
    
    # Si hay error, devuelve lista vacía
    return []

def marcar_item_checklist_completo(idCard, idCheckItem):
    """
    Marca un item específico de un checklist como completado en Trello
    
    Parámetros:
    idCard (str): El ID de la tarjeta que contiene el checklist
    idCheckItem (str): El ID del item específico a marcar como completado
    
    Retorna:
    bool: True si se marcó exitosamente, False si hubo error
    """
    # Construye la URL correcta para marcar el item como completado
    url = f"https://api.trello.com/1/cards/{idCard}/checkItem/{idCheckItem}?key={TRELLO_API_KEY}&token={TRELLO_TOKEN}"
    
    # Los datos a enviar (indicando que el estado es "completado")
    data = {'state': 'complete'}
    
    try:
        # Hace la solicitud PUT para actualizar el item
        response = requests.put(url, json=data, timeout=10)
        
        # Si la solicitud fue exitosa (código 200)
        if response.status_code == 200:
            return True
        else:
            # Muestra información de error si la hay
            print(f"  ❌ Error HTTP al marcar item: {response.status_code}")
            print(f"  ❌ Respuesta del servidor: {response.text}")
            return False
    except Exception as e:
        # Captura cualquier excepción y muestra el error
        print(f"  ❌ Excepción al marcar item: {str(e)}")
        return False

def normalizar_texto_trello(texto):
    """
    Normaliza texto para comparación, eliminando caracteres especiales y estandarizando formato
    
    Parámetros:
    texto (str): El texto a normalizar
    
    Retorna:
    str: El texto normalizado (mayúsculas, sin caracteres especiales, etc.)
    """
    # Convierte a mayúsculas y elimina espacios al inicio/final
    texto = texto.upper().strip()
    
    # Reemplaza múltiples espacios consecutivos por un solo espacio
    texto = re.sub(r'\s+', ' ', texto)
    
    # Elimina caracteres especiales pero mantiene letras, números, espacios y guiones
    texto = re.sub(r'[^\w\s-]', '', texto)
    
    return texto

def encontrar_item_checklist(checklists, nombre_buscado):
    """
    Busca un item específico en todos los checklists de una tarjeta
    
    Parámetros:
    checklists (list): Lista de checklists donde buscar
    nombre_buscado (str): El nombre del item a buscar
    
    Retorna:
    tuple: (checklist, item) si se encuentra, (None, None) si no se encuentra
    """
    # Normaliza el nombre buscado para comparación
    nombre_buscado_normalizado = normalizar_texto_trello(nombre_buscado)
    
    # Busca en todos los checklists y todos sus items
    for checklist in checklists:
        for item in checklist['checkItems']:
            # Normaliza el nombre del item actual para comparación
            item_normalizado = normalizar_texto_trello(item['name'])
            
            # Compara los nombres normalizados
            if nombre_buscado_normalizado == item_normalizado:
                # Coincidencia exacta encontrada
                return checklist, item
            
            # También verifica coincidencias parciales por si hay pequeñas diferencias
            if (nombre_buscado_normalizado in item_normalizado or 
                item_normalizado in nombre_buscado_normalizado):
                # Coincidencia parcial encontrada
                return checklist, item
    
    # Si no encuentra ninguna coincidencia
    return None, None

def encontrar_lista_por_fecha(listas, fecha):
    """
    Encuentra la lista de Trello correspondiente a una fecha específica
    
    Parámetros:
    listas (list): Lista de todas las listas disponibles
    fecha (datetime): La fecha para la cual buscar la lista correspondiente
    
    Retorna:
    dict: La lista encontrada, o None si no se encuentra
    """
    # Busca en todas las listas
    for lista in listas:
        nombre_lista = lista['name'].upper()
        
        # Patrones para detectar formatos de fecha en el nombre de la lista
        patrones = [
            r'(\d{1,2})\s*(\d{1,2})\s*AL\s*(\d{1,2})\s*(\d{1,2})\s*(\d{4})',  # Ej: "11 08 AL 15 08 2025"
            r'(\d{1,2})[/-](\d{1,2})\s*AL\s*(\d{1,2})[/-](\d{1,2})\s*(\d{4})',  # Ej: "11/08 AL 15/08 2025"
            r'(\d{1,2})\s*(\d{1,2})\s*-\s*(\d{1,2})\s*(\d{1,2})\s*(\d{4})'  # Ej: "11 08 - 15 08 2025"
        ]
        
        # Intenta coincidir con cada patrón
        for patron in patrones:
            match = re.search(patron, nombre_lista)
            if match:
                try:
                    # Extrae los componentes de la fecha del nombre
                    dia_inicio = int(match.group(1))
                    mes_inicio = int(match.group(2))
                    dia_fin = int(match.group(3))
                    mes_fin = int(match.group(4))
                    año = int(match.group(5))
                    
                    # Crea objetos de fecha para comparación
                    fecha_inicio = datetime(año, mes_inicio, dia_inicio)
                    fecha_fin = datetime(año, mes_fin, dia_fin)
                    
                    # Verifica si la fecha está dentro del rango
                    if fecha_inicio <= fecha <= fecha_fin:
                        return lista  # Lista encontrada
                        
                except (ValueError, IndexError):
                    # Si hay error al procesar las fechas, continúa con la siguiente lista
                    continue
    
    # Si no encontró con el formato esperado, busca por coincidencia simple
    for lista in listas:
        nombre_lista = lista['name'].upper()
        
        # Busca cualquier mención del día, mes o año en el nombre
        if any(str(x) in nombre_lista for x in [fecha.day, fecha.month, fecha.year]):
            # Si encuentra el año en el nombre, es probable que sea la lista correcta
            anyo_match = re.search(r'(\d{4})', nombre_lista)
            if anyo_match and int(anyo_match.group(1)) == fecha.year:
                return lista
                
    # No se encontró ninguna lista para esta fecha
    return None

def encontrar_tarjeta_por_fecha(tarjetas, fecha):
    """
    Encuentra la tarjeta de Trello correspondiente a un día específico
    
    Parámetros:
    tarjetas (list): Lista de todas las tarjetas disponibles
    fecha (datetime): La fecha para la cual buscar la tarjeta
    
    Retorna:
    dict: La tarjeta encontrada, o None si no se encuentra
    """
    # Obtiene el nombre del día en inglés (Monday, Tuesday, etc.)
    nombre_dia = fecha.strftime('%A').upper()
    
    # Diccionario para traducir días de inglés a español
    dias_espanol = {
        'MONDAY': 'LUNES',
        'TUESDAY': 'MARTES',
        'WEDNESDAY': 'MIERCOLES',
        'THURSDAY': 'JUEVES',
        'FRIDAY': 'VIERNES',
        'SATURDAY': 'SABADO',
        'SUNDAY': 'DOMINGO'
    }
    
    # Traduce el nombre del día al español
    nombre_dia_espanol = dias_espanol.get(nombre_dia, nombre_dia)
    
    # Genera posibles formatos de nombre para la tarjeta
    nombres_posibles = [
        f"{fecha.day} {nombre_dia_espanol}",  # Ej: "18 LUNES"
        f"{fecha.day:02d} {nombre_dia_espanol}",  # Ej: "18 LUNES" (día con dos dígitos)
        f"{fecha.day}/{fecha.month} {nombre_dia_espanol}",  # Ej: "18/8 LUNES"
        f"{fecha.day}-{fecha.month} {nombre_dia_espanol}"  # Ej: "18-8 LUNES"
    ]
    
    # Busca coincidencias exactas
    for tarjeta in tarjetas:
        nombre_tarjeta = tarjeta['name'].upper()
        for nombre_posible in nombres_posibles:
            if nombre_posible.upper() in nombre_tarjeta:
                return tarjeta
                
    # Si no encuentra coincidencia exacta, busca por número de día y nombre de día
    for tarjeta in tarjetas:
        nombre_tarjeta = tarjeta['name'].upper()
        if str(fecha.day) in nombre_tarjeta and any(dia in nombre_tarjeta for dia in ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']):
            return tarjeta
            
    # No se encontró ninguna tarjeta para esta fecha
    return None

def tildar_en_trello(destino, nombre_conductor, fecha):
    """
    Función principal para marcar un item como completado en Trello
    
    Parámetros:
    destino (str): El destino del PDF (ej: "MM VALENCIA")
    nombre_conductor (str): El nombre del conductor (ej: "BRIGIDO HENRIQUEZ")
    fecha (datetime): La fecha del PDF
    
    Retorna:
    bool: True si se marcó exitosamente, False si hubo error
    """
    try:
        print(f"  📅 Buscando lista para la fecha: {fecha.strftime('%d/%m/%Y')}")
        
        # Paso 1: Obtener el ID del tablero
        tablero_id = obtener_id_tablero_por_nombre(NOMBRE_TABLERO_TRELLO)
        if not tablero_id:
            print("  ❌ No se encontró el tablero en Trello")
            return False
        
        # Paso 2: Obtener todas las listas del tablero
        listas = obtener_listas_tablero(tablero_id)
        if not listas:
            print("  ❌ No se encontraron listas en el tablero")
            return False
            
        # Paso 3: Encontrar la lista correspondiente a la fecha
        lista_obj = encontrar_lista_por_fecha(listas, fecha)
        
        if not lista_obj:
            print(f"  ❌ No se encontró lista para la fecha: {fecha.strftime('%d/%m/%Y')}")
            print("  Listas disponibles:")
            for lista in listas:
                print(f"    - {lista['name']}")
            return False
        
        print(f"  ✅ Lista encontrada: {lista_obj['name']}")
        
        # Paso 4: Obtener todas las tarjetas de la lista
        tarjetas = obtener_tarjetas_lista(lista_obj['id'])
        if not tarjetas:
            print("  ❌ No se encontraron tarjetas en la lista")
            return False
            
        # Paso 5: Encontrar la tarjeta correspondiente al día
        tarjeta_obj = encontrar_tarjeta_por_fecha(tarjetas, fecha)
        
        if not tarjeta_obj:
            print(f"  ❌ No se encontró tarjeta para la fecha: {fecha.strftime('%d/%m/%Y')}")
            print("  Tarjetas disponibles en la lista:")
            for tarjeta in tarjetas:
                print(f"    - {tarjeta['name']}")
            return False
            
        print(f"  ✅ Tarjeta encontrada: {tarjeta_obj['name']}")
        
        # Paso 6: Buscar el item en el checklist
        nombre_buscado = f"{destino} - {nombre_conductor}"
        checklists = obtener_checklists_tarjeta(tarjeta_obj['id'])
        
        if not checklists:
            print("  ❌ No se encontraron checklists en la tarjeta")
            return False
        
        # Paso 7: Buscar el item específico en los checklists
        checklist_obj, item_obj = encontrar_item_checklist(checklists, nombre_buscado)
        
        if not item_obj:
            print(f"  ❌ No se encontró item en el checklist para: {nombre_buscado}")
            print("  Items disponibles en el checklist:")
            for checklist in checklists:
                for item in checklist['checkItems']:
                    estado = "✅" if item['state'] == 'complete' else "❌"
                    print(f"    {estado} {item['name']} (Normalizado: {normalizar_texto_trello(item['name'])})")
            return False
        
        # Paso 8: Verificar si ya está completado
        if item_obj['state'] == 'complete':
            print(f"  ℹ️ El item ya estaba completado: {item_obj['name']}")
            return True
        
        # Paso 9: Marcar como completado
        print(f"  🎯 Intentando marcar item: {item_obj['name']} (ID: {item_obj['id']})")
        if marcar_item_checklist_completo(tarjeta_obj['id'], item_obj['id']):
            print(f"  ✅ Item marcado como completo en Trello: {item_obj['name']}")
            return True
        else:
            print(f"  ❌ Error al marcar el item como completo: {item_obj['name']}")
            return False
        
    except Exception as e:
        # Captura cualquier error inesperado
        print(f"  ❌ Error al conectar con Trello: {e}")
        import traceback
        traceback.print_exc()
        return False

# ================= FUNCIONES DE ORGANIZACIÓN DE PDFs =================
# 📁 ESTAS FUNCIONES SE ENCARGAN DE ORGANIZAR LOS PDFs EN CARPETAS

def normalizar_nombre(nombre):
    """
    Normaliza un nombre para comparación (elimina espacios extras y convierte a mayúsculas)
    
    Parámetros:
    nombre (str): El nombre a normalizar
    
    Retorna:
    str: El nombre normalizado
    """
    return re.sub(r'\s+', ' ', nombre.strip()).upper()

def extraer_fecha_desde_nombre(nombre_archivo):
    """
    Extrae la fecha del nombre de un archivo PDF
    
    Parámetros:
    nombre_archivo (str): El nombre del archivo (ej: "15-8-2025 - MM COSTAZUL - LUIS FERMIN AVILA.PDF")
    
    Retorna:
    datetime: La fecha extraída, o None si no se puede extraer
    """
    try:
        # Busca el patrón de fecha (dd-mm-aaaa)
        fecha_match = re.search(r'(\d{1,2})-(\d{1,2})-(\d{4})', nombre_archivo)
        if fecha_match:
            # Extrae día, mes y año
            dia = int(fecha_match.group(1))
            mes = int(fecha_match.group(2))
            año = int(fecha_match.group(3))
            
            # Crea y devuelve un objeto datetime
            return datetime(año, mes, dia)
    except:
        # Si hay algún error, devuelve None
        pass
    
    return None

def obtener_nombre_mes(fecha):
    """
    Devuelve el nombre del mes en español
    
    Parámetros:
    fecha (datetime): La fecha de la cual obtener el nombre del mes
    
    Retorna:
    str: El nombre del mes en español (ej: "AGOSTO")
    """
    meses = {
        1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
        5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
        9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
    }
    return meses.get(fecha.month, "")

def obtener_nombre_dia_semana(fecha):
    """
    Devuelve el nombre del día de la semana en español
    
    Parámetros:
    fecha (datetime): La fecha de la cual obtener el nombre del día
    
    Retorna:
    str: El nombre del día en español (ej: "LUNES")
    """
    dias = {
        0: "LUNES", 1: "MARTES", 2: "MIERCOLES", 3: "JUEVES",
        4: "VIERNES", 5: "SABADO", 6: "DOMINGO"
    }
    return dias.get(fecha.weekday(), "")

def determinar_empresa(destino):
    """
    Determina la empresa basándose en el prefijo del destino
    
    Parámetros:
    destino (str): El destino del PDF (ej: "MM VALENCIA")
    
    Retorna:
    str: "MULTIMAX" para destinos que empiezan con "MM", "CLX" para los que empiezan con "CLX", None para otros
    """
    if destino.upper().startswith("MM"):
        return "MULTIMAX"
    elif destino.upper().startswith("CLX"):
        return "CLX"
    else:
        return None

def construir_ruta_base(fecha, destino):
    """
    Construye la ruta base donde se guardará el PDF
    
    Parámetros:
    fecha (datetime): La fecha del PDF
    destino (str): El destino del PDF
    
    Retorna:
    str: La ruta completa donde se debe guardar el PDF, o None si no se puede determinar la empresa
    """
    # Determina la empresa (MULTIMAX o CLX)
    empresa = determinar_empresa(destino)
    if not empresa:
        return None
    
    # Extrae año, mes y nombre del mes
    año = fecha.year
    mes_numero = fecha.month
    mes_nombre = obtener_nombre_mes(fecha)
    
    # Construye la ruta completa
    return os.path.join(
        RUTA_BASE,
        empresa,
        str(año),
        f"{mes_numero} - {mes_nombre}"
    )

def encontrar_carpeta_semana(ruta_base, fecha):
    """
    Encuentra la carpeta de semana correspondiente a una fecha
    
    Parámetros:
    ruta_base (str): La ruta base donde buscar
    fecha (datetime): La fecha para la cual buscar la carpeta
    
    Retorna:
    str: La ruta completa de la carpeta de semana, o None si no se encuentra
    """
    # Verifica que la ruta base exista y que se haya proporcionado una fecha
    if not fecha or not os.path.exists(ruta_base):
        return None
        
    # Busca en todas las carpetas de la ruta base
    for item in os.listdir(ruta_base):
        # Solo considera carpetas que contengan "SEMANA" en el nombre
        if "SEMANA" in item.upper():
            # Intenta extraer las fechas del nombre de la carpeta
            semana_match = re.search(r'(\d{1,2})\s*(\d{1,2}).*?(\d{1,2})\s*(\d{1,2}).*?(\d{4})', item)
            if semana_match:
                try:
                    # Extrae los componentes de la fecha
                    dia_inicio = int(semana_match.group(1))
                    mes_inicio = int(semana_match.group(2))
                    dia_fin = int(semana_match.group(3))
                    mes_fin = int(semana_match.group(4))
                    año = int(semana_match.group(5))
                    
                    # Crea objetos de fecha para comparación
                    fecha_inicio = datetime(año, mes_inicio, dia_inicio)
                    fecha_fin = datetime(año, mes_fin, dia_fin)
                    
                    # Verifica si la fecha está dentro del rango
                    if fecha_inicio <= fecha <= fecha_fin:
                        # Devuelve la ruta completa de la carpeta
                        return os.path.join(ruta_base, item)
                except:
                    # Si hay error al procesar las fechas, continúa con la siguiente carpeta
                    continue
    
    # No se encontró ninguna carpeta de semana para esta fecha
    return None

def encontrar_carpeta_dia(ruta_semana, fecha):
    """
    Encuentra la carpeta del día correspondiente a una fecha
    
    Parámetros:
    ruta_semana (str): La ruta de la carpeta de semana
    fecha (datetime): La fecha para la cual buscar la carpeta
    
    Retorna:
    str: La ruta completa de la carpeta del día, o None si no se encuentra
    """
    # Verifica que la ruta de semana exista y que se haya proporcionado una fecha
    if not fecha or not os.path.exists(ruta_semana):
        return None
        
    # Genera el nombre esperado para la carpeta del día (ej: "18 LUNES")
    nombre_dia_esperado = f"{fecha.day:02d} {obtener_nombre_dia_semana(fecha)}"
    
    # Busca en todas las carpetas de la semana
    for item in os.listdir(ruta_semana):
        # Compara los nombres normalizados
        if normalizar_nombre(item) == normalizar_nombre(nombre_dia_esperado):
            # Devuelve la ruta completa de la carpeta del día
            return os.path.join(ruta_semana, item)
    
    # No se encontró la carpeta del día
    return None

def encontrar_carpeta_destino(ruta_dia, destino):
    """
    Encuentra la carpeta de destino dentro de la carpeta del día
    
    Parámetros:
    ruta_dia (str): La ruta de la carpeta del día
    destino (str): El destino a buscar (ej: "MM VALENCIA")
    
    Retorna:
    str: La ruta completa de la carpeta de destino, o None si no se encuentra
    """
    # Verifica que la ruta del día exista y que se haya proporcionado un destino
    if not destino or not os.path.exists(ruta_dia):
        return None
        
    # Busca en todas las carpetas del día
    for item in os.listdir(ruta_dia):
        # Compara los nombres normalizados
        if normalizar_nombre(item) == normalizar_nombre(destino):
            # Devuelve la ruta completa de la carpeta de destino
            return os.path.join(ruta_dia, item)
    
    # No se encontró la carpeta de destino
    return None

def encontrar_carpeta_conductor(ruta_destino, conductor):
    """
    Encuentra la carpeta del conductor dentro de la carpeta de destino
    
    Parámetros:
    ruta_destino (str): La ruta de la carpeta de destino
    conductor (str): El nombre del conductor a buscar
    
    Retorna:
    str: La ruta completa de la carpeta del conductor, or None si no se encuentra
    """
    # Verifica que la ruta de destino exista y que se haya proporcionado un conductor
    if not conductor or not os.path.exists(ruta_destino):
        return None
        
    # Busca en todas las carpetas del destino
    for item in os.listdir(ruta_destino):
        # Compara los nombres normalizados
        if normalizar_nombre(item) == normalizar_nombre(conductor):
            # Devuelve la ruta completa de la carpeta del conductor
            return os.path.join(ruta_destino, item)
    
    # No se encontró la carpeta del conductor
    return None

# ================= FUNCIÓN PRINCIPAL =================
# 🚀 ESTA ES LA FUNCIÓN PRINCIPAL QUE ORQUESTA TODO EL PROCESO

def organizar_pdfs():
    """
    Función principal que organiza todos los PDFs en la carpeta especificada
    y marca los items correspondientes en Trello como completados
    """
    print("📁 ORGANIZADOR DE PDFS EN CARPETA COMPARTIDA CON TRELLO")
    print("=" * 60)
    
    # Verifica que la carpeta de PDFs exista
    if not os.path.exists(CARPETA_PDFS):
        print(f"❌ Error: No existe la carpeta de PDFs: {CARPETA_PDFS}")
        return
        
    # Verifica que se pueda acceder a la ruta base de la red
    if not os.path.exists(RUTA_BASE):
        print(f"❌ Error: No se puede acceder a la ruta compartida: {RUTA_BASE}")
        print("   Verifica la conexión de red y los permisos de acceso.")
        return

    # Procesa cada archivo en la carpeta de PDFs
    for archivo in os.listdir(CARPETA_PDFS):
        # Solo procesa archivos PDF (ignora otros tipos de archivo)
        if not archivo.lower().endswith('.pdf'):
            continue
            
        # Construye la ruta completa del archivo
        ruta_pdf = os.path.join(CARPETA_PDFS, archivo)
        
        try:
            # Paso 1: Extrae información del nombre del archivo
            # Los nombres deben tener el formato: "FECHA - DESTINO - NOMBRE.pdf"
            partes = archivo.split(' - ')
            if len(partes) < 3:
                print(f"❌ Formato incorrecto: {archivo}")
                continue
                
            # Extrae la fecha del nombre del archivo
            fecha_archivo = extraer_fecha_desde_nombre(archivo)
            # Extrae el destino (segunda parte)
            destino_archivo = partes[1].strip()
            # Extrae el nombre del conductor (tercera parte en adelante)
            nombre_archivo = ' - '.join(partes[2:])
            # Elimina la extensión .pdf del nombre
            nombre_archivo = os.path.splitext(nombre_archivo)[0].strip()
            
            # Muestra información del archivo que se está procesando
            print(f"\nProcesando: {archivo}")
            print(f"  Fecha: {fecha_archivo}")
            print(f"  Destino: {destino_archivo}")
            print(f"  Nombre: {nombre_archivo}")
            
            # Verifica que se pudo extraer la fecha
            if not fecha_archivo:
                print(f"  ❌ No se pudo extraer la fecha del archivo")
                continue
            
            # Paso 2: Construye la ruta base según la empresa (MULTIMAX o CLX)
            ruta_base_empresa = construir_ruta_base(fecha_archivo, destino_archivo)
            if not ruta_base_empresa:
                print(f"  ❌ No se pudo determinar la empresa para el destino: {destino_archivo}")
                continue
                
            # Verifica que la ruta base exista
            if not os.path.exists(ruta_base_empresa):
                print(f"  ❌ No se encuentra la ruta: {ruta_base_empresa}")
                continue
                
            # Paso 3: Encuentra la carpeta de semana correspondiente
            carpeta_semana = encontrar_carpeta_semana(ruta_base_empresa, fecha_archivo)
            if not carpeta_semana:
                print(f"  ❌ No se encontró carpeta de semana para la fecha: {fecha_archivo}")
                continue
                
            # Paso 4: Encuentra la carpeta del día correspondiente
            carpeta_dia = encontrar_carpeta_dia(carpeta_semana, fecha_archivo)
            if not carpeta_dia:
                print(f"  ❌ No se encontró carpeta de día para la fecha: {fecha_archivo}")
                continue
                
            # Paso 5: Encuentra la carpeta de destino correspondiente
            carpeta_destino = encontrar_carpeta_destino(carpeta_dia, destino_archivo)
            if not carpeta_destino:
                print(f"  ❌ No se encontró carpeta de destino para: {destino_archivo}")
                continue
                
            # Paso 6: Encuentra la carpeta del conductor correspondiente
            carpeta_conductor = encontrar_carpeta_conductor(carpeta_destino, nombre_archivo)
            if not carpeta_conductor:
                print(f"  ❌ No se encontró carpeta del conductor para: {nombre_archivo}")
                continue
                
            # Paso 7: Prepara la nueva ruta para el archivo
            nuevo_path = os.path.join(carpeta_conductor, archivo)
            
            # Paso 8: Maneja archivos duplicados (añade número entre paréntesis)
            counter = 1
            while os.path.exists(nuevo_path):
                nombre_base, extension = os.path.splitext(archivo)
                nuevo_nombre = f"{nombre_base} ({counter}){extension}"
                nuevo_path = os.path.join(carpeta_conductor, nuevo_nombre)
                counter += 1
                
            # Paso 9: Mueve el archivo a su ubicación final
            shutil.move(ruta_pdf, nuevo_path)
            print(f"  ✅ Movido a: {carpeta_conductor}")
            
            # Paso 10: Intenta marcar el item correspondiente en Trello como completado
            tildar_en_trello(destino_archivo, nombre_archivo, fecha_archivo)
            
        except Exception as e:
            # Captura cualquier error inesperado durante el procesamiento
            print(f"  ❌ Error procesando {archivo}: {str(e)}")
            import traceback
            traceback.print_exc()

# Punto de entrada del script
if __name__ == "__main__":
    # Ejecuta la función principal
    organizar_pdfs()