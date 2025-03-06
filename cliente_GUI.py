import sqlite3
import tkinter as tk
from tkinter import ttk
import webbrowser

db_path = "maximo_data.db"


def fetch_data(filter_text, search_by):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = f"SELECT * FROM maximo WHERE {search_by} LIKE ?"
    cursor.execute(query, (f"%{filter_text}%",))
    rows = cursor.fetchall()
    conn.close()
    return rows


def open_maximo(ot):
    url = f"https://eam.indraweb.net/maximo/ui/?ot={ot}"
    webbrowser.open(url)


def update_table():
    for row in tree.get_children():
        tree.delete(row)
    filter_text = search_var.get()
    search_by = search_option.get()
    data = fetch_data(filter_text, search_by)
    for row in data:
        tree.insert("", "end", values=row)


def create_gui():
    global tree, search_var, search_option

    root = tk.Tk()
    root.title("Cliente de Base de Datos Maximo")
    root.geometry("1000x600")

    frame = tk.Frame(root)
    frame.pack(pady=20)

    search_var = tk.StringVar()
    search_entry = tk.Entry(frame, textvariable=search_var, width=50)
    search_entry.pack(side=tk.LEFT, padx=10)
    search_entry.bind("<Return>", lambda event: update_table())

    search_option = tk.StringVar(value="OT")
    radio_frame = tk.Frame(frame)
    radio_frame.pack(side=tk.LEFT, padx=10)
    tk.Radiobutton(radio_frame, text="OT", variable=search_option, value="OT").pack(anchor='w')
    tk.Radiobutton(radio_frame, text="Nº de serie", variable=search_option, value="Nº_de_serie").pack(anchor='w')
    tk.Radiobutton(radio_frame, text="Descripción", variable=search_option, value="Descripción").pack(anchor='w')

    search_button = tk.Button(frame, text="Buscar", command=update_table)
    search_button.pack(side=tk.LEFT)

    columns = ("OT", "Descripción", "Nº de serie", "Fecha", "Cliente", "Tipo de trabajo", "Seguimiento", "Planta")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)

    tree.pack(expand=True, fill="both")

    def on_double_click(event):
        selected_item = tree.selection()
        if selected_item:
            ot = tree.item(selected_item, "values")[0]
            open_maximo(ot)

    tree.bind("<Double-1>", on_double_click)

    update_table()

    root.mainloop()


if __name__ == "__main__":
    create_gui()
