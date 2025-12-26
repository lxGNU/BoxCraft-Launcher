# BoxCraft-Launcher

Launcher no oficial de Minecraft Bedrock para GNU/Linux escrito en Python con Qt6, que cuenta con control de versiones y una fácil instalación de mods, mapas y más con un solo clic. Este software no está asociado, respaldado ni aprobado por Mojang AB, Microsoft Corporation ni ninguna entidad relacionada con Minecraft.

<img width="1147" height="727" alt="imagen" src="https://github.com/user-attachments/assets/b7dc18ce-7616-4609-a4e7-6a8b572faf72" />

Opciones:
- Permite instalar el juego utilizando un archivo APK (nosotros no proporcionamos acceso a archivos APK; el acceso a los mismos es responsabilidad del usuario).
- Permite iniciar el juego utilizando mcpelauncher-client y extraer sus datos usando mcpelauncher-extract (enlaces en los créditos).
- Proporciona acceso a la instalación de complementos (add-ons), paquetes de texturas, mundos y skins (opción futura) a través de la API de Curseforge.
- Permite la instalación y gestión fácil y rápida de mods, paquetes de texturas y mundos.

Creado usando los proyectos:
- mcpelauncher-client: https://codeberg.org/javiercplus/mcpelauncher-client-extend  
- mcpelauncher-extract: https://codeberg.org/javiercplus/mcpe-extract

Compilar binario:

    python build.py --clean --simple --test
(Mueve el archivo compilado en dist a la carpeta del proyecto)

Compilar paquete Deb:

    dch --create -D stable --package "boxcraft-launcher" --newversion=1.x.x "New release."

    sudo apt build-dep .

    dpkg-buildpackage -Zxz -rfakeroot -b


Agradecimientos especiales a Deepin Latin Code - Bajo la licencia GPL v3.0.
