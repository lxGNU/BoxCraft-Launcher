#!/usr/bin/env python3
# build.py - Script de construcción para BoxCraft Launcher

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path
import argparse

def get_qt_plugins_path():
    """Obtiene la ruta de los plugins de Qt."""
    try:
        import PySide6
        pyside6_path = Path(PySide6.__file__).parent
        
        # Buscar plugins en diferentes ubicaciones posibles
        possible_paths = [
            pyside6_path / "Qt" / "plugins",
            pyside6_path.parent / "PySide6" / "Qt" / "plugins",
            Path("/usr/lib/x86_64-linux-gnu/qt6/plugins"),
            Path("/usr/lib/qt6/plugins"),
            Path("/usr/local/lib/qt6/plugins"),
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "platforms").exists():
                print(f"✓ Plugins Qt encontrados en: {path}")
                return path
        
        print("⚠ No se encontraron plugins Qt automáticamente")
        return None
        
    except ImportError:
        print("✗ PySide6 no está instalado")
        return None

def collect_qt_plugins():
    """Copia los plugins de Qt necesarios."""
    try:
        import PySide6
    except ImportError:
        print("✗ PySide6 no está instalado")
        return []
    
    plugins_path = get_qt_plugins_path()
    
    if not plugins_path:
        print("✗ No se pudieron encontrar los plugins Qt")
        return []
    
    # Plugins esenciales para Linux
    essential_plugins = {
        'platforms': ['libqxcb.so'],  # Plugin XCB para Linux
        'xcbglintegrations': ['libqxcb-glx-integration.so'],  # Integración OpenGL
    }
    
    # Copiar plugins necesarios
    datas = []
    for plugin_dir, plugin_files in essential_plugins.items():
        src_dir = plugins_path / plugin_dir
        
        if src_dir.exists():
            if plugin_files:  # Archivos específicos
                for plugin_file in plugin_files:
                    src_file = src_dir / plugin_file
                    if src_file.exists():
                        dest = f"PySide6/Qt/plugins/{plugin_dir}/{plugin_file}"
                        datas.append((str(src_file), dest))
                        print(f"  ✓ Plugin: {plugin_dir}/{plugin_file}")
                    else:
                        print(f"  ✗ Plugin no encontrado: {plugin_dir}/{plugin_file}")
    
    return datas

