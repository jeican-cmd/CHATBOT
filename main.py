from flask import Flask, render_template, request
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
    # Conectar a la base de datos y obtener las carreras
    conn = sqlite3.connect("basedatos.db")
    cursor = conn.cursor()
    
    # Ejecutar consulta para obtener todas las carreras
    cursor.execute("SELECT codigo, nombre FROM carreras ORDER BY codigo")
    carreras_data = cursor.fetchall()
    
    # Cerrar conexión
    conn.close()
    
    # Renderizar template pasando los datos
    return render_template("listacarreras.html", Carreras=carreras_data)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)