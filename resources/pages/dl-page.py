from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize, QUrl, QRect, QDateTime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QListWidget, QListWidgetItem, 
                              QFrame, QMessageBox, QDialog, QProgressBar, 
                              QFileDialog, QApplication, QGroupBox,
                              QTextEdit, QLineEdit, QComboBox, QScrollArea,
                              QGridLayout, QSplitter, QScrollBar, QStyleFactory,
                              QRadioButton, QButtonGroup, QSizePolicy, QListWidgetItem)
from PySide6.QtGui import QPixmap, QFont, QFontDatabase, QDesktopServices, QPainter, QBrush, QColor
from pathlib import Path
import requests
import json
import os
import tempfile
import zipfile
import shutil
from io import BytesIO
from typing import Optional, List, Dict
from functools import lru_cache
import hashlib
import concurrent.futures

# ============================================================================
# CONFIGURACIÓN DE API
# ============================================================================

API_KEY = "$2a$10$8KaEt5p8ojzaXBd4.sUr/.eeWmsUytrNv3iNeVkK92oqtTbGFzKQC"
GAME_ID = 78022  # Minecraft Bedrock
HEADERS = {
    'Accept': 'application/json',
    'x-api-key': API_KEY
}

# Categorías de CurseForge
CATEGORIES = {
    "addons": {"id": 4984, "name": "Addons (Behavior/Resource Packs)", "icon": "🧩"},
    "maps": {"id": 6913, "name": "Maps (Mundos)", "icon": "🗺️"},
    "textures": {"id": 6929, "name": "Texture Packs", "icon": "🎨"},
    "scripts": {"id": 6940, "name": "Scripts", "icon": "📜"}
}

# Directorios de destino
GAMES_DIR = Path.home() / ".local" / "share" / "mcpelauncher" / "games" / "com.mojang"
DOWNLOAD_DIR = Path.home() / ".local" / "share" / "boxcraft" / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Cache para imágenes
IMAGE_CACHE = {}
executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

class ImageLoader:
    @staticmethod
    def load_from_url_async(url, callback):
        """Carga imagen desde URL de forma asíncrona"""
        if not url:
            callback(None)
            return
        
        cache_key = hashlib.md5(url.encode()).hexdigest()
        if cache_key in IMAGE_CACHE:
            callback(IMAGE_CACHE[cache_key])
            return
        
        def load_task():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    if not pixmap.isNull():
                        IMAGE_CACHE[cache_key] = pixmap
                        callback(pixmap)
                    else:
                        callback(None)
                else:
                    callback(None)
            except:
                callback(None)
        
        executor.submit(load_task)

# ============================================================================
# HILOS PARA OPERACIONES EN SEGUNDO PLANO
# ============================================================================

