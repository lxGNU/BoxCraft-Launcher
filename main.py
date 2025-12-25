import os
import sys
import json
import shutil
import tarfile
import subprocess
import tempfile
import threading
import zipfile
import requests
import signal
from pathlib import Path
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from typing import Optional, Tuple

# ============================================================================
# CONFIGURACIONES Y RUTAS
# ============================================================================

APP_NAME = "BoxCraft Launcher"
APP_VERSION = "1.0.0"

# Directorios
BASE_DIR = Path(__file__).parent
RESOURCES_DIR = BASE_DIR / "resources"
PAGES_DIR = RESOURCES_DIR / "pages"
FONTS_DIR = RESOURCES_DIR / "fonts"
MCPELAUNCHER_DIR = Path.home() / ".local" / "share" / "boxcraft"
VERSIONS_DIR = MCPELAUNCHER_DIR / "versions"
GAMES_DIR = MCPELAUNCHER_DIR / "games" / "com.mojang"
CONFIG_FILE = MCPELAUNCHER_DIR / "boxcraft_config.json"

# Ruta a los ejecutables mcpelauncher
MCPELAUNCHER_CLIENT = RESOURCES_DIR / "mcpelauncher-client"
MCPELAUNCHER_EXTRACT = RESOURCES_DIR / "mcpelauncher-extract"

# ============================================================================
# ESTILOS CSS (Estilo Minecraft Bedrock Launcher)
# ============================================================================

STYLE_CSS = """
/* ===== ESTILO GENERAL ===== */
QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
    font-family: 'Segoe UI', 'Noto Sans', sans-serif;
    font-size: 14px;
}

/* ===== VENTANA PRINCIPAL ===== */
QMainWindow {
    background-color: #1a1a1a;
    border-radius: 12px;
}

/* ===== BARRA DE TÍTULO PERSONALIZADA ===== */
#TitleBar {
    background-color: #141414;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    border-bottom: 2px solid #4CAF50;
    height: 40px;
}

#TitleBarLabel {
    font-size: 16px;
    font-weight: bold;
    color: #cccccc;
    qproperty-alignment: AlignCenter;
}

#TitleButton {
    background-color: transparent;
    border: none;
    border-radius: 4px;
    min-width: 30px;
    min-height: 30px;
    padding: 0;
    margin: 0 2px;
    color: #888888;
    font-size: 14px;
}

#TitleButton:hover {
    background-color: #2d2d2d;
    color: #ffffff;
}

#TitleButton#CloseButton:hover {
    background-color: #ff4444;
    color: white;
}

#TitleButton#MinimizeButton:hover {
    background-color: #2d2d2d;
    color: #4CAF50;
}

/* ===== BARRA LATERAL (PESTAÑAS) ===== */
#Sidebar {
    background-color: #141414;
    border-right: 1px solid #2d2d2d;
}

QPushButton#TabButton {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 16px 8px;
    margin: 4px;
    qproperty-iconSize: 24px;
    font-size: 20px;  /* <-- Tamaño de fuente para emojis/texto */
    color: #888888;
}

QPushButton#TabButton:hover {
    background-color: #2d2d2d;
    color: #ffffff;
}

QPushButton#TabButton:checked {
    background-color: #2d2d2d;
    color: #4CAF50;
    border-left: 3px solid #4CAF50;
}

/* ===== LISTA DE VERSIONES ===== */
QListWidget {
    background-color: #141414;
    border: 1px solid #2d2d2d;
    border-radius: 8px;
    padding: 4px;
    outline: none;
}

QListWidget::item {
    background-color: #1e1e1e;
    border-radius: 6px;
    padding: 12px;
    margin: 4px 0;
    border: 1px solid transparent;
}

QListWidget::item:hover {
    background-color: #252525;
    border: 1px solid #4CAF50;
}

QListWidget::item:selected {
    background-color: #2d2d2d;
    border: 2px solid #4CAF50;
}

/* ===== BOTONES PRINCIPALES ===== */
QPushButton#PlayButton {
    background-color: #4CAF50;
    border: none;
    border-radius: 6px;
    padding: 16px 32px;
    font-weight: bold;
    color: white;
    font-size: 16px;
    min-width: 180px;
    min-height: 50px;
}

QPushButton#PlayButton:hover {
    background-color: #45a049;
    transform: scale(1.02);
}

QPushButton#PlayButton:pressed {
    background-color: #3d8b40;
    transform: scale(0.98);
}

QPushButton#PrimaryButton {
    background-color: #4CAF50;
    border: none;
    border-radius: 6px;
    padding: 9px 24px;
    font-weight: bold;
    color: white;
    font-size: 14px;
}

QPushButton#PrimaryButton:hover {
    background-color: #45a049;
}

QPushButton#PrimaryButton:pressed {
    background-color: #3d8b40;
}

QPushButton#SecondaryButton {
    background-color: #333333;
    border: 1px solid #444444;
    border-radius: 6px;
    padding: 8px 16px;
    color: #cccccc;
    min-height: 19px;
}

QPushButton#SecondaryButton:hover {
    background-color: #3d3d3d;
    border: 1px solid #4CAF50;
}

/* ===== BOTONES DE ICONO ===== */
QPushButton#IconButton {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 6px;  /* Asegúrate de que esto esté presente */
    min-width: 33px;
    min-height: 33px;
    padding: 1px;
    font-size: 14px;
}

QPushButton#IconButton:hover {
    background-color: #3d3d3d;
    border: 1px solid #4CAF50;
    border-radius: 6px;  /* Mantener en hover también */
}

/* ===== GROUP BOX ===== */
QGroupBox {
    border: 1px solid #2d2d2d;
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 10px;
    background-color: #141414;
    color: #4CAF50;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px 0 8px;
    color: #4CAF50;
}

/* ===== LINE EDITS ===== */
QLineEdit {
    background-color: #1e1e1e;
    border: 1px solid #2d2d2d;
    border-radius: 6px;
    padding: 8px;
    color: white;
    selection-background-color: #4CAF50;
}

QLineEdit:focus {
    border: 2px solid #4CAF50;
}

/* ===== LABELS ===== */
QLabel {
    color: #cccccc;
}

QLabel#TitleLabel {
    font-size: 24px;
    font-weight: bold;
    color: #4CAF50;
    margin-bottom: 10px;
}

QLabel#SubtitleLabel {
    font-size: 14px;
    color: #888888;
    margin-bottom: 20px;
}

QLabel#VersionLabel {
    font-size: 18px;
    font-weight: bold;
    color: white;
    background-color: #2d2d2d;
    padding: 8px 16px;
    border-radius: 6px;
    border: 1px solid #3d3d3d;
}

/* ===== PROGRESS BAR ===== */
QProgressBar {
    border: 1px solid #2d2d2d;
    border-radius: 4px;
    background-color: #1e1e1e;
    text-align: center;
    color: white;
}

QProgressBar::chunk {
    background-color: #4CAF50;
    border-radius: 4px;
}

/* ===== SCROLLBAR ===== */
QScrollBar:vertical {
    border: none;
    background: #141414;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #3d3d3d;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #4CAF50;
}

/* ===== TAB WIDGET ===== */
QTabWidget::pane {
    border: 1px solid #2d2d2d;
    background-color: #141414;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #1e1e1e;
    color: #888888;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid #2d2d2d;
}

QTabBar::tab:hover {
    background-color: #252525;
    color: #cccccc;
}

QTabBar::tab:selected {
    background-color: #141414;
    color: #4CAF50;
    border-bottom: 2px solid #4CAF50;
}

/* ===== DIALOG ===== */
QDialog {
    background-color: #1a1a1a;
    border-radius: 8px;
}

/* ===== HEADER ===== */
#Header {
    background-color: #141414;
    border-bottom: 2px solid #4CAF50;
    padding: 12px;
}

#HeaderLabel {
    font-size: 20px;
    font-weight: bold;
    color: #4CAF50;
}

/* ===== FLOATING BUTTON ===== */
#FloatingPlayButton {
    background-color: #4CAF50;
    border: 2px solid #45a049;
    border-radius: 8px;
    padding: 12px 30px;
    font-weight: bold;
    color: white;
    font-size: 16px;
    min-width: 200px;
    min-height: 50px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    font-family: 'Minecraft', 'Arial Black', sans-serif;
}

#FloatingPlayButton:hover {
    background-color: #45a049;
    border: 2px solid #3d8b40;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
}

#FloatingPlayButton:pressed {
    background-color: #3d8b40;
    transform: translateY(2px);
}
/* ===== TOOLTIPS ===== */
QToolTip {
    background-color: #2d2d2d;
    border: 1px solid #4CAF50;
    border-radius: 8px;
    color: #ffffff;  /* Texto blanco */
    font-family: 'Segoe UI', 'Noto Sans', sans-serif;
    font-size: 12px;
    padding: 3px;
    opacity: 240;  /* Un poco de transparencia */
}
"""

