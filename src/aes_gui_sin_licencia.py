import os
import platform
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    import pyAesCrypt
    PYAESCRYPT_AVAILABLE = True
except ImportError:
    PYAESCRYPT_AVAILABLE = False

# ─────────────────────────────────────────────
#  Paleta de colores y estilos
# ─────────────────────────────────────────────
BG        = "#0f1117"
SURFACE   = "#1a1d27"
BORDER    = "#2a2d3e"
ACCENT    = "#6c63ff"
ACCENT_LT = "#8b85ff"
SUCCESS   = "#22c55e"
ERROR     = "#ef4444"
WARNING   = "#f59e0b"
TEXT      = "#e2e8f0"
MUTED     = "#64748b"
FONT_MAIN = ("Consolas", 10)
FONT_BOLD = ("Consolas", 10, "bold")
FONT_H1   = ("Consolas", 15, "bold")
FONT_H2   = ("Consolas", 11, "bold")
FONT_MONO = ("Courier New", 9)


class StyledButton(tk.Canvas):
    """Botón personalizado con efecto hover y diseño moderno."""

    def __init__(self, parent, text, command=None, accent=False, width=180, height=38, **kwargs):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bd=0, bg=BG, cursor="hand2")
        self.command  = command
        self.accent   = accent
        self.txt      = text
        self.w        = width
        self.h        = height
        self._enabled = True

        self._bg_normal  = ACCENT   if accent else SURFACE
        self._bg_hover   = ACCENT_LT if accent else "#22253a"
        self._current_bg = self._bg_normal

        self._draw()
        self.bind("<Enter>",    self._hover)
        self.bind("<Leave>",    self._leave)
        self.bind("<Button-1>", self._click)

    def _draw(self, bg=None):
        self.delete("all")
        bg = bg or self._current_bg
        r = 8
        x1, y1, x2, y2 = 1, 1, self.w - 1, self.h - 1

        # Rounded rect
        self.create_arc(x1, y1, x1+r*2, y1+r*2, start=90,  extent=90,  fill=bg, outline=bg)
        self.create_arc(x2-r*2, y1, x2, y1+r*2, start=0,   extent=90,  fill=bg, outline=bg)
        self.create_arc(x1, y2-r*2, x1+r*2, y2, start=180, extent=90,  fill=bg, outline=bg)
        self.create_arc(x2-r*2, y2-r*2, x2, y2, start=270, extent=90,  fill=bg, outline=bg)
        self.create_rectangle(x1+r, y1, x2-r, y2, fill=bg, outline=bg)
        self.create_rectangle(x1, y1+r, x2, y2-r, fill=bg, outline=bg)

        # Border
        bc = ACCENT if self.accent else BORDER
        self.create_arc(x1, y1, x1+r*2, y1+r*2, start=90,  extent=90,  style="arc", outline=bc)
        self.create_arc(x2-r*2, y1, x2, y1+r*2, start=0,   extent=90,  style="arc", outline=bc)
        self.create_arc(x1, y2-r*2, x1+r*2, y2, start=180, extent=90,  style="arc", outline=bc)
        self.create_arc(x2-r*2, y2-r*2, x2, y2, start=270, extent=90,  style="arc", outline=bc)
        self.create_line(x1+r, y1, x2-r, y1, fill=bc)
        self.create_line(x1+r, y2, x2-r, y2, fill=bc)
        self.create_line(x1, y1+r, x1, y2-r, fill=bc)
        self.create_line(x2, y1+r, x2, y2-r, fill=bc)

        color = TEXT if self._enabled else MUTED
        self.create_text(self.w // 2, self.h // 2, text=self.txt,
                         fill=color, font=FONT_BOLD)

    def _hover(self, _=None):
        if self._enabled:
            self._current_bg = self._bg_hover
            self._draw()

    def _leave(self, _=None):
        if self._enabled:
            self._current_bg = self._bg_normal
            self._draw()

    def _click(self, _=None):
        if self._enabled and self.command:
            self.command()

    def config_state(self, enabled: bool):
        self._enabled = enabled
        self._current_bg = self._bg_normal if enabled else "#12141e"
        self.configure(cursor="hand2" if enabled else "arrow")
        self._draw()


class AESDecryptorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AES Decrypt — Sin Licencia")
        self.root.geometry("680x480")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        # Icono de la ventana (barra de titulo, taskbar, alt+tab)
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aes_icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

        self.file_path    = tk.StringVar()
        self.password     = tk.StringVar()
        self.show_pass    = tk.BooleanVar(value=False)
        self.is_processing = False

        self._build_ui()

    # ─────────────────────────────────────────
    #  UI
    # ─────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=SURFACE, pady=18)
        header.pack(fill="x")

        tk.Label(header, text="🔐  AES DECRYPT", font=("Consolas", 18, "bold"),
                 bg=SURFACE, fg=ACCENT).pack()
        tk.Label(header, text="Desencriptador de archivos .aes · Sin licencia adicional",
                 font=FONT_MONO, bg=SURFACE, fg=MUTED).pack()

        # Separador
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

        # Badge de estado
        badge_color = SUCCESS if PYAESCRYPT_AVAILABLE else ERROR
        badge_text  = ("✔  pyAesCrypt disponible · listo para usar"
                       if PYAESCRYPT_AVAILABLE
                       else "✘  pyAesCrypt no instalado · ejecuta: pip install pyAesCrypt")

        badge = tk.Frame(self.root, bg=BG, pady=10)
        badge.pack(fill="x", padx=24)
        tk.Label(badge, text=badge_text, font=FONT_MONO,
                 bg=BG, fg=badge_color).pack(anchor="w")

        # ── Cuerpo ──
        body = tk.Frame(self.root, bg=BG, padx=24)
        body.pack(fill="both", expand=True)

        # Archivo
        self._section_label(body, "ARCHIVO DE ENTRADA  (.aes)")
        file_row = tk.Frame(body, bg=BG)
        file_row.pack(fill="x", pady=(4, 12))

        self.entry_file = tk.Entry(
            file_row, textvariable=self.file_path,
            font=FONT_MAIN, bg=SURFACE, fg=TEXT,
            insertbackground=ACCENT, relief="flat",
            highlightthickness=1, highlightcolor=ACCENT,
            highlightbackground=BORDER, bd=0
        )
        self.entry_file.pack(side="left", fill="x", expand=True,
                             ipady=7, padx=(0, 8))

        StyledButton(file_row, "📂  Explorar", command=self.pick_file,
                     width=120, height=36).pack(side="left")

        # Contraseña
        self._section_label(body, "CONTRASEÑA")
        pass_row = tk.Frame(body, bg=BG)
        pass_row.pack(fill="x", pady=(4, 6))

        self.entry_pass = tk.Entry(
            pass_row, textvariable=self.password, show="●",
            font=FONT_MAIN, bg=SURFACE, fg=TEXT,
            insertbackground=ACCENT, relief="flat",
            highlightthickness=1, highlightcolor=ACCENT,
            highlightbackground=BORDER, bd=0
        )
        self.entry_pass.pack(side="left", fill="x", expand=True, ipady=7)

        toggle = tk.Checkbutton(
            pass_row, text=" Mostrar", variable=self.show_pass,
            command=self._toggle_pass,
            bg=BG, fg=MUTED, activebackground=BG,
            activeforeground=TEXT, selectcolor=SURFACE,
            font=FONT_MONO, bd=0, highlightthickness=0
        )
        toggle.pack(side="left", padx=(10, 0))

        # Barra de progreso
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.Horizontal.TProgressbar",
                         troughcolor=SURFACE, background=ACCENT,
                         bordercolor=BORDER, lightcolor=ACCENT,
                         darkcolor=ACCENT, thickness=6)

        self.progress_bar = ttk.Progressbar(
            body, mode="indeterminate", length=632,
            style="Dark.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill="x", pady=(14, 0))

        # Estado
        self.lbl_status = tk.Label(
            body, text="", font=FONT_MONO, bg=BG, fg=MUTED, anchor="w"
        )
        self.lbl_status.pack(fill="x", pady=(6, 0))

        # ── Botones ──
        btn_row = tk.Frame(self.root, bg=BG, padx=24, pady=18)
        btn_row.pack(fill="x")

        self.btn_decrypt = StyledButton(
            btn_row, "🔓  Desencriptar",
            command=self.decrypt, accent=True, width=220, height=42
        )
        self.btn_decrypt.pack(side="left", padx=(0, 10))

        StyledButton(btn_row, "🧹  Limpiar",
                     command=self.clear, width=140, height=42).pack(side="left")

        # Footer
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")
        tk.Label(self.root, text="pyAesCrypt · AES-256-CBC · No requiere AES Crypt instalado",
                 font=FONT_MONO, bg=SURFACE, fg=MUTED, pady=8).pack(fill="x")

    def _section_label(self, parent, text):
        tk.Label(parent, text=text, font=("Consolas", 8, "bold"),
                 bg=BG, fg=MUTED).pack(anchor="w", pady=(6, 0))

    # ─────────────────────────────────────────
    #  Acciones
    # ─────────────────────────────────────────
    def _toggle_pass(self):
        self.entry_pass.config(show="" if self.show_pass.get() else "●")

    def pick_file(self):
        path = filedialog.askopenfilename(
            title="Seleccionar archivo .aes",
            filetypes=[("Archivos AES", "*.aes"), ("Todos los archivos", "*.*")]
        )
        if path:
            self.file_path.set(path)
            self._set_status(f"Archivo cargado: {os.path.basename(path)}", MUTED)

    def clear(self):
        self.file_path.set("")
        self.password.set("")
        self._set_status("", MUTED)

    def _set_status(self, msg, color=MUTED):
        self.lbl_status.config(text=msg, fg=color)

    def decrypt(self):
        if not PYAESCRYPT_AVAILABLE:
            messagebox.showerror(
                "Librería no disponible",
                "pyAesCrypt no está instalado.\n\n"
                "Abre una terminal y ejecuta:\n"
                "    pip install pyAesCrypt\n\n"
                "Luego reinicia esta aplicación."
            )
            return

        if self.is_processing:
            messagebox.showwarning("En proceso", "Ya hay una desencriptación en curso.")
            return

        in_file = self.file_path.get().strip()
        pwd     = self.password.get()

        if not in_file:
            messagebox.showwarning("Sin archivo", "Selecciona un archivo .aes primero.")
            return
        if not os.path.exists(in_file):
            messagebox.showerror("Error", "El archivo seleccionado no existe.")
            return
        if not pwd:
            messagebox.showwarning("Sin contraseña", "Ingresa la contraseña.")
            return

        default_out = in_file[:-4] if in_file.lower().endswith(".aes") else in_file + ".out"
        out_file = filedialog.asksaveasfilename(
            title="Guardar archivo desencriptado como…",
            initialfile=os.path.basename(default_out),
            defaultextension="",
            filetypes=[("Todos los archivos", "*.*")]
        )
        if not out_file:
            return

        self.is_processing = True
        self.btn_decrypt.config_state(False)
        self.progress_bar.start(12)
        self._set_status("⏳  Desencriptando, espera un momento…", ACCENT_LT)

        t = threading.Thread(target=self._decrypt_worker, args=(in_file, pwd, out_file))
        t.daemon = True
        t.start()

    # ─────────────────────────────────────────
    #  Worker (hilo secundario)
    # ─────────────────────────────────────────
    def _decrypt_worker(self, in_file, password, out_file):
        try:
            pyAesCrypt.decryptFile(in_file, out_file, password, 64 * 1024)
            self.root.after(0, self._on_success, out_file)
        except ValueError:
            self.root.after(0, self._on_error,
                            "Contraseña incorrecta o archivo corrupto.\n"
                            "Verifica la contraseña e intenta nuevamente.")
        except Exception as e:
            self.root.after(0, self._on_error, str(e))

    def _on_success(self, out_file):
        self._reset_ui()
        self._set_status(f"✔  Guardado en: {out_file}", SUCCESS)
        messagebox.showinfo("¡Listo!", f"Archivo desencriptado correctamente:\n\n{out_file}")

        if messagebox.askyesno("Abrir carpeta", "¿Abrir la carpeta del archivo resultado?"):
            folder = os.path.dirname(out_file)
            sys_name = platform.system()
            if sys_name == "Windows":
                os.startfile(folder)
            elif sys_name == "Darwin":
                subprocess.run(["open", folder])
            else:
                subprocess.run(["xdg-open", folder])

    def _on_error(self, msg):
        self._reset_ui()
        self._set_status("✘  Error durante la desencriptación.", ERROR)
        messagebox.showerror("Error al desencriptar", msg)

    def _reset_ui(self):
        self.is_processing = False
        self.progress_bar.stop()
        self.btn_decrypt.config_state(True)


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg=BG)
    app = AESDecryptorGUI(root)
    root.mainloop()