class SearchThread(QThread):
    """Hilo para buscar mods en CurseForge"""
    search_finished = Signal(list)
    search_error = Signal(str)
    
    def __init__(self, query, category_id, page_index=0):
        super().__init__()
        self.query = query
        self.category_id = category_id
        self.page_index = page_index
    
    def run(self):
        try:
            url = "https://api.curseforge.com/v1/mods/search"
            params = {
                'gameId': GAME_ID,
                'classId': self.category_id,
                'searchFilter': self.query,
                'sortField': 2,  # Popularidad
                'sortOrder': 'desc',
                'pageSize': 13,  # 13 resultados por página
                'index': self.page_index * 13  # Para paginación
            }
            
            response = requests.get(url, headers=HEADERS, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                self.search_finished.emit(data)
            else:
                self.search_error.emit(f"Error API: {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.search_error.emit("Tiempo de espera agotado")
        except requests.exceptions.ConnectionError:
            self.search_error.emit("Error de conexión")
        except Exception as e:
            self.search_error.emit(f"Error inesperado: {str(e)}")

class FilesFetchThread(QThread):
    """Hilo para obtener archivos disponibles de un mod"""
    files_fetched = Signal(list)
    files_error = Signal(str)
    
    def __init__(self, mod_id):
        super().__init__()
        self.mod_id = mod_id
    
    def run(self):
        try:
            url = f"https://api.curseforge.com/v1/mods/{self.mod_id}/files"
            params = {
                'pageSize': 15,  # Obtener hasta 15 archivos (reducido para mejor rendimiento)
                'sortDescending': True  # Los más recientes primero
            }
            
            response = requests.get(url, headers=HEADERS, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                self.files_fetched.emit(data)
            else:
                self.files_error.emit(f"Error al obtener archivos: {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.files_error.emit("Tiempo de espera agotado")
        except requests.exceptions.ConnectionError:
            self.files_error.emit("Error de conexión")
        except Exception as e:
            self.files_error.emit(f"Error inesperado: {str(e)}")

class DownloadThread(QThread):
    """Hilo para descargar archivos"""
    download_progress = Signal(int)
    download_finished = Signal(str, str, bytes)  # nombre, tipo, contenido
    download_error = Signal(str)
    
    def __init__(self, mod_id, file_id, file_name, file_type):
        super().__init__()
        self.mod_id = mod_id
        self.file_id = file_id
        self.file_name = file_name
        self.file_type = file_type
    
    def run(self):
        try:
            # Descargar archivo específico
            download_url = f"https://api.curseforge.com/v1/mods/{self.mod_id}/files/{self.file_id}/download"
            response = requests.get(download_url, headers=HEADERS, timeout=30, stream=True)
            
            if response.status_code != 200:
                # Intentar obtener información del archivo para usar downloadUrl directo
                url = f"https://api.curseforge.com/v1/mods/{self.mod_id}/files/{self.file_id}"
                file_response = requests.get(url, headers=HEADERS, timeout=15)
                
                if file_response.status_code == 200:
                    file_info = file_response.json().get('data', {})
                    if 'downloadUrl' in file_info and file_info['downloadUrl']:
                        response = requests.get(file_info['downloadUrl'], stream=True, timeout=30)
                    else:
                        self.download_error.emit("No se puede descargar este archivo")
                        return
                else:
                    self.download_error.emit(f"Error al obtener información del archivo: {file_response.status_code}")
                    return
            
            # Leer contenido
            content = BytesIO()
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    content.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = int((downloaded / total_size) * 100)
                        self.download_progress.emit(progress)
            
            self.download_finished.emit(self.file_name, self.file_type, content.getvalue())
            
        except Exception as e:
            self.download_error.emit(f"Error en descarga: {str(e)}")

# ============================================================================
# WIDGETS PERSONALIZADOS
# ============================================================================

class FileItemWidget(QWidget):
    """Widget para mostrar información de un archivo disponible con botón de descarga"""
    download_clicked = Signal(dict)  # Emite los datos del archivo cuando se hace click en descargar
    
    def __init__(self, file_data, mod_data):
        super().__init__()
        self.file_data = file_data
        self.mod_data = mod_data
        self.setup_ui()
        
        # Establecer tamaño mínimo
        self.setMinimumHeight(80)
        self.setMaximumHeight(100)
        self.update_style()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        
        # Contenedor izquierdo: Información del archivo
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(3)
        
        # Nombre del archivo (truncado si es muy largo)
        file_name = self.file_data.get('fileName', 'Archivo sin nombre')
        if len(file_name) > 40:
            display_name = file_name[:37] + "..."
        else:
            display_name = file_name
            
        name_label = QLabel(display_name)
        name_label.setObjectName("FileName")
        name_label.setStyleSheet("""
            QLabel#FileName {
                font-size: 13px;
                font-weight: bold;
                color: white;
            }
        """)
        name_label.setWordWrap(True)
        name_label.setToolTip(file_name)
        info_layout.addWidget(name_label)
        
        # Información adicional
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(8)
        
        # Versión del juego
        game_versions = self.file_data.get('gameVersions', [])
        version_text = game_versions[0] if game_versions else "Desconocido"
        version_label = QLabel(f"🎮 {version_text}")
        version_label.setObjectName("FileVersion")
        version_label.setStyleSheet("""
            QLabel#FileVersion {
                font-size: 11px;
                color: #888888;
            }
        """)
        meta_layout.addWidget(version_label)
        
        # Tamaño del archivo
        file_size = self.file_data.get('fileLength', 0)
        if file_size > 0:
            size_mb = file_size / (1024 * 1024)
            size_label = QLabel(f"📦 {size_mb:.1f} MB")
            size_label.setObjectName("FileSize")
            size_label.setStyleSheet("""
                QLabel#FileSize {
                    font-size: 11px;
                    color: #888888;
                }
            """)
            meta_layout.addWidget(size_label)
        
        # Fecha de lanzamiento
        release_date = self.file_data.get('fileDate', '')
        if release_date:
            date_label = QLabel(f"📅 {release_date[:10]}")
            date_label.setObjectName("FileDate")
            date_label.setStyleSheet("""
                QLabel#FileDate {
                    font-size: 11px;
                    color: #888888;
                }
            """)
            meta_layout.addWidget(date_label)
        
        meta_layout.addStretch()
        info_layout.addLayout(meta_layout)
        
        # Tipo de archivo
        file_type = self.determine_file_type(self.file_data.get('fileName', ''))
        type_label = QLabel(f"📄 {file_type}")
        type_label.setObjectName("FileType")
        type_label.setStyleSheet("""
            QLabel#FileType {
                font-size: 11px;
                color: #888888;
                font-style: italic;
            }
        """)
        info_layout.addWidget(type_label)
        
        layout.addWidget(info_container, 1)  # Peso 1 para que ocupe espacio disponible
        
        # Botón de descarga a la derecha
        download_btn = QPushButton("⬇️")
        download_btn.setObjectName("FileDownloadButton")
        download_btn.setFixedSize(40, 40)
        download_btn.setToolTip("Descargar e instalar esta versión")
        download_btn.setCursor(Qt.PointingHandCursor)
        download_btn.setStyleSheet("""
            QPushButton#FileDownloadButton {
                background-color: #4CAF50;
                border: 1px solid #3D8B40;
                border-radius: 6px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                qproperty-alignment: 'AlignCenter';
            }
            QPushButton#FileDownloadButton:hover {
                background-color: #5DBB63;
                border: 1px solid #4CAF50;
            }
            QPushButton#FileDownloadButton:pressed {
                background-color: #3D8B40;
                border: 1px solid #2D7B30;
            }
            QPushButton#FileDownloadButton:disabled {
                background-color: #555555;
                color: #888888;
                border: 1px solid #666666;
            }
        """)
        download_btn.clicked.connect(self.on_download_clicked)
        layout.addWidget(download_btn)
    
    def determine_file_type(self, filename):
        """Determina el tipo de archivo basado en la extensión"""
        filename_lower = filename.lower()
        if filename_lower.endswith('.mcpack'):
            return "Minecraft Pack"
        elif filename_lower.endswith('.mcaddon'):
            return "Minecraft Addon"
        elif filename_lower.endswith('.mcworld'):
            return "Minecraft World"
        elif filename_lower.endswith('.zip'):
            return "Archivo ZIP"
        elif filename_lower.endswith('.txt') or filename_lower.endswith('.md'):
            return "Documentación"
        return "Archivo"
    
    def on_download_clicked(self):
        """Maneja clic en el botón de descarga"""
        # Combinar datos del mod y del archivo
        mod_data_with_file = self.mod_data.copy()
        mod_data_with_file['selected_file'] = self.file_data
        self.download_clicked.emit(mod_data_with_file)
    
    def update_style(self):
        """Actualiza el estilo del widget"""
        self.setStyleSheet("""
            FileItemWidget {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
                margin: 2px;
            }
            FileItemWidget:hover {
                background-color: #353535;
                border: 1px solid #4CAF50;
            }
        """)

class ModItemWidget(QWidget):
    """Widget personalizado para mostrar un mod en la lista"""
    clicked = Signal(dict)  # Emite los datos del mod cuando se hace click
    
    def __init__(self, mod_data):
        super().__init__()
        self.mod_data = mod_data
        self.is_selected_flag = False
        self.setup_ui()
        
        # Hacer que todo el widget sea clickeable
        self.setCursor(Qt.PointingHandCursor)
        
        # Establecer tamaño fijo (aumentado para mejor visualización)
        self.setFixedHeight(70)  # Aumentado de 60 a 70
        
        # Estilo base sin selección
        self.update_style()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)  # Aumentado padding vertical
        layout.setSpacing(10)
        
        # Icono basado en categoría
        icon_label = QLabel(self.get_category_icon())
        icon_label.setFixedSize(40, 40)
        icon_label.setObjectName("ModIcon")
        icon_label.setStyleSheet("""
            QLabel#ModIcon {
                font-size: 20px;
                padding: 5px;
                background-color: #2d2d2d;
                border-radius: 8px;
                qproperty-alignment: 'AlignCenter';
            }
        """)
        layout.addWidget(icon_label)
        
        # Solo nombre del mod con limitación de líneas
        name_label = QLabel(self.get_truncated_name(self.mod_data['name']))
        name_label.setObjectName("ModName")
        name_label.setStyleSheet("""
            QLabel#ModName {
                font-size: 13px;  # Reducido de 14px
                font-weight: bold;
                color: white;
                max-height: 40px;
            }
        """)
        name_label.setWordWrap(True)
        name_label.setMaximumWidth(280)
        name_label.setMaximumHeight(40)  # Limitar altura para 2 líneas
        name_label.setToolTip(self.mod_data['name'])  # Tooltip con nombre completo
        layout.addWidget(name_label, 1)
        
        layout.addStretch()
    
    def get_truncated_name(self, full_name):
        """Trunca el nombre si es muy largo para mostrar máximo 2 líneas"""
        if len(full_name) <= 40:
            return full_name
        
        # Truncar para aproximadamente 2 líneas (40-50 caracteres)
        truncated = full_name[:47]
        if len(full_name) > 47:
            truncated += "..."
        return truncated
    
    def get_category_icon(self):
        """Obtiene icono basado en la categoría"""
        category_id = self.mod_data.get('classId', 0)
        for cat_key, cat_info in CATEGORIES.items():
            if cat_info['id'] == category_id:
                return cat_info['icon']
        return "📦"
    
    def emit_click(self):
        self.clicked.emit(self.mod_data)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Cambiar el estilo inmediatamente al hacer clic
            self.set_selected(True)
            self.emit_click()
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def update_style(self):
        """Actualiza el estilo basado en la selección - enfoque alternativo"""
        palette = self.palette()
        
        if self.is_selected_flag:
            # Colores para selección
            palette.setColor(self.backgroundRole(), QColor("#1e3a1e"))
            palette.setColor(self.foregroundRole(), QColor("#FFFFFF"))
        else:
            # Colores normales
            palette.setColor(self.backgroundRole(), QColor("#252525"))
            palette.setColor(self.foregroundRole(), QColor("#FFFFFF"))
        
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        # Aplicar borde
        if self.is_selected_flag:
            self.setStyleSheet("border: 2px solid #4CAF50; border-radius: 8px; margin: 2px;")
        else:
            self.setStyleSheet("border: 1px solid #3d3d3d; border-radius: 8px; margin: 2px;")
    
    def set_selected(self, selected):
        """Establece el estado de selección"""
        self.is_selected_flag = selected
        self.update_style()
        # Forzar repintado
        self.update()

class ModDetailWidget(QWidget):
    """Widget para mostrar detalles completos de un mod"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_mod = None
        self.current_files = []
        self.files_fetch_thread = None
        self.main_window = None
        self.file_widgets = []
        self.is_loading = False
    
    def setup_ui(self):
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # ============= CONTENIDO PRINCIPAL CON SCROLL ÚNICO =============
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)
        
        # Widget de contenido principal
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 10, 0)  # Margen derecho para la scrollbar
        content_layout.setSpacing(15)
        
        # Encabezado con nombre
        self.name_label = QLabel()
        self.name_label.setObjectName("DetailTitle")
        self.name_label.setStyleSheet("""
            QLabel#DetailTitle {
                font-size: 18px;
                font-weight: bold;
                color: #4CAF50;
                margin-bottom: 5px;
            }
        """)
        self.name_label.setWordWrap(True)
        content_layout.addWidget(self.name_label)
        
        # Autor y versión
        self.meta_label = QLabel()
        self.meta_label.setObjectName("DetailMeta")
        self.meta_label.setStyleSheet("""
            QLabel#DetailMeta {
                color: #888888; 
                font-size: 12px;
            }
        """)
        self.meta_label.setWordWrap(True)
        content_layout.addWidget(self.meta_label)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #2d2d2d; margin: 5px 0;")
        content_layout.addWidget(separator)
        
        # Imagen del mod
        self.image_container = QWidget()
        image_layout = QVBoxLayout(self.image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = QLabel()
        self.image_label.setMinimumHeight(150)
        self.image_label.setMaximumHeight(200)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setObjectName("DetailImage")
        self.image_label.setStyleSheet("""
            QLabel#DetailImage {
                border: 2px solid #2d2d2d;
                border-radius: 8px;
                background-color: #1e1e1e;
            }
        """)
        image_layout.addWidget(self.image_label)
        content_layout.addWidget(self.image_container)
        
        # Descripción
        self.description_label = QLabel()
        self.description_label.setObjectName("DetailDescription")
        self.description_label.setStyleSheet("""
            QLabel#DetailDescription {
                color: #cccccc;
                font-size: 13px;
                line-height: 140%;
            }
        """)
        self.description_label.setWordWrap(True)
        self.description_label.setTextFormat(Qt.RichText)
        self.description_label.setOpenExternalLinks(True)
        content_layout.addWidget(self.description_label)
        
        # Sección para archivos disponibles (SIN scroll interna)
        self.files_section = QWidget()
        files_layout = QVBoxLayout(self.files_section)
        files_layout.setContentsMargins(0, 10, 0, 0)
        
        files_title = QLabel("📁 Versiones disponibles:")
        files_title.setObjectName("FilesTitle")
        files_title.setStyleSheet("""
            QLabel#FilesTitle {
                font-size: 14px;
                font-weight: bold;
                color: #4CAF50;
                margin-bottom: 8px;
            }
        """)
        files_layout.addWidget(files_title)
        
        # Contenedor para los widgets de archivos (SIN scroll interna)
        self.files_container = QWidget()
        self.files_container_layout = QVBoxLayout(self.files_container)
        self.files_container_layout.setContentsMargins(0, 0, 0, 0)
        self.files_container_layout.setSpacing(10)
        
        # Añadir el contenedor de archivos directamente (sin QScrollArea)
        files_layout.addWidget(self.files_container)
        
        # Label para estado de carga de archivos
        self.files_status_label = QLabel()
        self.files_status_label.setObjectName("FilesStatus")
        self.files_status_label.setStyleSheet("""
            QLabel#FilesStatus {
                color: #888888;
                font-size: 12px;
                font-style: italic;
            }
        """)
        self.files_status_label.setAlignment(Qt.AlignCenter)
        files_layout.addWidget(self.files_status_label)
        
        content_layout.addWidget(self.files_section)
        content_layout.addStretch(1)
        
        # Establecer el widget de contenido en el scroll principal
        main_scroll.setWidget(content_widget)
        layout.addWidget(main_scroll, 1)
        # ==============================================================
        
        # Botón para ver en CurseForge (FUERA del scroll)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.view_website_btn = QPushButton("🌐 Ver en CurseForge")
        self.view_website_btn.setObjectName("SecondaryButton")
        self.view_website_btn.setFixedHeight(40)
        self.view_website_btn.setStyleSheet("""
            QPushButton#SecondaryButton {
                background-color: #4A86E8;
                border: 2px solid #3A75D4;
                border-radius: 6px;
                color: white;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton#SecondaryButton:hover {
                background-color: #5D9CFA;
                border: 2px solid #4A86E8;
            }
            QPushButton#SecondaryButton:pressed {
                background-color: #3A75D4;
                border: 2px solid #2A65C4;
            }
            QPushButton#SecondaryButton:disabled {
                background-color: #555555;
                color: #888888;
                border: 2px solid #666666;
            }
        """)
        self.view_website_btn.clicked.connect(self.open_website)
        
        button_layout.addWidget(self.view_website_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def load_mod_data(self, mod_data):
        """Carga los datos de un mod en el widget - NO BLOQUEANTE"""
        if self.is_loading:
            return
            
        self.is_loading = True
        self.current_mod = mod_data
        
        # Limpiar archivos anteriores primero
        self.clear_files_container()
        self.current_files = []
        
        # Nombre
        self.name_label.setText(mod_data['name'])
        
        # Metadatos (procesamiento simple y rápido)
        author = mod_data.get('authors', [{}])[0].get('name', 'Desconocido')
        downloads = f"{mod_data.get('downloadCount', 0):,}"
        meta_text = f"👤 {author} | ⬇️ {downloads}"
        self.meta_label.setText(meta_text)
        
        # Descripción (procesar de forma diferida)
        description = mod_data.get('summary', 'Sin descripción disponible.')
        # Usar timer para procesar la descripción sin bloquear
        QTimer.singleShot(10, lambda: self.set_description(description))
        
        # Cargar imagen de forma asíncrona
        logo_url = mod_data.get('logo', {}).get('url')
        if logo_url:
            self.load_image_async(logo_url)
        else:
            self.set_category_icon()
        
        # Configurar sección de archivos
        self.files_section.setVisible(False)
        self.files_status_label.setText("Cargando versiones...")
        self.view_website_btn.setEnabled(True)
        
        # Cargar archivos en segundo plano
        QTimer.singleShot(50, lambda: self.load_mod_files_async(mod_data['id']))
    
    def set_description(self, description):
        """Establece la descripción de forma segura"""
        try:
            html_description = self.markdown_to_html(description)
            self.description_label.setText(html_description)
        except:
            self.description_label.setText("<i>Error al cargar la descripción</i>")
    
    def load_image_async(self, url):
        """Carga imagen de forma asíncrona"""
        self.image_label.setText("🖼️ Cargando...")
        
        def on_image_loaded(pixmap):
            if pixmap and not pixmap.isNull():
                # Escalar manteniendo proporciones
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.set_category_icon()
        
        ImageLoader.load_from_url_async(url, on_image_loaded)
    
    def set_category_icon(self):
        """Establece el icono de categoría"""
        if self.current_mod:
            category_id = self.current_mod.get('classId', 0)
            for cat_info in CATEGORIES.values():
                if cat_info['id'] == category_id:
                    self.image_label.setText(cat_info['icon'])
                    self.image_label.setStyleSheet("""
                        QLabel#DetailImage {
                            border: 2px solid #2d2d2d;
                            border-radius: 8px;
                            background-color: #1e1e1e;
                            font-size: 48px;
                            qproperty-alignment: 'AlignCenter';
                        }
                    """)
                    return
        self.image_label.setText("📦")
    
    def load_mod_files_async(self, mod_id):
        """Carga archivos de forma asíncrona"""
        if self.files_fetch_thread and self.files_fetch_thread.isRunning():
            self.files_fetch_thread.terminate()
        
        self.files_fetch_thread = FilesFetchThread(mod_id)
        self.files_fetch_thread.files_fetched.connect(self.on_files_fetched)
        self.files_fetch_thread.files_error.connect(self.on_files_error)
        self.files_fetch_thread.finished.connect(lambda: self.set_loading_finished())
        self.files_fetch_thread.start()
    
    def set_loading_finished(self):
        """Marca que la carga ha terminado"""
        self.is_loading = False
    
    def clear_files_container(self):
        """Limpia el contenedor de archivos"""
        for widget in self.file_widgets:
            widget.deleteLater()
        self.file_widgets.clear()
        
        while self.files_container_layout.count():
            item = self.files_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def on_files_fetched(self, files):
        """Maneja archivos obtenidos exitosamente"""
        self.current_files = files
        
        if not files:
            self.files_status_label.setText("❌ No hay versiones disponibles")
            self.files_section.setVisible(True)
            self.set_loading_finished()
            return
        
        # Mostrar archivos disponibles
        self.files_section.setVisible(True)
        
        # Limpiar archivos anteriores
        self.clear_files_container()
        
        # Limitar a 10 archivos para mejor rendimiento
        display_files = files[:10]
        
        for file_data in display_files:
            file_widget = FileItemWidget(file_data, self.current_mod)
            file_widget.download_clicked.connect(self.on_file_download_clicked)
            self.files_container_layout.addWidget(file_widget)
            self.file_widgets.append(file_widget)
        
        if len(files) > 10:
            more_label = QLabel(f"... y {len(files) - 10} versiones más")
            more_label.setStyleSheet("color: #888888; font-size: 11px; font-style: italic;")
            more_label.setAlignment(Qt.AlignCenter)
            self.files_container_layout.addWidget(more_label)
        
        self.files_status_label.setText(f"✅ {len(files)} versión(es) disponible(s)")
        self.set_loading_finished()
    
    def on_files_error(self, error_msg):
        """Maneja errores al obtener archivos"""
        self.files_status_label.setText(f"❌ Error: {error_msg}")
        self.files_section.setVisible(True)
        self.set_loading_finished()
    
    def on_file_download_clicked(self, mod_data_with_file):
        """Maneja clic en el botón de descarga de un archivo"""
        start_download_mod(mod_data_with_file)
    
    def markdown_to_html(self, text):
        """Convierte Markdown básico a HTML de forma simple"""
        if not text:
            return "<i>Sin descripción disponible.</i>"
        
        try:
            # Solo reemplazos básicos
            text = text.replace('\n', '<br>')
            # Evitar procesamiento complejo que pueda bloquear
            return f'<div style="font-family: Arial, sans-serif;">{text}</div>'
        except:
            return f'<div style="font-family: Arial, sans-serif;">{text}</div>'
    
    def open_website(self):
        if self.current_mod:
            url = self.current_mod.get('links', {}).get('websiteUrl')
            if url:
                QDesktopServices.openUrl(QUrl(url))
            else:
                QMessageBox.information(self, "Información", "URL no disponible")

# ============================================================================
# PÁGINA PRINCIPAL DE DESCARGA
# ============================================================================

# Configurar layout de la página
layout = QVBoxLayout(page_widget)
layout.setContentsMargins(15, 15, 15, 15)
layout.setSpacing(10)

# Barra de búsqueda y filtros
search_container = QWidget()
search_layout = QHBoxLayout(search_container)
search_layout.setContentsMargins(0, 0, 0, 0)
search_layout.setSpacing(10)

# Campo de búsqueda
search_input = QLineEdit()
search_input.setPlaceholderText("Buscar mods, texturas, mundos...")
search_input.setMinimumHeight(35)
search_input.setMaximumHeight(35)
search_input.setObjectName("SearchInput")
search_input.setStyleSheet("""
    QLineEdit#SearchInput {
        background-color: #141414;
        border: 1px solid #2d2d2d;
        border-radius: 6px;
        padding: 8px 12px;
        color: white;
        font-size: 13px;
    }
    QLineEdit#SearchInput:focus {
        border: 1px solid #4CAF50;
    }
