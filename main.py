from flask import Flask, render_template, request, redirect, url_for, jsonify
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
    # Mostrar el listado de materias registrado en la base de datos
    conn = sqlite3.connect("basedatos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, semestre FROM materias ORDER BY id DESC")
    materias = cursor.fetchall()
    conn.close()
    return render_template("programas.html", materias=materias)

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
    # Mostrar lista de carreras y formulario para agregar nuevas
    conn = sqlite3.connect("basedatos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT codigo, nombre FROM carreras ORDER BY codigo")
    carreras_data = cursor.fetchall()
    conn.close()
    return render_template("listacarreras.html", Carreras=carreras_data, mensaje=None)


@app.route('/listacarreras', methods=['POST'])
def agregar_carrera():
    codigo = request.form.get('codigo')
    nombre = request.form.get('nombre')
    if not codigo or not nombre:
        # Re-render con mensaje de error
        conn = sqlite3.connect("basedatos.db")
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, nombre FROM carreras ORDER BY codigo")
        carreras_data = cursor.fetchall()
        conn.close()
        return render_template('listacarreras.html', Carreras=carreras_data, mensaje='Error: todos los campos son obligatorios')

    try:
        conn = sqlite3.connect("basedatos.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO carreras (codigo, nombre) VALUES (?, ?)", (codigo.strip().upper(), nombre.strip()))
        conn.commit()
    except sqlite3.IntegrityError:
        # Código duplicado
        conn.rollback()
        cursor.execute("SELECT codigo, nombre FROM carreras ORDER BY codigo")
        carreras_data = cursor.fetchall()
        conn.close()
        return render_template('listacarreras.html', Carreras=carreras_data, mensaje='Error: el código ya existe')
    finally:
        try:
            conn.close()
        except:
            pass

    return redirect(url_for('listacarreras'))


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
    if request.method == 'POST':
        # Actualizar la carrera con los datos enviados
        nuevo_nombre = request.form.get('nombre')
        nuevo_codigo = request.form.get('codigo')
        if not nuevo_codigo or not nuevo_nombre:
            return render_template('actualizar.html', carrera=carrera, mensaje='Todos los campos son obligatorios')

        try:
            conn = sqlite3.connect("basedatos.db")
            cursor = conn.cursor()
            # Permitir cambiar el codigo (con cuidado con duplicados)
            cursor.execute("UPDATE carreras SET codigo = ?, nombre = ? WHERE codigo = ?", (nuevo_codigo.strip().upper(), nuevo_nombre.strip(), codigo))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            return render_template('actualizar.html', carrera=carrera, mensaje='Error: el nuevo código ya existe')
        finally:
            conn.close()

        return redirect(url_for('listacarreras'))
    else:
        if carrera:
            return render_template('actualizar.html', carrera=carrera)
        else:
            return redirect(url_for('listacarreras'))


@app.route('/chat')
def chat():
    # Página de chat (cliente). El usuario integrará la API de Gemini en el frontend o conectará el backend.
    return render_template('chat.html')


@app.route('/api/chat', methods=['POST'])
def api_chat():
    # Endpoint placeholder para que el usuario conecte su API de Gemini.
    data = request.get_json() or {}
    user_message = data.get('message') or ''

    # Simple echo/respuesta placeholder. El usuario reemplazará este bloque
    # para integrar con Gemini u otro LLM.
    response_text = f"(placeholder) recibí: {user_message}"
    return jsonify({'reply': response_text})

if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0',port = 81, debug=True)