# Página de contenido y mods
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QListWidget, QListWidgetItem, 
                              QFrame, QMessageBox, QDialog, QProgressBar, 
                              QFileDialog, QApplication, QGroupBox, QTabWidget)
from pathlib import Path
import shutil
import os

# RUTA UNIFICADA: Todos los archivos van aquí
GAMES_DIR = Path.home() / ".local" / "share" / "mcpelauncher" / "games" / "com.mojang"
# Asegurar que el directorio exista
GAMES_DIR.mkdir(parents=True, exist_ok=True)
# Crear subdirectorios específicos de Minecraft Bedrock
for subdir in ["behavior_packs", "resource_packs", "minecraftWorlds"]:
    (GAMES_DIR / subdir).mkdir(parents=True, exist_ok=True)

# Configurar layout de la página
layout = QVBoxLayout(page_widget)
layout.setContentsMargins(20, 20, 20, 20)

# Tabs para diferentes tipos de contenido
content_tabs = QTabWidget()

# Pestaña de Mods
mods_tab = QWidget()
mods_layout = QVBoxLayout(mods_tab)
mods_layout.setContentsMargins(10, 10, 10, 10)

mods_label = QLabel("BEHAVIOR PACKS")
mods_label.setStyleSheet("""
    font-size: 20px;
    font-weight: bold;
    color: #4CAF50;
    margin-bottom: 10px;
""")
mods_layout.addWidget(mods_label)

desc_label = QLabel("Mods y complementos que añaden o modifican comportamiento del juego")
desc_label.setStyleSheet("color: #888888; font-size: 12px; margin-bottom: 20px;")
desc_label.setWordWrap(True)
mods_layout.addWidget(desc_label)

# Contenedor de dos columnas
mods_columns = QHBoxLayout()

# Columna izquierda: Instalar
install_group = QGroupBox("Instalar nuevo")
install_layout = QVBoxLayout(install_group)

