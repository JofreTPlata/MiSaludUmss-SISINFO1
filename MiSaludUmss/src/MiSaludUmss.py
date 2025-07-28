import customtkinter as ctk
from tkinter import messagebox
import os

# Apariencia
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

# ------------------ FUNCIONES DE ARCHIVO ------------------

def crear_directorio():
    os.makedirs("datos", exist_ok=True)
    open("datos/usuarios.txt", "a").close()
    open("datos/fichas.txt", "a").close()

def usuario_existe(usuario):
    with open("datos/usuarios.txt", "r") as f:
        for linea in f:
            if not linea.strip(): continue
            partes = linea.strip().split(",")
            if len(partes) < 2: continue
            u, _ = partes
            if u == usuario:
                return True
    return False

def guardar_usuario(usuario, contrasena):
    if usuario_existe(usuario):
        return False
    with open("datos/usuarios.txt", "a") as f:
        f.write(f"{usuario},{contrasena}\n")
    return True

def validar_credenciales(usuario, contrasena):
    with open("datos/usuarios.txt", "r") as f:
        for linea in f:
            if not linea.strip(): continue
            partes = linea.strip().split(",")
            if len(partes) < 2: continue
            u, c = partes
            if u == usuario and c == contrasena:
                return True
    return False

def guardar_ficha(usuario, fecha, hora, doctor):
    with open("datos/fichas.txt", "a") as f:
        f.write(f"{usuario},{fecha},{hora},{doctor}\n")

def leer_fichas(usuario):
    fichas = []
    with open("datos/fichas.txt", "r") as f:
        for linea in f:
            if not linea.strip(): continue
            partes = linea.strip().split(",")
            if len(partes) < 4: continue
            u, fecha, hora, doctor = partes
            if u == usuario:
                fichas.append((fecha, hora, doctor))
    return fichas

def cancelar_ficha(usuario, fecha):
    nuevas = []
    cancelada = False
    with open("datos/fichas.txt", "r") as f:
        for linea in f:
            if not linea.strip(): continue
            partes = linea.strip().split(",")
            if len(partes) < 4: continue
            u, f_fecha, hora, doctor = partes
            if u == usuario and f_fecha == fecha:
                cancelada = True
                continue
            nuevas.append(linea)
    with open("datos/fichas.txt", "w") as f:
        for linea in nuevas:
            f.write(linea + "\n")
    return cancelada

def generar_comprobante(usuario, ficha):
    contenido = (
        f"--- COMPROBANTE DE RESERVA ---\n"
        f"Usuario: {usuario}\nFecha: {ficha[0]}\nHora: {ficha[1]}\nDoctor: {ficha[2]}"
    )
    archivo = f"datos/comprobante_{usuario}_{ficha[0].replace('-', '')}.txt"
    with open(archivo, "w") as f:
        f.write(contenido)
    return archivo

# ------------------ INTERFACES ------------------

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MiSalud UMSS - Ingreso")
        self.geometry("400x300")

        ctk.CTkLabel(self, text="Usuario:").pack(pady=(20, 0))
        self.usuario_entry = ctk.CTkEntry(self)
        self.usuario_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Contraseña:").pack()
        self.contra_entry = ctk.CTkEntry(self, show="*")
        self.contra_entry.pack(pady=5)

        ctk.CTkButton(self, text="Iniciar Sesión", command=self.login).pack(pady=10)
        ctk.CTkButton(self, text="Registrarse", command=self.registrar).pack()

    def login(self):
        usuario = self.usuario_entry.get()
        contrasena = self.contra_entry.get()
        if validar_credenciales(usuario, contrasena):
            self.destroy()
            MenuPrincipal(usuario).mainloop()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    def registrar(self):
        usuario = self.usuario_entry.get()
        contrasena = self.contra_entry.get()
        if not usuario or not contrasena:
            messagebox.showwarning("Advertencia", "Completa todos los campos")
            return
        if guardar_usuario(usuario, contrasena):
            messagebox.showinfo("Registro", "Usuario registrado correctamente")
        else:
            messagebox.showerror("Error", "El usuario ya existe")

