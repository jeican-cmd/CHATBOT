from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Inicializar Base de Datos
def init_db():
    conn = sqlite3.connect("basedatos.db")
    cursor = conn.cursor()
    
    # Tabla de materias
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS materias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        semestre TEXT NOT NULL
    )
    """)
    
    # Tabla de carreras
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS carreras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL UNIQUE,
        nombre TEXT NOT NULL
    )
    """)
    
    # Insertar datos de ejemplo si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM carreras")
    if cursor.fetchone()[0] == 0:
        carreras_ejemplo = [
            ('ING001', 'Ingeniería de Sistemas'),
            ('ADM002', 'Administración de Empresas'),
            ('DER003', 'Derecho'),
            ('PSI004', 'Psicología'),
            ('CON005', 'Contaduría Pública'),
            ('MED006', 'Medicina'),
            ('ARQ007', 'Arquitectura'),
            ('COM008', 'Comunicación Social'),
            ('ING009', 'Ingeniería Civil'),
            ('ECO010', 'Economía')
        ]
        cursor.executemany("INSERT INTO carreras (codigo, nombre) VALUES (?, ?)", carreras_ejemplo)
    
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/vision")
def vision():
    return render_template("vision.html")

@app.route("/programas", methods=["GET"])
def programas():
    return render_template("programas.html")

@app.route("/mision", methods=["GET", "POST"])
def mision():
    if request.method == "POST":
        # Recibir datos del formulario
        materia = request.form.get("materia")
        semestre = request.form.get("semestre")
        
        # Validar que los campos no estén vacíos
        if materia and semestre:
            # Guardar en la base de datos
            conn = sqlite3.connect("basedatos.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO materias (nombre, semestre) VALUES (?, ?)", (materia, semestre))
            conn.commit()
            conn.close()
            
            return render_template("respuesta.html", mensaje="Registro exitoso")
        else:
            return render_template("respuesta.html", mensaje="Error: Todos los campos son obligatorios")
    
    # Si es GET, mostrar la misión de la universidad
    return render_template("mision.html")

@app.route("/listacarreras")
def listacarreras():
    print("Ejecutando listacarreras()")  # Debug
    conn = sqlite3.connect("basedatos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT codigo, nombre FROM carreras ORDER BY codigo")
    carreras_data = cursor.fetchall()
    print(f"Carreras encontradas: {len(carreras_data)}")  # Debug
    print(f"Datos: {carreras_data}")  # Debug
    conn.close()
    return render_template("listacarreras.html", Carreras=carreras_data)


@app.route("/eliminar/<codigo>")
def eliminar(codigo):
    # Conectar a la base de datos
    conn = sqlite3.connect("basedatos.db")
    cursor = conn.cursor()
    
    # Eliminar la carrera por código
    cursor.execute("DELETE FROM carreras WHERE codigo = ?", (codigo,))
    conn.commit()
    conn.close()
    
    # Redirigir a la lista de carreras
    return redirect(url_for('listacarreras'))

@app.route("/actualizar/<codigo>",methods=["GET", "POST"])
def actualizar(codigo):
    # Conectar a la base de datos para obtener los datos de la carrera
    conn = sqlite3.connect("basedatos.db")
    cursor = conn.cursor()
    
    # Obtener la carrera específica
    cursor.execute("SELECT codigo, nombre FROM carreras WHERE codigo = ?", (codigo,))
    carrera = cursor.fetchone()
    conn.close()
    
    if carrera == "POST":
        # Renderizar un template para actualizar (necesitarás crear este template)
        return render_template("actualizar.html", carrera=carrera)
    else:
        # Si no existe la carrera, redirigir a la lista
        return redirect(url_for('listacarreras'))

if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0',port = 81, debug=True)