""")
search_layout.addWidget(search_input, 3)

# Selector de categoría
category_combo = QComboBox()
category_combo.setMinimumHeight(35)
category_combo.setMaximumHeight(35)
category_combo.setObjectName("CategoryCombo")

category_combo.setStyleSheet("""
    QComboBox#CategoryCombo {
        background-color: #141414;
        border: 1px solid #2d2d2d;
        border-radius: 6px;
        padding: 8px 12px;
        padding-right: 25px;
        color: white;
        font-size: 13px;
        min-width: 120px;
    }
    
    QComboBox#CategoryCombo:hover {
        border: 1px solid #4CAF50;
    }
    
    QComboBox#CategoryCombo QAbstractItemView {
        background-color: #141414;
        border: 1px solid #2d2d2d;
        color: white;
        selection-background-color: #2d2d2d;
    }
""")

# Añadir categorías
for key, cat_info in CATEGORIES.items():
    category_combo.addItem(f"{cat_info['icon']} {cat_info['name']}", cat_info['id'])

search_layout.addWidget(category_combo, 1)

# Botón de búsqueda
search_btn = QPushButton("🔍 Buscar")
search_btn.setObjectName("SearchButton")
search_btn.setMinimumHeight(35)
search_btn.setMaximumHeight(35)
search_btn.setMinimumWidth(100)
search_btn.setStyleSheet("""
    QPushButton#SearchButton {
        background-color: #4CAF50;
        border: 1px solid #3D8B40;
        border-radius: 6px;
        color: white;
        padding: 8px 16px;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton#SearchButton:hover {
        background-color: #5DBB63;
        border: 1px solid #4CAF50;
    }
    QPushButton#SearchButton:pressed {
        background-color: #3D8B40;
        border: 1px solid #2D7B30;
    }
