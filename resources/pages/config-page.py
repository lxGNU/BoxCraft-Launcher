# Página de configuración
import json
from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QGroupBox, QLineEdit, QPushButton, 
    QListWidget, QListWidgetItem, QMessageBox, QWidget, 
    QHBoxLayout, QDialog, QSizePolicy, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QSize, Signal
from pathlib import Path

# Configurar rutas
CONFIG_FILE = Path.home() / ".config" / "boxcraft-launcher" / "config.json"

# Clase VersionConfig
class VersionConfig:
    def __init__(self, version_name):
        self.version_name = version_name
        self.config_dir = Path.home() / ".config" / "boxcraft-launcher" / "versions"
        self.config_file = self.config_dir / f"{version_name}.json"
        self.args = ""
        self.load()
    
    def set_launch_args(self, args):
        self.args = args
    
    def get_launch_args(self):
        return self.args
    
    def save(self):
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            data = {"launch_args": self.args}
            with open(self.config_file, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error guardando configuración: {e}")
            return False
    
    def load(self):
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    data = json.load(f)
                    self.args = data.get("launch_args", "")
        except:
            self.args = ""

class VersionConfigDialog(QDialog):
    """Diálogo para configurar argumentos de lanzamiento de una versión."""
    
    config_saved = Signal(str, str)  # version_name, args
    
    def __init__(self, version_name, parent=None):
        super().__init__(parent)
        self.version_name = version_name
        self.setup_ui()
        self.load_current_config()
        
    def setup_ui(self):
        self.setWindowTitle(f"Configurar {self.version_name}")
        self.setFixedSize(500, 350)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                border-radius: 12px;
                border: 1px solid #2d2d2d;
            }
            QLabel {
                color: #cccccc;
            }
        """)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        title_label = QLabel(f"⚙️ Configurar versión: {self.version_name}")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #4CAF50;
                margin-bottom: 5px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #2d2d2d;")
        layout.addWidget(separator)
        
        # Área de scroll para contenido
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)
        
        # Widget de contenido
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)
        
        # Instrucciones
        instructions_label = QLabel("Argumentos de lanzamiento adicionales:")
        instructions_label.setStyleSheet("color: #cccccc;")
        content_layout.addWidget(instructions_label)
        
        # Ejemplos
        examples_label = QLabel("Ejemplos:\n• VARIABLE=valor\n• LD_LIBRARY_PATH=/ruta/lib\n• MESA_GL_VERSION_OVERRIDE=4.5")
        examples_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 12px;
                background-color: #252525;
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #2d2d2d;
            }
        """)
        examples_label.setWordWrap(True)
        content_layout.addWidget(examples_label)
        
        # Campo de texto para argumentos
        self.args_edit = QLineEdit()
        self.args_edit.setPlaceholderText("Deja vacío si no necesitas argumentos adicionales")
        self.args_edit.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #2d2d2d;
                border-radius: 6px;
                padding: 10px;
                color: white;
                font-size: 13px;
                margin-top: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        content_layout.addWidget(self.args_edit)
        
        content_layout.addStretch()
        
        # Establecer widget de contenido
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area, 1)
        
        # Separador
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setStyleSheet("background-color: #2d2d2d; margin-top: 10px;")
        layout.addWidget(separator2)
        
        # Botones - CORREGIDO: Cancelar a la izquierda, Guardar a la derecha
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Botón Cancelar (izquierda)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setObjectName("CancelButton")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #BB5D5D;
                border: 3px solid;
                border-top-color: #CF6B6B;
                border-left-color: #CF6B6B;
                border-right-color: #8B3D3D;
                border-bottom-color: #8B3D3D;
                color: white;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #CF6B6B;
                border-top-color: #E27D7D;
                border-left-color: #E27D7D;
            }
            QPushButton:pressed {
                background-color: #AF4C4C;
                border-top-color: #BB5D5D;
                border-left-color: #BB5D5D;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        # Espaciador para empujar el botón Guardar a la derecha
        button_layout.addStretch()
        
        # Botón Guardar (derecha) - CAMBIADO: Solo dice "Guardar"
        save_btn = QPushButton("💾 Guardar")
        save_btn.setObjectName("SaveButton")
        save_btn.clicked.connect(self.save_config)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5DBB63;
                border: 3px solid;
                border-top-color: #6BCF72;
                border-left-color: #6BCF72;
                border-right-color: #3D8B40;
                border-bottom-color: #3D8B40;
                color: white;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #6BCF72;
                border-top-color: #7DE285;
                border-left-color: #7DE285;
            }
            QPushButton:pressed {
                background-color: #4CAF50;
                border-top-color: #5DBB63;
                border-left-color: #5DBB63;
            }
        """)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
    def load_current_config(self):
        """Carga la configuración actual de la versión."""
        config = VersionConfig(self.version_name)
        current_args = config.get_launch_args()
        self.args_edit.setText(current_args)
        
    def save_config(self):
        """Guarda la configuración."""
        args = self.args_edit.text().strip()
        config = VersionConfig(self.version_name)
        config.set_launch_args(args)
        
        if config.save():
            self.config_saved.emit(self.version_name, args)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar la configuración")

layout = QVBoxLayout(page_widget)
layout.setContentsMargins(20, 20, 20, 20)

title_label = QLabel("⚙️ Configuración de Versiones")
title_label.setStyleSheet("""
    QLabel {
        font-size: 22px;
        font-weight: bold;
        color: #4CAF50;
        margin-bottom: 5px;
    }
