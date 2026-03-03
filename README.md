# 🔐 AES Decrypt — Sin Licencia

Herramienta de escritorio para desencriptar archivos `.aes` generados con el estándar
AES Crypt (AES-256-CBC), sin necesidad de tener AES Crypt instalado en el sistema.

## Características

- Desencriptación de archivos `.aes` con AES-256-CBC via `pyAesCrypt`
- Interfaz gráfica oscura construida con Tkinter
- Procesamiento en hilo secundario (no bloquea la UI durante la operación)
- Ícono personalizado en barra de título, taskbar y Alt+Tab
- Generación automática del ejecutable `.exe` con ícono incluido (PyInstaller)
- Compatible con Windows, Linux y macOS

## Archivos del proyecto

| Archivo | Descripción |
|---|---|
| `aes_gui_sin_licencia.py` | Aplicación principal con interfaz gráfica |
| `crear_ejecutable.py` | Script para compilar el `.exe` con PyInstaller |
| `aes_icon.ico` | Ícono del programa (generado automáticamente si no existe) |

## Requisitos

- Python 3.8 o superior
- `pyAesCrypt` — desencriptación AES-256-CBC
- `Pillow` — generación del ícono (opcional)
- `PyInstaller` — solo si deseas compilar el ejecutable

Instalación de dependencias:

pip install pyAesCrypt Pillow pyinstaller


## Uso

### Ejecutar desde Python

python aes_gui_sin_licencia.py


### Compilar ejecutable

python crear_ejecutable.py

El script limpia compilaciones anteriores, instala las dependencias necesarias,
genera el ícono automáticamente si no existe y produce la carpeta `dist/AES_Decrypt/`
lista para distribuir.

> El ejecutable usa modo `--onedir` para arranque instantáneo sin descompresión temporal.

## Distribución

Comprime la carpeta `dist/AES_Decrypt/` en un `.zip`.
El destinatario solo extrae y ejecuta `AES_Decrypt.exe`, sin necesidad de Python instalado.

## Licencia

MIT
