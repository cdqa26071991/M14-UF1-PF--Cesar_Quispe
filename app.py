from flask import Flask,render_template,request; 
import mysql.connector
import pandas as pd
from werkzeug.utils import secure_filename
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import base64


app = Flask(__name__)



# connectBD: conectamos a la base de datos users en MySQL
def connectBD():
    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        passwd = "cdqa26071991",
        database = "users"
    )
    return db


# inicioBD: crea una tabla en la BD users, con un registro, si está vacía
def inicioBD():
    bd=connectBD()
    cursor=bd.cursor()
    
    # cursor.execute("DROP TABLE IF EXISTS contacts;")
    # Operación de creación de la tabla contacts (si no existe en BD)
    query="CREATE TABLE IF NOT EXISTS contacts(\
            id INTEGER PRIMARY KEY AUTO_INCREMENT,\
            fullname VARCHAR (255),\
            phone VARCHAR(255), \
            email VARCHAR(255)); "
    cursor.execute(query)
    
        
    # Operación de inicialización de la tabla contacts (si está vacía)
    query="SELECT count(*) FROM contacts;"
    cursor.execute(query)
    count = cursor.fetchall()[0][0]
    if(count == 0):
        query = "INSERT INTO contacts \
            VALUES('1','Cesar Quispe Arenas','698745210','cesar10@gmail.com');"
        cursor.execute(query)

    bd.commit()
    bd.close()

# createUser: creamos un nuevo usuario en la BD
def createUser2(id,fullname,phone,email):
    bd = connectBD()
    cursor = bd.cursor()

    query = f"INSERT INTO contacts (id,fullname,phone,email) \
             VALUES (%s, %s, %s, %s)"
    values = (id,fullname,phone,email)

    cursor.execute(query, values)
    bd.commit()
    bd.close()
    return
   



    

# Declaración de rutas de la aplicación web
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login" , methods=["GET","POST"])
def login():
    inicioBD()
    return render_template("login.html")
  


# Declaración de ruta para procesar el formulario de registro
@app.route("/createUser", methods=['POST'])
def createUser():
    # Obtener los datos enviados desde el formulario
    id = request.form['id']
    fullname = request.form['fullname']
    phone = request.form['phone']
    gmail = request.form['gmail']

    # Llamar a la función `createUser` para insertar los datos en la base de datos
    createUser2(id, fullname, phone, gmail)

    # Redirigir a una página de éxito o mostrar un mensaje de confirmación
    return "registro exitoso"


@app.route("/plot")
def plot():
     # Link de descarga de datos:
     # https://datos.gob.ar/dataset/produccion-precios-internacionales-minerales-siacam/archivo/produccion_e16a98b6-0043-47ab-a35e-44a0d2d917c5
    
    # Extracción de datos
    metal = pd.read_csv("info/precios-siacam.csv", delimiter=";")
    
    # Dividir los valores de la columna en columnas separadas
    metal[['Año', 'Mes', 'Fecha', 'Precio', 'Mineral', 'Unidad de medida', 'Numero Índice']] = metal['Año;Mes;Fecha;Precio;Mineral;Unidad de medida;Numero Índice'].str.split(';', expand=True)
    
    # Eliminar la columna original
    metal.drop(columns=['Año;Mes;Fecha;Precio;Mineral;Unidad de medida;Numero Índice'], inplace=True)
    
    # Manipulación del dataset
    # Cambiar el formato de la columna "Fecha" a datetime
    metal["Fecha"] = pd.to_datetime(metal["Fecha"], format="%YM%m")
    # Convertir la columna "Precio" de tipo string a float
    metal["Precio"] = metal["Precio"].str.replace(',', '.').astype(float)
    
    # Obtener la lista de minerales disponibles en el dataset
    minerales = metal["Mineral"].unique()
    
    # Configurar el tamaño del gráfico
    plt.figure(figsize=(10, 6))
    
    # Visualización de datos
    for mineral in minerales:
        # Filtrar el DataFrame para el mineral actual
        df_mineral = metal[metal["Mineral"] == mineral]
        
        # Graficar la serie de tiempo del precio para el mineral actual
        plt.plot(df_mineral["Fecha"], df_mineral["Precio"], label=mineral)
    
    # Configurar la leyenda y los ejes
    plt.title("Serie de tiempo del precio por mineral")
    plt.xlabel("Fecha")
    plt.ylabel("Precio")
    plt.legend(loc="upper left")
    
    # Guardar el gráfico en un objeto BytesIO
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    
    # Codificar la imagen en base64
    plot_url = base64.b64encode(img.getvalue()).decode()
    return render_template("plot.html", plot_url=plot_url)



app.config['TEMPLATES_AUTO_RELOAD'] = True
app.run(host='localhost', port=5000, debug=True)