class MenuPrincipal(ctk.CTk):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.title(f"Bienvenido {usuario}")
        self.geometry("400x320")

        ctk.CTkLabel(self, text="Menú Principal", font=("Arial", 18)).pack(pady=15)
        ctk.CTkButton(self, text="Reservar Ficha", command=self.abrir_reserva).pack(pady=5)
        ctk.CTkButton(self, text="Ver Fichas Reservadas", command=self.ver_fichas).pack(pady=5)
        ctk.CTkButton(self, text="Cancelar Ficha", command=self.cancelar_ficha).pack(pady=5)
        ctk.CTkButton(self, text="Cerrar Sesión", command=self.destroy).pack(pady=10)

    def abrir_reserva(self):
        ReservaWindow(self.usuario)

    def ver_fichas(self):
        FichasWindow(self.usuario)

    def cancelar_ficha(self):
        CancelarWindow(self.usuario)

class ReservaWindow(ctk.CTkToplevel):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.title("Reservar Ficha")
        self.geometry("350x250")

        ctk.CTkLabel(self, text="Fecha (YYYY-MM-DD):").pack()
        self.fecha_entry = ctk.CTkEntry(self)
        self.fecha_entry.pack()

        ctk.CTkLabel(self, text="Hora (HH:MM):").pack()
        self.hora_entry = ctk.CTkEntry(self)
        self.hora_entry.pack()

        ctk.CTkLabel(self, text="Doctor:").pack()
        self.doctor_entry = ctk.CTkEntry(self)
        self.doctor_entry.pack()

        ctk.CTkButton(self, text="Reservar", command=self.reservar).pack(pady=10)

    def reservar(self):
        fecha = self.fecha_entry.get()
        hora = self.hora_entry.get()
        doctor = self.doctor_entry.get()
        if fecha and hora and doctor:
            guardar_ficha(self.usuario, fecha, hora, doctor)
            messagebox.showinfo("Éxito", "Ficha reservada correctamente")
            self.destroy()
        else:
            messagebox.showwarning("Campos incompletos", "Llena todos los campos")

class FichasWindow(ctk.CTkToplevel):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.title("Fichas Reservadas")
        self.geometry("400x300")

        ctk.CTkLabel(self, text="Tus fichas reservadas:").pack(pady=5)
        fichas = leer_fichas(usuario)
        for ficha in fichas:
            texto = f"Fecha: {ficha[0]}, Hora: {ficha[1]}, Doctor: {ficha[2]}"
            ctk.CTkLabel(self, text=texto).pack()

        if fichas:
            ctk.CTkButton(self, text="Generar Comprobante", command=lambda: self.generar(fichas[-1])).pack(pady=10)

    def generar(self, ficha):
        archivo = generar_comprobante(self.usuario, ficha)
        messagebox.showinfo("Comprobante", f"Guardado en:\n{archivo}")

class CancelarWindow(ctk.CTkToplevel):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.title("Cancelar Ficha")
        self.geometry("300x150")

        ctk.CTkLabel(self, text="Fecha a cancelar (YYYY-MM-DD):").pack()
        self.fecha_entry = ctk.CTkEntry(self)
        self.fecha_entry.pack()

        ctk.CTkButton(self, text="Cancelar Ficha", command=self.cancelar).pack(pady=10)

    def cancelar(self):
        fecha = self.fecha_entry.get()
        if cancelar_ficha(self.usuario, fecha):
            messagebox.showinfo("Éxito", "Ficha cancelada exitosamente")
            self.destroy()
        else:
            messagebox.showerror("Error", "No se encontró ficha para esa fecha")

# ------------------ EJECUCIÓN ------------------

if __name__ == "__main__":
    crear_directorio()
    app = LoginWindow()
    app.mainloop()