""")
layout.addWidget(title_label)

subtitle_label = QLabel("Configura argumentos y establece versión predeterminada")
subtitle_label.setStyleSheet("color: #888888; margin-bottom: 20px;")
layout.addWidget(subtitle_label)

# Separador
separator = QFrame()
separator.setFrameShape(QFrame.HLine)
separator.setStyleSheet("background-color: #2d2d2d; margin-bottom: 15px;")
layout.addWidget(separator)

# Información sobre versión predeterminada actual
default_info_widget = QWidget()
default_info_layout = QHBoxLayout(default_info_widget)
default_info_layout.setContentsMargins(0, 0, 0, 0)

default_info_label = QLabel("Versión predeterminada actual:")
default_info_label.setStyleSheet("color: #cccccc;")

default_info_value = QLabel("Cargando...")
default_info_value.setStyleSheet("""
    QLabel {
        color: #4CAF50;
        font-weight: bold;
        background-color: #2d2d2d;
        padding: 6px 12px;
        border-radius: 6px;
        border: 1px solid #3d3d3d;
        margin-left: 10px;
    }
""")

default_info_layout.addWidget(default_info_label)
default_info_layout.addWidget(default_info_value)
default_info_layout.addStretch()

layout.addWidget(default_info_widget)

# Espaciador
layout.addSpacing(10)

# Grupo de lista de versiones
versions_group = QGroupBox("Versiones instaladas")
versions_layout = QVBoxLayout(versions_group)

# Descripción
desc_label = QLabel("Para cada versión puedes configurar argumentos o establecerla como predeterminada:")
desc_label.setStyleSheet("color: #cccccc; margin-bottom: 10px;")
versions_layout.addWidget(desc_label)

# Contenedor para la lista (con scroll si es necesario)
list_scroll_area = QScrollArea()
list_scroll_area.setWidgetResizable(True)
list_scroll_area.setStyleSheet("""
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    QScrollArea > QWidget > QWidget {
        background-color: transparent;
    }
""")

list_container = QWidget()
list_container_layout = QVBoxLayout(list_container)
list_container_layout.setContentsMargins(0, 0, 0, 0)
list_container_layout.setSpacing(0)

# Lista de versiones
version_list = QListWidget()
version_list.setSelectionMode(QListWidget.NoSelection)
version_list.setStyleSheet("""
    QListWidget {
        background-color: #141414;
        border: 1px solid #2d2d2d;
        border-radius: 8px;
        padding: 4px;
        outline: none;
    }
    QListWidget::item {
        background-color: transparent;
        border: none;
        padding: 0;
        margin: 4px 0;
        min-height: 0;
        height: auto;
    }
