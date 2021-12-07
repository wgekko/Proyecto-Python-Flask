from flask import Flask, render_template, request, redirect, url_for, abort
from flask_mysqldb import MySQL
from datetime import datetime
import os

app = Flask(__name__)
mysql = MySQL()
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_BD"] = "flask"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql.init_app(app)

@app.route("/")
@app.route("/<name>")
def index():
    sql = "SELECT * FROM flask.empleado"
    cursor = mysql.connection.cursor()
    cursor.execute(sql)
    empleados = cursor.fetchall()
    mysql.connection.commit()
    cursor.close()
    return render_template("empleados/index.html", empleados = empleados)


@app.route("/create", methods = ["GET", "POST"])   
def create():
    if request.method == "GET":
        return render_template("empleados/create.html")
    elif request.method == "POST":
        _nombre = request.form["nombre"]
         _direccion = request.form["direccion"]
        _correo = request.form["correo"]
        tiempo = datetime.now().strftime("%Y%H%M%S")
        archivo = tiempo + request.files["fotos"].filename
        file = request.files["fotos"]
        file.save("static/files/" + archivo)
        _fotos = archivo
        cursor = mysql.connection.cursor()
        sql = "INSERT INTO flask.empleado (nombre, direccion, correo, fotos) VALUES (%s, %s, %s, %s)"
        datos = (_nombre, _correo, _fotos)
        cursor.execute(sql, datos)
        mysql.connection.commit()
        cursor.close()
        return render_template("empleados/create.html", msg="Creado con exito...")


@app.route("/<id>/edit", methods=["GET", "POST"])
def edit(id):
    if request.method == "GET":
        sql = "SELECT * FROM flask.empleado WHERE id = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(sql, [id])
        empleado = cursor.fetchone()
        return render_template("empleados/edit.html", empleado=empleado)
    else:
        if id:
            CARPETA = os.path.join("static/files")
            app.config["CARPETA"] = CARPETA
            _nombre = request.form["nombre"]
            _nombre = request.form["direccion"]
            _correo = request.form["correo"]
            _fotos = request.files["fotos"]
            now = datetime.now()
            tiempo = now.strftime("%Y%H%M%S")
            nuevo_nombre = tiempo + _fotos.filename
            _fotos.save("static/files/" + nuevo_nombre)
            datos = (_nombre, _correo, nuevo_nombre, id)
            sql = "UPDATE flask.empleado SET nombre = %s, direccion = %s, correo = %s, fotos = %s WHERE id = %s"
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT fotos FROM flask.empleado WHERE id = %s", [id])
            foto = cursor.fetchone()
            os.remove(os.path.join(app.config["CARPETA"], foto["fotos"]))
            cursor.execute(sql, datos)
            mysql.connection.commit()
            return redirect("/")


@app.route("/<id>/delete", methods=["POST"])
def delete(id):
    if id:
        CARPETA = os.path.join("static/files")
        app.config["CARPETA"] = CARPETA
        sql = "DELETE FROM flask.empleado WHERE id = %s"
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT fotos FROM flask.empleado WHERE id = %s", [id])
        foto = cursor.fetchone()
        os.remove(os.path.join(app.config["CARPETA"], foto["fotos"]))
        cursor.execute(sql, [id])
        mysql.connection.commit()
        return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
