import os
import time
import getpass
import shutil
import sqlite3
import pandas as pd
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

download_dir = os.path.expanduser("~/Downloads")
db_path = "maximo_data.db"


def setup_driver():
    print("Inicializando el navegador...")
    options = webdriver.FirefoxOptions()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", download_dir)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.ms-excel")
    options.set_preference("pdfjs.disabled", True)
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    print("Navegador inicializado correctamente.")
    return driver


def login(driver, url, username, password):
    max_attempts = 3
    attempt = 0
    while attempt < max_attempts:
        print(f"Intento {attempt + 1} de {max_attempts} para cargar la página de login...")
        driver.get(url)
        time.sleep(5)
        body_text = driver.find_element(By.TAG_NAME, "body").text
        if "Maximo" in driver.title and len(body_text) > 50:
            print("Página de login cargada correctamente.")
            break
        else:
            print("Error al cargar la página. Reintentando...")
            attempt += 1
            if attempt == max_attempts:
                print("No se pudo cargar la página después de 3 intentos. Saliendo...")
                driver.quit()
                exit(1)
    print("Ingresando credenciales...")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password + Keys.RETURN)
    time.sleep(5)

    # Verificar si hay error de login
    try:
        error_element = driver.find_element(By.CLASS_NAME, "errorText")
        error_message = error_element.text if error_element else ""
        if "BMXAA7901E" in error_message:
            print("Error: Credenciales incorrectas. No se puede iniciar sesión.")
            driver.quit()
            exit(1)
            print("Error: Credenciales incorrectas. No se puede iniciar sesión.")
            driver.quit()
            exit(1)
    except:
        print("Login exitoso. Continuando...")

    print("Accediendo a la sección de filtros...")
    driver.find_element(By.ID, "FavoriteApp_WO_TR").click()
    time.sleep(5)
    print("Sección de filtros abierta.")


def apply_filter(driver, filters):
    print("Aplicando filtros...")
    for field_id, value in filters.items():
        print(f"Llenando campo {field_id} con {value}")
        field = driver.find_element(By.ID, field_id)
        field.clear()
        field.send_keys(value)
        time.sleep(1)
    field.send_keys(Keys.RETURN)
    time.sleep(3)
    print("Filtros aplicados correctamente.")


def download_file(driver):
    print("Descargando archivo...")
    time.sleep(3)
    download_button = driver.find_element(By.ID, "mx38-lb4")
    driver.execute_script("arguments[0].click();", download_button)
    time.sleep(45)
    print("Archivo descargado correctamente.")


def move_latest_file(destination_folder):
    print("Moviendo archivo descargado...")
    files = sorted([f for f in os.listdir(download_dir) if f.endswith(".xls")],
                   key=lambda x: os.path.getctime(os.path.join(download_dir, x)), reverse=True)
    if files:
        latest_file = os.path.join(download_dir, files[0])
        new_location = os.path.join(destination_folder, files[0])
        shutil.move(latest_file, new_location)
        print(f"Archivo movido a {new_location}")
        return new_location
    print("No se encontró archivo para mover.")
    return None


def process_html_table(file_path):
    print(f"Procesando archivo: {file_path}")
    dfs = pd.read_html(file_path)
    print("Columnas detectadas en la tabla HTML:", dfs[0].columns)
    print("Columnas reales en la tabla HTML:", dfs[0].columns)
    df = dfs[0].iloc[1:, [0, 12, 15, 2, 3, 9, 5, 13]].copy()
    df.columns = ["OT", "Descripción", "Nº de serie", "Fecha", "Cliente", "Tipo de trabajo", "Seguimiento", "Planta"]
    df["Fecha"] = pd.to_datetime(df["Fecha"], format='%d/%m/%y %H:%M:%S', errors='coerce').dt.strftime('%Y-%m-%d')
    df['Planta'] = df['Planta'].fillna('').astype(str).str.strip()
    df = df.where(pd.notnull(df), None)
    if 'ColumnaExtra' in df.columns:
        df = df.drop(columns=['ColumnaExtra'])
    # Eliminar columna extra innecesaria
    print("Valores en la columna seleccionada como 'Planta':", df['Planta'].unique())
    print("Archivo procesado correctamente.")

    # Guardar clientes únicos
    unique_clients = [c.replace(' ', ' ').strip() for c in df['Cliente'].dropna().unique().tolist()]
    with open("clientes_unicos.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(unique_clients))
    print("Clientes únicos guardados en clientes_unicos.txt")

    # Guardar descripciones únicas
    unique_descriptions = [d.replace(' ', ' ').strip() for d in df['Descripción'].dropna().unique().tolist()]
    with open("descripciones_unicas.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(unique_descriptions))
    print("Descripciones únicas guardadas en descripciones_unicas.txt")
    return df


def update_database(df):
    print("Actualizando base de datos...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS maximo (
                        OT TEXT PRIMARY KEY,
                        Descripción TEXT,
                        Nº_de_serie TEXT,
                        Fecha TEXT,
                        Cliente TEXT,
                        Tipo_de_trabajo TEXT,
                        Seguimiento TEXT,
                        Planta TEXT)''')
    for _, row in df.iterrows():
        cursor.execute('''INSERT OR IGNORE INTO maximo VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', tuple(row))
    conn.commit()
    conn.close()
    print("Base de datos actualizada.")


def save_credentials(username, password, filepath="credentials.json"):
    credentials = {"username": username, "password": password}
    with open(filepath, "w") as file:
        json.dump(credentials, file)


def load_credentials(filepath="credentials.json"):
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            return json.load(file)
    return None


if __name__ == "__main__":
    URL = "https://eam.indraweb.net/maximo/webclient/login/login.jsp"
    stored_credentials = load_credentials()
    if stored_credentials:
        print("Usando credenciales guardadas.")
        USERNAME = stored_credentials["username"]
        PASSWORD = stored_credentials.get("password")
    else:
        USERNAME = input("Usuario: ")
        PASSWORD = getpass.getpass("Contraseña: ")
        save_credentials(USERNAME, PASSWORD)

    DEST_FOLDER = os.path.expanduser("~/Documents/Maximo")
    os.makedirs(DEST_FOLDER, exist_ok=True)

    filters = {"mx38_tfrow_[C:26]_txt-tb": "=LAB-BAD"}  # Ajustar filtros según proyecto

    driver = setup_driver()
    try:
        login(driver, URL, USERNAME, PASSWORD)
        apply_filter(driver, filters)
        download_file(driver)
        file_path = move_latest_file(DEST_FOLDER)
        if file_path:
            df = process_html_table(file_path)
            update_database(df)
            print("Base de datos actualizada con éxito.")
    finally:
        driver.quit()
        print("Navegador cerrado.")