""")

list_container_layout.addWidget(version_list)
list_scroll_area.setWidget(list_container)

versions_layout.addWidget(list_scroll_area)
layout.addWidget(versions_group)

current_selected_widget = None

current_default_version = ""

def load_default_version():
    """Carga la versión predeterminada desde el archivo de configuración."""
    global current_default_version
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                config_data = json.load(f)
                current_default_version = config_data.get("default_version", "")
        else:
            current_default_version = ""
    except:
        current_default_version = ""
    
    # Actualizar la etiqueta
    if current_default_version:
        default_info_value.setText(current_default_version)
        default_info_value.setStyleSheet("""
            QLabel {
                color: #FF9800;
                font-weight: bold;
                background-color: #2d2d2d;
                padding: 6px 12px;
                border-radius: 6px;
                border: 2px solid #FF9800;
                margin-left: 10px;
            }
        """)
    else:
        default_info_value.setText("Ninguna")
        default_info_value.setStyleSheet("""
            QLabel {
                color: #888888;
                font-weight: bold;
                background-color: #2d2d2d;
                padding: 6px 12px;
                border-radius: 6px;
                border: 1px solid #3d3d3d;
                margin-left: 10px;
            }
        """)

def load_versions_list():
    """Carga las versiones en la lista."""
    version_list.clear()
    global current_selected_widget
    current_selected_widget = None
    
    try:
        vm = VersionManager()
        versions = vm.get_installed_versions()
        
        if not versions:
            # Mostrar mensaje de que no hay versiones
            item = QListWidgetItem()
            item.setFlags(Qt.NoItemFlags)
            item.setSizeHint(QSize(0, 150))
            
            message_widget = QWidget()
            message_layout = QVBoxLayout(message_widget)
            message_layout.setAlignment(Qt.AlignCenter)
            message_layout.setSpacing(15)
            
            icon_label = QLabel("📦")
            icon_label.setStyleSheet("font-size: 48px; color: #888888;")
            icon_label.setAlignment(Qt.AlignCenter)
            message_layout.addWidget(icon_label)
            
            text_label = QLabel("No hay versiones instaladas\n\nAñade una versión desde un archivo APK")
            text_label.setStyleSheet("""
                color: #aaaaaa;
                font-size: 14px;
                font-weight: bold;
                text-align: center;
            """)
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setWordWrap(True)
            message_layout.addWidget(text_label)
            
            version_list.addItem(item)
            version_list.setItemWidget(item, message_widget)
        else:
            # Mostrar versiones disponibles
            for version in versions:
                add_version_item(version)
                
    except Exception as e:
        print(f"Error cargando versiones: {e}")

def add_version_item(version_name):
    """Añade un ítem de versión a la lista."""
    # Crear widget personalizado
    item_widget = QWidget()
    item_widget.setFixedHeight(60)
    item_widget.setProperty("version_name", version_name)
    
    # Contenedor principal con borde transparente
    main_container = QWidget()
    main_container.setProperty("version_name", version_name)
    main_container.setStyleSheet("""
        QWidget {
            background-color: #1e1e1e;
            border: 1px solid transparent;
            border-radius: 6px;
            margin: 2px 0;
        }
        QWidget:hover {
            background-color: #252525;
            border: 1px solid #3d3d3d;
        }
    """)
    
    main_layout = QHBoxLayout(main_container)
    main_layout.setContentsMargins(12, 8, 12, 8)
    main_layout.setSpacing(10)
    
    # Icono y nombre de versión
    icon_label = QLabel("📦")
    icon_label.setObjectName("versionIcon")
    icon_label.setStyleSheet("""
        QLabel#versionIcon {
            font-size: 20px;
            background-color: transparent;
            border: none;
        }
    """)
    main_layout.addWidget(icon_label)
    
    version_label = QLabel(version_name)
    version_label.setObjectName("versionLabel")
    
    # Verificar si es la versión predeterminada
    global current_default_version
    if version_name == current_default_version:
        version_label.setText(f"👑 {version_name}")
        version_label.setStyleSheet("""
            QLabel#versionLabel {
                font-size: 14px;
                color: #FF9800;
                font-weight: bold;
                background-color: transparent;
                border: none;
            }
        """)
    else:
        version_label.setStyleSheet("""
            QLabel#versionLabel {
                font-size: 14px;
                color: white;
                font-weight: bold;
                background-color: transparent;
                border: none;
            }
        """)
    
    version_label.setMinimumWidth(200)
    main_layout.addWidget(version_label)
    
    main_layout.addStretch()
    
    # Botón de configuración (siempre visible)
    config_btn = QPushButton("⚙️")
    config_btn.setObjectName("configButton")
    config_btn.setToolTip(f"Configurar argumentos para {version_name}")
    config_btn.setFixedSize(36, 36)
    config_btn.setCursor(Qt.PointingHandCursor)
    config_btn.setStyleSheet("""
        QPushButton#configButton {
            background-color: #4A86E8;
            border: 3px solid;
            border-top-color: #5D9CFA;
            border-left-color: #5D9CFA;
            border-right-color: #3A75D4;
            border-bottom-color: #3A75D4;
            color: white;
            font-size: 16px;
            font-weight: bold;
            border-radius: 6px;
        }
        QPushButton#configButton:hover {
            background-color: #5D9CFA;
            border-top-color: #6EB0FF;
            border-left-color: #6EB0FF;
        }
        QPushButton#configButton:pressed {
            background-color: #3A75D4;
            border-top-color: #4A86E8;
            border-left-color: #4A86E8;
        }
    """)
    config_btn.clicked.connect(lambda checked, v=version_name: open_config_dialog(v))
    main_layout.addWidget(config_btn)
    
    # Botón de establecer como predeterminada (SOLO si NO es la actual)
    if version_name != current_default_version:
        default_btn = QPushButton("👑")
        default_btn.setObjectName("defaultButton")
        default_btn.setToolTip(f"Establecer {version_name} como predeterminada")
        default_btn.setFixedSize(36, 36)
        default_btn.setCursor(Qt.PointingHandCursor)
        default_btn.setStyleSheet("""
            QPushButton#defaultButton {
                background-color: #FF6B6B;
                border: 3px solid;
                border-top-color: #FF8E8E;
                border-left-color: #FF8E8E;
                border-right-color: #E64A4A;
                border-bottom-color: #E64A4A;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton#defaultButton:hover {
                background-color: #FF8E8E;
                border-top-color: #FFAAAA;
                border-left-color: #FFAAAA;
            }
            QPushButton#defaultButton:pressed {
                background-color: #E64A4A;
                border-top-color: #FF6B6B;
                border-left-color: #FF6B6B;
            }
        """)
        default_btn.clicked.connect(lambda checked, v=version_name: set_as_default(v))
        main_layout.addWidget(default_btn)
    # NO agregar espaciador - el botón simplemente no estará presente
    
    # Layout principal para el item_widget
    item_layout = QVBoxLayout(item_widget)
    item_layout.setContentsMargins(0, 0, 0, 0)
    item_layout.addWidget(main_container)
    
    # Crear item de lista
    list_item = QListWidgetItem()
    list_item.setSizeHint(QSize(0, 60))
    list_item.setData(Qt.UserRole, version_name)
    
    version_list.addItem(list_item)
    version_list.setItemWidget(list_item, item_widget)
    
    # Conectar clic en el widget principal
    def on_widget_clicked(event=None, w=main_container, v=version_name):
        on_version_selected(w, v)
    
    # Usar un evento filter para detectar clics en el contenedor principal
    main_container.mousePressEvent = on_widget_clicked

def on_version_selected(widget, version_name):
    """Cuando se selecciona una versión en la lista."""
    global current_selected_widget
    
    # Resetear estilo anterior
    if current_selected_widget:
        current_selected_widget.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border: 1px solid transparent;
                border-radius: 6px;
                margin: 2px 0;
            }
            QWidget:hover {
                background-color: #252525;
                border: 1px solid #3d3d3d;
            }
        """)
    
    # Aplicar estilo de selección SOLO al contenedor principal
    widget.setStyleSheet("""
        QWidget {
            background-color: #1e1e1e;
            border: 2px solid #5DBB63;
            border-radius: 6px;
            margin: 2px 0;
        }
        QWidget:hover {
            background-color: #252525;
        }
        QWidget QLabel {
            border: none !important;
            background-color: transparent !important;
        }
        QWidget QPushButton {
            border: none !important;
        }
    """)
    
    current_selected_widget = widget

