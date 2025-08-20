import os

# Configuración
RUTA_BASE = r"E:\Desktop\despachos"  # ¡Cambia esto!

def crear_carpetas():
    print("📂 CREADOR DE CARPETAS PARA LOGÍSTICA")
    print("-" * 40)
    print(f"Las carpetas se crearán en: {RUTA_BASE}\n")
    
    # Ingresar múltiples pares "Destino - Chofer" (uno por línea)
    print("""Ingresa la lista de carpetas (formato: "Destino - Chofer"): 
(Ejemplo: Los Cortijos - Manuel Carrillo)""")
    print("Presiona Enter 2 veces para finalizar.\n")
    
    lineas = []
    while True:
        linea = input().strip()
        if not linea:
            break
        lineas.append(linea)
    
    # Procesar cada entrada
    for linea in lineas:
        try:
            destino, chofer = map(str.strip, linea.split("-", 1))
            ruta_carpeta = os.path.join(RUTA_BASE, destino, chofer)
            os.makedirs(ruta_carpeta, exist_ok=True)
            print(f"✅ {destino}/{chofer}")
        except ValueError:
            print(f"❌ Error en formato: '{linea}'. Usa 'Destino - Chofer'")
    
    print("\n¡Todas las carpetas fueron creadas!")

if __name__ == "__main__":
    crear_carpetas()