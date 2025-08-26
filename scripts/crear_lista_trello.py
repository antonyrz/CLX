# crear_lista_semanal_trello.py
import requests
from datetime import datetime, timedelta
import logging

# Configuración de Trello
TRELLO_API_KEY = '42787586eee516566278d073c147d0a6'
TRELLO_TOKEN = 'ATTA12214504dfa0e26f448ea4cfa62b9965aa4f0173461637b794192feea6f39d782E0B66A6'
NOMBRE_TABLERO_TRELLO = 'RECEPCIÓN DESPACHOS'

# Configurar logging
logging.basicConfig(
    filename='crear_lista_semanal.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def obtener_id_tablero_por_nombre(nombre_tablero):
    """Obtiene el ID de un tablero por su nombre"""
    url = f"https://api.trello.com/1/members/me/boards?key={TRELLO_API_KEY}&token={TRELLO_TOKEN}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            boards = response.json()
            for board in boards:
                if nombre_tablero.upper() in board['name'].upper():
                    return board['id']
        else:
            logging.error(f"Error al obtener tableros: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Excepción al obtener tableros: {str(e)}")
    return None

def obtener_listas_tablero(tablero_id):
    """Obtiene todas las listas de un tablero"""
    url = f"https://api.trello.com/1/boards/{tablero_id}/lists?key={TRELLO_API_KEY}&token={TRELLO_TOKEN}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Error al obtener listas: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Excepción al obtener listas: {str(e)}")
    return []

def crear_lista_trello(id_tablero, nombre_lista):
    """Crea una lista en Trello"""
    url = "https://api.trello.com/1/lists"
    query = {
        'name': nombre_lista,
        'idBoard': id_tablero,
        'key': TRELLO_API_KEY,
        'token': TRELLO_TOKEN
    }
    try:
        response = requests.post(url, params=query, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Error al crear lista: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Excepción al crear lista: {str(e)}")
    return None

def crear_tarjeta_trello(id_lista, nombre_tarjeta):
    """Crea una tarjeta en Trello"""
    url = "https://api.trello.com/1/cards"
    query = {
        'idList': id_lista,
        'name': nombre_tarjeta,
        'key': TRELLO_API_KEY,
        'token': TRELLO_TOKEN
    }
    try:
        response = requests.post(url, params=query, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Error al crear tarjeta: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Excepción al crear tarjeta: {str(e)}")
    return None

def crear_checklist_tarjeta(id_tarjeta, nombre_checklist):
    """Crea un checklist en una tarjeta de Trello"""
    url = "https://api.trello.com/1/checklists"
    query = {
        'idCard': id_tarjeta,
        'name': nombre_checklist,
        'key': TRELLO_API_KEY,
        'token': TRELLO_TOKEN
    }
    try:
        response = requests.post(url, params=query, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Error al crear checklist: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Excepción al crear checklist: {str(e)}")
    return None

def crear_lista_semanal_trello():
    """Crea la lista semanal en Trello con las tarjetas de cada día"""
    logging.info("Iniciando creación de lista semanal en Trello")
    
    # Obtener el lunes de esta semana
    hoy = datetime.now()
    lunes = hoy - timedelta(days=hoy.weekday())
    viernes = lunes + timedelta(days=4)

    # Formatear el nombre de la lista (usando el número del día en lugar de "VIERNES")
    nombre_lista = f"SEMANA DEL {lunes.strftime('%d %m')} AL {viernes.strftime('%d %m %Y')}"
    logging.info(f"Nombre de lista a crear: {nombre_lista}")

    # Obtener el ID del tablero
    tablero_id = obtener_id_tablero_por_nombre(NOMBRE_TABLERO_TRELLO)
    if not tablero_id:
        logging.error("No se pudo obtener el ID del tablero")
        return False

    # Verificar si la lista ya existe
    listas = obtener_listas_tablero(tablero_id)
    for lista in listas:
        if lista['name'] == nombre_lista:
            logging.info("La lista de esta semana ya existe")
            return True

    # Crear la lista
    nueva_lista = crear_lista_trello(tablero_id, nombre_lista)
    if not nueva_lista:
        logging.error("Error al crear la lista")
        return False

    lista_id = nueva_lista['id']
    logging.info(f"Lista creada: {nombre_lista}")

    # Nombres de los días en español
    nombres_dias = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES"]

    # Crear una tarjeta para cada día de lunes a viernes
    for i in range(5):
        fecha = lunes + timedelta(days=i)
        nombre_tarjeta = f"{fecha.strftime('%d')} {nombres_dias[i]}"
        
        # Crear la tarjeta
        tarjeta = crear_tarjeta_trello(lista_id, nombre_tarjeta)
        if not tarjeta:
            logging.error(f"Error al crear la tarjeta para {nombre_tarjeta}")
            continue

        # Crear el checklist "despachos" en la tarjeta
        checklist = crear_checklist_tarjeta(tarjeta['id'], "despachos")
        if checklist:
            logging.info(f"Tarjeta y checklist creados: {nombre_tarjeta}")
        else:
            logging.info(f"Tarjeta creada pero sin checklist: {nombre_tarjeta}")
    
    logging.info("Proceso de creación de lista semanal completado")
    return True

if __name__ == "__main__":
    crear_lista_semanal_trello()