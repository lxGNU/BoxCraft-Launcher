from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QCheckBox, QScrollArea, QFrame,
                              QWidget, QSizePolicy)
from PySide6.QtGui import QFont, QPixmap
from pathlib import Path

class TermsDialog(QDialog):
    """Diálogo de términos y condiciones con opción de no mostrar más."""
    
    # Señal emitida cuando el usuario acepta los términos
    terms_accepted = Signal(bool)  # bool: si se debe mostrar de nuevo
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Términos y Condiciones - BoxCraft Launcher")
        self.resize(800, 600)
        self.setup_ui()
        self.setStyleSheet(self.get_style_sheet())
    
    def get_style_sheet(self):
        """Retorna el estilo CSS para el diálogo."""
        return """
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
            
            QLabel#SubtitleLabel {
                font-size: 14px;
                color: #888888;
                margin-bottom: 20px;
            }
            
            QLabel#SectionTitle {
                font-size: 18px;
                font-weight: bold;
                color: #4CAF50;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            
            QLabel#SectionContent {
                font-size: 14px;
                color: #cccccc;
                line-height: 150%;
                margin-bottom: 15px;
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
                image: url(:/icons/check.svg);
            }
            
            QCheckBox::indicator:hover {
                border: 2px solid #45a049;
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
        """
    
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
        subtitle_label.setObjectName("SubtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)
        
        # Área de scroll para los términos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Widget de contenido de los términos
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Contenido de los términos y condiciones
        self.create_terms_content(content_layout)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area, 1)  # Factor de expansión 1
        
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
        self.reject_button = QPushButton("RECHAZAR")
        self.reject_button.setObjectName("RejectButton")
        self.reject_button.setCursor(Qt.PointingHandCursor)
        self.reject_button.setFixedHeight(40)
        self.reject_button.clicked.connect(self.on_reject)
        
        # Botón Aceptar (Verde)
        self.accept_button = QPushButton("ACEPTAR")
        self.accept_button.setObjectName("AcceptButton")
        self.accept_button.setCursor(Qt.PointingHandCursor)
        self.accept_button.setFixedHeight(40)
        self.accept_button.clicked.connect(self.on_accept)
        
        button_layout.addWidget(self.reject_button)
        button_layout.addStretch()
        button_layout.addWidget(self.accept_button)
        
        layout.addLayout(button_layout)
        
        # Estilos específicos para los botones
        self.reject_button.setStyleSheet("""
            #RejectButton {
                background-color: #BB5D5D;
                border: 3px solid;
                border-top-color: #CF6B6B;
                border-left-color: #CF6B6B;
                border-right-color: #8B3D3D;
                border-bottom-color: #8B3D3D;
                color: white;
                padding: 8px 30px;
                font-family: 'Segoe UI', 'Noto Sans', sans-serif;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                min-width: 120px;
            }
            #RejectButton:hover {
                background-color: #CF6B6B;
                border-top-color: #E27D7D;
                border-left-color: #E27D7D;
            }
            #RejectButton:pressed {
                background-color: #AF4C4C;
                border-top-color: #BB5D5D;
                border-left-color: #BB5D5D;
            }
        """)
        
        self.accept_button.setStyleSheet("""
            #AcceptButton {
                background-color: #5DBB63;
                border: 3px solid;
                border-top-color: #6BCF72;
                border-left-color: #6BCF72;
                border-right-color: #3D8B40;
                border-bottom-color: #3D8B40;
                color: white;
                padding: 8px 30px;
                font-family: 'Segoe UI', 'Noto Sans', sans-serif;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                min-width: 120px;
            }
            #AcceptButton:hover {
                background-color: #6BCF72;
                border-top-color: #7DE285;
                border-left-color: #7DE285;
            }
            #AcceptButton:pressed {
                background-color: #4CAF50;
                border-top-color: #5DBB63;
                border-left-color: #5DBB63;
            }
        """)
    
    def create_terms_content(self, layout):
        """Crea el contenido de los términos y condiciones."""
        
        # 1. Introducción
        intro_title = QLabel("1. ACEPTACIÓN DE TÉRMINOS")
        intro_title.setObjectName("SectionTitle")
        layout.addWidget(intro_title)
        
        intro_content = QLabel(
            "Al utilizar BoxCraft Launcher, aceptas cumplir con estos términos y condiciones. "
            "Si no estás de acuerdo con alguno de estos términos, no debes usar esta aplicación."
        )
        intro_content.setObjectName("SectionContent")
        intro_content.setWordWrap(True)
        layout.addWidget(intro_content)
        
        # 2. Descargo de Responsabilidad
        disclaimer_title = QLabel("2. DESCARGO DE RESPONSABILIDAD")
        disclaimer_title.setObjectName("SectionTitle")
        layout.addWidget(disclaimer_title)
        
        disclaimer_content = QLabel(
            "BoxCraft Launcher es un software de código abierto que actúa como lanzador para Minecraft: "
            "Bedrock Edition. Este software NO está asociado, avalado o aprobado por Mojang AB, "
            "Microsoft Corporation, o cualquier entidad relacionada con Minecraft.\n\n"
            
            "El launcher NO incluye ni distribuye el juego Minecraft: Bedrock Edition. "
            "Es responsabilidad del usuario obtener una copia legítima del juego. "
            "BoxCraft Launcher no promueve, facilita ni tolera la piratería de software.\n\n"
            
            "El uso de este launcher con versiones no autorizadas del juego es responsabilidad exclusiva del usuario."
        )
        disclaimer_content.setObjectName("SectionContent")
        disclaimer_content.setWordWrap(True)
        layout.addWidget(disclaimer_content)
        
        # 3. Librerías de Terceros
        libraries_title = QLabel("3. LIBRERÍAS DE TERCEROS")
        libraries_title.setObjectName("SectionTitle")
        layout.addWidget(libraries_title)
        
        libraries_content = QLabel(
            "BoxCraft Launcher utiliza las siguientes librerías de terceros:\n\n"
            
            "• <b>mcpelauncher-client</b>: Proyecto de código abierto disponible en "
            "<a href='https://codeberg.org/javiercplus/mcpelauncher-client-extend' style='color: #4CAF50;'>"
            "Codeberg</a>\n"
            
            "• <b>mcpelauncher-extract</b>: Proyecto de código abierto disponible en "
            "<a href='https://codeberg.org/javiercplus/mcpe-extract' style='color: #4CAF50;'>"
            "Codeberg</a>\n\n"
            
            "Estos proyectos son independientes y mantenidos por terceros. "
            "Los desarrolladores de BoxCraft Launcher no son responsables de:"
            "\n\n• El funcionamiento, actualizaciones o cambios en estas librerías\n"
            "• Problemas de compatibilidad con versiones específicas del juego\n"
            "• Cualquier modificación realizada por el usuario en estas librerías"
        )
        libraries_content.setObjectName("SectionContent")
        libraries_content.setWordWrap(True)
        libraries_content.setTextFormat(Qt.RichText)
        libraries_content.setOpenExternalLinks(True)
        layout.addWidget(libraries_content)
        
        # 4. Limitación de Garantías
        warranty_title = QLabel("4. LIMITACIÓN DE GARANTÍAS")
        warranty_title.setObjectName("SectionTitle")
        layout.addWidget(warranty_title)
        
        warranty_content = QLabel(
            "EL SOFTWARE SE PROPORCIONA \"TAL CUAL\", SIN GARANTÍA DE NINGÚN TIPO, EXPRESA O IMPLÍCITA, "
            "INCLUYENDO PERO NO LIMITADO A GARANTÍAS DE COMERCIALIZACIÓN, IDONEIDAD PARA UN PROPÓSITO "
            "PARTICULAR Y NO INFRACCIÓN. EN NINGÚN CASO LOS AUTORES O TITULARES DE DERECHOS DE AUTOR "
            "SERÁN RESPONSABLES DE NINGUNA RECLAMACIÓN, DAÑOS U OTRAS RESPONSABILIDADES, YA SEA EN UNA "
            "ACCIÓN DE CONTRATO, AGRAVIO O CUALQUIER OTRA RAZÓN, QUE SURJA DE O EN CONEXIÓN CON EL "
            "SOFTWARE O EL USO U OTROS TRATOS EN EL SOFTWARE."
        )
        warranty_content.setObjectName("SectionContent")
        warranty_content.setWordWrap(True)
        warranty_content.setStyleSheet("color: #ff4444; font-style: italic;")
        layout.addWidget(warranty_content)
        
        # 5. Licencia
        license_title = QLabel("5. LICENCIA")
        license_title.setObjectName("SectionTitle")
        layout.addWidget(license_title)
        
        license_content = QLabel(
            "BoxCraft Launcher está licenciado bajo la GNU General Public License v3.0 (GPLv3). "
            "Puedes consultar la licencia completa en el archivo LICENSE.txt incluido con el software.\n\n"
            
            "<b>Código fuente:</b> "
            "<a href='https://github.com/krafairus/BoxCraft-Launcher' style='color: #4CAF50;'>"
            "https://github.com/krafairus/BoxCraft-Launcher</a>\n\n"
            
            "Eres libre de usar, modificar y distribuir este software de acuerdo con los términos "
            "de la GPLv3."
        )
        license_content.setObjectName("SectionContent")
        license_content.setWordWrap(True)
        license_content.setTextFormat(Qt.RichText)
        license_content.setOpenExternalLinks(True)
        layout.addWidget(license_content)
        
        # 6. Privacidad
        privacy_title = QLabel("6. PRIVACIDAD")
        privacy_title.setObjectName("SectionTitle")
        layout.addWidget(privacy_title)
        
        privacy_content = QLabel(
            "BoxCraft Launcher respeta tu privacidad. El software:\n\n"
            "• No recopila ni transmite información personal\n"
            "• No realiza seguimiento de tu actividad\n"
            "• No incluye anuncios ni software de terceros con fines comerciales\n"
            "• Solo accede a archivos locales necesarios para su funcionamiento\n\n"
            "Toda la configuración y datos del usuario se almacenan localmente en tu equipo."
        )
        privacy_content.setObjectName("SectionContent")
        privacy_content.setWordWrap(True)
        layout.addWidget(privacy_content)
        
        # 7. Contacto
        contact_title = QLabel("7. CONTACTO Y APOYO")
        contact_title.setObjectName("SectionTitle")
        layout.addWidget(contact_title)
        
        contact_content = QLabel(
            "BoxCraft Launcher es un proyecto de código abierto mantenido por la comunidad. "
            "Para reportar problemas o contribuir:\n\n"
            
            "<b>Repositorio:</b> "
            "<a href='https://github.com/krafairus/BoxCraft-Launcher/issues' style='color: #4CAF50;'>"
            "Issues en GitHub</a>\n\n"
            
            "El apoyo se proporciona en la medida de lo posible y no hay garantía de "
            "tiempo de respuesta o resolución de problemas."
        )
        contact_content.setObjectName("SectionContent")
        contact_content.setWordWrap(True)
        contact_content.setTextFormat(Qt.RichText)
        contact_content.setOpenExternalLinks(True)
        layout.addWidget(contact_content)
        
        # Espaciador
        layout.addStretch()
    
    def on_accept(self):
        """Maneja la aceptación de los términos."""
        dont_show_again = self.dont_show_checkbox.isChecked()
        self.terms_accepted.emit(dont_show_again)
        self.accept()
    
    def on_reject(self):
        """Maneja el rechazo de los términos (cierra la aplicación)."""
        self.reject()
        # Cerrar la aplicación completa
        import sys
        sys.exit(0)
