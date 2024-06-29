from flask import Flask, request, jsonify

from flask_cors import CORS

import mysql.connector

import mysql.connector.errorcode
from werkzeug.utils import secure_filename

import os
import time

app= Flask(__name__)
CORS(app)# Esto habilita cors para todas las rutas

class Donantes:
    
        #CONSTRUCTOR DE LA CLASE
        def __init__(self,host,user,password,database):
        
             self.conn=mysql.connector.connect(
             host=host,
             user=user,
             password=password,
             )
    
             self.cursor=self.conn.cursor()
             #INTENTAMOS SELECCIONAR LA BASE DE DATOS
             try:
                 self.cursor.execute(f"USE {database}")
             except mysql.connector.Error as err:
                 #SI LA BASE DE DATOS NO EXISTE, LA CREAMOS
                 if err.errno==mysql.connector.errorcode.ER_BAD_DB_ERROR:
                     self.cursor.execute(f"CREATE DATABASE {database}")
                     self.conn.database=database
                 else:
                    raise err
                     
                     
             self.cursor.execute('''CREATE TABLE IF NOT EXISTS donantes (
                nombres VARCHAR(45) NOT NULL,
                apellido VARCHAR (45) NOT NULL,
                domicilio VARCHAR (45) NOT NULL,
                edad INT (2) NOT NULL,
                imagen_url VARCHAR(255),
                grupo_sanguineo VARCHAR(45) NOT NULL,
                telefono VARCHAR (15)  not null,
                mail VARCHAR (45) not null,
                dni INT PRIMARY KEY NOT NULL)''' )
             self.conn.commit()
             
             # Cerrar el cursor inicial y abrir uno nuevo con el parámetro dictionary=True
             self.cursor.close()
             self.cursor = self.conn.cursor(dictionary=True)
             
        def agregar_donante(self,nombres,apellido,domicilio,edad,grupo_sanguineo,imagen_url,telefono,mail,dni):
      
          sql= "INSERT INTO donantes (nombres,apellido,domicilio,edad,grupo_sanguineo,imagen_url,telefono,mail,dni)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
          valores=(nombres,apellido,domicilio,edad,grupo_sanguineo,imagen_url,telefono,mail,dni)
          
          self.cursor.execute(sql,valores)
          self.conn.commit()
          return self.cursor.lastrowid  
      
        def consultar_donante(self,dni):
        #consutamos un donante a partir de su dni
          self.cursor.execute(f"SELECT * FROM donantes WHERE dni=   {dni}")
          return self.cursor.fetchone() #metodo del cursor que trae una sola fila
         
        def modificar_datos_donante(self,nuevo_domicilio,nuevo_edad,nuevo_telefono,nueva_imagen,nuevo_mail,dni):
            sql="UPDATE donantes SET domicilio=%s, edad=%s, telefono=%s,imagen_url=%s, mail=%s WHERE dni= %s"
            valores=(nuevo_domicilio,nuevo_edad,nuevo_telefono,nueva_imagen,nuevo_mail,dni)
      
            self.cursor.execute(sql,valores)
            self.conn.commit()
            return self.cursor.rowcount > 0  
        
        
        def listar_donantes(self):
            self.cursor.execute("SELECT * FROM donantes")
            donantes=self.cursor.fetchall()
            return donantes
             
        def eliminarDonante(self,dni):
            self.cursor.execute(f"DELETE FROM donantes WHERE dni= {dni}")
            self.conn.commit()
            return self.cursor.rowcount >0
            return False       
         
        def mostrar_donante(self,dni):
           donante=self.consultar_donante(dni)
           if donante:
            print("*"*50)
            print(f"Id......:{donante ['id']}")
            print(f"Nombres..........:{donante['nombres']}")
            print(f"Apellido......:{donante['apellido']}")
            print(f"Grupo Sanguineo......:{donante['grupo_sanguineo']}")
            print(f"Telefono......:{donante['telefono']}")
            print(f"Imagen.........:{donante['imagen_url']}")
            print(f"Localidad......:{donante['domicilio']}")
            print(f"E-mail......:{donante['mail']}")
            print("*"*50)
           else:
            print("Donante no encontrado")
             
        
      
        
        
        
            
             
#--------------------------------------------------------------------
# Cuerpo del programa
#--------------------------------------------------------------------
# Crear una instancia de la clase Catalogo
datos_donante = Donantes(host='almona25.mysql.pythonanywhere-services.com', user='almona25', password='', database='almona25$miapp')
# Carpeta para guardar las imagenes
ruta_destino = '/home/almona25/mysite/static/img/'


@app.route("/donantes", methods=["GET"])
def listar_donantes():
    donantes = datos_donante.listar_donantes()
    return jsonify(donantes)