def clean_build_dirs():
    """Limpia directorios de compilación anteriores."""
    dirs_to_clean = ['build', 'dist', 'boxcraft.egg-info', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Limpiando {dir_name}...")
            shutil.rmtree(dir_name, ignore_errors=True)

def verify_resources():
    """Verifica que los recursos existan."""
    print("\nVerificando recursos...")
    
    resources = {
        'resources/': 'Directorio principal de recursos',
        'resources/pages/': 'Páginas de la aplicación',
        'resources/fonts/': 'Fuentes personalizadas',
    }
    
    all_ok = True
    for path, description in resources.items():
        if os.path.exists(path):
            print(f"  ✓ {description}: {path}")
        else:
            print(f"  ✗ FALTANTE: {description} - {path}")
            all_ok = False
    
    return all_ok

def collect_resources_for_spec():
    """Prepara los datos de recursos para el archivo .spec."""
    # NOTA: pages/ está dentro de resources/pages/
    resources = [
        ('resources/', 'resources/'),  # Incluye todo resources/
    ]
    
    return resources

def generate_spec_file():
    """Genera archivo .spec optimizado para PyInstaller."""
    
    # Verificar recursos primero
    if not verify_resources():
        print("\n⚠ ADVERTENCIA: Algunos recursos no se encontraron")
        print("  La aplicación puede no funcionar correctamente")
    
    # Obtener plugins Qt
    qt_datas = collect_qt_plugins()
    
    # Obtener recursos
    resource_datas = collect_resources_for_spec()
    
    # Combinar todos los datos
    all_datas = resource_datas + qt_datas
    
    # Convertir a string para el template
    datas_str = str(all_datas)
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# Configurar Qt antes de cualquier import
def setup_qt_environment():
    """Configura el entorno Qt para PyInstaller."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # En modo empaquetado
        plugin_path = os.path.join(sys._MEIPASS, 'PySide6', 'Qt', 'plugins')
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
        os.environ['QT_PLUGIN_PATH'] = plugin_path
        print(f"[QT] Plugin path: {{plugin_path}}")
    
    # Forzar xcb en Linux
    if sys.platform.startswith('linux'):
        os.environ['QT_QPA_PLATFORM'] = 'xcb'
        print(f"[QT] Platform: xcb")

# Ejecutar configuración Qt
setup_qt_environment()

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas={datas_str},
    hiddenimports=[
        # PySide6 esencial
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'PySide6.QtNetwork',
        'PySide6.QtXcbQpa',
        
        # Sistema básico
        'os',
        'sys',
        'json',
        'pathlib',
        'shutil',
        'subprocess',
        'tempfile',
        'threading',
        'zipfile',
        'tarfile',
        'signal',
        
        # Redes
        'requests',
        'urllib3',
        'chardet',
        'certifi',
        'idna',
        
        # SSL/Crypto
        'ssl',
        '_ssl',
        'cryptography',
        'cryptography.x509',
        
        # Tipado
        'typing',
        'collections.abc',
        
        # Importación dinámica
        'importlib',
        'importlib.util',
        'importlib.metadata',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        # Excluir módulos no necesarios para reducir tamaño
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        
        # Tests
        'test',
        'unittest',
        
        # Desarrollo
        'setuptools',
        'pip',
        'wheel',
        
        # Módulos Qt no usados
        'PySide6.QtQml',
        'PySide6.QtQuick',
        'PySide6.Qt3D',
        'PySide6.QtBluetooth',
        'PySide6.QtSql',
        'PySide6.QtSvg',
        'PySide6.QtWebEngine',
        'PySide6.QtXml',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PyZ
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Executable para Linux
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='boxcraft-launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('boxcraft.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("\n✓ Archivo .spec generado")
    return True

def run_pyinstaller_with_spec():
    """Ejecuta PyInstaller con el archivo .spec."""
    print("\nEjecutando PyInstaller...")
    
    cmd = ['pyinstaller', '--clean', 'boxcraft.spec']
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Mostrar salida importante
        output_lines = result.stdout.split('\n') + result.stderr.split('\n')
        for line in output_lines:
            if any(keyword in line.lower() for keyword in ['error', 'warning', 'writing', 'checking']):
                print(f"  {line}")
        
        print("✓ PyInstaller completado")
        return True
        
    except subprocess.CalledProcessError as e:
        print("✗ Error en PyInstaller:")
        print(e.stderr[:500])  # Mostrar primeros 500 caracteres del error
        return False

def create_simple_build():
    """Crea un build simple sin especificar plugins manualmente."""
    print("\nCreando build simple...")
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name', 'boxcraft-launcher',
        '--add-data', 'resources:resources',
        '--hidden-import', 'PySide6.QtCore',
        '--hidden-import', 'PySide6.QtGui',
        '--hidden-import', 'PySide6.QtWidgets',
        '--hidden-import', 'PySide6.QtNetwork',
        '--hidden-import', 'PySide6.QtXcbQpa',
        '--exclude-module', 'tkinter',
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'numpy',
        '--clean',
        'main.py'
    ]
    
    try:
        print("Ejecutando: " + " ".join(cmd[:10]) + "...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Build simple creado exitosamente")
            return True
        else:
            print("✗ Build simple falló")
            return False
            
    except subprocess.CalledProcessError as e:
        print("✗ Error en build simple:")
        print(e.stderr[:500])
        return False

def check_binary():
    """Verifica el binario generado."""
    binary_path = Path('dist') / 'boxcraft-launcher'
    
    if binary_path.exists():
        size = binary_path.stat().st_size / (1024 * 1024)
        print(f"\n✓ Binario creado: {binary_path}")
        print(f"  Tamaño: {size:.2f} MB")
        
        # Hacer ejecutable en Linux
        if os.name == 'posix':
            os.chmod(binary_path, 0o755)
            print("  Permisos: 755 (ejecutable)")
        
        return True
    else:
        print("\n✗ No se encontró el binario en dist/boxcraft-launcher")
        return False

def create_test_script():
    """Crea script para probar el binario."""
    script_content = '''#!/bin/bash
# test-binary.sh - Probar el binario compilado

BINARY="dist/boxcraft-launcher"

echo "=== Probando BoxCraft Launcher ==="
echo ""

if [ ! -f "$BINARY" ]; then
    echo "❌ ERROR: No se encontró $BINARY"
    echo "Primero compila con: python build.py"
    exit 1
fi

echo "✅ Binario encontrado: $BINARY"
echo "📏 Tamaño: $(du -h "$BINARY" | cut -f1)"
echo ""

echo "🔍 Verificando dependencias..."
echo "--- Dependencias XCB ---"
ldd "$BINARY" 2>/dev/null | grep -i xcb || echo "  (No se encontraron dependencias XCB)"
echo ""

echo "--- Dependencias Qt ---"
ldd "$BINARY" 2>/dev/null | grep -i qt || echo "  (No se encontraron dependencias Qt)"
echo ""

echo "🚀 Ejecutando aplicación..."
echo "Para depuración Qt, usa: QT_DEBUG_PLUGINS=1 $BINARY"
echo ""

# Intentar ejecutar
if [ "$1" == "--run" ]; then
    echo "Iniciando BoxCraft Launcher..."
    echo ""
    "$BINARY"
fi
'''
    
    with open('test-binary.sh', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    os.chmod('test-binary.sh', 0o755)
    print("✓ Script de prueba creado: test-binary.sh")

def main():
    parser = argparse.ArgumentParser(description='Compilar BoxCraft Launcher')
    parser.add_argument('--clean', action='store_true', help='Limpiar antes de compilar')
    parser.add_argument('--simple', action='store_true', help='Usar build simple')
    parser.add_argument('--test', action='store_true', help='Crear script de prueba')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("BoxCraft Launcher - Compilador")
    print("=" * 60)
    
    # Limpiar si se solicita
    if args.clean:
        clean_build_dirs()
    
    # Verificar estructura
    print("\n1. Verificando estructura del proyecto...")
    if not verify_resources():
        print("\n⚠ La estructura no es correcta.")
        print("  Asegúrate de que existan:")
        print("  - resources/ (directorio principal)")
        print("  - resources/pages/ (páginas .py)")
        print("  - resources/fonts/ (fuentes .ttf)")
        response = input("\n¿Continuar de todos modos? (s/N): ")
        if response.lower() != 's':
            print("Compilación cancelada.")
            return
    
    # Elegir método de compilación
    success = False
    if args.simple:
        print("\n2. Usando método de compilación simple...")
        success = create_simple_build()
    else:
        print("\n2. Generando archivo .spec...")
        if generate_spec_file():
            print("\n3. Ejecutando PyInstaller...")
            success = run_pyinstaller_with_spec()
    
    # Verificar resultado
    if success:
        print("\n4. Verificando binario...")
        if check_binary():
            print("\n✅ ¡Compilación exitosa!")
            
            if args.test:
                create_test_script()
                print("\n📋 Para probar el binario:")
                print("   ./test-binary.sh")
                print("   ./test-binary.sh --run  # Para ejecutar")
            
            print("\n🚀 Para ejecutar la aplicación:")
            print("   ./dist/boxcraft-launcher")
            
            print("\n🐛 Para depurar problemas Qt:")
            print("   QT_DEBUG_PLUGINS=1 ./dist/boxcraft-launcher")
        else:
            print("\n❌ No se pudo verificar el binario.")
    else:
        print("\n❌ La compilación falló.")
        print("\n💡 Soluciones posibles:")
        print("   1. Verifica que todos los recursos existan")
        print("   2. Usa --simple para un build más básico")
        print("   3. Instala dependencias: pip install -r requirements.txt")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()