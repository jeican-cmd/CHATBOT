from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
try:
    import requests
except Exception:
    requests = None

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
    # Endpoint que intenta usar Gemini si la variable de entorno GEMINI_API_KEY está configurada.
    data = request.get_json() or {}
    user_message = data.get('message') or ''

    api_key = os.environ.get('GEMINI_API_KEY')
    api_url = os.environ.get('GEMINI_API_URL')  # opcional, por si se quiere apuntar a otro host

    if api_key:
        # Use the configured API URL or fall back to a safe default
        url = api_url or 'https://generativelanguage.googleapis.com/v1beta/models/text-bison:generateContent'

        # Detect Google Generative Language endpoint and adapt headers/payload
        is_google_gen = 'generativelanguage.googleapis.com' in url or 'googleapis.com' in url

        try:
            if not requests:
                raise RuntimeError('La librería requests no está instalada en el entorno. Instálala con: pip install requests')

            if is_google_gen:
                # Google example: use X-goog-api-key header and the generateContent payload
                headers = {
                    'Content-Type': 'application/json',
                    'X-goog-api-key': api_key
                }
                payload = {
                    'contents': [
                        {
                            'parts': [
                                { 'text': user_message }
                            ]
                        }
                    ]
                }
                resp = requests.post(url, headers=headers, json=payload, timeout=20)
            else:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                payload = { 'input': user_message }
                resp = requests.post(url, headers=headers, json=payload, timeout=20)

            resp.raise_for_status()
            body = resp.json()

            # Heuristic: buscar recursivamente el texto más probable en la respuesta
            def find_text(obj):
                if obj is None:
                    return None
                if isinstance(obj, str):
                    return obj
                if isinstance(obj, dict):
                    # keys that often contain text
                    for k in ('text', 'content', 'output', 'message', 'reply'):
                        if k in obj and isinstance(obj[k], (str, dict)):
                            v = obj[k]
                            if isinstance(v, str):
                                return v
                            # if dict, try deeper
                            deeper = find_text(v)
                            if deeper:
                                return deeper

                    # candidates array
                    if 'candidates' in obj and isinstance(obj['candidates'], list) and len(obj['candidates'])>0:
                        for cand in obj['candidates']:
                            res = find_text(cand)
                            if res:
                                return res

                    # items / outputs
                    for k in ('items', 'outputs', 'result'):
                        if k in obj:
                            res = find_text(obj[k])
                            if res:
                                return res

                    # otherwise search all values
                    for v in obj.values():
                        res = find_text(v)
                        if res:
                            return res
                    return None

                if isinstance(obj, list):
                    for item in obj:
                        res = find_text(item)
                        if res:
                            return res
                    return None

                return None

            reply = find_text(body)
            if not reply:
                try:
                    import json as _json
                    reply = _json.dumps(body)
                except Exception:
                    reply = str(body)

            return jsonify({'reply': reply})
        except Exception as e:
            return jsonify({'reply': f'Error al conectar con Gemini: {e}'}), 500

    # Fallback: comportamiento placeholder local
    response_text = f"(placeholder) recibí: {user_message}"
    return jsonify({'reply': response_text})


if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=81, debug=True)