# ============================================================================
# DIÁLOGO DE TÉRMINOS Y CONDICIONES
# ============================================================================

class TermsDialog(QDialog):
    """Diálogo de términos y condiciones con opción de no mostrar más."""
    
    # Señal emitida cuando el usuario acepta los términos
    terms_accepted = Signal(bool)  # bool: si se debe mostrar de nuevo
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Términos y Condiciones - BoxCraft Launcher")
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.resize(800, 600)
        self.setup_ui()
        self.apply_styles()
    
    def apply_styles(self):
        """Aplica estilos al diálogo."""
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                border: 2px solid #2d2d2d;
                border-radius: 12px;
            }
            
            QLabel#TitleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #4CAF50;
                margin-bottom: 10px;
            }
            
            QLabel {
                color: #cccccc;
                font-size: 14px;
            }
            
            QCheckBox {
                color: #cccccc;
                font-size: 14px;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #4CAF50;
                border-radius: 4px;
                background-color: #1e1e1e;
            }
            
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
            }
            
            QScrollArea {
                border: 1px solid #2d2d2d;
                border-radius: 8px;
                background-color: #141414;
            }
            
            QScrollBar:vertical {
                background: #141414;
                width: 10px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical {
                background: #3d3d3d;
                border-radius: 5px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #4CAF50;
            }
        """)
    
    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        title_label = QLabel("TÉRMINOS Y CONDICIONES")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Subtítulo
        subtitle_label = QLabel("Por favor, lee y acepta los términos antes de usar BoxCraft Launcher")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)
        
        # Área de scroll para los términos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Widget de contenido de los términos
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #141414;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Contenido completo de los términos
        terms_content = QLabel("""
            <h2 style='color:#4CAF50; text-align:center;'>TÉRMINOS Y CONDICIONES</h2>
            
            <h3 style='color:#4CAF50;'>1. ACEPTACIÓN DE TÉRMINOS</h3>
            <p>Al utilizar BoxCraft Launcher, aceptas cumplir con estos términos y condiciones. 
            Si no estás de acuerdo con alguno de estos términos, no debes usar esta aplicación.</p>
            
            <h3 style='color:#4CAF50;'>2. DESCARGO DE RESPONSABILIDAD</h3>
            <p><b>BoxCraft Launcher</b> es un software de código abierto que actúa como lanzador para 
            <b>Minecraft: Bedrock Edition</b>. Este software <b>NO</b> está asociado, avalado o aprobado 
            por <b>Mojang AB</b>, <b>Microsoft Corporation</b>, o cualquier entidad relacionada con Minecraft.</p>
            
            <p>El launcher <b>NO</b> incluye ni distribuye el juego Minecraft: Bedrock Edition. 
            Es responsabilidad del usuario obtener una copia legítima del juego. 
            BoxCraft Launcher no promueve, facilita ni tolera la piratería de software.</p>
            
            <p>El uso de este launcher con versiones no autorizadas del juego es responsabilidad exclusiva del usuario.</p>
            
            <h3 style='color:#4CAF50;'>3. LIBRERÍAS DE TERCEROS</h3>
            <p>BoxCraft Launcher utiliza las siguientes librerías de terceros:</p>
            <ul>
                <li><b>mcpelauncher-client</b>: https://codeberg.org/javiercplus/mcpelauncher-client-extend</li>
                <li><b>mcpelauncher-extract</b>: https://codeberg.org/javiercplus/mcpe-extract</li>
            </ul>
            <p>Estos proyectos son independientes y mantenidos por terceros. 
            Los desarrolladores de BoxCraft Launcher no son responsables del funcionamiento, 
            actualizaciones o cambios en estas librerías.</p>
            
            <h3 style='color:#ff4444;'>4. LIMITACIÓN DE GARANTÍAS</h3>
            <p><i>EL SOFTWARE SE PROPORCIONA "TAL CUAL", SIN GARANTÍA DE NINGÚN TIPO, EXPRESA O IMPLÍCITA, 
            INCLUYENDO PERO NO LIMITADO A GARANTÍAS DE COMERCIALIZACIÓN, IDONEIDAD PARA UN PROPÓSITO 
            PARTICULAR Y NO INFRACCIÓN. EN NINGÚN CASO LOS AUTORES O TITULARES DE DERECHOS DE AUTOR 
            SERÁN RESPONSABLES DE NINGUNA RECLAMACIÓN, DAÑOS U OTRAS RESPONSABILIDADES.</i></p>
            
            <h3 style='color:#4CAF50;'>5. LICENCIA</h3>
            <p>BoxCraft Launcher está licenciado bajo la <b>GNU General Public License v3.0 (GPLv3)</b>.</p>
            
            <h3 style='color:#4CAF50;'>6. PRIVACIDAD</h3>
            <p>BoxCraft Launcher respeta tu privacidad. El software:</p>
            <ul>
                <li>No recopila ni transmite información personal</li>
                <li>No realiza seguimiento de tu actividad</li>
                <li>No incluye anuncios ni software de terceros con fines comerciales</li>
                <li>Solo accede a archivos locales necesarios para su funcionamiento a excepcion de la api de terceros de CurseForge</li>
            </ul>
            
            <h3 style='color:#4CAF50;'>7. CONTACTO Y APOYO</h3>
            <p>BoxCraft Launcher es un proyecto de código abierto mantenido por la comunidad. 
            El apoyo se proporciona en la medida de lo posible y no hay garantía de 
            tiempo de respuesta o resolución de problemas.</p>
            
            <p style='color:#ff4444; text-align:center; font-weight:bold;'>
            NOT ASSOCIATED OR APPROVED BY MOJANG
            </p>
        """)
        terms_content.setAlignment(Qt.AlignLeft)
        terms_content.setWordWrap(True)
        terms_content.setTextFormat(Qt.RichText)
        
        content_layout.addWidget(terms_content)
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area, 1)
        
        # Checkbox "No mostrar de nuevo"
        self.dont_show_checkbox = QCheckBox("No mostrar estos términos de nuevo")
        self.dont_show_checkbox.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.dont_show_checkbox)
        
        # Línea separadora
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #2d2d2d; margin: 10px 0;")
        layout.addWidget(separator)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Botón Rechazar (Rojo)
        reject_button = QPushButton("RECHAZAR")
        reject_button.setCursor(Qt.PointingHandCursor)
        reject_button.setFixedHeight(40)
        reject_button.setStyleSheet("""
            QPushButton {
                background-color: #BB5D5D;
                border: 3px solid;
                border-top-color: #CF6B6B;
                border-left-color: #CF6B6B;
                border-right-color: #8B3D3D;
                border-bottom-color: #8B3D3D;
                color: white;
                padding: 8px 30px;
                font-weight: bold;
                border-radius: 6px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #CF6B6B;
                border-top-color: #E27D7D;
                border-left-color: #E27D7D;
            }
        """)
        reject_button.clicked.connect(self.reject)
        
        # Botón Aceptar (Verde)
        accept_button = QPushButton("ACEPTAR")
        accept_button.setCursor(Qt.PointingHandCursor)
        accept_button.setFixedHeight(40)
        accept_button.setStyleSheet("""
            QPushButton {
                background-color: #5DBB63;
                border: 3px solid;
                border-top-color: #6BCF72;
                border-left-color: #6BCF72;
                border-right-color: #3D8B40;
                border-bottom-color: #3D8B40;
                color: white;
                padding: 8px 30px;
                font-weight: bold;
                border-radius: 6px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #6BCF72;
                border-top-color: #7DE285;
                border-left-color: #7DE285;
            }
        """)
        accept_button.clicked.connect(self.on_accept)
        
        button_layout.addWidget(reject_button)
        button_layout.addStretch()
        button_layout.addWidget(accept_button)
        
        layout.addLayout(button_layout)
    
    def on_accept(self):
        """Maneja la aceptación de los términos."""
        dont_show_again = self.dont_show_checkbox.isChecked()
        self.terms_accepted.emit(dont_show_again)
        self.accept()

# ============================================================================
# GESTOR DE TÉRMINOS
# ============================================================================

class TermsManager:
    """Maneja la aceptación y almacenamiento de términos y condiciones."""
    
    def __init__(self):
        self.config_file = CONFIG_FILE
    
    def should_show_terms(self) -> bool:
        """Verifica si se deben mostrar los términos."""
        if not self.config_file.exists():
            print(f"Archivo de configuración no existe: {self.config_file}")
            return True  # Mostrar si no existe configuración
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Verificar si los términos fueron aceptados
            terms_accepted = config.get('terms_accepted', False)
            dont_show_again = config.get('dont_show_terms_again', False)
            
            print(f"Configuración leída: terms_accepted={terms_accepted}, dont_show_again={dont_show_again}")
            
            # Mostrar términos si no están aceptados
            if not terms_accepted:
                print("Términos no aceptados, mostrando diálogo...")
                return True
            
            # Si están aceptados pero no marcó "no mostrar de nuevo", mostrar de nuevo
            if terms_accepted and not dont_show_again:
                print("Términos aceptados pero no marcó 'no mostrar de nuevo', mostrando diálogo...")
                return True
            
            print("Términos ya aceptados y marcados para no mostrar de nuevo, omitiendo...")
            return False
            
        except (json.JSONDecodeError, KeyError, IOError) as e:
            print(f"Error leyendo configuración: {e}")
            return True
    
    def save_terms_accepted(self, dont_show_again: bool):
        """Guarda la aceptación de términos."""
        try:
            config = {}
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                except (json.JSONDecodeError, IOError):
                    config = {}
            
            config['terms_accepted'] = True
            config['dont_show_terms_again'] = dont_show_again
            
            # Asegurarse de que el directorio existe
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            print(f"Términos guardados en {self.config_file}, dont_show_again={dont_show_again}")
            
        except Exception as e:
            print(f"Error guardando términos: {e}")
    
    def check_and_show_terms(self) -> bool:
        """Muestra el diálogo de términos si es necesario."""
        if not self.should_show_terms():
            return True  # Ya aceptados, no mostrar
        
        print("Creando diálogo de términos...")
        
        # Crear y mostrar el diálogo
        dialog = TermsDialog()
        dialog.setModal(True)
        
        # Variable para almacenar el resultado
        result = [False]  # Usamos lista para modificar desde closure
        
        # Conectar señal
        def on_terms_accepted(dont_show_again):
            print(f"Usuario aceptó términos, dont_show_again={dont_show_again}")
            self.save_terms_accepted(dont_show_again)
            result[0] = True
        
        dialog.terms_accepted.connect(on_terms_accepted)
        
        # Mostrar diálogo
        dialog.exec()
        
        # Verificar si el usuario cerró el diálogo sin aceptar
        if not result[0]:
            print("Usuario rechazó términos o cerró el diálogo")
            return False
        
        return True

# ============================================================================
# BARRA DE TÍTULO PERSONALIZADA
# ============================================================================

class TitleBar(QWidget):
    """Barra de título personalizada estilo Deepin DTK."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setup_ui()
        
        # Variables para arrastre de ventana
        self.drag_position = QPoint()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(5)
        
        # Espaciador izquierdo
        layout.addStretch(1)
        
        # Título de la aplicación (centro)
        self.title_label = QLabel(APP_NAME)
        self.title_label.setObjectName("TitleBarLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label, 2)  # Peso 2 para mantener centrado
        
        # Espaciador derecho
        layout.addStretch(1)
        
        # Botones de la barra de título (derecha)
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(2)
        
        # Botón minimizar
        self.minimize_button = QPushButton("━")
        self.minimize_button.setObjectName("TitleButton")
        self.minimize_button.setProperty("id", "MinimizeButton")
        self.minimize_button.setToolTip("Minimizar")
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.clicked.connect(self.minimize_window)
        
        # Botón cerrar
        self.close_button = QPushButton("✕")
        self.close_button.setObjectName("TitleButton")
        self.close_button.setProperty("id", "CloseButton")
        self.close_button.setToolTip("Cerrar")
        self.close_button.setFixedSize(30, 30)
        self.close_button.clicked.connect(self.close_window)
        
        button_layout.addWidget(self.minimize_button)
        button_layout.addWidget(self.close_button)
        
        layout.addWidget(button_container)
    
    def minimize_window(self):
        self.window().showMinimized()
    
    def close_window(self):
        self.window().close()
    
    # Funciones para arrastre de ventana
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

# ============================================================================
# CLASES DE CONFIGURACIÓN
# ============================================================================

class VersionConfig:
    """Maneja la configuración de una versión específica."""
    
    def __init__(self, version_name: str):
        self.version_name = version_name
        self.launch_args = ""
        self.load()
    
    def get_launch_args(self) -> str:
        return self.launch_args
    
    def set_launch_args(self, args: str):
        self.launch_args = args
    
    def config_path(self) -> Path:
        return VERSIONS_DIR / self.version_name / "boxcraft-config.txt"
    
    def save(self) -> bool:
        try:
            self.config_path().parent.mkdir(parents=True, exist_ok=True)
            self.config_path().write_text(self.launch_args)
            return True
        except Exception:
            return False
    
    def load(self) -> bool:
        try:
            if self.config_path().exists():
                self.launch_args = self.config_path().read_text().strip()
            return True
        except Exception:
            return False

# ============================================================================
# CLASES DE GESTIÓN
# ============================================================================

class VersionManager(QObject):
    """Gestiona las versiones de Minecraft instaladas."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_process = None
        self.cancelled = False
    
    def get_installed_versions(self) -> list:
        """Retorna lista de versiones instaladas."""
        if VERSIONS_DIR.exists():
            versions = []
            for d in VERSIONS_DIR.iterdir():
                if d.is_dir():
                    # Verificar si es una versión válida
                    lib_path = d / "lib" / "x86_64" / "libminecraftpe.so"
                    if lib_path.exists():
                        versions.append(d.name)
            return sorted(versions)  # Ordenar alfabéticamente
        return []
    
    def get_version_path(self, version_name: str) -> Path:
        """Retorna la ruta de una versión."""
        return VERSIONS_DIR / version_name
    
    def is_version_valid(self, version_name: str) -> bool:
        """Verifica si una versión es válida."""
        lib_path = self.get_version_path(version_name) / "lib" / "x86_64" / "libminecraftpe.so"
        return lib_path.exists()
    
    def extract_apk(self, apk_path: str, version_name: str, progress_dialog=None) -> Tuple[bool, str]:
        """Extrae un APK a una nueva versión."""
        dest_dir = self.get_version_path(version_name)
        
        try:
            # Limpiar directorio si existe
            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Verificar que el extractor existe
            if not MCPELAUNCHER_EXTRACT.exists():
                return False, "mcpelauncher-extract no encontrado en resources/"
            
            self.cancelled = False
            
            # Ejecutar extractor
            self.current_process = subprocess.Popen(
                [str(MCPELAUNCHER_EXTRACT), apk_path, str(dest_dir)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid
            )
            
            # Monitorear progreso
            while self.current_process.poll() is None:
                QCoreApplication.processEvents()
                QThread.msleep(100)
                
                # Verificar si se canceló
                if self.cancelled:
                    self.kill_extraction_process()
                    return False, "Cancelado por el usuario"
            
            if self.current_process.returncode == 0:
                return True, f"Versión {version_name} extraída exitosamente"
            else:
                error = self.current_process.stderr.read() or "Error desconocido"
                return False, f"Error en extracción: {error}"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            self.current_process = None
    
    def kill_extraction_process(self):
        """Mata el proceso de extracción actual."""
        if self.current_process and self.current_process.poll() is None:
            try:
                os.killpg(os.getpgid(self.current_process.pid), signal.SIGTERM)
                self.current_process.wait(timeout=2)
            except:
                try:
                    os.killpg(os.getpgid(self.current_process.pid), signal.SIGKILL)
                except:
                    pass
    
    def cancel_extraction(self):
        """Cancela la extracción actual."""
        self.cancelled = True
        self.kill_extraction_process()
    
    def delete_version(self, version_name: str) -> Tuple[bool, str]:
        """Elimina una versión."""
        version_path = self.get_version_path(version_name)
        try:
            if version_path.exists():
                shutil.rmtree(version_path)
                return True, f"Versión {version_name} eliminada"
            else:
                return False, f"La versión {version_name} no existe"
        except Exception as e:
            return False, f"No se pudo eliminar: {str(e)}"

class PackInstaller:
    """Instala packs de recursos y mundos."""
    
    def __init__(self):
        self.base_game_dir = GAMES_DIR
    
    def get_target_name(self, source_path: str) -> str:
        return Path(source_path).name
    
    def item_exists(self, source_path: str, target_subdir: str) -> bool:
        target_dir = self.base_game_dir / target_subdir
        final_dest = target_dir / self.get_target_name(source_path)
        return final_dest.exists()
    
    def install_item(self, source_path: str, target_subdir: str, force_overwrite: bool = False) -> Tuple[bool, str]:
        source = Path(source_path)
        if not source.exists():
            return False, "La ruta seleccionada no existe"
        
        target_dir = self.base_game_dir / target_subdir
        target_dir.mkdir(parents=True, exist_ok=True)
        
        final_dest = target_dir / source.name
        
        if final_dest.exists():
            if not force_overwrite:
                return False, "El elemento ya existe"
            
            # Eliminar existente
            try:
                if final_dest.is_dir():
                    shutil.rmtree(final_dest)
                else:
                    final_dest.unlink()
            except Exception as e:
                return False, f"No se pudo eliminar existente: {str(e)}"
        
        try:
            if source.is_dir():
                shutil.copytree(source, final_dest)
            else:
                shutil.copy2(source, final_dest)
            return True, f"Instalado en {target_subdir}"
        except Exception as e:
            return False, f"Error al copiar: {str(e)}"

class GameLauncher:
    """Lanza Minecraft y otras herramientas."""
    
    def __init__(self):
        self.current_process = None
        self.monitor_timer = None
    
    def launch_game(self, version_name: str) -> Tuple[bool, str]:
        vm = VersionManager()
        version_path = vm.get_version_path(version_name)
        
        # Verificar que el cliente existe
        if not MCPELAUNCHER_CLIENT.exists():
            return False, "mcpelauncher-client no encontrado en resources/"
        
        # Verificar que la versión existe
        if not version_path.exists():
            return False, f"La versión {version_name} no existe"
        
        # Leer argumentos adicionales
        config = VersionConfig(version_name)
        extra_env = config.get_launch_args()
        
        try:
            if extra_env:
                # Ejecutar con variables de entorno adicionales
                env = os.environ.copy()
                # Parsear variables de entorno
                env_vars = {}
                for item in extra_env.split():
                    if "=" in item:
                        key, value = item.split("=", 1)
                        env_vars[key] = value
                env.update(env_vars)
                self.current_process = subprocess.Popen(
                    [str(MCPELAUNCHER_CLIENT), "-dg", str(version_path)],
                    env=env,
                    preexec_fn=os.setsid
                )
            else:
                self.current_process = subprocess.Popen(
                    [str(MCPELAUNCHER_CLIENT), "-dg", str(version_path)],
                    preexec_fn=os.setsid
                )
            
            # Iniciar monitoreo del proceso
            self.start_monitoring(version_name)
            
            return True, f"Iniciando Minecraft {version_name}..."
        except Exception as e:
            return False, f"Error al lanzar: {str(e)}"
    
    def start_monitoring(self, version_name):
        """Inicia el monitoreo del proceso del juego."""
        if self.monitor_timer:
            self.monitor_timer.stop()
        
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(lambda: self.check_game_status(version_name))
        self.monitor_timer.start(2000)  # Verificar cada 2 segundos
    
    def check_game_status(self, version_name):
        """Verifica si el juego sigue corriendo."""
        if self.current_process and self.current_process.poll() is not None:
            # El juego terminó
            self.monitor_timer.stop()
            self.current_process = None
            
            # Mostrar la ventana principal
            app = QApplication.instance()
            if app:
                for widget in app.topLevelWidgets():
                    if isinstance(widget, BoxCraftLauncher):
                        widget.show()
                        
                        # Enviar notificación
                        self.send_desktop_notification(
                            "BoxCraft Launcher",
                            f"Minecraft {version_name} ha terminado.\nEl launcher está disponible de nuevo."
                        )
                        break
    
    def send_desktop_notification(self, title, message):
        """Envía una notificación al escritorio."""
        try:
            subprocess.run([
                "notify-send", 
                "-i", "minecraft",
                title,
                message,
                "-t", "3000"
            ])
        except Exception:
            pass

class Exporter(QObject):
    """Exporta e importa versiones."""
    
    export_finished = Signal(bool, str)
    import_finished = Signal(bool, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def export_version(self, version_name: str, parent_widget):
        """Exporta una versión a archivo TAR."""
        vm = VersionManager()
        version_path = vm.get_version_path(version_name)
        
        if not version_path.exists():
            QMessageBox.critical(parent_widget, "Error", "La versión no existe")
            return
        
        # Preguntar si incluir datos del APK
        reply = QMessageBox.question(
            parent_widget,
            "Exportar versión",
            f"¿Exportar '{version_name}' con datos del APK?\n\n"
            "Sí: Incluye la versión completa (datos del juego).\n"
            "No: Solo exporta mods, mapas, etc.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        export_with_apk = reply == QMessageBox.Yes
        
        # Seleccionar archivo de destino
        file_path, _ = QFileDialog.getSaveFileName(
            parent_widget,
            "Guardar como archivo",
            f"{version_name}.tar.gz",
            "Archivos TAR (*.tar.gz);;Todos los archivos (*)"
        )
        
        if not file_path:
            return
        
        # Diálogo de progreso
        progress_dialog = QDialog(parent_widget)
        progress_dialog.setWindowTitle("Exportando...")
        progress_dialog.setFixedSize(300, 100)
        
        layout = QVBoxLayout(progress_dialog)
        label = QLabel("Exportando versión...")
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 0)  # Indefinido
        
        layout.addWidget(label)
        layout.addWidget(progress_bar)
        progress_dialog.show()
        QApplication.processEvents()
        
        # Crear directorio temporal
        temp_dir = Path(tempfile.gettempdir()) / f"boxcraft_export_{version_name}"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True)
        
        export_dir = temp_dir / f"boxcraft_export_{version_name}"
        export_dir.mkdir(parents=True)
        
        try:
            # Copiar version_content si se incluye
            if export_with_apk:
                version_content_dest = export_dir / "version_content"
                shutil.copytree(version_path, version_content_dest)
            
            # Copiar games/com.mojang
            games_dest = export_dir / "games"
            if GAMES_DIR.exists():
                shutil.copytree(GAMES_DIR, games_dest)
            
            # Comprimir con tar
            with tarfile.open(file_path, "w:gz") as tar:
                tar.add(export_dir, arcname=".")
            
            # Limpiar
            shutil.rmtree(temp_dir)
            progress_dialog.close()
            self.export_finished.emit(True, f"Versión {version_name} exportada como {file_path}")
            
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            progress_dialog.close()
            self.export_finished.emit(False, f"Error en exportación: {str(e)}")
    
    def import_version(self, parent_widget):
        """Importa una versión desde archivo TAR."""
        file_path, _ = QFileDialog.getOpenFileName(
            parent_widget,
            "Seleccionar archivo TAR",
            "",
            "Archivos TAR (*.tar.gz *.tar);;Todos los archivos (*)"
        )
        
        if not file_path:
            return
        
        file_name = Path(file_path).stem
        
        # Verificar si ya existen
        dest_version_dir = VERSIONS_DIR / file_name
        dest_games_dir = GAMES_DIR
        
        version_exists = dest_version_dir.exists()
        games_exists = GAMES_DIR.exists() and any(GAMES_DIR.iterdir())
        
        if version_exists or games_exists:
            reply = QMessageBox.warning(
                parent_widget,
                "Advertencia",
                f"¡Este proceso puede tardar!\n¿Quiere continuar?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Diálogo de progreso
        progress_dialog = QDialog(parent_widget)
        progress_dialog.setWindowTitle("Importando...")
        progress_dialog.setFixedSize(300, 100)
        
        layout = QVBoxLayout(progress_dialog)
        label = QLabel("Importando versión...")
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 0)
        
        layout.addWidget(label)
        layout.addWidget(progress_bar)
        progress_dialog.show()
        QApplication.processEvents()
        
        # Directorio temporal
        temp_dir = Path(tempfile.gettempdir()) / f"boxcraft_import_{file_name}"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True)
        
        try:
            # Extraer tar
            with tarfile.open(file_path, "r:*") as tar:
                tar.extractall(temp_dir)
            
            # Buscar directorios
            version_content_path = None
            games_path = None
            
            for root, dirs, _ in os.walk(temp_dir):
                if "version_content" in dirs:
                    version_content_path = Path(root) / "version_content"
                if "games" in dirs:
                    games_path = Path(root) / "games"
            
            # Mover contenido
            if version_content_path and version_content_path.exists():
                if version_exists:
                    shutil.rmtree(dest_version_dir, ignore_errors=True)
                dest_version_dir.mkdir(parents=True, exist_ok=True)
                
                for item in version_content_path.iterdir():
                    dest_item = dest_version_dir / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest_item)
                    else:
                        shutil.copy2(item, dest_item)
            
            if games_path and games_path.exists():
                games_com_mojang = games_path / "com.mojang"
                if games_com_mojang.exists():
                    if games_exists:
                        shutil.rmtree(GAMES_DIR, ignore_errors=True)
                    shutil.copytree(games_com_mojang, GAMES_DIR)
            
            # Limpiar
            shutil.rmtree(temp_dir)
            progress_dialog.close()
            self.import_finished.emit(True, f"Versión {file_name} importada correctamente")
            
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            progress_dialog.close()
            self.import_finished.emit(False, f"Error en importación: {str(e)}")

# ============================================================================
# DIÁLOGOS
# ============================================================================

class ExtractDialog(QDialog):
    """Diálogo para extraer nueva versión desde APK."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.apk_path = ""
        self.version_name = ""
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Nueva versión desde APK")
        self.resize(400, 200)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("Extraer nueva versión desde APK")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)
        
        # Selector de APK
        apk_group = QGroupBox("Archivo APK")
        apk_layout = QVBoxLayout(apk_group)
        
        apk_button = QPushButton("Seleccionar APK...")
        apk_button.setObjectName("SecondaryButton")
        self.apk_label = QLabel("Ningún archivo seleccionado")
        self.apk_label.setWordWrap(True)
        self.apk_label.setStyleSheet("color: #888888;")
        apk_button.clicked.connect(self.select_apk)
        
        apk_layout.addWidget(apk_button)
        apk_layout.addWidget(self.apk_label)
        
        layout.addWidget(apk_group)
        
        # Nombre de versión
        name_group = QGroupBox("Nombre de la versión")
        name_layout = QVBoxLayout(name_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ejemplo: 1.21.0")
        self.name_edit.textChanged.connect(self.on_name_changed)
        
        name_layout.addWidget(self.name_edit)
        layout.addWidget(name_group)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("Extraer")
        ok_button.setObjectName("PrimaryButton")
        ok_button.clicked.connect(self.on_accept)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #BB5D5D;
                border: 3px solid;
                border-top-color: #CF6B6B;
                border-left-color: #CF6B6B;
                border-right-color: #8B3D3D;
                border-bottom-color: #8B3D3D;
                color: white;
                padding: 5px 5px;
                font-size: 18px;
                font-weight: bold;
                border-radius: 6px;
                text-shadow: 1px 1px 0 #8B3D3D;
                image: none;
            }
            QPushButton:hover {
                background-color: #CF6B6B;
                border-top-color: #E27D7D;
                border-left-color: #E27D7D;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #AF4C4C;
                transform: translateY(1px);
                border-top-color: #BB5D5D;
                border-left-color: #BB5D5D;
            }
        """)
        
        cancel_button = QPushButton("Cancelar")
        cancel_button.setObjectName("SecondaryButton")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #5DBB63;
                border: 3px solid;
                border-top-color: #6BCF72;
                border-left-color: #6BCF72;
                border-right-color: #3D8B40;
                border-bottom-color: #3D8B40;
                color: white;
                padding: 5px 5px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 6px;
                text-shadow: 1px 1px 0 #3D8B40;
                image: none;
            }
            QPushButton:hover {
                background-color: #6BCF72;
                border-top-color: #7DE285;
                border-left-color: #7DE285;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #4CAF50;
                transform: translateY(1px);
                border-top-color: #5DBB63;
                border-left-color: #5DBB63;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
    
    def select_apk(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar APK de Minecraft", 
            str(Path.home()), "Archivos APK (*.apk)"
        )
        if file_path:
            self.apk_path = file_path
            self.apk_label.setText(f"📁 {Path(file_path).name}")
            self.apk_label.setStyleSheet("color: #4CAF50;")
            
            # Sugerir nombre basado en el archivo
            if not self.name_edit.text():
                suggested_name = Path(file_path).stem.replace("_", ".")
                self.name_edit.setText(suggested_name)
    
    def on_name_changed(self, text):
        self.version_name = text.strip()
    
    def on_accept(self):
        if not self.apk_path:
            QMessageBox.warning(self, "Error", "Debes seleccionar un archivo APK")
            return
        if not self.version_name:
            QMessageBox.warning(self, "Error", "Debes ingresar un nombre para la versión")
            return
        
        # Verificar si ya existe la versión
        if (VERSIONS_DIR / self.version_name).exists():
            reply = QMessageBox.question(
                self,
                "Versión existente",
                f"Ya existe una versión llamada '{self.version_name}'.\n¿Deseas reemplazarla?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        self.accept()
    
    def get_apk_path(self):
        return self.apk_path
    
    def get_version_name(self):
        return self.version_name

# ============================================================================
# PÁGINAS EXTERNAS
# ============================================================================

class PageLoader:
    """Carga páginas desde módulos externos."""
    
    @staticmethod
    def load_page(page_name: str, main_window=None):
        """Carga una página desde el archivo correspondiente."""
        page_path = PAGES_DIR / f"{page_name}.py"
        
        if not page_path.exists():
            # Si no existe la página, crear widget de respaldo
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.addWidget(QLabel(f"Página {page_name} no encontrada"))
            return widget
        
        try:
            # Crear un namespace para el módulo
            module_globals = {
                # Variables globales
                'APP_NAME': APP_NAME,
                'APP_VERSION': APP_VERSION,
                'BASE_DIR': BASE_DIR,
                'RESOURCES_DIR': RESOURCES_DIR,
                'MCPELAUNCHER_DIR': MCPELAUNCHER_DIR,
                'VERSIONS_DIR': VERSIONS_DIR,
                'GAMES_DIR': GAMES_DIR,
                'CONFIG_FILE': CONFIG_FILE,
                
                # Clases principales
                'QWidget': QWidget,
                'QTextEdit': QTextEdit,
                'QVBoxLayout': QVBoxLayout,
                'QHBoxLayout': QHBoxLayout,
                'QScrollArea': QScrollArea,
                'QThread': QThread,
                'Signal': Signal,
                'QSize': QSize,
                'QPixmap': QPixmap,
                'QImage': QImage,
                'QIcon': QIcon,
                'QPainter': QPainter,
                'QBrush': QBrush,
                'QColor': QColor,
                'QGridLayout': QGridLayout,
                'QLabel': QLabel,
                'QPushButton': QPushButton,
                'QListWidget': QListWidget,
                'QListWidgetItem': QListWidgetItem,
                'QFrame': QFrame,
                'QGroupBox': QGroupBox,
                'QTabWidget': QTabWidget,
                'QComboBox': QComboBox,
                'QLineEdit': QLineEdit,
                'QProgressBar': QProgressBar,
                'QDialog': QDialog,
                'QMessageBox': QMessageBox,
                'QFileDialog': QFileDialog,
                'QApplication': QApplication,
                'QTimer': QTimer,

                # Módulos necesarios
                'requests': requests,
                'tempfile': tempfile,
                'zipfile': zipfile,
                
                # Constantes de Qt
                'Qt': Qt,
                'AlignmentFlag': Qt.AlignmentFlag,
                'QSizePolicy': QSizePolicy,
                'Policy': QSizePolicy.Policy,

                # Utilidades
                'Path': Path,
                'shutil': shutil,
                'json': json,
                'subprocess': subprocess,
                'os': os,
                
                # Clases personalizadas
                'VersionManager': VersionManager,
                'GameLauncher': GameLauncher,
                'Exporter': Exporter,
                'ExtractDialog': ExtractDialog,
                'PackInstaller': PackInstaller,
                'VersionConfig': VersionConfig,
                
                # Referencia a la ventana principal
                'main_window': main_window
            }
            
            # Ejecutar el código de la página
            with open(page_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Crear un widget contenedor
            page_widget = QWidget()
            # Inyectar page_widget en el namespace
            module_globals['page_widget'] = page_widget
            
            # Ejecutar el código
            exec(code, module_globals)
            
            return page_widget
            
        except Exception as e:
            import traceback
            print(f"Error cargando página {page_name}: {e}")
            print(traceback.format_exc())
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.addWidget(QLabel(f"Error cargando página: {str(e)}"))
            return widget

# ============================================================================
# VENTANA PRINCIPAL
# ============================================================================

class BoxCraftLauncher(QMainWindow):
    """Ventana principal del launcher."""
    
    def __init__(self):
        super().__init__()
        # Quitar barra de título del sistema
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        self.exporter = Exporter()
        self.current_version = None
        self.setup_ui()
        self.setup_connections()
        self.load_fonts()
        self.load_page("start-page")
    
    def setup_ui(self):
        self.setWindowTitle(f"{APP_NAME}")
        self.resize(1100, 700)
        self.setStyleSheet(STYLE_CSS)
        
        # Crear widget central
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #1a1a1a; border-radius: 0 0 12px 12px;")
        self.setCentralWidget(central_widget)
        
        # Layout principal con barra de título
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ===== BARRA DE TÍTULO PERSONALIZADA =====
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        # Contenedor para el resto de la interfaz
        content_container = QWidget()
        content_container.setStyleSheet("background-color: #1a1a1a;")
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # ===== BARRA LATERAL IZQUIERDA (PESTAÑAS) =====
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(70)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(4, 20, 4, 20)
        sidebar_layout.setSpacing(2)
        
        # Logo en la parte superior de la barra lateral
        logo_path = RESOURCES_DIR / "logo.png"
        if logo_path.exists():
            logo_label = QLabel()
            logo_label.setAlignment(Qt.AlignCenter)
            pixmap = QPixmap(str(logo_path))
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
                logo_label.setStyleSheet("""
                    background-color: #1a1a1a;
                    border-radius: 8px;
                    padding: 5px;
                    margin-bottom: 20px;
                """)
            else:
                # Fallback si no se puede cargar la imagen
                logo_label.setText("BC")
                logo_label.setStyleSheet("""
                    font-size: 24px;
                    font-weight: bold;
                    color: #4CAF50;
                    padding: 10px;
                    background-color: #1a1a1a;
                    border-radius: 8px;
                    margin-bottom: 20px;
                """)
        else:
            # Fallback si el archivo no existe
            logo_label = QLabel("BC")
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setStyleSheet("""
                font-size: 24px;
                font-weight: bold;
                color: #4CAF50;
                padding: 10px;
                background-color: #1a1a1a;
                border-radius: 8px;
                margin-bottom: 20px;
            """)
        
        sidebar_layout.addWidget(logo_label)
        
        # Botones de pestañas (solo iconos)
        self.tab_buttons = QButtonGroup()
        # ELIMINADO: "⬇️", "dl-page", "Descargar Mods"
        tab_data = [
            ("🎮", "start-page", "Jugar / Versiones"),
            ("📦", "conts-page", "Contenido y Mods"),
            ("⬇️", "dl-page", "Descargar Mods"),
            ("⚙️", "config-page", "Configuración"),
            ("ℹ️", "about-page", "Acerca de")
        ]
        
        for icon, page_name, tooltip in tab_data:
            btn = QPushButton(icon)
            btn.setObjectName("TabButton")
            btn.setCheckable(True)
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("page_name", page_name)
            btn.clicked.connect(lambda checked, p=page_name: self.load_page(p))
            self.tab_buttons.addButton(btn)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        # Footer con versión
        footer_label = QLabel(f"v{APP_VERSION}")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: #666666; font-size: 10px; padding: 5px;")
        sidebar_layout.addWidget(footer_label)
        
        content_layout.addWidget(sidebar)
        
        # ===== CONTENIDO PRINCIPAL =====
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #1a1a1a;")
        content_inner_layout = QVBoxLayout(content_widget)
        content_inner_layout.setContentsMargins(0, 0, 0, 0)
        
        header = QWidget()
        header.setObjectName("Header")
        header.setFixedHeight(70)  # Aumenta la altura para más espacio
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)  # Aumenta margen vertical
        
        self.header_label = QLabel("BOX CRAFT LAUNCHER")
        self.header_label.setObjectName("HeaderLabel")
        self.header_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Centra verticalmente
        header_layout.addWidget(self.header_label)
        header_layout.addStretch()
        
        content_inner_layout.addWidget(header)
        
        # Stacked widget para las páginas
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #1a1a1a;")
        content_inner_layout.addWidget(self.stacked_widget)
        
        content_layout.addWidget(content_widget)
        
        main_layout.addWidget(content_container)
        
        # Establecer pestaña inicial
        if self.tab_buttons.buttons():
            self.tab_buttons.buttons()[0].setChecked(True)
        self.header_label.setText("VERSIONES INSTALADAS")
    
    def load_fonts(self):
        """Carga fuentes personalizadas."""
        if FONTS_DIR.exists():
            for font_file in FONTS_DIR.glob("*.ttf"):
                try:
                    font_id = QFontDatabase.addApplicationFont(str(font_file))
                    if font_id != -1:
                        print(f"Fuente cargada: {font_file.name}")
                except Exception as e:
                    print(f"Error cargando fuente {font_file}: {e}")
    
    def setup_connections(self):
        """Conecta todas las señales."""
        # Exportador
        self.exporter.export_finished.connect(self.on_export_finished)
        self.exporter.import_finished.connect(self.on_import_finished)
    
    def load_page(self, page_name: str):
        """Carga una página en el stacked widget."""
        # Limpiar stacked widget
        while self.stacked_widget.count():
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        
        # Cargar nueva página
        page_widget = PageLoader.load_page(page_name, self)
        if page_widget:
            self.stacked_widget.addWidget(page_widget)
        
        # Actualizar header
        headers = {
            "start-page": "VERSIONES INSTALADAS",
            "conts-page": "GESTOR DE CONTENIDO",
            "dl-page": "DESCARGAR MODS",
            "config-page": "CONFIGURACIÓN",
            "about-page": "ACERCA DE"
        }
        self.header_label.setText(headers.get(page_name, "BOX CRAFT LAUNCHER"))
    
    def on_export_finished(self, success, message):
        """Maneja finalización de exportación."""
        # Crear diálogo personalizado
        dialog = QDialog(self)
        
        if success:
            dialog.setWindowTitle("Exportación completada")
            dialog.setFixedSize(400, 180)
            icon_style = "✅"
            text_color = "#4CAF50"
        else:
            dialog.setWindowTitle("Error en exportación")
            dialog.setFixedSize(450, 200)
            icon_style = "❌"
            text_color = "#FF6B6B"
        
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        label = QLabel(f"{icon_style} {message}")
        label.setStyleSheet(f"color: {text_color}; font-size: 14px;")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        layout.addStretch()
        
        ok_btn = QPushButton("✅ Aceptar")
        ok_btn.setMinimumHeight(40)
        ok_btn.setStyleSheet("""
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
        
        def on_ok():
            dialog.accept()
        
        ok_btn.clicked.connect(on_ok)
        layout.addWidget(ok_btn)
        
        dialog.exec()

    def on_import_finished(self, success, message):
        """Maneja finalización de importación."""
        # Crear diálogo personalizado (código idéntico al anterior)
        dialog = QDialog(self)
        
        if success:
            dialog.setWindowTitle("Importación completada")
            dialog.setFixedSize(400, 180)
            icon_style = "✅"
            text_color = "#4CAF50"
        else:
            dialog.setWindowTitle("Error en importación")
            dialog.setFixedSize(450, 200)
            icon_style = "❌"
            text_color = "#FF6B6B"
        
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        label = QLabel(f"{icon_style} {message}")
        label.setStyleSheet(f"color: {text_color}; font-size: 14px;")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        layout.addStretch()
        
        ok_btn = QPushButton("✅ Aceptar")
        ok_btn.setMinimumHeight(40)
        ok_btn.setStyleSheet("""
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
        
        def on_ok():
            dialog.accept()
        
        ok_btn.clicked.connect(on_ok)
        layout.addWidget(ok_btn)
        
        dialog.exec()
    
    # Sobrescribir métodos para manejar bordes redondeados con barra de título personalizada
    def paintEvent(self, event):
        """Pintar bordes redondeados para la ventana."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor("#1a1a1a")))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 12, 12)

# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

def handle_command_line():
    """Maneja argumentos de línea de comandos."""
    import argparse
    
    parser = argparse.ArgumentParser(description='BoxCraft Launcher')
    parser.add_argument('--launch', help='Launch a specific version')
    parser.add_argument('--version', action='store_true', help='Show version')
    
    args = parser.parse_args()
    
    if args.version:
        print(f"BoxCraft Launcher v{APP_VERSION}")
        sys.exit(0)
    
    if args.launch:
        launcher = GameLauncher()
        success, message = launcher.launch_game(args.launch)
        if success:
            print(f"Launching Minecraft {args.launch}...")
        else:
            print(f"Error: {message}")
        sys.exit(0 if success else 1)
    
    return True

def main():
    """Función principal."""
    # Manejar línea de comandos
    if not handle_command_line():
        return
    
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setApplicationDisplayName(APP_NAME)
    
    # Establecer estilo de aplicación
    app.setStyle("Fusion")
    
    # Añadir mensaje de inicio
    print(f"Iniciando {APP_NAME} v{APP_VERSION}")
    
    # Crear directorios necesarios
    for directory in [RESOURCES_DIR, PAGES_DIR, FONTS_DIR, VERSIONS_DIR, GAMES_DIR, MCPELAUNCHER_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Directorio verificado/creado: {directory}")
    
    # Verificar ejecutables mcpelauncher
    if not MCPELAUNCHER_CLIENT.exists():
        print(f"ADVERTENCIA: mcpelauncher-client no encontrado en {RESOURCES_DIR}/")
        print("Por favor, coloca mcpelauncher-client en la carpeta resources/")
    
    if not MCPELAUNCHER_EXTRACT.exists():
        print(f"ADVERTENCIA: mcpelauncher-extract no encontrado en {RESOURCES_DIR}/")
        print("Por favor, coloca mcpelauncher-extract en la carpeta resources/")
    
    print("Verificando términos y condiciones...")
    
    # Verificar y mostrar términos ANTES de cualquier otra cosa
    terms_manager = TermsManager()
    
    # Forzar mostrar términos (para pruebas - descomentar si es necesario)
    # if CONFIG_FILE.exists():
    #     backup = CONFIG_FILE.with_suffix('.json.backup')
    #     import shutil
    #     shutil.copy2(CONFIG_FILE, backup)
    #     CONFIG_FILE.unlink()
    #     print(f"Archivo de configuración borrado para pruebas: {CONFIG_FILE}")
    
    if not terms_manager.check_and_show_terms():
        # Si el usuario rechazó los términos, cerrar la aplicación
        print("Aplicación cerrada por rechazo de términos")
        sys.exit(0)
    
    print("Términos aceptados, creando ventana principal...")
    
    # Crear y mostrar ventana principal
    window = BoxCraftLauncher()
    window.show()
    
    print("Aplicación iniciada correctamente")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
