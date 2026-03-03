#!/usr/bin/env python3
"""
Crea el ejecutable AES_Decrypt en carpeta (onedir) - arranque instantaneo.
Coloca este archivo junto a aes_gui_sin_licencia.py y ejecutalo.
"""

import subprocess
import sys
import os
import shutil
import platform

FUENTE = "aes_gui_sin_licencia.py"
ICONO  = "aes_icon.ico"
EXE    = "AES_Decrypt"


def c(text, code):
    return f"\033[{code}m{text}\033[0m"

def OK(t):   print(c(f"  OK     {t}", "32"))
def ERR(t):  print(c(f"  ERROR  {t}", "31"))
def WARN(t): print(c(f"  AVISO  {t}", "33"))
def INFO(t): print(c(f"  >>     {t}", "36"))
def HDR(t):  print(c(t, "1;35"))


def clean_previous():
    """Elimina dist/, build/ y el .spec de la compilacion anterior."""
    removed = []
    for folder in ["dist", "build"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            removed.append(folder + "/")
    spec = f"{EXE}.spec"
    if os.path.exists(spec):
        os.remove(spec)
        removed.append(spec)
    if removed:
        for r in removed:
            OK(f"Eliminado: {r}")
    else:
        INFO("No habia compilaciones anteriores")


def ensure_package(pip_name, import_name=None):
    import_name = import_name or pip_name
    try:
        __import__(import_name)
        OK(f"{pip_name} ya instalado")
        return True
    except ImportError:
        INFO(f"Instalando {pip_name}...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pip_name],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            OK(f"{pip_name} instalado")
            return True
        except subprocess.CalledProcessError:
            ERR(f"No se pudo instalar {pip_name}")
            return False


def generate_icon():
    if os.path.exists(ICONO):
        OK(f"Icono encontrado: {ICONO}")
        return True

    INFO("Generando icono con Pillow...")
    try:
        from PIL import Image, ImageDraw

        sizes  = [256, 128, 64, 48, 32, 16]
        frames = []

        for size in sizes:
            s   = size
            img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            for i in range(s // 2, 0, -1):
                ratio = i / (s // 2)
                r = int(15 + (80  - 15)  * (1 - ratio))
                g = int(5  + (50  - 5)   * (1 - ratio))
                b = int(40 + (180 - 40)  * (1 - ratio))
                draw.ellipse([s//2-i, s//2-i, s//2+i, s//2+i], fill=(r, g, b, 255))

            pad = int(s * 0.20); lw = s - pad * 2
            lh  = int(s * 0.38); lx = pad; ly = int(s * 0.46)
            draw.rounded_rectangle(
                [lx, ly, lx+lw, ly+lh],
                radius=max(2, int(s*0.07)),
                fill=(230, 220, 255, 255)
            )

            aw = int(lw * 0.50); ax = lx + (lw - aw) // 2
            draw.arc(
                [ax, int(s*0.14), ax+aw, int(s*0.56)],
                start=180, end=0,
                fill=(180, 165, 255, 255),
                width=max(2, int(s*0.065))
            )

            ey = int(ly + lh * 0.36); er = max(2, int(s * 0.058))
            ex = lx + lw // 2
            draw.ellipse([ex-er, ey-er, ex+er, ey+er], fill=(108, 99, 255, 255))
            kw = max(1, er // 2)
            draw.rectangle([ex-kw, ey, ex+kw, ey+int(s*0.10)], fill=(108, 99, 255, 255))
            frames.append(img)

        frames[0].save(
            ICONO, format="ICO",
            sizes=[(f.width, f.height) for f in frames],
            append_images=frames[1:]
        )
        OK(f"Icono generado: {ICONO}")
        return True

    except Exception as e:
        WARN(f"No se pudo generar el icono ({e}). Se usara icono por defecto.")
        return False


def build_exe(with_icon):
    # --onedir: carpeta con todos los archivos separados = arranque instantaneo
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",          # carpeta en vez de un solo .exe
        "--noconsole",
        f"--name={EXE}",
        "--clean",
    ]
    if with_icon and os.path.exists(ICONO):
        cmd.append(f"--icon={ICONO}")
    cmd.append(FUENTE)

    INFO("Ejecutando PyInstaller (modo carpeta)...")
    print()
    result = subprocess.run(cmd)
    return result.returncode == 0


def open_folder(path):
    sys_name = platform.system()
    if sys_name == "Windows":
        os.startfile(path)
    elif sys_name == "Darwin":
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])


def main():
    os.system("cls" if platform.system() == "Windows" else "clear")

    HDR("=" * 58)
    HDR("   CREADOR DE EJECUTABLE -- AES DECRYPT  (onedir)")
    HDR("=" * 58)
    print()
    INFO("Modo: CARPETA  --  arranque instantaneo, sin espera")
    print()

    if not os.path.exists(FUENTE):
        ERR(f"No se encuentra '{FUENTE}'")
        ERR("Asegurate de estar en la carpeta del proyecto.")
        input("\nPresiona Enter para salir...")
        return 1

    INFO(f"Sistema:  {platform.system()} {platform.release()}")
    INFO(f"Python:   {sys.version.split()[0]}")
    INFO(f"Fuente:   {FUENTE}")
    print()

    # Limpiar anterior
    HDR("[ 1 / 4 ]  Limpiando compilacion anterior")
    print()
    clean_previous()
    print()

    # Dependencias
    HDR("[ 2 / 4 ]  Verificando dependencias")
    print()
    ok_pi  = ensure_package("pyinstaller", "PyInstaller")
    ok_aes = ensure_package("pyAesCrypt")
    ok_pil = ensure_package("Pillow", "PIL")

    if not ok_pi or not ok_aes:
        print()
        ERR("Faltan dependencias criticas.")
        input("\nPresiona Enter para salir...")
        return 1

    print()

    # Icono
    HDR("[ 3 / 4 ]  Preparando icono")
    print()
    icon_ok = generate_icon()
    print()

    # Compilar
    HDR("[ 4 / 4 ]  Compilando ejecutable")
    print()
    success = build_exe(with_icon=icon_ok)
    print()

    if success:
        sys_name = platform.system()
        ext      = ".exe" if sys_name == "Windows" else ""
        dist_dir = os.path.abspath(os.path.join("dist", EXE))
        exe_path = os.path.join(dist_dir, f"{EXE}{ext}")

        HDR("=" * 58)
        HDR("   EJECUTABLE CREADO CORRECTAMENTE")
        HDR("=" * 58)
        print()
        INFO(f"Carpeta:    {dist_dir}")
        INFO(f"Ejecutable: {exe_path}")
        print()
        print("  Como distribuirlo:")
        print(f"    * Comprime la carpeta  dist/{EXE}/  en un .zip")
        print("    * El destinatario extrae el .zip y ejecuta AES_Decrypt.exe")
        print("    * Arranque instantaneo, sin espera")
        print()
        print("  Notas:")
        print("    * NO muevas solo el .exe fuera de la carpeta")
        print("    * Todos los archivos de la carpeta son necesarios")
        print("    * No requiere Python instalado")
        print()

        resp = input(f"  Abrir carpeta dist/{EXE}/? (s/n) [s]: ").strip().lower()
        if resp != "n":
            open_folder(dist_dir)
        return 0

    else:
        HDR("=" * 58)
        ERR("  ERROR AL CREAR EL EJECUTABLE")
        HDR("=" * 58)
        print()
        print("  Soluciones:")
        print("    1. pip install --upgrade pyinstaller")
        print("    2. Cierra programas que bloqueen archivos")
        print("    3. Ejecuta como administrador")
        print()
        input("  Presiona Enter para salir...")
        return 1


if __name__ == "__main__":
    try:
        code = main()
    except KeyboardInterrupt:
        print("\n\n  Cancelado.")
        code = 1
    except Exception as e:
        ERR(f"Error inesperado: {e}")
        code = 1

    input("\nPresiona Enter para salir...")
    sys.exit(code)