import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import os

# ==========================
# CONFIGURACIÓN
# ==========================

MONTO_MINIMO = 5000

# ==========================
# FUNCIONES DE FORMATO
# ==========================

def limpiar_numero(valor):
    valor = valor.replace(".", "").replace(",", "")
    return float(valor)

def formato_cop(valor):
    return f"$ {valor:,.0f}".replace(",", ".")

# ==========================
# BASE DE DATOS
# ==========================

conn = sqlite3.connect("finanzas.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS movimientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    monto REAL,
    dia TEXT,
    fecha TEXT,
    hora TEXT
)
""")
conn.commit()

# ==========================
# FUNCIONES PRINCIPALES
# ==========================

def obtener_saldo_total():
    cursor.execute("SELECT tipo, monto FROM movimientos")
    registros = cursor.fetchall()
    total = 0
    for tipo, monto in registros:
        if tipo == "Gasto":
            total -= monto
        else:
            total += monto
    return total

def agregar_movimiento(tipo):
    dia = combo_dia.get()
    monto_texto = entry_monto.get()

    if monto_texto == "":
        messagebox.showwarning("Error", "Ingrese un monto")
        return

    try:
        monto = limpiar_numero(monto_texto)
    except:
        messagebox.showerror("Error", "Monto inválido")
        return

    if monto < MONTO_MINIMO:
        messagebox.showerror(
            "Monto mínimo no permitido",
            f"No se puede agregar menos de {formato_cop(MONTO_MINIMO)}"
        )
        return

    saldo_actual = obtener_saldo_total()

    if tipo == "Gasto" and monto > saldo_actual:
        messagebox.showerror(
            "Saldo insuficiente",
            f"Saldo actual: {formato_cop(saldo_actual)}"
        )
        return

    ahora = datetime.now()
    fecha_actual = ahora.strftime("%Y-%m-%d")
    hora_actual = ahora.strftime("%I:%M:%S %p")

    cursor.execute("""
        INSERT INTO movimientos (tipo, monto, dia, fecha, hora)
        VALUES (?, ?, ?, ?, ?)
    """, (tipo, monto, dia, fecha_actual, hora_actual))

    conn.commit()

    messagebox.showinfo(
        "Éxito",
        f"{tipo} registrado a las {hora_actual}"
    )

    entry_monto.delete(0, tk.END)
    mostrar_movimientos()

def mostrar_movimientos():
    dia = combo_dia.get()
    lista.delete(*lista.get_children())

    cursor.execute("""
        SELECT tipo, monto, fecha, hora
        FROM movimientos
        WHERE dia=?
    """, (dia,))

    registros = cursor.fetchall()
    total_dia = 0

    for tipo, monto, fecha, hora in registros:
        if tipo == "Gasto":
            total_dia -= monto
        else:
            total_dia += monto

        lista.insert("", tk.END,
                     values=(tipo, formato_cop(monto), fecha, hora))

    label_total.config(text=f"Total del día: {formato_cop(total_dia)}")
    label_saldo.config(text=f"Saldo Total: {formato_cop(obtener_saldo_total())}")

# ==========================
# INTERFAZ
# ==========================

ventana = tk.Tk()
ventana.title("Sistema de Finanzas - FC Barcelona")
ventana.geometry("750x600")
ventana.resizable(False, False)

# 🚨 CARGAR IMAGEN DE FONDO (RUTA ABSOLUTA)
ruta_imagen = r"C:\Users\APRENDIZ.SOPORTEPQ\Desktop\Python\PYTHON\project_python\barcelona.png"

if os.path.exists(ruta_imagen):
    fondo = tk.PhotoImage(file=ruta_imagen)
    label_fondo = tk.Label(ventana, image=fondo)
    label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
else:
    messagebox.showwarning("Aviso", f"No se encontró la imagen '{ruta_imagen}'")

frame_principal = tk.Frame(ventana, bg="#000000")
frame_principal.place(relwidth=1, relheight=1)

tk.Label(frame_principal, text="Sistema de Finanzas",
         font=("Arial", 16, "bold"),
         fg="yellow", bg="#000000").pack(pady=10)

tk.Label(frame_principal, text="Seleccione el día:",
         fg="white", bg="#000000").pack()

dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves",
               "Viernes", "Sábado", "Domingo"]

combo_dia = ttk.Combobox(frame_principal, values=dias_semana, state="readonly")
combo_dia.pack()
combo_dia.current(0)

tk.Label(frame_principal, text="Ingrese el monto (mínimo $5.000):",
         fg="white", bg="#000000").pack(pady=5)

entry_monto = tk.Entry(frame_principal)
entry_monto.pack()

frame_botones = tk.Frame(frame_principal, bg="#020202")
frame_botones.pack(pady=10)

tk.Button(frame_botones, text="Agregar Gasto",
          bg="red", fg="white", font=("Arial", 10, "bold"),
          command=lambda: agregar_movimiento("Gasto")).grid(row=0, column=0, padx=10)

tk.Button(frame_botones, text="Agregar Dinero",
          bg="green", fg="white", font=("Arial", 10, "bold"),
          command=lambda: agregar_movimiento("Ganancia")).grid(row=0, column=1, padx=10)

# ========================================================
# MODIFICACIÓN AQUÍ: BOTÓN "VER MOVIMIENTOS" CON COLOR
# ========================================================
tk.Button(frame_principal, 
          text="Ver Movimientos",
          bg="#004d98",             # Azul Barça
          fg="#edbb00",             # Amarillo Barça
          font=("Arial", 11, "bold"), # Fuente más llamativa
          width=20,                 # Un poco más ancho
          command=mostrar_movimientos).pack(pady=10)
# ========================================================

columnas = ("Tipo", "Monto", "Fecha", "Hora")
lista = ttk.Treeview(frame_principal, columns=columnas, show="headings", height=8)

for col in columnas:
    lista.heading(col, text=col)
    lista.column(col, width=160)

lista.pack(pady=10)

label_total = tk.Label(frame_principal, text="Total del día: $ 0",
                       fg="yellow", bg="#000000",
                       font=("Arial", 12, "bold"))
label_total.pack()

label_saldo = tk.Label(frame_principal, text="Saldo Total: $ 0",
                       fg="cyan", bg="#000000",
                       font=("Arial", 12, "bold"))
label_saldo.pack()

ventana.mainloop()