install_btn = QPushButton("Seleccionar archivo...")
install_btn.setObjectName("SecondaryButton")
# ESTILO PIXELADO CON ESQUINAS REDONDEADAS
install_btn.setStyleSheet("""
    QPushButton {
        background-color: #5DBB63;
        border: 3px solid;
        border-top-color: #6BCF72;
        border-left-color: #6BCF72;
        border-right-color: #3D8B40;
        border-bottom-color: #3D8B40;
        color: white;
        padding: 10px 20px;
        font-family: 'Minecraft', 'Arial Black', monospace;
        font-size: 12px;
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
install_btn.clicked.connect(lambda: install_pack("behavior_packs"))
install_layout.addWidget(install_btn)

install_info = QLabel("Formatos soportados: .zip, .mcpack")
install_info.setStyleSheet("color: #666666; font-size: 11px; margin-top: 10px;")
install_layout.addWidget(install_info)

install_layout.addStretch()
mods_columns.addWidget(install_group)

# Columna derecha: Gestionar
manage_group = QGroupBox("Gestionar instalados")
manage_layout = QVBoxLayout(manage_group)

mods_list = QListWidget()
manage_layout.addWidget(mods_list)

# Botones de gestión
btn_layout = QHBoxLayout()
refresh_btn = QPushButton("↻")
refresh_btn.setObjectName("IconButton")
refresh_btn.setToolTip("Recargar lista")
refresh_btn.clicked.connect(lambda: load_packs("behavior_packs", mods_list))
refresh_btn.setStyleSheet("""
    QPushButton {
        background-color: #5DBB63;
        border: 3px solid;
        border-top-color: #6BCF72;
        border-left-color: #6BCF72;
        border-right-color: #3D8B40;
        border-bottom-color: #3D8B40;
        color: white;
        padding: 0.2px 0.2px;
        font-family: 'Minecraft', 'Arial Black', monospace;
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
btn_layout.addWidget(refresh_btn)

delete_btn = QPushButton("🗑️")
delete_btn.setObjectName("IconButton")
delete_btn.setToolTip("Eliminar seleccionado")
delete_btn.clicked.connect(lambda: delete_pack("behavior_packs", mods_list))
delete_btn.setStyleSheet("""
    QPushButton {
        background-color: #BB5D5D;
        border: 3px solid;
        border-top-color: #CF6B6B;
        border-left-color: #CF6B6B;
        border-right-color: #8B3D3D;
        border-bottom-color: #8B3D3D;
        color: white;
        padding: 0.2px 0.2px;
        font-family: 'Minecraft', 'Arial Black', monospace;
        font-size: 16px;
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
btn_layout.addWidget(delete_btn)

btn_layout.addStretch()
manage_layout.addLayout(btn_layout)

mods_columns.addWidget(manage_group)
mods_columns.setStretch(0, 1)
mods_columns.setStretch(1, 2)

mods_layout.addLayout(mods_columns)
content_tabs.addTab(mods_tab, "Mods")

# Pestaña de Texturas
textures_tab = QWidget()
textures_layout = QVBoxLayout(textures_tab)
textures_layout.setContentsMargins(10, 10, 10, 10)

textures_label = QLabel("RESOURCE PACKS")
textures_label.setStyleSheet("""
    font-size: 20px;
    font-weight: bold;
    color: #4CAF50;
    margin-bottom: 10px;
""")
textures_layout.addWidget(textures_label)

textures_desc = QLabel("Paquetes de recursos que modifican texturas, sonidos y modelos")
textures_desc.setStyleSheet("color: #888888; font-size: 12px; margin-bottom: 20px;")
textures_desc.setWordWrap(True)
textures_layout.addWidget(textures_desc)

# Contenedor de dos columnas
textures_columns = QHBoxLayout()

# Columna izquierda: Instalar
textures_install_group = QGroupBox("Instalar nuevo")
textures_install_layout = QVBoxLayout(textures_install_group)

textures_install_btn = QPushButton("Seleccionar archivo...")
textures_install_btn.setObjectName("SecondaryButton")
# Mismo estilo pixelado
textures_install_btn.setStyleSheet(install_btn.styleSheet())
textures_install_btn.clicked.connect(lambda: install_pack("resource_packs"))
textures_install_layout.addWidget(textures_install_btn)

textures_install_info = QLabel("Formatos soportados: .zip, .mcpack")
textures_install_info.setStyleSheet("color: #666666; font-size: 11px; margin-top: 10px;")
textures_install_layout.addWidget(textures_install_info)

textures_install_layout.addStretch()
textures_columns.addWidget(textures_install_group)

# Columna derecha: Gestionar
textures_manage_group = QGroupBox("Gestionar instalados")
textures_manage_layout = QVBoxLayout(textures_manage_group)

textures_list = QListWidget()
textures_manage_layout.addWidget(textures_list)

# Botones de gestión
textures_btn_layout = QHBoxLayout()
textures_refresh_btn = QPushButton("↻")
textures_refresh_btn.setObjectName("IconButton")
textures_refresh_btn.setToolTip("Recargar lista")
textures_refresh_btn.clicked.connect(lambda: load_packs("resource_packs", textures_list))
textures_refresh_btn.setStyleSheet("""
    QPushButton {
        background-color: #5DBB63;
        border: 3px solid;
        border-top-color: #6BCF72;
        border-left-color: #6BCF72;
        border-right-color: #3D8B40;
        border-bottom-color: #3D8B40;
        color: white;
        padding: 0.2px 0.2px;
        font-family: 'Minecraft', 'Arial Black', monospace;
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
textures_btn_layout.addWidget(textures_refresh_btn)

textures_delete_btn = QPushButton("🗑️")
textures_delete_btn.setObjectName("IconButton")
textures_delete_btn.setToolTip("Eliminar seleccionado")
textures_delete_btn.clicked.connect(lambda: delete_pack("resource_packs", textures_list))
textures_btn_layout.addWidget(textures_delete_btn)
textures_delete_btn.setStyleSheet("""
    QPushButton {
        background-color: #BB5D5D;
        border: 3px solid;
        border-top-color: #CF6B6B;
        border-left-color: #CF6B6B;
        border-right-color: #8B3D3D;
        border-bottom-color: #8B3D3D;
        color: white;
        padding: 0.2px 0.2px;
        font-family: 'Minecraft', 'Arial Black', monospace;
        font-size: 16px;
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

textures_btn_layout.addStretch()
textures_manage_layout.addLayout(textures_btn_layout)

textures_columns.addWidget(textures_manage_group)
textures_columns.setStretch(0, 1)
textures_columns.setStretch(1, 2)

textures_layout.addLayout(textures_columns)
content_tabs.addTab(textures_tab, "Texturas")

# Pestaña de Mundos
worlds_tab = QWidget()
worlds_layout = QVBoxLayout(worlds_tab)
worlds_layout.setContentsMargins(10, 10, 10, 10)

worlds_label = QLabel("MUNDOS GUARDADOS")
worlds_label.setStyleSheet("""
    font-size: 20px;
    font-weight: bold;
    color: #4CAF50;
    margin-bottom: 20px;
""")
worlds_layout.addWidget(worlds_label)

# Contenedor principal
worlds_main = QHBoxLayout()

# Panel izquierdo: Añadir mundo
worlds_add_group = QGroupBox("Añadir mundo")
worlds_add_layout = QVBoxLayout(worlds_add_group)

worlds_add_btn = QPushButton("📁 Seleccionar carpeta del mundo")
worlds_add_btn.setObjectName("SecondaryButton")
# Mismo estilo pixelado
worlds_add_btn.setStyleSheet(install_btn.styleSheet())
worlds_add_btn.clicked.connect(lambda: install_pack("minecraftWorlds", True))
worlds_add_layout.addWidget(worlds_add_btn)

worlds_add_info = QLabel("Selecciona una carpeta que contenga los archivos del mundo de Minecraft")
worlds_add_info.setStyleSheet("color: #666666; font-size: 11px; margin-top: 10px;")
worlds_add_info.setWordWrap(True)
worlds_add_layout.addWidget(worlds_add_info)

worlds_add_layout.addStretch()
worlds_main.addWidget(worlds_add_group)

# Panel derecho: Gestionar mundos
worlds_manage_group = QGroupBox("Mundos instalados")
worlds_manage_layout = QVBoxLayout(worlds_manage_group)

worlds_list_widget = QListWidget()  # Cambiado el nombre para evitar conflicto
worlds_manage_layout.addWidget(worlds_list_widget)

# Botones
worlds_btn_layout = QHBoxLayout()
worlds_refresh_btn = QPushButton("↻")
worlds_refresh_btn.setObjectName("IconButton")
worlds_refresh_btn.setToolTip("Recargar lista")
worlds_refresh_btn.clicked.connect(lambda: load_worlds_func())
worlds_refresh_btn.setStyleSheet("""
    QPushButton {
        background-color: #5DBB63;
        border: 3px solid;
        border-top-color: #6BCF72;
        border-left-color: #6BCF72;
        border-right-color: #3D8B40;
        border-bottom-color: #3D8B40;
        color: white;
        padding: 0.2px 0.2px;
        font-family: 'Minecraft', 'Arial Black', monospace;
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
worlds_btn_layout.addWidget(worlds_refresh_btn)

worlds_delete_btn = QPushButton("🗑️")
worlds_delete_btn.setObjectName("IconButton")
worlds_delete_btn.setToolTip("Eliminar mundo seleccionado")
worlds_delete_btn.clicked.connect(lambda: delete_world_func())
worlds_delete_btn.setStyleSheet("""
    QPushButton {
        background-color: #BB5D5D;
        border: 3px solid;
        border-top-color: #CF6B6B;
        border-left-color: #CF6B6B;
        border-right-color: #8B3D3D;
        border-bottom-color: #8B3D3D;
        color: white;
        padding: 0.2px 0.2px;
        font-family: 'Minecraft', 'Arial Black', monospace;
        font-size: 16px;
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
worlds_btn_layout.addWidget(worlds_delete_btn)

worlds_btn_layout.addStretch()
worlds_manage_layout.addLayout(worlds_btn_layout)

worlds_main.addWidget(worlds_manage_group)
worlds_main.setStretch(0, 1)
worlds_main.setStretch(1, 2)

worlds_layout.addLayout(worlds_main)
content_tabs.addTab(worlds_tab, "Mundos")

layout.addWidget(content_tabs)

# Funciones auxiliares - REEMPLAZADAS para usar directamente GAMES_DIR
def install_pack(pack_type, is_folder=False):
    if is_folder:
        source_path = QFileDialog.getExistingDirectory(main_window, "Seleccionar carpeta del mundo")
    else:
        source_path, _ = QFileDialog.getOpenFileName(
            main_window,
            "Seleccionar archivo",
            str(Path.home()),
            "Archivos compatibles (*.zip *.mcpack *.mcaddon);;Todos los archivos (*)"
        )
    
    if not source_path:
        return
    
    source_path = Path(source_path)
    
    # Obtener nombre del pack (sin extensión)
    if is_folder:
        pack_name = source_path.name
    else:
        pack_name = source_path.stem
    
    # Ruta destino en la nueva ubicación
    target_path = GAMES_DIR / pack_type / pack_name
    
    # Verificar si ya existe
    if target_path.exists():
        msg_box = QMessageBox(main_window)
        msg_box.setWindowTitle("Confirmar Reemplazo")
        
        # Determinar el tipo de contenido para el mensaje
        if pack_type == "behavior_packs":
            content_type = "behavior pack"
        elif pack_type == "resource_packs":
            content_type = "resource pack"
        elif pack_type == "minecraftWorlds":
            content_type = "mundo"
        else:
            content_type = "contenido"
        
        msg_box.setText(f"El {content_type} '{pack_name}' ya existe.\n¿Deseas reemplazarlo?")
        
        # Crear botones personalizados
        aceptar_btn = msg_box.addButton("Reemplazar", QMessageBox.AcceptRole)
        cancelar_btn = msg_box.addButton("Cancelar", QMessageBox.RejectRole)
        
        # Estilos personalizados
        aceptar_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A86E8;
                border: 3px solid;
                border-top-color: #5D9CFA;
                border-left-color: #5D9CFA;
                border-right-color: #3A75D4;
                border-bottom-color: #3A75D4;
                color: white;
                padding: 5px 15px;
                font-family: 'Minecraft', 'Arial Black', monospace;
                font-size: 12px;
                font-weight: bold;
                border-radius: 6px;
                text-shadow: 1px 1px 0 #3A75D4;
                min-width: 80px;
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
        
        cancelar_btn.setStyleSheet("""
            QPushButton {
                background-color: #5DBB63;
                border: 3px solid;
                border-top-color: #6BCF72;
                border-left-color: #6BCF72;
                border-right-color: #3D8B40;
                border-bottom-color: #3D8B40;
                color: white;
                padding: 5px 15px;
                font-family: 'Minecraft', 'Arial Black', monospace;
                font-size: 12px;
                font-weight: bold;
                border-radius: 6px;
                text-shadow: 1px 1px 0 #3D8B40;
                min-width: 80px;
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
        
        msg_box.exec()
        
        if msg_box.clickedButton() == cancelar_btn:
            return
    
    # Resto del código de instalación...
    progress_dialog = QDialog(main_window)
    progress_dialog.setWindowTitle("Instalando...")
    progress_dialog.setFixedSize(300, 100)
    
    progress_layout = QVBoxLayout(progress_dialog)
    label = QLabel(f"Instalando {pack_name}...")
    progress_bar = QProgressBar()
    progress_bar.setRange(0, 0)
    
    progress_layout.addWidget(label)
    progress_layout.addWidget(progress_bar)
    progress_dialog.show()
    QApplication.processEvents()
    
    def install():
        try:
            # Eliminar si ya existe
            if target_path.exists():
                if target_path.is_dir():
                    shutil.rmtree(target_path)
                else:
                    target_path.unlink()
            
            # Copiar o extraer
            if is_folder or source_path.is_dir():
                shutil.copytree(source_path, target_path)
                success = True
                
                # Mensaje específico según tipo
                if pack_type == "minecraftWorlds":
                    message = f"¡Mundo '{pack_name}' instalado correctamente!"
                else:
                    message = f"¡{pack_name} instalado correctamente!"
                    
            elif source_path.suffix in ['.zip', '.mcpack', '.mcaddon']:
                # Extraer archivo comprimido
                import zipfile
                with zipfile.ZipFile(source_path, 'r') as zip_ref:
                    zip_ref.extractall(target_path)
                success = True
                message = f"¡{pack_name} extraído e instalado correctamente!"
            else:
                # Copiar archivo simple
                shutil.copy2(source_path, target_path)
                success = True
                message = f"¡{pack_name} copiado correctamente!"
                
        except Exception as e:
            success = False
            message = f"Error al instalar: {str(e)}"
        
        progress_dialog.close()
        
        if success:
            QMessageBox.information(main_window, "Instalación completada", message)
            # Actualizar la lista correspondiente
            if pack_type == "behavior_packs":
                load_packs("behavior_packs", mods_list)
            elif pack_type == "resource_packs":
                load_packs("resource_packs", textures_list)
            elif pack_type == "minecraftWorlds":
                load_worlds_func()
        else:
            QMessageBox.critical(main_window, "Error en instalación", message)
    
    QTimer.singleShot(100, install)
    
def load_packs(pack_type, list_widget):
    """Cargar packs desde el directorio correcto"""
    list_widget.clear()
    pack_dir = GAMES_DIR / pack_type
    
    if not pack_dir.exists():
        return
    
    # Obtener todos los elementos en el directorio
    items = []
    for item in pack_dir.iterdir():
        if item.name not in [".", ".."]:
            items.append(item)
    
    # Ordenar por nombre
    items.sort(key=lambda x: x.name.lower())
    
    # Añadir a la lista
    for item in items:
        if item.is_dir():
            icon = "📁"
            text = f"{icon} {item.name}"
        else:
            icon = "📄"
            text = f"{icon} {item.name}"
        
        list_item = QListWidgetItem(text)
        list_item.setData(Qt.UserRole, str(item))  # Guardar ruta completa
        list_widget.addItem(list_item)
    
    # Si no hay elementos, mostrar mensaje
    if list_widget.count() == 0:
        if pack_type == "behavior_packs":
            list_item = QListWidgetItem("📭 No hay behavior packs instalados")
        elif pack_type == "resource_packs":
            list_item = QListWidgetItem("📭 No hay resource packs instalados")
        else:
            list_item = QListWidgetItem("📭 No hay contenido instalado")
        
        list_item.setFlags(Qt.NoItemFlags)  # No seleccionable
        list_widget.addItem(list_item)

def delete_pack(pack_type, list_widget):
    selected = list_widget.currentItem()
    if not selected or selected.flags() & Qt.NoItemFlags:
        QMessageBox.warning(main_window, "Advertencia", "Por favor, selecciona un elemento primero.")
        return
    
    item_text = selected.text()
    # Extraer nombre del pack (eliminar icono y espacio)
    pack_name = item_text.split(" ", 1)[1] if " " in item_text else item_text
    
    # Determinar el tipo de contenido para el mensaje
    if pack_type == "behavior_packs":
        content_type = "behavior pack"
    elif pack_type == "resource_packs":
        content_type = "resource pack"
    else:
        content_type = "contenido"
    
    msg_box = QMessageBox(main_window)
    msg_box.setWindowTitle("Confirmar Eliminación")
    msg_box.setText(f"¿Estás seguro de que quieres eliminar el {content_type} '{pack_name}'?\nEsta acción no se puede deshacer.")
    
    # Crear botones personalizados
    aceptar_btn = msg_box.addButton("Eliminar", QMessageBox.AcceptRole)
    cancelar_btn = msg_box.addButton("Cancelar", QMessageBox.RejectRole)
    
    # Estilos personalizados
    aceptar_btn.setStyleSheet("""
        QPushButton {
            background-color: #E84A4A;
            border: 3px solid;
            border-top-color: #FA5D5D;
            border-left-color: #FA5D5D;
            border-right-color: #D43A3A;
            border-bottom-color: #D43A3A;
            color: white;
            padding: 5px 15px;
            font-family: 'Minecraft', 'Arial Black', monospace;
            font-size: 12px;
            font-weight: bold;
            border-radius: 6px;
            text-shadow: 1px 1px 0 #D43A3A;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #FA5D5D;
            border-top-color: #FF6E6E;
            border-left-color: #FF6E6E;
            transform: translateY(-1px);
        }
        QPushButton:pressed {
            background-color: #D43A3A;
            transform: translateY(1px);
            border-top-color: #E84A4A;
            border-left-color: #E84A4A;
        }
    """)
    
    cancelar_btn.setStyleSheet("""
        QPushButton {
            background-color: #5DBB63;
            border: 3px solid;
            border-top-color: #6BCF72;
            border-left-color: #6BCF72;
            border-right-color: #3D8B40;
            border-bottom-color: #3D8B40;
            color: white;
            padding: 5px 15px;
            font-family: 'Minecraft', 'Arial Black', monospace;
            font-size: 12px;
            font-weight: bold;
            border-radius: 6px;
            text-shadow: 1px 1px 0 #3D8B40;
            min-width: 80px;
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
    
    msg_box.exec()
    
    if msg_box.clickedButton() == aceptar_btn:
        pack_path = GAMES_DIR / pack_type / pack_name
        try:
            if pack_path.exists():
                if pack_path.is_dir():
                    shutil.rmtree(pack_path)
                else:
                    pack_path.unlink()
                
                QMessageBox.information(main_window, "Eliminación completada", f"¡{content_type} '{pack_name}' eliminado correctamente!")
                load_packs(pack_type, list_widget)
            else:
                QMessageBox.warning(main_window, "Advertencia", f"No se encontró el {content_type} '{pack_name}'")
        except Exception as e:
            QMessageBox.critical(main_window, "Error", f"No se pudo eliminar: {str(e)}")

def load_worlds_func():
    """Cargar mundos desde el directorio correcto"""
    worlds_list_widget.clear()
    worlds_dir = GAMES_DIR / "minecraftWorlds"
    
    if not worlds_dir.exists():
        return
    
    # Buscar carpetas que contengan level.dat (mundo de Minecraft)
    worlds = []
    for world_folder in worlds_dir.iterdir():
        if world_folder.is_dir() and world_folder.name not in [".", ".."]:
            # Verificar si tiene level.dat (es un mundo válido)
            level_dat = world_folder / "level.dat"
            if level_dat.exists():
                worlds.append(world_folder)
    
    # Ordenar por nombre
    worlds.sort(key=lambda x: x.name.lower())
    
    # Añadir a la lista
    for world in worlds:
        world_item = QListWidgetItem(f"🌍 {world.name}")
        world_item.setData(Qt.UserRole, str(world))  # Guardar ruta completa
        worlds_list_widget.addItem(world_item)
    
    # Si no hay mundos, mostrar mensaje
    if worlds_list_widget.count() == 0:
        world_item = QListWidgetItem("🌍 No hay mundos guardados")
        world_item.setFlags(Qt.NoItemFlags)  # No seleccionable
        worlds_list_widget.addItem(world_item)

def delete_world_func():
    selected = worlds_list_widget.currentItem()
    if not selected or selected.flags() & Qt.NoItemFlags:
        QMessageBox.warning(main_window, "Advertencia", "Por favor, selecciona un mundo primero.")
        return
    
    world_name = selected.text().split(" ", 1)[1]
    
    msg_box = QMessageBox(main_window)
    msg_box.setWindowTitle("Confirmar Eliminación")
    msg_box.setText(f"¿Estás seguro de que quieres eliminar el mundo '{world_name}'?\nEsta acción no se puede deshacer.")
    
    # Crear botones personalizados
    aceptar_btn = msg_box.addButton("Eliminar", QMessageBox.AcceptRole)
    cancelar_btn = msg_box.addButton("Cancelar", QMessageBox.RejectRole)
    
    # Estilos personalizados
    aceptar_btn.setStyleSheet("""
        QPushButton {
            background-color: #E84A4A;
            border: 3px solid;
            border-top-color: #FA5D5D;
            border-left-color: #FA5D5D;
            border-right-color: #D43A3A;
            border-bottom-color: #D43A3A;
            color: white;
            padding: 5px 15px;
            font-family: 'Minecraft', 'Arial Black', monospace;
            font-size: 12px;
            font-weight: bold;
            border-radius: 6px;
            text-shadow: 1px 1px 0 #D43A3A;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #FA5D5D;
            border-top-color: #FF6E6E;
            border-left-color: #FF6E6E;
            transform: translateY(-1px);
        }
        QPushButton:pressed {
            background-color: #D43A3A;
            transform: translateY(1px);
            border-top-color: #E84A4A;
            border-left-color: #E84A4A;
        }
    """)
    
    cancelar_btn.setStyleSheet("""
        QPushButton {
            background-color: #5DBB63;
            border: 3px solid;
            border-top-color: #6BCF72;
            border-left-color: #6BCF72;
            border-right-color: #3D8B40;
            border-bottom-color: #3D8B40;
            color: white;
            padding: 5px 15px;
            font-family: 'Minecraft', 'Arial Black', monospace;
            font-size: 12px;
            font-weight: bold;
            border-radius: 6px;
            text-shadow: 1px 1px 0 #3D8B40;
            min-width: 80px;
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
    
    msg_box.exec()
    
    if msg_box.clickedButton() == aceptar_btn:
        world_path = GAMES_DIR / "minecraftWorlds" / world_name
        try:
            if world_path.exists() and world_path.is_dir():
                shutil.rmtree(world_path)
                QMessageBox.information(main_window, "Eliminación completada", f"¡Mundo '{world_name}' eliminado correctamente!")
                load_worlds_func()
            else:
                QMessageBox.warning(main_window, "Advertencia", f"No se encontró el mundo '{world_name}'")
        except Exception as e:
            QMessageBox.critical(main_window, "Error", f"No se pudo eliminar el mundo: {str(e)}")

# Cargar datos iniciales
load_packs("behavior_packs", mods_list)
load_packs("resource_packs", textures_list)
load_worlds_func()