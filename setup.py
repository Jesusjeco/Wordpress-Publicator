"""
Script de configuración para WordPress Publicator
"""

import subprocess
import sys
import os


def create_virtual_environment():
    """Crea el entorno virtual"""
    print("🔧 Creando entorno virtual...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Entorno virtual creado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al crear entorno virtual: {e}")
        return False


def get_activation_command():
    """Obtiene el comando de activación según el sistema operativo"""
    if sys.platform == "win32":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"


def install_dependencies():
    """Instala las dependencias"""
    print("📦 Instalando dependencias...")
    
    # Determinar el ejecutable de pip en el entorno virtual
    if sys.platform == "win32":
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:
        pip_path = os.path.join("venv", "bin", "pip")
    
    try:
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencias instaladas exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar dependencias: {e}")
        return False


def main():
    """Función principal de configuración"""
    print("🚀 Configurando WordPress Publicator")
    print("=" * 40)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("requirements.txt"):
        print("❌ Error: No se encontró requirements.txt")
        print("   Asegúrate de ejecutar este script desde el directorio del proyecto")
        return
    
    # Crear entorno virtual
    if not create_virtual_environment():
        return
    
    # Instalar dependencias
    if not install_dependencies():
        return
    
    print("\n🎉 ¡Configuración completada!")
    print("\nPara usar la aplicación:")
    print(f"1. Activa el entorno virtual: {get_activation_command()}")
    print("2. Ejecuta la aplicación: python main.py")
    print("\n📝 Notas importantes:")
    print("- Asegúrate de que tu sitio WordPress tenga la REST API habilitada")
    print("- Usa credenciales de un usuario con permisos de publicación")
    print("- La URL debe incluir el protocolo (http:// o https://)")


if __name__ == "__main__":
    main()