""")
search_layout.addWidget(search_btn)

layout.addWidget(search_container)

# ==================== NUEVA SECCIÓN AÑADIDA ====================
# Mensaje informativo inicial
info_container = QWidget()
info_layout = QVBoxLayout(info_container)
info_layout.setContentsMargins(5, 5, 5, 5)

info_label = QLabel(
    "📝 Escribe en la barra de búsqueda y haz clic en 'Buscar' para encontrar mods, texturas y mundos.\n"
    "🔧 Utilizando la API oficial de CurseForge para obtener contenido actualizado."
)
info_label.setObjectName("InfoLabel")
info_label.setStyleSheet("""
    QLabel#InfoLabel {
        background-color: #2a2a2a;
        border: 1px solid #3a3a3a;
        border-radius: 8px;
        padding: 12px;
        color: #bbbbbb;
        font-size: 12px;
        line-height: 140%;
    }
""")
info_label.setWordWrap(True)
info_label.setAlignment(Qt.AlignCenter)
info_layout.addWidget(info_label)

layout.addWidget(info_container)
# ==================== FIN DE NUEVA SECCIÓN ====================

# Separador
separator = QFrame()
separator.setFrameShape(QFrame.HLine)
separator.setStyleSheet("background-color: #2d2d2d; margin: 5px 0;")
layout.addWidget(separator)

# Contenedor principal con splitter
main_splitter = QSplitter(Qt.Horizontal)
main_splitter.setStyleSheet("""
    QSplitter::handle {
        background-color: #2d2d2d;
        width: 1px;
    }
    QSplitter::handle:hover {
        background-color: #4CAF50;
    }
""")

# Panel izquierdo: Lista de resultados
results_panel = QWidget()
results_panel.setMinimumWidth(300)
results_panel.setMaximumWidth(500)
results_layout = QVBoxLayout(results_panel)
results_layout.setContentsMargins(0, 0, 0, 0)
results_layout.setSpacing(5)

# Lista de resultados - ESTILO SIMPLIFICADO
results_list = QListWidget()
results_list.setSelectionMode(QListWidget.SingleSelection)
results_list.setStyleSheet("""
    QListWidget {
        background-color: #141414;
        border: 1px solid #2d2d2d;
        border-radius: 6px;
        outline: none;
    }
    QListWidget::item {
        background-color: transparent;
        border: none;
        margin: 0px;
        padding: 0px;
    }
""")

# Scrollbar
results_list.verticalScrollBar().setStyleSheet("""
    QScrollBar:vertical {
        background-color: #141414;
        width: 10px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background-color: #3d3d3d;
        border-radius: 5px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #4CAF50;
    }
""")

results_layout.addWidget(results_list)

# Etiqueta de estado
status_label = QLabel("🔍 Escribe algo para buscar")
status_label.setObjectName("StatusLabel")
status_label.setStyleSheet("""
    QLabel#StatusLabel {
        color: #888888; 
        font-size: 12px; 
        margin-top: 5px;
    }
""")
status_label.setAlignment(Qt.AlignCenter)
results_layout.addWidget(status_label)

# ============= MENSAJE DE SIN RESULTADOS =============
no_results_container = QWidget()
no_results_layout = QVBoxLayout(no_results_container)
no_results_layout.setContentsMargins(20, 20, 20, 20)

no_results_label = QLabel("😔 No se encontraron resultados para tu búsqueda.\n\nIntenta con otros términos o ajusta los filtros.")
no_results_label.setObjectName("NoResultsLabel")
no_results_label.setStyleSheet("""
    QLabel#NoResultsLabel {
        color: #888888;
        font-size: 13px;
        line-height: 140%;
        text-align: center;
    }
""")
no_results_label.setWordWrap(True)
no_results_label.setAlignment(Qt.AlignCenter)
no_results_layout.addWidget(no_results_label)

# Botón para volver a buscar
back_search_btn = QPushButton("🔄 Volver a buscar")
back_search_btn.setObjectName("BackSearchButton")
back_search_btn.setMinimumHeight(40)
back_search_btn.setStyleSheet("""
    QPushButton#BackSearchButton {
        background-color: #4CAF50;
        border: 1px solid #3D8B40;
        border-radius: 6px;
        color: white;
        padding: 10px 20px;
        font-size: 13px;
        font-weight: bold;
        margin-top: 15px;
    }
    QPushButton#BackSearchButton:hover {
        background-color: #5DBB63;
        border: 1px solid #4CAF50;
    }
    QPushButton#BackSearchButton:pressed {
        background-color: #3D8B40;
        border: 1px solid #2D7B30;
    }
