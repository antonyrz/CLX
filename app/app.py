import os
import shutil
import re
import requests
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
from datetime import datetime
import threading
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader

# ================= CONFIGURACIÓN =================
TRELLO_API_KEY = '42787586eee516566278d073c147d0a6'
TRELLO_TOKEN = 'ATTA12214504dfa0e26f448ea4cfa62b9965aa4f0173461637b794192feea6f39d782E0B66A6'
NOMBRE_TABLERO_TRELLO = 'RECEPCIÓN DESPACHOS'

CARPETA_PDFS = r'E:/Desktop/Scanner'
RUTA_BASE_CREAR = r'E:/Desktop/despachos'
RUTA_BASE = r"\\10.10.53.21\Logistica\COMPARTIDA LOGISTICA\DESPACHO TIENDAS"

# Configuración de Tesseract (para OCR)
pytesseract.pytesseract.tesseract_cmd = r'C:/Users/Windows/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'

# ================= PALETA DE COLORES =================
COLOR_FONDO = "#222831"      # Color de fondo de interfaz
COLOR_CONSOLA = "#393E46"    # Color de consola
COLOR_BOTONES = "#00ADB5"    # Color de botones
COLOR_TEXTO = "#EEEEEE"      # Letras de botones y título

# ================= CLASE PRINCIPAL DE LA APLICACIÓN =================
class PDFOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Organizador de PDFs - Sistema Completo")
        self.root.geometry("1000x700")
        self.root.configure(bg=COLOR_FONDO)
        
        # Configurar el estilo de la interfaz
        self.setup_styles()
        self.setup_ui()
        
    def setup_styles(self):
        """Configura los estilos de la interfaz con la paleta de colores especificada"""
        self.style = ttk.Style()
        
        # Configurar estilos para los diferentes elementos
        self.style.configure('TFrame', background=COLOR_FONDO)
        self.style.configure('TLabel', background=COLOR_FONDO, foreground=COLOR_TEXTO, font=('Arial', 10))
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground=COLOR_TEXTO)
        self.style.configure('TButton', font=('Arial', 10), padding=10)
        
        # Configurar estilo personalizado para botones
        self.style.configure('Action.TButton', 
                           background=COLOR_BOTONES, 
                           foreground=COLOR_TEXTO,
                           focuscolor=COLOR_BOTONES)
        
        # Configurar el mapa de colores para los botones
        self.style.map('Action.TButton',
                      background=[('active', '#0097A7'), ('pressed', '#00838F')],
                      foreground=[('active', COLOR_TEXTO), ('pressed', COLOR_TEXTO)])
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="📁 SISTEMA ORGANIZADOR DE PDFs", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E))
        
        # Botones de acción
        btn_renombrar = tk.Button(button_frame, text="🔄 Renombrar PDFs", 
                                 command=self.renombrar_pdfs, 
                                 bg=COLOR_BOTONES, fg=COLOR_TEXTO,
                                 font=('Arial', 10, 'bold'),
                                 relief='flat', padx=15, pady=10)
        btn_renombrar.grid(row=0, column=0, padx=5, pady=5)
        
        btn_crear_carpetas = tk.Button(button_frame, text="📂 Crear Carpetas", 
                                      command=self.crear_carpetas,
                                      bg=COLOR_BOTONES, fg=COLOR_TEXTO,
                                      font=('Arial', 10, 'bold'),
                                      relief='flat', padx=15, pady=10)
        btn_crear_carpetas.grid(row=0, column=1, padx=5, pady=5)
        
        btn_organizar = tk.Button(button_frame, text="🚀 Organizar PDFs", 
                                 command=self.organizar_pdfs,
                                 bg=COLOR_BOTONES, fg=COLOR_TEXTO,
                                 font=('Arial', 10, 'bold'),
                                 relief='flat', padx=15, pady=10)
        btn_organizar.grid(row=0, column=2, padx=5, pady=5)
        
        btn_limpiar = tk.Button(button_frame, text="🧹 Limpiar Consola", 
                               command=self.limpiar_consola,
                               bg=COLOR_BOTONES, fg=COLOR_TEXTO,
                               font=('Arial', 10, 'bold'),
                               relief='flat', padx=15, pady=10)
        btn_limpiar.grid(row=0, column=3, padx=5, pady=5)
        
        # Área de consola
        console_frame = ttk.Frame(main_frame)
        console_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.console = scrolledtext.ScrolledText(console_frame, height=20, width=100, 
                                               bg=COLOR_CONSOLA, fg=COLOR_TEXTO, 
                                               font=('Consolas', 9), relief='flat')
        self.console.pack(fill=tk.BOTH, expand=True)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status bar
        self.status_var = tk.StringVar(value="Listo para comenzar...")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, 
                             relief='sunken', anchor='w', bg=COLOR_CONSOLA, fg=COLOR_TEXTO)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Configurar pesos de grid para que los elementos se expandan correctamente
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Aplicar efectos hover a los botones
        self.setup_button_hover(btn_renombrar)
        self.setup_button_hover(btn_crear_carpetas)
        self.setup_button_hover(btn_organizar)
        self.setup_button_hover(btn_limpiar)
        
    def setup_button_hover(self, button):
        """Añade efectos hover a los botones"""
        def on_enter(e):
            button['bg'] = '#0097A7'  # Color más claro al pasar el mouse
            
        def on_leave(e):
            button['bg'] = COLOR_BOTONES  # Volver al color original
            
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
    def log(self, message):
        """Agrega un mensaje a la consola"""
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)
        self.root.update_idletasks()
        
    def limpiar_consola(self):
        """Limpia la consola de texto"""
        self.console.delete(1.0, tk.END)
        
    def start_progress(self):
        """Inicia la animación de progreso"""
        self.progress.start(10)
        
    def stop_progress(self):
        """Detiene la animación de progreso"""
        self.progress.stop()
        
    def renombrar_pdfs(self):
        """Ejecuta la función de renombrar PDFs en un hilo separado"""
        def run_renombrar():
            self.start_progress()
            self.status_var.set("Renombrando PDFs...")
            try:
                self.renombrar_pdfs_escaneados(CARPETA_PDFS)
                self.log("✅ Renombrado completado exitosamente!")
                messagebox.showinfo("Éxito", "PDFs renombrados correctamente")
            except Exception as e:
                self.log(f"❌ Error durante el renombrado: {str(e)}")
                messagebox.showerror("Error", f"Error durante el renombrado: {str(e)}")
            finally:
                self.stop_progress()
                self.status_var.set("Renombrado completado")
                
        threading.Thread(target=run_renombrar, daemon=True).start()
        
    def crear_carpetas(self):
        """Abre una ventana para crear carpetas"""
        # Crear ventana de diálogo para ingresar datos
        dialog = tk.Toplevel(self.root)
        dialog.title("Crear Carpetas")
        dialog.geometry("500x400")
        dialog.configure(bg=COLOR_FONDO)
        
        # Título
        title_label = tk.Label(dialog, text="📂 CREADOR DE CARPETAS", 
                              font=('Arial', 14, 'bold'), bg=COLOR_FONDO, fg=COLOR_TEXTO)
        title_label.pack(pady=10)
        
        # Instrucciones
        instructions = tk.Label(dialog, 
                               text="Ingresa la lista de carpetas (formato: 'Destino - Chofer')\nEjemplo: Los Cortijos - Manuel Carrillo", 
                               justify=tk.CENTER, bg=COLOR_FONDO, fg=COLOR_TEXTO)
        instructions.pack(pady=5)
        
        # Área de texto para ingresar datos
        text_frame = tk.Frame(dialog, bg=COLOR_FONDO)
        text_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        text_area = scrolledtext.ScrolledText(text_frame, height=10, width=50, 
                                            bg=COLOR_CONSOLA, fg=COLOR_TEXTO)
        text_area.pack(fill=tk.BOTH, expand=True)
        
        # Botones
        button_frame = tk.Frame(dialog, bg=COLOR_FONDO)
        button_frame.pack(pady=10)
        
        def crear_carpetas_handler():
            lineas = text_area.get("1.0", tk.END).strip().split('\n')
            lineas = [linea.strip() for linea in lineas if linea.strip()]
            
            if not lineas:
                messagebox.showwarning("Advertencia", "No se ingresaron datos")
                return
                
            try:
                self.crear_carpetas_desde_lista(lineas)
                messagebox.showinfo("Éxito", "Carpetas creadas correctamente")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear carpetas: {str(e)}")
        
        btn_crear = tk.Button(button_frame, text="Crear Carpetas", 
                             command=crear_carpetas_handler,
                             bg=COLOR_BOTONES, fg=COLOR_TEXTO,
                             font=('Arial', 10, 'bold'),
                             relief='flat', padx=15, pady=5)
        btn_crear.grid(row=0, column=0, padx=5)
        
        btn_cancelar = tk.Button(button_frame, text="Cancelar", 
                                command=dialog.destroy,
                                bg=COLOR_BOTONES, fg=COLOR_TEXTO,
                                font=('Arial', 10, 'bold'),
                                relief='flat', padx=15, pady=5)
        btn_cancelar.grid(row=0, column=1, padx=5)
        
        # Aplicar efectos hover a los botones
        self.setup_button_hover(btn_crear)
        self.setup_button_hover(btn_cancelar)
        
    def organizar_pdfs(self):
        """Ejecuta la función de organizar PDFs en un hilo separado"""
        def run_organizar():
            self.start_progress()
            self.status_var.set("Organizando PDFs...")
            try:
                self.organizar_pdfs_completo()
                self.log("✅ Organización completada exitosamente!")
                messagebox.showinfo("Éxito", "PDFs organizados correctamente")
            except Exception as e:
                self.log(f"❌ Error durante la organización: {str(e)}")
                messagebox.showerror("Error", f"Error durante la organización: {str(e)}")
            finally:
                self.stop_progress()
                self.status_var.set("Organización completada")
                
        threading.Thread(target=run_organizar, daemon=True).start()

    # ================= FUNCIONES DE RENOMBRADO =================
    def extraer_texto_de_pdf_escaneado(self, pdf_path):
        """Extrae texto de PDF escaneado usando OCR"""
        try:
            images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=1)
            if not images:
                return ""
            text = pytesseract.image_to_string(images[0], lang='spa')
            return text
        except Exception as e:
            self.log(f"❌ Error en OCR: {str(e)}")
            return ""

    def extraer_datos(self, texto):
        """Extrae datos del texto del PDF"""
        try:
            # Extraer fecha
            fecha_match = re.search(r'(?i)(fecha\s*[:.]\s*)(\d{1,2}/\d{1,2}/\d{4})', texto)
            fecha = fecha_match.group(2) if fecha_match else "SIN_FECHA"
            
            # Extraer CLIENTE
            lugar = re.search(r'(?i)(CLIENTE)[:\s]*([^\n]+)', texto)
            lugar = lugar.group(2).strip() if lugar else "SIN_LUGAR"
            lugar = "".join(c for c in lugar if c.isalnum() or c in (' ', '-', '_')).strip()

            # Extraer nombre
            nombre_match = re.search(r'(?i)(Sr\.\s*[:.]\s*)([^\n]+)', texto) or \
                         re.search(r'(?i)(.:*[:.]\s*)([^\n]+)', texto)
            nombre = nombre_match.group(2).strip() if nombre_match else "SIN_NOMBRE"
            nombre = "".join(c for c in nombre if c.isalnum() or c in (' ', '-', '_')).strip()

            return fecha, lugar, nombre
        except Exception as e:
            self.log(f"❌ Error extrayendo datos: {str(e)}")
            return "SIN_FECHA", "SIN_LUGAR", "SIN_NOMBRE"

    def renombrar_pdfs_escaneados(self, carpeta):
        """Función principal de renombrado"""
        for archivo in os.listdir(carpeta):
            if archivo.lower().endswith('.pdf'):
                ruta_completa = os.path.join(carpeta, archivo)
                try:
                    self.log(f"\nProcesando: {archivo}")
                    
                    # Extraer texto
                    with open(ruta_completa, 'rb') as f:
                        reader = PdfReader(f)
                        texto = reader.pages[0].extract_text()
                        if not texto or len(texto.strip()) < 20:
                            texto = self.extraer_texto_de_pdf_escaneado(ruta_completa)
                    
                    fecha, lugar, nombre = self.extraer_datos(texto)
                    self.log(f"Datos extraídos - Fecha: {fecha}, Cliente: {lugar}, Nombre: {nombre}")
                    
                    # Crear nuevo nombre
                    nombreSinFormato = f"{fecha} - {lugar} - {nombre}.pdf".strip()
                    nuevo_nombre = nombreSinFormato.upper()
                    
                    # Limpieza segura para nombres de archivo
                    nuevo_nombre = "".join(c for c in nuevo_nombre 
                                          if c.isprintable() and c not in {'\\', ':', '*', '?', '"', '<', '>', '|'})
                    nuevo_nombre = nuevo_nombre.replace('/', '-')
                    
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
                    self.log(f"✅ Renombrado a: {nuevo_nombre}")
                    
                except Exception as e:
                    self.log(f"❌ Error procesando {archivo}: {str(e)}")

    # ================= FUNCIONES DE CREACIÓN DE CARPETAS =================
    def crear_carpetas_desde_lista(self, lineas):
        """Crea carpetas a partir de una lista de textos"""
        self.log("📂 Creando carpetas...")
        
        for linea in lineas:
            try:
                destino, chofer = map(str.strip, linea.split("-", 1))
                ruta_carpeta = os.path.join(RUTA_BASE_CREAR, destino, chofer)
                os.makedirs(ruta_carpeta, exist_ok=True)
                self.log(f"✅ {destino}/{chofer}")
            except ValueError:
                self.log(f"❌ Error en formato: '{linea}'. Usa 'Destino - Chofer'")
        
        self.log("\n¡Todas las carpetas fueron creadas!")

    # ================= FUNCIONES DE ORGANIZACIÓN =================
    def normalizar_nombre(self, nombre):
        """Normaliza el nombre para comparación"""
        return re.sub(r'\s+', ' ', nombre.strip()).upper()

    def extraer_fecha_desde_nombre(self, nombre_archivo):
        """Extrae fecha del nombre del archivo"""
        try:
            fecha_match = re.search(r'(\d{1,2})-(\d{1,2})-(\d{4})', nombre_archivo)
            if fecha_match:
                dia = int(fecha_match.group(1))
                mes = int(fecha_match.group(2))
                año = int(fecha_match.group(3))
                return datetime(año, mes, dia)
        except:
            pass
        return None

    def obtener_nombre_mes(self, fecha):
        """Obtiene el nombre del mes en español"""
        meses = {
            1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
            5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
            9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
        }
        return meses.get(fecha.month, "")

    def obtener_nombre_dia_semana(self, fecha):
        """Obtiene el nombre del día de la semana en español"""
        dias = {
            0: "LUNES", 1: "MARTES", 2: "MIERCOLES", 3: "JUEVES",
            4: "VIERNES", 5: "SABADO", 6: "DOMINGO"
        }
        return dias.get(fecha.weekday(), "")

    def determinar_empresa(self, destino):
        """Determina la empresa basándose en el prefijo del destino"""
        if destino.upper().startswith("MM"):
            return "MULTIMAX"
        elif destino.upper().startswith("CLX"):
            return "CLX"
        else:
            return None

    def construir_ruta_base(self, fecha, destino):
        """Construye la ruta base según la fecha y el destino"""
        empresa = self.determinar_empresa(destino)
        if not empresa:
            return None
        
        año = fecha.year
        mes_numero = fecha.month
        mes_nombre = self.obtener_nombre_mes(fecha)
        
        return os.path.join(
            RUTA_BASE,
            empresa,
            str(año),
            f"{mes_numero} - {mes_nombre}"
        )

    def encontrar_carpeta_semana(self, ruta_base, fecha):
        """Encuentra la carpeta de semana correspondiente a una fecha"""
        if not fecha or not os.path.exists(ruta_base):
            return None
            
        for item in os.listdir(ruta_base):
            if "SEMANA" in item.upper():
                semana_match = re.search(r'(\d{1,2})\s*(\d{1,2}).*?(\d{1,2})\s*(\d{1,2}).*?(\d{4})', item)
                if semana_match:
                    try:
                        dia_inicio = int(semana_match.group(1))
                        mes_inicio = int(semana_match.group(2))
                        dia_fin = int(semana_match.group(3))
                        mes_fin = int(semana_match.group(4))
                        año = int(semana_match.group(5))
                        
                        fecha_inicio = datetime(año, mes_inicio, dia_inicio)
                        fecha_fin = datetime(año, mes_fin, dia_fin)
                        
                        if fecha_inicio <= fecha <= fecha_fin:
                            return os.path.join(ruta_base, item)
                    except:
                        continue
        return None

    def encontrar_carpeta_dia(self, ruta_semana, fecha):
        """Encuentra la carpeta del día correspondiente a una fecha"""
        if not fecha or not os.path.exists(ruta_semana):
            return None
            
        nombre_dia_esperado = f"{fecha.day:02d} {self.obtener_nombre_dia_semana(fecha)}"
        
        for item in os.listdir(ruta_semana):
            if self.normalizar_nombre(item) == self.normalizar_nombre(nombre_dia_esperado):
                return os.path.join(ruta_semana, item)
        
        return None

    def encontrar_carpeta_destino(self, ruta_dia, destino):
        """Encuentra la carpeta de destino dentro de la carpeta del día"""
        if not destino or not os.path.exists(ruta_dia):
            return None
            
        for item in os.listdir(ruta_dia):
            if self.normalizar_nombre(item) == self.normalizar_nombre(destino):
                return os.path.join(ruta_dia, item)
        
        return None

    def encontrar_carpeta_conductor(self, ruta_destino, conductor):
        """Encuentra la carpeta del conductor dentro de la carpeta de destino"""
        if not conductor or not os.path.exists(ruta_destino):
            return None
            
        for item in os.listdir(ruta_destino):
            if self.normalizar_nombre(item) == self.normalizar_nombre(conductor):
                return os.path.join(ruta_destino, item)
        
        return None

    # ================= FUNCIONES DE TRELLO =================
    def obtener_id_tablero_por_nombre(self, nombre_tablero):
        """Obtiene el ID de un tablero por su nombre"""
        url = f"https://api.trello.com/1/members/me/boards?key={TRELLO_API_KEY}&token={TRELLO_TOKEN}"
        response = requests.get(url)
        
        if response.status_code == 200:
            boards = response.json()
            for board in boards:
                if nombre_tablero.upper() in board['name'].upper():
                    return board['id']
        return None

    def obtener_listas_tablero(self, tablero_id):
        """Obtiene todas las listas de un tablero"""
        url = f"https://api.trello.com/1/boards/{tablero_id}/lists?key={TRELLO_API_KEY}&token={TRELLO_TOKEN}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        return []

    def obtener_tarjetas_lista(self, lista_id):
        """Obtiene todas las tarjetas de una lista"""
        url = f"https://api.trello.com/1/lists/{lista_id}/cards?key={TRELLO_API_KEY}&token={TRELLO_TOKEN}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        return []

    def obtener_checklists_tarjeta(self, tarjeta_id):
        """Obtiene los checklists de una tarjeta"""
        url = f"https://api.trello.com/1/cards/{tarjeta_id}/checklists?key={TRELLO_API_KEY}&token={TRELLO_TOKEN}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        return []

    def marcar_item_checklist_completo(self, idCard, idCheckItem):
        """Marca un item de checklist como completo"""
        url = f"https://api.trello.com/1/cards/{idCard}/checkItem/{idCheckItem}?key={TRELLO_API_KEY}&token={TRELLO_TOKEN}"
        data = {'state': 'complete'}
        
        try:
            response = requests.put(url, json=data, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                self.log(f"  ❌ Error HTTP al marcar item: {response.status_code}")
                self.log(f"  ❌ Respuesta del servidor: {response.text}")
                return False
        except Exception as e:
            self.log(f"  ❌ Excepción al marcar item: {str(e)}")
            return False

    def normalizar_texto_trello(self, texto):
        """Normaliza texto para comparación con items de Trello"""
        texto = texto.upper().strip()
        texto = re.sub(r'\s+', ' ', texto)
        texto = re.sub(r'[^\w\s-]', '', texto)
        return texto

    def encontrar_item_checklist(self, checklists, nombre_buscado):
        """Encuentra un item en los checklists con coincidencia flexible"""
        nombre_buscado_normalizado = self.normalizar_texto_trello(nombre_buscado)
        
        for checklist in checklists:
            for item in checklist['checkItems']:
                item_normalizado = self.normalizar_texto_trello(item['name'])
                
                if nombre_buscado_normalizado == item_normalizado:
                    return checklist, item
                
                if (nombre_buscado_normalizado in item_normalizado or 
                    item_normalizado in nombre_buscado_normalizado):
                    return checklist, item
        
        return None, None

    def encontrar_lista_por_fecha(self, listas, fecha):
        """Encuentra la lista correcta basándose en la fecha del PDF"""
        for lista in listas:
            nombre_lista = lista['name'].upper()
            
            patrones = [
                r'(\d{1,2})\s*(\d{1,2})\s*AL\s*(\d{1,2})\s*(\d{1,2})\s*(\d{4})',
                r'(\d{1,2})[/-](\d{1,2})\s*AL\s*(\d{1,2})[/-](\d{1,2})\s*(\d{4})',
                r'(\d{1,2})\s*(\d{1,2})\s*-\s*(\d{1,2})\s*(\d{1,2})\s*(\d{4})'
            ]
            
            for patron in patrones:
                match = re.search(patron, nombre_lista)
                if match:
                    try:
                        dia_inicio = int(match.group(1))
                        mes_inicio = int(match.group(2))
                        dia_fin = int(match.group(3))
                        mes_fin = int(match.group(4))
                        año = int(match.group(5))
                        
                        fecha_inicio = datetime(año, mes_inicio, dia_inicio)
                        fecha_fin = datetime(año, mes_fin, dia_fin)
                        
                        if fecha_inicio <= fecha <= fecha_fin:
                            return lista
                            
                    except (ValueError, IndexError):
                        continue
        
        for lista in listas:
            nombre_lista = lista['name'].upper()
            
            if any(str(x) in nombre_lista for x in [fecha.day, fecha.month, fecha.year]):
                anyo_match = re.search(r'(\d{4})', nombre_lista)
                if anyo_match and int(anyo_match.group(1)) == fecha.year:
                    return lista
                    
        return None

    def encontrar_tarjeta_por_fecha(self, tarjetas, fecha):
        """Encuentra la tarjeta correcta basándose en la fecha del PDF"""
        nombre_dia = fecha.strftime('%A').upper()
        
        dias_espanol = {
            'MONDAY': 'LUNES',
            'TUESDAY': 'MARTES',
            'WEDNESDAY': 'MIERCOLES',
            'THURSDAY': 'JUEVES',
            'FRIDAY': 'VIERNES',
            'SATURDAY': 'SABADO',
            'SUNDAY': 'DOMINGO'
        }
        
        nombre_dia_espanol = dias_espanol.get(nombre_dia, nombre_dia)
        
        nombres_posibles = [
            f"{fecha.day} {nombre_dia_espanol}",
            f"{fecha.day:02d} {nombre_dia_espanol}",
            f"{fecha.day}/{fecha.month} {nombre_dia_espanol}",
            f"{fecha.day}-{fecha.month} {nombre_dia_espanol}"
        ]
        
        for tarjeta in tarjetas:
            nombre_tarjeta = tarjeta['name'].upper()
            for nombre_posible in nombres_posibles:
                if nombre_posible.upper() in nombre_tarjeta:
                    return tarjeta
                    
        for tarjeta in tarjetas:
            nombre_tarjeta = tarjeta['name'].upper()
            if str(fecha.day) in nombre_tarjeta and any(dia in nombre_tarjeta for dia in ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']):
                return tarjeta
                
        return None

    def tildar_en_trello(self, destino, nombre_conductor, fecha):
        """Busca y marca el item correspondiente en Trello"""
        try:
            self.log(f"  📅 Buscando lista para la fecha: {fecha.strftime('%d/%m/%Y')}")
            
            tablero_id = self.obtener_id_tablero_por_nombre(NOMBRE_TABLERO_TRELLO)
            if not tablero_id:
                self.log("  ❌ No se encontró el tablero en Trello")
                return False
            
            listas = self.obtener_listas_tablero(tablero_id)
            if not listas:
                self.log("  ❌ No se encontraron listas en el tablero")
                return False
                
            lista_obj = self.encontrar_lista_por_fecha(listas, fecha)
            
            if not lista_obj:
                self.log(f"  ❌ No se encontró lista para la fecha: {fecha.strftime('%d/%m/%Y')}")
                self.log("  Listas disponibles:")
                for lista in listas:
                    self.log(f"    - {lista['name']}")
                return False
            
            self.log(f"  ✅ Lista encontrada: {lista_obj['name']}")
            
            tarjetas = self.obtener_tarjetas_lista(lista_obj['id'])
            if not tarjetas:
                self.log("  ❌ No se encontraron tarjetas en la lista")
                return False
                
            tarjeta_obj = self.encontrar_tarjeta_por_fecha(tarjetas, fecha)
            
            if not tarjeta_obj:
                self.log(f"  ❌ No se encontró tarjeta para la fecha: {fecha.strftime('%d/%m/%Y')}")
                self.log("  Tarjetas disponibles en la lista:")
                for tarjeta in tarjetas:
                    self.log(f"    - {tarjeta['name']}")
                return False
                
            self.log(f"  ✅ Tarjeta encontrada: {tarjeta_obj['name']}")
            
            nombre_buscado = f"{destino} - {nombre_conductor}"
            checklists = self.obtener_checklists_tarjeta(tarjeta_obj['id'])
            
            if not checklists:
                self.log("  ❌ No se encontraron checklists en la tarjeta")
                return False
            
            checklist_obj, item_obj = self.encontrar_item_checklist(checklists, nombre_buscado)
            
            if not item_obj:
                self.log(f"  ❌ No se encontró item en el checklist para: {nombre_buscado}")
                self.log("  Items disponibles en el checklist:")
                for checklist in checklists:
                    for item in checklist['checkItems']:
                        estado = "✅" if item['state'] == 'complete' else "❌"
                        self.log(f"    {estado} {item['name']} (Normalizado: {self.normalizar_texto_trello(item['name'])})")
                return False
            
            if item_obj['state'] == 'complete':
                self.log(f"  ℹ️ El item ya estaba completado: {item_obj['name']}")
                return True
            
            self.log(f"  🎯 Intentando marcar item: {item_obj['name']} (ID: {item_obj['id']})")
            if self.marcar_item_checklist_completo(tarjeta_obj['id'], item_obj['id']):
                self.log(f"  ✅ Item marcado como completo en Trello: {item_obj['name']}")
                return True
            else:
                self.log(f"  ❌ Error al marcar el item como completo: {item_obj['name']}")
                return False
            
        except Exception as e:
            self.log(f"  ❌ Error al conectar con Trello: {e}")
            return False

    def organizar_pdfs_completo(self):
        """Función principal de organización de PDFs"""
        if not os.path.exists(CARPETA_PDFS):
            self.log(f"❌ Error: No existe la carpeta de PDFs: {CARPETA_PDFS}")
            return
            
        if not os.path.exists(RUTA_BASE):
            self.log(f"❌ Error: No se puede acceder a la ruta compartida: {RUTA_BASE}")
            self.log("   Verifica la conexión de red y los permisos de acceso.")
            return

        for archivo in os.listdir(CARPETA_PDFS):
            if not archivo.lower().endswith('.pdf'):
                continue
                
            ruta_pdf = os.path.join(CARPETA_PDFS, archivo)
            
            try:
                partes = archivo.split(' - ')
                if len(partes) < 3:
                    self.log(f"❌ Formato incorrecto: {archivo}")
                    continue
                    
                fecha_archivo = self.extraer_fecha_desde_nombre(archivo)
                destino_archivo = partes[1].strip()
                nombre_archivo = ' - '.join(partes[2:])
                nombre_archivo = os.path.splitext(nombre_archivo)[0].strip()
                
                self.log(f"\nProcesando: {archivo}")
                self.log(f"  Fecha: {fecha_archivo}")
                self.log(f"  Destino: {destino_archivo}")
                self.log(f"  Nombre: {nombre_archivo}")
                
                if not fecha_archivo:
                    self.log(f"  ❌ No se pudo extraer la fecha del archivo")
                    continue
                
                ruta_base_empresa = self.construir_ruta_base(fecha_archivo, destino_archivo)
                if not ruta_base_empresa:
                    self.log(f"  ❌ No se pudo determinar la empresa para el destino: {destino_archivo}")
                    continue
                    
                if not os.path.exists(ruta_base_empresa):
                    self.log(f"  ❌ No se encuentra la ruta: {ruta_base_empresa}")
                    continue
                    
                carpeta_semana = self.encontrar_carpeta_semana(ruta_base_empresa, fecha_archivo)
                if not carpeta_semana:
                    self.log(f"  ❌ No se encontró carpeta de semana para la fecha: {fecha_archivo}")
                    continue
                    
                carpeta_dia = self.encontrar_carpeta_dia(carpeta_semana, fecha_archivo)
                if not carpeta_dia:
                    self.log(f"  ❌ No se encontró carpeta de día para la fecha: {fecha_archivo}")
                    continue
                    
                carpeta_destino = self.encontrar_carpeta_destino(carpeta_dia, destino_archivo)
                if not carpeta_destino:
                    self.log(f"  ❌ No se encontró carpeta de destino para: {destino_archivo}")
                    continue
                    
                carpeta_conductor = self.encontrar_carpeta_conductor(carpeta_destino, nombre_archivo)
                if not carpeta_conductor:
                    self.log(f"  ❌ No se encontró carpeta del conductor para: {nombre_archivo}")
                    continue
                    
                nuevo_path = os.path.join(carpeta_conductor, archivo)
                
                counter = 1
                while os.path.exists(nuevo_path):
                    nombre_base, extension = os.path.splitext(archivo)
                    nuevo_nombre = f"{nombre_base} ({counter}){extension}"
                    nuevo_path = os.path.join(carpeta_conductor, nuevo_nombre)
                    counter += 1
                    
                shutil.move(ruta_pdf, nuevo_path)
                self.log(f"  ✅ Movido a: {carpeta_conductor}")
                
                self.tildar_en_trello(destino_archivo, nombre_archivo, fecha_archivo)
                
            except Exception as e:
                self.log(f"  ❌ Error procesando {archivo}: {str(e)}")

# ================= INICIO DE LA APLICACIÓN =================
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFOrganizerApp(root)
    root.mainloop()