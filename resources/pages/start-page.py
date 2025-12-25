# Página de inicio - Versiones instaladas
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QListWidget, QListWidgetItem, 
                              QFrame, QMessageBox, QDialog, QProgressBar, 
                              QFileDialog, QApplication, QSizePolicy, QSpacerItem)
from PySide6.QtGui import QFont
from pathlib import Path
import shutil
import subprocess
import os

# Configurar layout de la página
layout = QVBoxLayout(page_widget)
layout.setContentsMargins(20, 20, 20, 10)
layout.setSpacing(10)

# Encabezado
header_layout = QHBoxLayout()

title_label = QLabel("MINECRAFT: BEDROCK EDITION")
title_label.setStyleSheet("""
    font-size: 24px;
    font-weight: bold;
    color: white;
    margin-bottom: 10px;
""")
header_layout.addWidget(title_label)

header_layout.addStretch()

install_buttons_layout = QHBoxLayout()
install_buttons_layout.setSpacing(5)

install_btn = QPushButton("➕ Nueva instalación")
install_btn.setObjectName("SecondaryButton")
install_btn.setCursor(Qt.PointingHandCursor)
install_btn.setFixedHeight(33)
install_btn.setToolTip("Extraer nueva versión desde archivo APK")
install_btn.setMinimumWidth(140)
install_btn.clicked.connect(lambda: main_window.show_extract_dialog())
install_buttons_layout.addWidget(install_btn)
install_btn.setStyleSheet("""
    QPushButton {
        background-color: #5DBB63;
        border: 3px solid;
        border-top-color: #6BCF72;
        border-left-color: #6BCF72;
        border-right-color: #3D8B40;
        border-bottom-color: #3D8B40;
        color: white;
        padding: 8px 20px;
        font-family: 'Minecraft', 'Arial Black', monospace;
        font-size: 12px;
        font-weight: bold;
        border-radius: 6px;
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

# Botón de importar versión (solo icono, mismo tamaño)
import_btn = QPushButton("📥")
import_btn.setObjectName("IconButton")
import_btn.setToolTip("Importar versión desde archivo")
import_btn.setFixedSize(36, 36)
import_btn.setCursor(Qt.PointingHandCursor)
import_btn.clicked.connect(lambda: main_window.exporter.import_version(main_window))
import_btn.setStyleSheet("""
    QPushButton {
        background-color: #5DBB63;
        border: 3px solid;
        border-top-color: #6BCF72;
        border-left-color: #6BCF72;
        border-right-color: #3D8B40;
        border-bottom-color: #3D8B40;
        color: white;
        font-family: 'Minecraft', 'Arial Black', monospace;
        font-size: 16px;
        font-weight: bold;
        border-radius: 6px;
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
install_buttons_layout.addWidget(import_btn)

header_layout.addLayout(install_buttons_layout)
layout.addLayout(header_layout)

# Separador
separator = QFrame()
separator.setFrameShape(QFrame.HLine)
separator.setStyleSheet("background-color: #2d2d2d; margin: 10px 0;")
layout.addWidget(separator)

# Contenedor principal - USAR SOLO UN CONTENEDOR
main_container = QWidget()
main_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
main_container_layout = QVBoxLayout(main_container)
main_container_layout.setContentsMargins(0, 0, 0, 0)
main_container_layout.setSpacing(0)

# Lista de versiones
version_list = QListWidget()
version_list.setSelectionMode(QListWidget.SingleSelection)
version_list.itemClicked.connect(lambda item: on_version_selected(item))
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

main_container_layout.addWidget(version_list, 1)

# Espaciador
main_container_layout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

# Botón Lanzar Juego
play_button = QPushButton("LANZAR JUEGO")
play_button.setObjectName("FloatingPlayButton")
play_button.setVisible(False)
play_button.setCursor(Qt.PointingHandCursor)
play_button.clicked.connect(lambda: launch_game())
play_button.setStyleSheet("""
    #FloatingPlayButton {
        background-color: #5DBB63;
        border: 3px solid;
        border-top-color: #6BCF72;
        border-left-color: #6BCF72;
        border-right-color: #3D8B40;
        border-bottom-color: #3D8B40;
        color: white;
        padding: 12px 30px;
        font-family: 'Minecraft', 'Arial Black', monospace;
        font-size: 18px;
        font-weight: bold;
        border-radius: 6px;
        min-width: 200px;
        min-height: 50px;
    }
    #FloatingPlayButton:hover {
        background-color: #6BCF72;
        border-top-color: #7DE285;
        border-left-color: #7DE285;
    }
    #FloatingPlayButton:pressed {
        background-color: #4CAF50;
        border-top-color: #5DBB63;
        border-left-color: #5DBB63;
    }
""")

# Aplicar fuente Minecraft si está disponible
try:
    minecraft_font = QFont("Minecraft", 14, QFont.Bold)
    play_button.setFont(minecraft_font)
except:
    pass

# Contenedor para centrar el botón
button_container = QWidget()
button_layout = QVBoxLayout(button_container)
button_layout.setContentsMargins(0, 0, 0, 0)
button_layout.addWidget(play_button, 0, Qt.AlignCenter)

main_container_layout.addWidget(button_container)

# Añadir el contenedor principal al layout de la página
layout.addWidget(main_container, 1)

# Guardar referencias en la ventana principal
main_window.floating_play_button = play_button
main_window.version_list = version_list

# Variable global para trackear el widget seleccionado
current_selected_widget = None

# Cargar versiones - FUNCIÓN SIMPLIFICADA
def load_versions():
    """Carga las versiones instaladas en la lista."""
    # Limpiar lista actual
    version_list.clear()
    
    vm = VersionManager()
    versions = vm.get_installed_versions()
    
    if not versions:
        # Mostrar mensaje de que no hay versiones
        play_button.setVisible(False)
        
        # Crear item especial para mensaje
        item = QListWidgetItem()
        item.setFlags(Qt.NoItemFlags)  # No seleccionable
        item.setSizeHint(QSize(0, 200))
        
        message_widget = QWidget()
        message_layout = QVBoxLayout(message_widget)
        message_layout.setAlignment(Qt.AlignCenter)
        message_layout.setSpacing(15)
        
        # Icono
        icon_label = QLabel("📦")
        icon_label.setStyleSheet("font-size: 54px; color: #888888;")
        icon_label.setAlignment(Qt.AlignCenter)
        message_layout.addWidget(icon_label)
        
        # Texto
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
        
        # Botón
        add_button = QPushButton("➕ Añadir primera versión")
        add_button.setFixedSize(200, 40)
        add_button.setCursor(Qt.PointingHandCursor)
        add_button.clicked.connect(lambda: main_window.show_extract_dialog())
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #5DBB63;
                border: 3px solid;
                border-top-color: #6BCF72;
                border-left-color: #6BCF72;
                border-right-color: #3D8B40;
                border-bottom-color: #3D8B40;
                color: white;
                font-family: 'Minecraft', 'Arial Black', monospace;
                font-size: 13px;
                font-weight: bold;
                border-radius: 6px;
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
        message_layout.addWidget(add_button, 0, Qt.AlignCenter)
        
        version_list.addItem(item)
        version_list.setItemWidget(item, message_widget)
        
    else:
        # Mostrar versiones disponibles
        for version in versions:
            # Crear widget personalizado
            item_widget = QWidget()
            item_widget.setFixedHeight(60)
            item_widget.setObjectName(f"item_{version}")
            item_widget.setProperty("version_name", version)
            
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(12, 8, 12, 8)
            item_layout.setSpacing(10)
            
            # Icono y nombre
            version_label = QLabel(f"📦 {version}")
            version_label.setStyleSheet("""
                font-size: 16px;
                color: white;
                font-weight: bold;
            """)
            version_label.setMinimumWidth(200)
            item_layout.addWidget(version_label)
            
            item_layout.addStretch()
            
            # Botón exportar
            export_btn = QPushButton("📤")
            export_btn.setToolTip(f"Exportar versión {version}")
            export_btn.setFixedSize(36, 36)
            export_btn.setCursor(Qt.PointingHandCursor)
            export_btn.setStyleSheet("""
                QPushButton {
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
                QPushButton:hover {
                    background-color: #5D9CFA;
                    border-top-color: #6EB0FF;
                    border-left-color: #6EB0FF;
                }
                QPushButton:pressed {
                    background-color: #3A75D4;
                    border-top-color: #4A86E8;
                    border-left-color: #4A86E8;
                }
            """)
            export_btn.clicked.connect(lambda checked, v=version: export_version(v))
            item_layout.addWidget(export_btn)
            
            # Botón acceso directo
            shortcut_btn = QPushButton("📝")
            shortcut_btn.setToolTip(f"Crear acceso directo para {version}")
            shortcut_btn.setFixedSize(36, 36)
            shortcut_btn.setCursor(Qt.PointingHandCursor)
            shortcut_btn.setStyleSheet("""
                QPushButton {
                    background-color: #9C27B0;
                    border: 3px solid;
                    border-top-color: #BA68C8;
                    border-left-color: #BA68C8;
                    border-right-color: #7B1FA2;
                    border-bottom-color: #7B1FA2;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #BA68C8;
                    border-top-color: #CE93D8;
                    border-left-color: #CE93D8;
                }
                QPushButton:pressed {
                    background-color: #8E24AA;
                    border-top-color: #9C27B0;
                    border-left-color: #9C27B0;
                }
            """)
            shortcut_btn.clicked.connect(lambda checked, v=version: create_shortcut(v))
            item_layout.addWidget(shortcut_btn)
            
            # Botón eliminar
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip(f"Eliminar versión {version}")
            delete_btn.setFixedSize(36, 36)
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #BB5D5D;
                    border: 3px solid;
                    border-top-color: #CF6B6B;
                    border-left-color: #CF6B6B;
                    border-right-color: #8B3D3D;
                    border-bottom-color: #8B3D3D;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 6px;
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
            delete_btn.clicked.connect(lambda checked, v=version: confirm_delete_version(v))
            item_layout.addWidget(delete_btn)
            
            # Crear item de lista
            list_item = QListWidgetItem()
            list_item.setSizeHint(QSize(0, 60))
            list_item.setData(Qt.UserRole, version)
            
            version_list.addItem(list_item)
            version_list.setItemWidget(list_item, item_widget)
        
        # Esconder el botón de jugar inicialmente
        play_button.setVisible(False)

# Función para exportar versión
def export_version(version_name):
    main_window.exporter.export_version(version_name, main_window)

# Función para crear acceso directo
def create_shortcut(version_name):
    desktop_dir = Path.home() / "Desktop"
    shortcut_path = desktop_dir / f"BoxCraft-{version_name}.desktop"
    
    script_path = Path.cwd()
    launcher_path = script_path / "main.py"
    
    if not launcher_path.exists():
        import sys
        launcher_path = Path(sys.argv[0]).resolve()
    
    shortcut_content = f"""[Desktop Entry]
Type=Application
Name=BoxCraft Launcher - {version_name}
Comment=Lanzar Minecraft {version_name}
Exec=python3 "{launcher_path}" --launch "{version_name}"
Icon=minecraft
Terminal=false
Categories=Game;
StartupWMClass=BoxCraftLauncher
"""
    
    try:
        shortcut_path.write_text(shortcut_content)
        shortcut_path.chmod(0o755)
        QMessageBox.information(main_window, "Éxito", f"Acceso directo creado en Escritorio para {version_name}")
    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"No se pudo crear acceso directo: {str(e)}")

# Función para confirmar eliminación de versión
def confirm_delete_version(version_name):
    reply = QMessageBox.question(
        main_window,
        "Confirmar eliminación",
        f"¿Estás seguro de eliminar la versión '{version_name}'?\n\nEsta acción no se puede deshacer.",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
        delete_version(version_name)

# Función para eliminar versión
def delete_version(version_name):
    vm = VersionManager()
    success, message = vm.delete_version(version_name)
    
    if success:
        # Diálogo personalizado para éxito
        success_dialog = QDialog(main_window)
        success_dialog.setWindowTitle("Versión eliminada")
        success_dialog.setFixedSize(400, 180)
        success_dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(success_dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        label = QLabel(message)
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
            success_dialog.accept()
        
        ok_btn.clicked.connect(on_ok)
        layout.addWidget(ok_btn)
        
        success_dialog.exec()
    else:
        # Diálogo personalizado para error
        error_dialog = QDialog(main_window)
        error_dialog.setWindowTitle("Error al eliminar")
        error_dialog.setFixedSize(450, 200)
        error_dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(error_dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        label = QLabel(message)
        label.setStyleSheet("color: #FF6B6B; font-size: 14px;")
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
            error_dialog.accept()
        
        ok_btn.clicked.connect(on_ok)
        layout.addWidget(ok_btn)
        
        error_dialog.exec()

# Función cuando se selecciona una versión
def on_version_selected(item):
    global current_selected_widget
    
    if item and item.flags() & Qt.ItemIsSelectable:
        version_name = item.data(Qt.UserRole)
        main_window.current_version = version_name
        
        # Obtener widget del item
        selected_widget = version_list.itemWidget(item)
        
        # Resetear estilo anterior
        if current_selected_widget:
            current_selected_widget.setStyleSheet("")
        
        # Aplicar estilo de selección SOLO al widget contenedor
        # PERO excluyendo explícitamente los QLabel
        if selected_widget:
            selected_widget.setStyleSheet("""
                QWidget {
                    background-color: #1e1e1e;
                    border: 2px solid #5DBB63;
                    border-radius: 8px;
                }
                QWidget QLabel {
                    border: none !important;
                    background-color: transparent !important;
                }
            """)
            current_selected_widget = selected_widget
        
        # Mostrar botón de jugar
        play_button.setVisible(True)

# Función para enviar notificación al escritorio
def send_desktop_notification(title, message):
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

# Función para lanzar el juego
def launch_game():
    if not main_window.current_version:
        QMessageBox.warning(main_window, "Advertencia", "Selecciona una versión primero")
        return
    
    # Ocultar la ventana
    main_window.hide()
    
    # Enviar notificación
    send_desktop_notification(
        "BoxCraft Launcher",
        f"Lanzando Minecraft {main_window.current_version}\nEl launcher se ha ocultado mientras el juego está activo."
    )
    
    # Lanzar el juego
    launcher = GameLauncher()
    success, message = launcher.launch_game(main_window.current_version)
    
    if not success:
        # Mostrar error y restaurar ventana
        main_window.show()
        QMessageBox.critical(main_window, "Error", message)

# Variable para el proceso de extracción
current_extract_process = None

# Función para cancelar extracción
def cancel_extraction(progress_dialog):
    """Cancela el proceso de extracción."""
    global current_extract_process
    if current_extract_process and current_extract_process.poll() is None:
        try:
            # Matar proceso
            import signal
            os.killpg(os.getpgid(current_extract_process.pid), signal.SIGTERM)
            current_extract_process.wait(timeout=2)
        except:
            try:
                os.killpg(os.getpgid(current_extract_process.pid), signal.SIGKILL)
            except:
                pass
    
    current_extract_process = None
    progress_dialog.close()
    QMessageBox.information(main_window, "Extracción cancelada", "La extracción ha sido cancelada.")

# Función para mostrar diálogo de extracción
def show_extract_dialog():
    dialog = ExtractDialog(main_window)
    if dialog.exec() == QDialog.Accepted:
        apk_path = dialog.get_apk_path()
        version_name = dialog.get_version_name()
        
        # Crear diálogo de progreso
        progress_dialog = QDialog(main_window)
        progress_dialog.setWindowTitle("Extrayendo APK...")
        progress_dialog.setFixedSize(400, 120)
        progress_dialog.setModal(True)
        
        progress_layout = QVBoxLayout(progress_dialog)
        label = QLabel(f"Extrayendo {version_name}...")
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 0)  # Indeterminado
        
        progress_layout.addWidget(label)
        progress_layout.addWidget(progress_bar)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #BB5D5D;
                border: 3px solid;
                border-top-color: #CF6B6B;
                border-left-color: #CF6B6B;
                border-right-color: #8B3D3D;
                border-bottom-color: #8B3D3D;
                color: white;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
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
        progress_layout.addWidget(cancel_btn)
        
        progress_dialog.show()
        QApplication.processEvents()
        
        # Función para extraer en segundo plano
        def extract():
            global current_extract_process
            vm = VersionManager()
            
            # Conectar señal de cancelación
            cancel_btn.clicked.connect(lambda: cancel_extraction(progress_dialog))
            
            try:
                success, message = vm.extract_apk(apk_path, version_name, progress_dialog)
                progress_dialog.close()
                
                if success:
                    QMessageBox.information(main_window, "Extracción completada", message)
                    # Recargar versiones
                    load_versions()
                else:
                    if "Cancelado" not in message:
                        QMessageBox.critical(main_window, "Error en extracción", message)
            except Exception as e:
                progress_dialog.close()
                QMessageBox.critical(main_window, "Error", f"Error inesperado: {str(e)}")
            finally:
                current_extract_process = None
        
        # Iniciar extracción después de un pequeño delay
        QTimer.singleShot(100, extract)

# Añadir función a la ventana principal
main_window.show_extract_dialog = show_extract_dialog

# Cargar versiones al iniciar
load_versions()