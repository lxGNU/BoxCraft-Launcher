# Contenedor principal con scroll area
scroll_area = QScrollArea()
scroll_area.setWidgetResizable(True)
scroll_area.setStyleSheet("""
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    QScrollBar:vertical {
        background: transparent;
        width: 8px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical {
        background: #3d3d3d;
        border-radius: 4px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: #4CAF50;
    }
""")

# Widget de contenido
content_widget = QWidget()
content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

layout = QVBoxLayout(content_widget)
layout.setContentsMargins(40, 40, 40, 40)
layout.setSpacing(20)

# Logo grande
logo = QLabel("BoxCraft Launcher")
logo.setStyleSheet("""
    font-size: 48px;
    font-weight: 900;
    color: #4CAF50;
    letter-spacing: 2px;
    margin-bottom: 10px;
    text-align: center;
""")
logo.setAlignment(Qt.AlignCenter)
logo.setWordWrap(True)
layout.addWidget(logo)

# Subtítulo
subtitle = QLabel("Lanzador de: Minecraft: Bedrock Edition")
subtitle.setStyleSheet("""
    font-size: 20px;
    color: #cccccc;
    margin-bottom: 20px;
    text-align: center;
""")
subtitle.setAlignment(Qt.AlignCenter)
subtitle.setWordWrap(True)
layout.addWidget(subtitle)

# Información de versión
version_info = QLabel(f"Versión {APP_VERSION}")
version_info.setStyleSheet("""
    font-size: 16px;
    color: #888888;
    margin-bottom: 30px;
    text-align: center;
""")
version_info.setAlignment(Qt.AlignCenter)
layout.addWidget(version_info)

# Descripción
description = QLabel(
    "Un launcher no oficial para Minecraft: Bedrock Edition<br>"
    "Funciona con mcpelauncher-client y mcpelauncher-extract para correr Minecraft Bedrock<br><br>"
    "No somos responsables del programa mcpelauncher-client y tampoco de mcpelauncher-extract<br><br>"
    "<b>Código fuente:</b> <a href='https://github.com/lxGNU/BoxCraft-Launcher' style='color: #4CAF50;'>"
    "https://github.com/lxGNU/BoxCraft-Launcher</a><br><br>"
    "<b>Mcpelauncher-client:</b> <a href='https://codeberg.org/javiercplus/mcpelauncher-client-extend' style='color: #4CAF50;'>"
    "https://codeberg.org/javiercplus/mcpelauncher-client-extend</a><br><br>"
    "<b>Mcpelauncher-extract:</b> <a href='https://codeberg.org/javiercplus/mcpe-extract' style='color: #4CAF50;'>"
    "https://codeberg.org/javiercplus/mcpe-extract</a><br><br>"
    "<span style='color: #ff4444'>Este software no está asociado, avalado o aprobado por Mojang AB,<br>"
    "Microsoft Corporation, o cualquier entidad relacionada con Minecraft.</span><br><br>"
)
description.setAlignment(Qt.AlignCenter)
description.setStyleSheet("""
    QLabel {
        font-size: 14px;
        line-height: 180%;
        color: #a9b1d6;
        margin-bottom: 30px;
        text-align: center;
    }
    QLabel a {
        color: #4CAF50;
        text-decoration: none;
    }
    QLabel a:hover {
        color: #45a049;
        text-decoration: underline;
    }
""")
description.setWordWrap(True)
description.setTextFormat(Qt.RichText)
description.setOpenExternalLinks(True)
layout.addWidget(description)

# Línea separadora
separator = QFrame()
separator.setFrameShape(QFrame.HLine)
separator.setFrameShadow(QFrame.Sunken)
separator.setStyleSheet("color: #2d2d2d; margin: 20px 0;")
layout.addWidget(separator)

# Créditos
credits = QLabel("© 2026 BoxCraft Launcher - Software de código abierto - GPLv3")
credits.setAlignment(Qt.AlignCenter)
credits.setStyleSheet("color: #666666; font-size: 12px;")
layout.addWidget(credits)

# Disclaimer
disclaimer = QLabel("NOT ASSOCIATED OR APPROVED BY MOJANG")
disclaimer.setAlignment(Qt.AlignCenter)
disclaimer.setStyleSheet("""
    color: #ff4444;
    font-size: 10px;
    margin-top: 10px;
    font-style: italic;
""")
layout.addWidget(disclaimer)

# Espaciador flexible para mantener contenido arriba
layout.addStretch()

# Configurar el scroll area
content_widget.setMinimumWidth(600)  # Ancho mínimo
scroll_area.setWidget(content_widget)

# Layout principal
main_layout = QVBoxLayout(page_widget)
main_layout.setContentsMargins(0, 0, 0, 0)
main_layout.addWidget(scroll_area)