def open_config_dialog(version_name):
    """Abre el diálogo de configuración para una versión."""
    dialog = VersionConfigDialog(version_name, main_window)
    dialog.config_saved.connect(on_config_saved)
    dialog.exec()

def on_config_saved(version_name, args):
    """Cuando se guarda la configuración de una versión."""
    # Crear diálogo personalizado
    dialog = QDialog(main_window)
    dialog.setWindowTitle("Configuración guardada")
    dialog.setFixedSize(400, 180)
    dialog.setStyleSheet("""
        QDialog {
            background-color: #1a1a1a;
            border-radius: 8px;
        }
    """)
    
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(15)
    
    label = QLabel(f"✅ Configuración guardada para {version_name}")
    label.setStyleSheet("color: #4CAF50; font-size: 14px;")
    label.setAlignment(Qt.AlignCenter)
    label.setWordWrap(True)
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

def set_as_default(version_name):
    """Establece una versión como predeterminada."""
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        config_data = {"default_version": version_name}
        CONFIG_FILE.write_text(json.dumps(config_data, indent=2))
        
        # Actualizar la interfaz
        load_default_version()
        load_versions_list()
        
        QMessageBox.information(main_window, "Versión predeterminada establecida", 
                               f"{version_name} es ahora la versión predeterminada")
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"No se pudo establecer como predeterminada: {str(e)}")

def refresh_config_page():
    """Refresca toda la página de configuración."""
    load_default_version()
    load_versions_list()

# Cargar datos iniciales
refresh_config_page()

# Hacer que las funciones sean accesibles desde fuera
main_window.update_config_page = refresh_config_page
main_window.refresh_config_page = refresh_config_page