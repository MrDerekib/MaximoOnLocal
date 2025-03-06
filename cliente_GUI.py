import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import webbrowser
import tkinter.font as tkFont

db_path = "maximo_data.db"


def fetch_data(filter_text, search_by):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = f"SELECT * FROM maximo WHERE {search_by} LIKE ?"
    cursor.execute(query, (f"%{filter_text}%",))
    rows = cursor.fetchall()
    conn.close()
    return rows


from update_database import setup_driver, login
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


def open_maximo(ot):
    URL = "https://eam.indraweb.net/maximo/webclient/login/login.jsp"
    from update_database import load_credentials
    stored_credentials = load_credentials()
    if not stored_credentials:
        cred_window = tk.Toplevel()
        cred_window.geometry("300x150")
        cred_window.title("Ingrese sus credenciales")
        tk.Label(cred_window, text="Usuario:").pack()
        username_entry = tk.Entry(cred_window)
        username_entry.focus_set()
        username_entry.pack()
        tk.Label(cred_window, text="Contraseña:").pack()
        password_entry = tk.Entry(cred_window, show="*")
        password_entry.pack()
        password_entry.bind("<Return>", lambda event: save_credentials())

        def save_credentials():
            from update_database import save_credentials
            nonlocal stored_credentials
            stored_credentials = {"username": username_entry.get(), "password": password_entry.get()}
            save_credentials(stored_credentials["username"], stored_credentials["password"])
            cred_window.destroy()

        tk.Button(cred_window, text="Guardar", command=save_credentials).pack()
        cred_window.wait_window()
    if not stored_credentials:
        print("Error: No hay credenciales guardadas.")
        return

    USERNAME = stored_credentials["username"]
    PASSWORD = stored_credentials["password"]

    driver = setup_driver()
    try:
        login(driver, URL, USERNAME, PASSWORD)
        print("Login exitoso, accediendo a la búsqueda de OT...")

        time.sleep(5)  # Esperar a que cargue la interfaz de Maximo
        search_box = driver.find_element(By.ID, "quicksearch")
        search_box.send_keys(ot)
        search_box.send_keys(Keys.RETURN)
        print("OT ingresada y búsqueda ejecutada correctamente.")
        # Próximo paso: esperar tu guía para encontrar el input donde pegar la OT

    except Exception as e:
        print(f"Error al abrir Maximo: {e}")
        driver.quit()


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

    def copy_to_clipboard():
        selected_item = tree.selection()
        if selected_item:
            item_values = tree.item(selected_item, "values")
            if item_values:
                col_index = selected_column
                col_index = selected_column  # Convertir a índice de columna (0-based)
                if 0 <= col_index < len(item_values):
                    value = item_values[col_index]
                    root.clipboard_clear()
                    root.clipboard_append(value)
                    root.update()
                    print(f"Copiado al portapapeles: {value}")
                    tk.messagebox.showinfo("Copiado", f"Se copió: {value}")

    # Crear menú contextual
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Copiar", command=copy_to_clipboard)

    def show_context_menu(event):
        global selected_column
        selected_item = tree.selection()
        if selected_item:
            col = tree.identify_column(event.x)
            selected_column = int(col[1:]) - 1  # Convertir a índice de columna (0-based)
            menu.post(event.x_root, event.y_root)
        menu.post(event.x_root, event.y_root)

    tree.bind("<Button-3>", show_context_menu)

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

