# 📌 MaximoOnLocal

**MaximoOnLocal** es una herramienta automatizada para interactuar con IBM Maximo, facilitando la extracción de datos y la actualización de la base de datos local. Incluye una interfaz gráfica en **Tkinter** para la consulta y gestión de registros de manera eficiente.

## 🚀 Características

✅ Automación con Selenium para interactuar con IBM Maximo.  
✅ Extracción y procesamiento de datos en tablas HTML con Pandas.  
✅ Base de datos local en SQLite para almacenamiento eficiente.  
✅ Interfaz gráfica con Tkinter para consulta y administración.  
✅ Gestión de credenciales segura con almacenamiento en JSON.

## 📂 Estructura del Proyecto


```
MaximoOnLocal/ 
│── cliente_GUI.py # Interfaz gráfica en Tkinter 
│── update_database.py # Automatización y gestión de la base de datos 
│── requirements.txt # Dependencias del proyecto 
│── README.md # Documentación del proyecto
```


## 🛠️ Instalación y Configuración

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/MrDerekib/MaximoOnLocal.git
cd MaximoOnLocal
```

### 2️⃣ Instalar dependencias

```
pip install -r requirements.txt
```
### 3️⃣ Configurar credenciales

El sistema guarda credenciales en credentials.json. La primera vez que ejecutes el programa, se te pedirá ingresar usuario y contraseña.

## 🖥️ Uso del Proyecto
### Ejecutar la Interfaz Gráfica

```
python cliente_GUI.py
```
### Ejecutar la Actualización de Base de Datos
```
python update_database.py

```

## 🤖 Tecnologías Usadas

🔹 Python – Lenguaje principal del proyecto.

🔹 Selenium – Automatización del navegador para IBM Maximo.

🔹 SQLite – Base de datos local para almacenamiento eficiente.

🔹 Tkinter – Interfaz gráfica para consulta y gestión.

🔹 Pandas – Procesamiento y limpieza de datos.

🔹 Webdriver-Manager – Gestión automática del driver de Firefox para Selenium.

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Puedes usarlo, modificarlo y distribuirlo libremente.


## 📌 Desarrollado por MrDerekib 🚀