""")
no_results_layout.addWidget(back_search_btn)

# Inicialmente oculto
no_results_container.setVisible(False)
results_layout.addWidget(no_results_container)
# ====================================================

main_splitter.addWidget(results_panel)

# Panel derecho: Detalles del mod
details_panel = QWidget()
details_panel.setMinimumWidth(400)
details_layout = QVBoxLayout(details_panel)
details_layout.setContentsMargins(0, 0, 0, 0)
details_layout.setSpacing(0)

# Widget de detalles
mod_details = ModDetailWidget()
mod_details.main_window = main_window
details_layout.addWidget(mod_details)

# ============= MENSAJE DE ESPERA EN DETALLES =============
waiting_container = QWidget()
waiting_layout = QVBoxLayout(waiting_container)
waiting_layout.setContentsMargins(20, 20, 20, 20)

waiting_label = QLabel("👈 Selecciona un mod de la lista para ver sus detalles aquí.\n\nAquí aparecerá toda la información, descripción y versiones disponibles para descargar.")
waiting_label.setObjectName("WaitingLabel")
waiting_label.setStyleSheet("""
    QLabel#WaitingLabel {
        color: #888888;
        font-size: 13px;
        line-height: 140%;
        text-align: center;
    }
""")
waiting_label.setWordWrap(True)
waiting_label.setAlignment(Qt.AlignCenter)
waiting_layout.addWidget(waiting_label)

waiting_container.setVisible(False)  # Oculto inicialmente
details_layout.addWidget(waiting_container)
# ========================================================

main_splitter.addWidget(details_panel)

# Configurar proporciones iniciales
main_splitter.setSizes([350, 650])

layout.addWidget(main_splitter, 1)

# ============================================================================
# VARIABLES Y FUNCIONES
# ============================================================================

search_thread = None
download_thread = None
current_search_results = []
current_page = 0
is_loading_more = False
has_more_results = True
current_query = ""
current_category = CATEGORIES['addons']['id']

# Timer para debounce del scroll
scroll_debounce_timer = QTimer()
scroll_debounce_timer.setSingleShot(True)
scroll_debounce_timer.setInterval(300)

# Track currently selected mod
currently_selected_mod_id = None

def search_mods(load_more=False):
    """Realiza búsqueda de mods"""
    global current_page, is_loading_more, current_query, current_category, has_more_results
    
    if not load_more:
        query = search_input.text().strip()
        if not query:
            status_label.setText("⚠️ Escribe algo para buscar")
            return
        
        # Ocultar mensaje informativo inicial
        info_container.setVisible(False)
        
        # Mostrar paneles principales
        results_panel.setVisible(True)
        details_panel.setVisible(True)
        
        # Ocultar mensajes de no resultados
        no_results_container.setVisible(False)
        waiting_container.setVisible(True)  # Mostrar mensaje de espera hasta que cargue
        
        current_query = query
        current_category = category_combo.currentData()  # Obtener categoría seleccionada del ComboBox
        current_page = 0
        has_more_results = True
        
        # Actualizar estado
        status_label.setText("🔍 Buscando...")
        search_btn.setEnabled(False)
        search_btn.setText("Buscando...")
        
        # Limpiar resultados anteriores
        results_list.clear()
        current_search_results.clear()
        
        # Reset selección
        global currently_selected_mod_id
        currently_selected_mod_id = None
        
        # Limpiar detalles
        mod_details.name_label.clear()
        mod_details.meta_label.clear()
        mod_details.description_label.clear()
        mod_details.image_label.clear()
        mod_details.view_website_btn.setEnabled(False)
        mod_details.files_section.setVisible(False)
        mod_details.clear_files_container()
        mod_details.files_status_label.clear()
        mod_details.current_mod = None
    else:
        if not has_more_results or is_loading_more:
            return
        
        current_page += 1
        status_label.setText("📥 Cargando más resultados...")
    
    is_loading_more = True
    
    # Iniciar hilo de búsqueda
    global search_thread
    if search_thread and search_thread.isRunning():
        search_thread.terminate()
    
    search_thread = SearchThread(current_query, current_category, current_page)
    search_thread.search_finished.connect(on_search_finished)
    search_thread.search_error.connect(on_search_error)
    search_thread.start()

def on_search_finished(results):
    """Maneja resultados de búsqueda exitosa"""
    global is_loading_more, has_more_results
    
    search_btn.setEnabled(True)
    search_btn.setText("🔍 Buscar")
    is_loading_more = False
    
    if not results:
        if current_page == 0:
            # Mostrar mensaje de no resultados
            status_label.setText("😔 No se encontraron resultados")
            
            # Ocultar lista y mostrar mensaje de no resultados
            results_list.setVisible(False)
            no_results_container.setVisible(True)
            
            # Ocultar mensaje de espera y limpiar detalles
            waiting_container.setVisible(False)
            mod_details.name_label.clear()
            mod_details.meta_label.clear()
            mod_details.description_label.clear()
            mod_details.image_label.clear()
            mod_details.view_website_btn.setEnabled(False)
            mod_details.files_section.setVisible(False)
            mod_details.clear_files_container()
            mod_details.files_status_label.clear()
        else:
            has_more_results = False
            status_label.setText("✅ Fin de los resultados")
        return
    
    # Ocultar mensaje de no resultados
    no_results_container.setVisible(False)
    results_list.setVisible(True)
    waiting_container.setVisible(False)  # Ocultar mensaje de espera
    
    current_search_results.extend(results)
    
    # Desconectar temporalmente señales para mejor rendimiento
    results_list.blockSignals(True)
    
    # Limpiar selección actual
    global currently_selected_mod_id
    currently_selected_mod_id = None
    
    # Mostrar resultados
    for mod in results:
        # Crear widget personalizado
        item_widget = ModItemWidget(mod)
        item_widget.clicked.connect(lambda mod_data=mod: show_mod_details(mod_data))
        
        # Crear item de lista
        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(0, 70))
        list_item.setData(Qt.UserRole, mod)
        
        results_list.addItem(list_item)
        results_list.setItemWidget(list_item, item_widget)
    
    results_list.blockSignals(False)
    
    if current_page == 0:
        status_label.setText(f"✅ Mostrando {len(current_search_results)} resultados")
        
        # Seleccionar el primer item si hay resultados
        if results_list.count() > 0:
            results_list.setCurrentRow(0)
            # Pequeño delay para asegurar que la UI esté lista
            QTimer.singleShot(50, lambda: select_first_item())
    else:
        status_label.setText(f"✅ {len(current_search_results)} resultados cargados")
    
    # Verificar si hay más resultados
    if len(results) < 13:
        has_more_results = False

def select_first_item():
    """Selecciona el primer item después de un pequeño delay"""
    if results_list.count() > 0:
        first_item = results_list.item(0)
        if first_item:
            widget = results_list.itemWidget(first_item)
            if widget and hasattr(widget, 'mod_data'):
                # Establecer visualmente como seleccionado
                widget.set_selected(True)
                # Mostrar detalles
                show_mod_details(widget.mod_data)

def on_search_error(error_msg):
    """Maneja errores de búsqueda"""
    global is_loading_more
    
    search_btn.setEnabled(True)
    search_btn.setText("🔍 Buscar")
    is_loading_more = False
    status_label.setText(f"❌ {error_msg}")
    
    # Si no hay resultados, mostrar mensaje de error
    if results_list.count() == 0:
        no_results_container.setVisible(True)
        results_list.setVisible(False)
        waiting_container.setVisible(False)
        
        # Actualizar mensaje de error
        no_results_label.setText(f"❌ Error en la búsqueda:\n{error_msg}\n\nIntenta nuevamente.")
        
        # Limpiar detalles
        mod_details.name_label.clear()
        mod_details.meta_label.clear()
        mod_details.description_label.clear()
        mod_details.image_label.clear()
        mod_details.view_website_btn.setEnabled(False)
        mod_details.files_section.setVisible(False)
        mod_details.clear_files_container()
        mod_details.files_status_label.clear()

def show_mod_details(mod_data):
    """Muestra detalles de un mod seleccionado"""
    global currently_selected_mod_id
    
    mod_id = mod_data.get('id')
    
    # Solo procesar si es un mod diferente
    if mod_id == currently_selected_mod_id:
        return
    
    currently_selected_mod_id = mod_id
    
    # Ocultar mensaje de espera
    waiting_container.setVisible(False)
    
    # Actualizar todos los widgets de la lista para reflejar la selección correcta
    for i in range(results_list.count()):
        item = results_list.item(i)
        widget = results_list.itemWidget(item)
        if widget and hasattr(widget, 'mod_data'):
            item_mod_id = widget.mod_data.get('id')
            # Actualizar estado visual basado en si coincide con el mod seleccionado
            is_selected = (item_mod_id == mod_id)
            widget.set_selected(is_selected)
            
            # También actualizar el estado del item de la lista si es necesario
            if is_selected:
                results_list.setCurrentRow(i)
    
    # LIMPIAR COMPLETAMENTE antes de cargar nuevos datos
    mod_details.name_label.clear()
    mod_details.meta_label.clear()
    mod_details.description_label.clear()
    mod_details.image_label.clear()
    mod_details.view_website_btn.setEnabled(False)
    mod_details.files_section.setVisible(False)
    mod_details.clear_files_container()
    mod_details.files_status_label.clear()
    
    # Cargar datos del mod (no bloqueante)
    mod_details.load_mod_data(mod_data)

# Conectar scroll infinito
def on_scroll():
    """Carga más resultados al llegar al final del scroll"""
    if not is_loading_more and has_more_results:
        scrollbar = results_list.verticalScrollBar()
        if scrollbar.value() >= scrollbar.maximum() - 100:
            search_mods(load_more=True)

def on_scroll_debounced():
    if not scroll_debounce_timer.isActive():
        on_scroll()
        scroll_debounce_timer.start()

results_list.verticalScrollBar().valueChanged.connect(on_scroll_debounced)

# Conectar selección por teclado/flechas
def on_current_item_changed(current, previous):
    """Maneja cambios en la selección de la lista (teclado/flechas)"""
    # Limpiar selección anterior
    if previous:
        widget = results_list.itemWidget(previous)
        if widget:
            widget.set_selected(False)
    
    # Aplicar nueva selección
    if current:
        widget = results_list.itemWidget(current)
        if widget:
            widget.set_selected(True)
            # Mostrar detalles del mod seleccionado
            mod_data = current.data(Qt.UserRole)
            if mod_data:
                show_mod_details(mod_data)

results_list.currentItemChanged.connect(on_current_item_changed)

# Función para iniciar descarga
def start_download_mod(mod_data_with_file):
    """Inicia descarga de un archivo específico de un mod"""
    mod_data = mod_data_with_file.copy()
    selected_file = mod_data.pop('selected_file', None)
    
    if not selected_file:
        QMessageBox.warning(main_window, "Error", "No se ha seleccionado ningún archivo para descargar")
        return
    
    # Mostrar diálogo para seleccionar tipo de archivo si es addon
    category_id = mod_data.get('classId')
    
    if category_id == CATEGORIES['addons']['id']:
        dialog = QDialog(main_window)
        dialog.setWindowTitle("Seleccionar tipo de addon")
        dialog.setFixedSize(450, 180)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        
        label = QLabel(f"¿Cómo quieres instalar '{mod_data['name']}'?")
        label.setStyleSheet("color: white; font-size: 14px; margin-bottom: 20px;")
        layout.addWidget(label)
        
        btn_layout = QHBoxLayout()
        
        behavior_btn = QPushButton("🧩 Behavior Pack")
        behavior_btn.setStyleSheet("""
            QPushButton {
                background-color: #5DBB63;
                border: 1px solid #4CAF50;
                border-radius: 6px;
                color: white;
                padding: 12px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6BCF72;
                border: 1px solid #5DBB63;
            }
        """)
        behavior_btn.clicked.connect(lambda: on_addon_type_selected("behavior_packs"))
        
        resource_btn = QPushButton("🎨 Resource Pack")
        resource_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A86E8;
                border: 1px solid #3A75D4;
                border-radius: 6px;
                color: white;
                padding: 12px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5D9CFA;
                border: 1px solid #4A86E8;
            }
        """)
        resource_btn.clicked.connect(lambda: on_addon_type_selected("resource_packs"))
        
        btn_layout.addWidget(behavior_btn)
        btn_layout.addWidget(resource_btn)
        layout.addLayout(btn_layout)
        
        def on_addon_type_selected(pack_type):
            dialog.accept()
            mod_data['_install_type'] = pack_type
            mod_data['selected_file'] = selected_file
            confirm_download(mod_data)
        
        dialog.exec()
    else:
        # Para otros tipos, asignar automáticamente
        if category_id == CATEGORIES['maps']['id']:
            mod_data['_install_type'] = 'minecraftWorlds'
        elif category_id == CATEGORIES['textures']['id']:
            mod_data['_install_type'] = 'resource_packs'
        else:
            mod_data['_install_type'] = 'behavior_packs'  # Por defecto
        
        mod_data['selected_file'] = selected_file
        confirm_download(mod_data)