@app.route("/donantes/<int:dni>", methods=["GET"])
def mostrar_donante(dni):
   donador = datos_donante.consultar_donante(dni)
   if donador:
     return jsonify(donador), 201
   else:
     return "Dni no encontrado", 404

@app.route("/donantes", methods=["POST"])
def agregar_donante():
#Recojo los datos del form
    nombres = request.form['nombres_donante']
    apellido = request.form['apellido_donante']
    domicilio = request.form['domicilio_donante']
    edad = request.form['edad_donante']
    imagen = request.files['imagen_donante']
    grupo_sanguineo = request.form['grupo_sanguineo']
    telefono=request.form['telefono_donante']
    mail=request.form['mail_donante']
    dni=request.form['dni_donante']
    nombre_imagen = ""
 
# Genero el nombre de la imagen
    nombre_imagen = secure_filename(imagen.filename)
    nombre_base, extension = os.path.splitext(nombre_imagen)
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"
 
    nuevo_dni = datos_donante.agregar_donante(nombres,apellido,domicilio,edad,grupo_sanguineo,nombre_imagen,telefono,mail,dni)
    if nuevo_dni:
        imagen.save(os.path.join(ruta_destino, nombre_imagen))
        return jsonify({"mensaje": "Datos agregado correctamente.",
        "DNI": nuevo_dni, "imagen": nombre_imagen}), 201
    else:
        return jsonify({"mensaje": "Error al agregar al donante."}), 500


@app.route("/donantes/<int:dni>", methods=["PUT"])
def modificar_datos_donante(dni):
#Se recuperan los nuevos datos del formulario
   nuevo_domicilio= request.form.get("domicilio")
   nuevo_edad = request.form.get("edad")
   nuevo_telefono=request.form.get("telefono")
   nuevo_mail=request.form.get("mail")
   

# Verifica si se proporcionó una nueva imagen
   if 'imagen' in request.files:
    imagen = request.files['imagen']
# Procesamiento de la imagen
    nombre_imagen = secure_filename(imagen.filename)
    nombre_base, extension = os.path.splitext(nombre_imagen)
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"
# Guardar la imagen en el servidor
    imagen.save(os.path.join(ruta_destino, nombre_imagen))
# Busco el producto guardado

   donante = datos_donante.consultar_donante(dni)
   if donante: # Si existe el producto...
    imagen_vieja = donante["imagen_url"]
# Armo la ruta a la imagen
    ruta_imagen = os.path.join(ruta_destino, imagen_vieja)
# Y si existe la borro.
   if os.path.exists(ruta_imagen):
    os.remove(ruta_imagen)

   else:
    donante = datos_donante.consultar_donante(dni)
   if donante:
    nombre_imagen = donante["imagen_url"]

# Se llama al método modificar_producto pasando el codigo del producto y los nuevos datos.
   if datos_donante.modificar_datos_donante(nuevo_domicilio,nuevo_edad,nuevo_telefono,nombre_imagen,nuevo_mail,dni):
    return jsonify({"mensaje": "Datos modificado"}), 200
   else:
    return jsonify({"mensaje": "Donante no encontrado"}), 403


@app.route("/donantes/<int:dni>",methods=["DELETE"])

#La ruta Flask /productos/<int:codigo> con el método HTTP DELETE está diseñada para eliminar un producto específico de la base de datos, utilizando su código como identificador.
#La función eliminar_producto se asocia con esta URL y es llamada cuando se realiza una solicitud DELETE a /productos/ seguido de un número (el código del producto).
def eliminarDonante(dni):
# Busco el producto en la base de datos
 donante = datos_donante.consultar_donante(dni)
 if donante: # Si el producto existe, verifica si hay una imagen asociada en el servidor.
# Armo la ruta a la imagen
   ruta_imagen = os.path.join(ruta_destino, donante["imagen_url"])
# Y si existe, la elimina del sistema de archivos.
   if os.path.exists(ruta_imagen):
      os.remove(ruta_imagen)
# Luego, elimina el producto del catálogo
   if datos_donante.eliminarDonante(dni):
#Si el donante se elimina correctamente, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
       return jsonify({"mensaje": "Donante eliminado"}), 200
   else:
#Si ocurre un error durante la eliminación (por ejemplo, si el donante no se puede eliminar de la base de datos por alguna razón), se devuelve un mensaje de error con un código de estado HTTP 500 (Error Interno del Servidor).
    return jsonify({"mensaje": "Error al eliminar el donante"}), 500
 else:
#Si el producto no se encuentra (por ejemplo, si no existe un producto con el codigo proporcionado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado).
  return jsonify({"mensaje": "Donante no encontrado"}), 404
#--------------------------------------------------------------------
if __name__ == "__main__":
   app.run(debug=True)