def confirm_download(mod_data):
    """Muestra diálogo de confirmación antes de descargar"""
    selected_file = mod_data['selected_file']
    file_name = selected_file.get('fileName', 'archivo')
    file_size = selected_file.get('fileLength', 0)
    size_text = f" ({file_size / (1024*1024):.1f} MB)" if file_size > 0 else ""
    
    # Crear diálogo personalizado
    dialog = QDialog(main_window)
    dialog.setWindowTitle("Confirmar descarga")
    dialog.setFixedSize(400, 250)
    dialog.setStyleSheet("""
        QDialog {
            background-color: #1a1a1a;
            border-radius: 8px;
        }
    """)
    
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(15)
    
    # Mensaje
    message_label = QLabel(
        f"¿Descargar e instalar '{mod_data['name']}'?\n\n"
        f"Archivo: {file_name}{size_text}\n"
        f"Se instalará en: {mod_data['_install_type']}"
    )
    message_label.setStyleSheet("color: white; font-size: 14px;")
    message_label.setWordWrap(True)
    layout.addWidget(message_label)
    
    layout.addStretch()
    
    # Botones
    buttons_layout = QHBoxLayout()
    buttons_layout.setSpacing(15)
    
    # Botón Cancelar (verde)
    cancel_btn = QPushButton("❌ Cancelar")
    cancel_btn.setMinimumHeight(40)
    cancel_btn.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            border: 3px solid;
            border-top-color: #5DBB63;
            border-left-color: #5DBB63;
            border-right-color: #3D8B40;
            border-bottom-color: #3D8B40;
            color: white;
            padding: 3px 3px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 6px;
            text-shadow: 1px 1px 0 #3D8B40;
            image: none;
        }
        QPushButton:hover {
            background-color: #5DBB63;
            border-top-color: #6BCF72;
            border-left-color: #6BCF72;
            transform: translateY(-1px);
        }
        QPushButton:pressed {
            background-color: #3D8B40;
            transform: translateY(1px);
            border-top-color: #4CAF50;
            border-left-color: #4CAF50;
        }
    """)
    
    # Botón Aceptar (azul)
    accept_btn = QPushButton("✅ Aceptar")
    accept_btn.setMinimumHeight(40)
    accept_btn.setStyleSheet("""
        QPushButton {
            background-color: #4A86E8;
            border: 3px solid;
            border-top-color: #5D9CFA;
            border-left-color: #5D9CFA;
            border-right-color: #3A75D4;
            border-bottom-color: #3A75D4;
            color: white;
            padding: 3px 3px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 6px;
            text-shadow: 1px 1px 0 #3A75D4;
            image: none;
        }
        QPushButton:hover {
            background-color: #5D9CFA;
            border-top-color: #6EB0FF;
            border-left-color: #6EB0FF;
            transform: translateY(-1px);
        }
        QPushButton:pressed {
            background-color: #3A75D4;
            transform: translateY(1px);
            border-top-color: #4A86E8;
            border-left-color: #4A86E8;
        }
    """)
    
    buttons_layout.addWidget(cancel_btn)
    buttons_layout.addWidget(accept_btn)
    layout.addLayout(buttons_layout)
    
    # Variables para resultado
    result = False
    
    def on_cancel():
        nonlocal result
        result = False
        dialog.reject()
    
    def on_accept():
        nonlocal result
        result = True
        dialog.accept()
    
    cancel_btn.clicked.connect(on_cancel)
    accept_btn.clicked.connect(on_accept)
    
    dialog.exec()
    
    if result:
        download_mod(mod_data)

def download_mod(mod_data):
    """Descarga el archivo seleccionado del mod"""
    selected_file = mod_data['selected_file']
    mod_id = mod_data['id']
    mod_name = mod_data['name']
    file_id = selected_file['id']
    file_name = selected_file['fileName']
    file_type = determine_file_type(file_name)
    install_type = mod_data['_install_type']
    
    # Diálogo de progreso
    progress_dialog = QDialog(main_window)
    progress_dialog.setWindowTitle(f"Descargando {mod_name}")
    progress_dialog.setFixedSize(350, 140)
    progress_dialog.setStyleSheet("""
        QDialog {
            background-color: #1a1a1a;
            border-radius: 8px;
        }
    """)
    
    layout = QVBoxLayout(progress_dialog)
    layout.setContentsMargins(20, 20, 20, 20)
    
    label = QLabel(f"Descargando: {file_name}")
    label.setStyleSheet("color: white; font-size: 13px;")
    layout.addWidget(label)
    
    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setTextVisible(True)
    progress_bar.setStyleSheet("""
        QProgressBar {
            border: 1px solid #2d2d2d;
            border-radius: 4px;
            text-align: center;
            background-color: #141414;
            color: white;
            height: 20px;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
            border-radius: 4px;
        }
    """)
    layout.addWidget(progress_bar)
    
    cancel_btn = QPushButton("Cancelar")
    cancel_btn.setStyleSheet("""
        QPushButton {
            background-color: #BB5D5D;
            border: 1px solid #AF4C4C;
            border-radius: 6px;
            color: white;
            padding: 8px;
            font-size: 13px;
            font-weight: bold;
            margin-top: 15px;
        }
        QPushButton:hover {
            background-color: #CF6B6B;
            border: 1px solid #BB5D5D;
        }
    """)
    layout.addWidget(cancel_btn)
    
    progress_dialog.show()
    QApplication.processEvents()
    
    # Iniciar hilo de descarga
    global download_thread
    if download_thread and download_thread.isRunning():
        download_thread.terminate()
    
    download_thread = DownloadThread(mod_id, file_id, file_name, file_type)
    download_thread.download_progress.connect(lambda p: progress_bar.setValue(p))
    download_thread.download_finished.connect(
        lambda name, ftype, content: on_download_finished(name, ftype, content, install_type, progress_dialog))
    download_thread.download_error.connect(
        lambda msg: on_download_error(msg, progress_dialog))
    
    def cancel_download():
        if download_thread and download_thread.isRunning():
            download_thread.terminate()
        progress_dialog.close()
    
    cancel_btn.clicked.connect(cancel_download)
    download_thread.start()

def determine_file_type(filename):
    """Determina el tipo de archivo basado en la extensión"""
    filename_lower = filename.lower()
    if filename_lower.endswith('.mcpack'):
        return "mcpack"
    elif filename_lower.endswith('.mcaddon'):
        return "mcaddon"
    elif filename_lower.endswith('.mcworld'):
        return "mcworld"
    elif filename_lower.endswith('.zip'):
        return "zip"
    return "unknown"

def on_download_finished(file_name, file_type, content, install_type, progress_dialog):
    """Maneja descarga exitosa"""
    progress_dialog.close()
    
    # Guardar archivo temporalmente
    temp_file = DOWNLOAD_DIR / file_name
    with open(temp_file, 'wb') as f:
        f.write(content)
    
    # Instalar archivo
    try:
        # Asegurar que el directorio de destino existe
        target_dir = GAMES_DIR / install_type
        target_dir.mkdir(parents=True, exist_ok=True)
        
        if file_type in ['mcpack', 'mcaddon', 'mcworld', 'zip']:
            # Determinar directorio de extracción
            if file_type == 'mcworld':
                # Para .mcworld, crear subcarpeta con nombre del archivo (sin extensión)
                world_name = Path(file_name).stem
                extract_dir = target_dir / world_name
            else:
                # Para otros, extraer en subcarpeta con nombre del archivo
                extract_dir = target_dir / Path(file_name).stem
            
            # Verificar si ya existe
            if extract_dir.exists():
                # Crear diálogo personalizado para confirmar reemplazo
                replace_dialog = QDialog(main_window)
                replace_dialog.setWindowTitle("Reemplazar")
                replace_dialog.setFixedSize(400, 200)
                replace_dialog.setStyleSheet("""
                    QDialog {
                        background-color: #1a1a1a;
                        border-radius: 8px;
                    }
                """)
                
                replace_layout = QVBoxLayout(replace_dialog)
                replace_layout.setContentsMargins(20, 20, 20, 20)
                replace_layout.setSpacing(15)
                
                replace_label = QLabel(f"'{Path(file_name).stem}' ya existe.\n¿Deseas reemplazarlo?")
                replace_label.setStyleSheet("color: white; font-size: 14px;")
                replace_label.setWordWrap(True)
                replace_layout.addWidget(replace_label)
                
                replace_layout.addStretch()
                
                # Botones de reemplazo
                replace_buttons_layout = QHBoxLayout()
                replace_buttons_layout.setSpacing(15)
                
                replace_cancel_btn = QPushButton("❌ Conservar existente")
                replace_cancel_btn.setMinimumHeight(40)
                replace_cancel_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        border: 3px solid;
                        border-top-color: #5DBB63;
                        border-left-color: #5DBB63;
                        border-right-color: #3D8B40;
                        border-bottom-color: #3D8B40;
                        color: white;
                        padding: 3px 3px;
                        font-size: 14px;
                        font-weight: bold;
                        border-radius: 6px;
                        text-shadow: 1px 1px 0 #3D8B40;
                        image: none;
                    }
                    QPushButton:hover {
                        background-color: #5DBB63;
                        border-top-color: #6BCF72;
                        border-left-color: #6BCF72;
                        transform: translateY(-1px);
                    }
                    QPushButton:pressed {
                        background-color: #3D8B40;
                        transform: translateY(1px);
                        border-top-color: #4CAF50;
                        border-left-color: #4CAF50;
                    }
                """)
                
                replace_accept_btn = QPushButton("✅ Reemplazar")
                replace_accept_btn.setMinimumHeight(40)
                replace_accept_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4A86E8;
                        border: 3px solid;
                        border-top-color: #5D9CFA;
                        border-left-color: #5D9CFA;
                        border-right-color: #3A75D4;
                        border-bottom-color: #3A75D4;
                        color: white;
                        padding: 3px 3px;
                        font-size: 14px;
                        font-weight: bold;
                        border-radius: 6px;
                        text-shadow: 1px 1px 0 #3A75D4;
                        image: none;
                    }
                    QPushButton:hover {
                        background-color: #5D9CFA;
                        border-top-color: #6EB0FF;
                        border-left-color: #6EB0FF;
                        transform: translateY(-1px);
                    }
                    QPushButton:pressed {
                        background-color: #3A75D4;
                        transform: translateY(1px);
                        border-top-color: #4A86E8;
                        border-left-color: #4A86E8;
                    }
                """)
                
                replace_buttons_layout.addWidget(replace_cancel_btn)
                replace_buttons_layout.addWidget(replace_accept_btn)
                replace_layout.addLayout(replace_buttons_layout)
                
                replace_result = False
                
                def on_replace_cancel():
                    nonlocal replace_result
                    replace_result = False
                    replace_dialog.reject()
                
                def on_replace_accept():
                    nonlocal replace_result
                    replace_result = True
                    replace_dialog.accept()
                
                replace_cancel_btn.clicked.connect(on_replace_cancel)
                replace_accept_btn.clicked.connect(on_replace_accept)
                
                replace_dialog.exec()
                
                if not replace_result:
                    temp_file.unlink()
                    return
                else:
                    shutil.rmtree(extract_dir, ignore_errors=True)
            
            # Crear directorio si no existe
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            # Extraer contenido
            with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Mostrar mensaje de éxito
            success_dialog = QDialog(main_window)
            success_dialog.setWindowTitle("Instalación completada")
            success_dialog.setFixedSize(450, 180)
            success_dialog.setStyleSheet("""
                QDialog {
                    background-color: #1a1a1a;
                    border-radius: 8px;
                }
            """)
            
            success_layout = QVBoxLayout(success_dialog)
            success_layout.setContentsMargins(20, 20, 20, 20)
            success_layout.setSpacing(15)
            
            success_label = QLabel(f"✅ '{Path(file_name).stem}' instalado!")
            success_label.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: bold;")
            success_label.setAlignment(Qt.AlignCenter)
            success_layout.addWidget(success_label)
            
            path_label = QLabel(f"Ubicación: {extract_dir}")
            path_label.setStyleSheet("color: #cccccc; font-size: 12px;")
            path_label.setWordWrap(True)
            path_label.setAlignment(Qt.AlignCenter)
            success_layout.addWidget(path_label)
            
            success_layout.addStretch()
            
            ok_btn = QPushButton("✅ Aceptar")
            ok_btn.setMinimumHeight(40)
            ok_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    border: 3px solid;
                    border-top-color: #5DBB63;
                    border-left-color: #5DBB63;
                    border-right-color: #3D8B40;
                    border-bottom-color: #3D8B40;
                    color: white;
                    padding: 3px 3px;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 6px;
                    text-shadow: 1px 1px 0 #3D8B40;
                    image: none;
                }
                QPushButton:hover {
                    background-color: #5DBB63;
                    border-top-color: #6BCF72;
                    border-left-color: #6BCF72;
                    transform: translateY(-1px);
                }
                QPushButton:pressed {
                    background-color: #3D8B40;
                    transform: translateY(1px);
                    border-top-color: #4CAF50;
                    border-left-color: #4CAF50;
                }
            """)
            
            def on_ok():
                success_dialog.accept()
            
            ok_btn.clicked.connect(on_ok)
            success_layout.addWidget(ok_btn)
            
            success_dialog.exec()
            
        else:
            # Para formatos no soportados
            error_dialog = QDialog(main_window)
            error_dialog.setWindowTitle("Formato no soportado")
            error_dialog.setFixedSize(400, 180)
            error_dialog.setStyleSheet("""
                QDialog {
                    background-color: #1a1a1a;
                    border-radius: 8px;
                }
            """)
            
            error_layout = QVBoxLayout(error_dialog)
            error_layout.setContentsMargins(20, 20, 20, 20)
            
            error_label = QLabel(f"El formato {file_type} no está soportado para instalación automática.")
            error_label.setStyleSheet("color: #FF6B6B; font-size: 14px;")
            error_label.setWordWrap(True)
            error_label.setAlignment(Qt.AlignCenter)
            error_layout.addWidget(error_label)
            
            error_layout.addStretch()
            
            ok_error_btn = QPushButton("✅ Aceptar")
            ok_error_btn.setMinimumHeight(40)
            ok_error_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4A86E8;
                    border: 3px solid;
                    border-top-color: #5D9CFA;
                    border-left-color: #5D9CFA;
                    border-right-color: #3A75D4;
                    border-bottom-color: #3A75D4;
                    color: white;
                    padding: 3px 3px;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 6px;
                    text-shadow: 1px 1px 0 #3A75D4;
                    image: none;
                }
                QPushButton:hover {
                    background-color: #5D9CFA;
                    border-top-color: #6EB0FF;
                    border-left-color: #6EB0FF;
                    transform: translateY(-1px);
                }
                QPushButton:pressed {
                    background-color: #3A75D4;
                    transform: translateY(1px);
                    border-top-color: #4A86E8;
                    border-left-color: #4A86E8;
                }
            """)
            
            def on_error_ok():
                error_dialog.accept()
            
            ok_error_btn.clicked.connect(on_error_ok)
            error_layout.addWidget(ok_error_btn)
            
            error_dialog.exec()
    
    except Exception as e:
        # Diálogo de error
        error_dialog = QDialog(main_window)
        error_dialog.setWindowTitle("Error en instalación")
        error_dialog.setFixedSize(450, 200)
        error_dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                border-radius: 8px;
            }
        """)
        
        error_layout = QVBoxLayout(error_dialog)
        error_layout.setContentsMargins(20, 20, 20, 20)
        
        error_label = QLabel(f"Error al instalar archivo:\n{str(e)}")
        error_label.setStyleSheet("color: #FF6B6B; font-size: 14px;")
        error_label.setWordWrap(True)
        error_label.setAlignment(Qt.AlignCenter)
        error_layout.addWidget(error_label)
        
        error_layout.addStretch()
        
        ok_error_btn = QPushButton("✅ Aceptar")
        ok_error_btn.setMinimumHeight(40)
        ok_error_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A86E8;
                border: 3px solid;
                border-top-color: #5D9CFA;
                border-left-color: #5D9CFA;
                border-right-color: #3A75D4;
                border-bottom-color: #3A75D4;
                color: white;
                padding: 3px 3px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                text-shadow: 1px 1px 0 #3A75D4;
                image: none;
            }
            QPushButton:hover {
                background-color: #5D9CFA;
                border-top-color: #6EB0FF;
                border-left-color: #6EB0FF;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #3A75D4;
                transform: translateY(1px);
                border-top-color: #4A86E8;
                border-left-color: #4A86E8;
            }
        """)
        
        def on_error_ok():
            error_dialog.accept()
        
        ok_error_btn.clicked.connect(on_error_ok)
        error_layout.addWidget(ok_error_btn)
        
        error_dialog.exec()
    
    finally:
        # Limpiar archivo temporal
        if temp_file.exists():
            temp_file.unlink()

def on_download_error(error_msg, progress_dialog):
    """Maneja errores de descarga"""
    progress_dialog.close()
    
    # Crear diálogo personalizado
    error_dialog = QDialog(main_window)
    error_dialog.setWindowTitle("Error en descarga")
    error_dialog.setFixedSize(450, 200)
    error_dialog.setStyleSheet("""
        QDialog {
            background-color: #1a1a1a;
            border-radius: 8px;
        }
    """)
    
    error_layout = QVBoxLayout(error_dialog)
    error_layout.setContentsMargins(20, 20, 20, 20)
    error_layout.setSpacing(15)
    
    error_label = QLabel(f"No se pudo descargar el archivo:\n{error_msg}")
    error_label.setStyleSheet("color: #FF6B6B; font-size: 14px;")
    error_label.setWordWrap(True)
    error_label.setAlignment(Qt.AlignCenter)
    error_layout.addWidget(error_label)
    
    error_layout.addStretch()
    
    ok_error_btn = QPushButton("✅ Aceptar")
    ok_error_btn.setMinimumHeight(40)
    ok_error_btn.setStyleSheet("""
        QPushButton {
            background-color: #4A86E8;
            border: 3px solid;
            border-top-color: #5D9CFA;
            border-left-color: #5D9CFA;
            border-right-color: #3A75D4;
            border-bottom-color: #3A75D4;
            color: white;
            padding: 3px 3px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 6px;
            text-shadow: 1px 1px 0 #3A75D4;
            image: none;
        }
        QPushButton:hover {
            background-color: #5D9CFA;
            border-top-color: #6EB0FF;
            border-left-color: #6EB0FF;
            transform: translateY(-1px);
        }
        QPushButton:pressed {
            background-color: #3A75D4;
            transform: translateY(1px);
            border-top-color: #4A86E8;
            border-left-color: #4A86E8;
        }
    """)
    
    def on_error_ok():
        error_dialog.accept()
    
    ok_error_btn.clicked.connect(on_error_ok)
    error_layout.addWidget(ok_error_btn)
    
    error_dialog.exec()

# ============================================================================
# CONEXIONES Y CONFIGURACIÓN INICIAL
# ============================================================================

# Conectar botones
search_btn.clicked.connect(lambda: search_mods(load_more=False))
search_input.returnPressed.connect(lambda: search_mods(load_more=False))

# Conectar botón de volver a buscar en el mensaje de no resultados
back_search_btn.clicked.connect(lambda: search_mods(load_more=False))

# ============= CONFIGURACIÓN VISUAL INICIAL =============
# Ocultar paneles principales inicialmente
results_panel.setVisible(False)
details_panel.setVisible(False)
no_results_container.setVisible(False)
waiting_container.setVisible(False)

# Mostrar solo el mensaje informativo inicial
info_container.setVisible(True)
# =======================================================

# Configurar estado inicial
status_label.setText("🔍 Escribe algo para buscar")

# Deshabilitar botón de website inicialmente
mod_details.view_website_btn.setEnabled(False)
