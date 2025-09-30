from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import sqlite3
import os
try:
    import requests
except Exception:
    requests = None
try:
    from flask_session import Session
except Exception:
    Session = None
import markdown
import logging

# Limitar el historial de interacciones en sesión
MAX_HISTORY = 4

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
# Configurar sesiones en el servidor (filesystem) si flask_session está disponible
if Session:
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')
    app.config['SESSION_PERMANENT'] = False
    Session(app)

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
    # Página de chat (GET) y procesamiento de formulario (POST)
    error = None
    prompt = None
    response_html = None

    if request.method == 'POST':
        prompt = request.form.get('message')
        if not prompt:
            error = 'No hay mensaje para enviar.'
        else:
            reply, err = send_to_gemini(prompt)
            if err:
                error = err
            else:
                # convertir reply a HTML simple (escape/markdown)
                try:
                    response_html = markdown.markdown(reply)
                except Exception:
                    response_html = reply

                # guardar en historial de sesión
                hist = session.get('history', [])
                hist.insert(0, {'prompt': prompt, 'response_html': response_html})
                session['history'] = hist[:MAX_HISTORY]

    history = session.get('history', [])
    return render_template('chat.html', error=error, prompt=prompt, response_html=response_html, history=history)


@app.route('/api/chat', methods=['POST'])
def api_chat():
    # Endpoint que intenta usar Gemini si la variable de entorno GEMINI_API_KEY está configurada.
    data = request.get_json() or {}
    user_message = data.get('message') or ''

    # Delegate to helper that can be reused from the server-rendered chat
    reply, error = send_to_gemini(user_message)
    if error:
        return jsonify({'reply': f'Error al conectar con Gemini: {error}'}), 500
    return jsonify({'reply': reply})


def send_to_gemini(user_message: str):
    """Llamar al endpoint configurado (GEMINI_API_URL) usando GEMINI_API_KEY.
    Devuelve (reply_string, error_string_or_None).
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    api_url = os.environ.get('GEMINI_API_URL')
    if not api_key:
        logging.info('GEMINI_API_KEY not set; returning placeholder reply')
        return (f"(placeholder) recibí: {user_message}", None)

    url = api_url or 'https://generativelanguage.googleapis.com/v1beta/models/text-bison:generateContent'
    is_google_gen = 'generativelanguage.googleapis.com' in url or 'googleapis.com' in url

    try:
        if not requests:
            logging.error('requests library missing')
            return (None, 'La librería requests no está instalada. Ejecuta: pip install requests')

        # Prepare request
        if is_google_gen:
            headers = {'Content-Type': 'application/json', 'X-goog-api-key': api_key}
            payload = {'contents': [{'parts': [{'text': user_message}]}]}
            logging.debug('Prepared payload snippet: %s', str(payload)[:300])
            logging.info('Calling Google Generative endpoint %s', url)
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
        else:
            headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
            payload = {'input': user_message}
            logging.info('Calling generic endpoint %s', url)
            resp = requests.post(url, headers=headers, json=payload, timeout=20)

        # Log status and small snippet of body for debugging (without API key)
        status = resp.status_code
        logging.info('External API responded with status %s', status)
        try:
            body = resp.json()
            import json as _json
            body_snippet = _json.dumps(body)[:2000]
            logging.debug('Response body snippet: %s', body_snippet)
        except Exception:
            body = resp.text
            logging.debug('Response text (non-json) snippet: %s', str(body)[:2000])

        # Log headers (without exposing sensitive fields)
        try:
            headers_snippet = {k: v for k, v in resp.headers.items() if k.lower() not in ('set-cookie',)}
            logging.debug('Response headers: %s', headers_snippet)
        except Exception:
            logging.debug('Could not read response headers')

        resp.raise_for_status()

        # buscar texto en la respuesta
        def find_text(obj):
            if obj is None:
                return None
            if isinstance(obj, str):
                return obj
            if isinstance(obj, dict):
                # Common keys
                for k in ('text', 'content', 'output', 'message', 'reply'):
                    if k in obj:
                        v = obj[k]
                        if isinstance(v, str):
                            return v
                        res = find_text(v)
                        if res:
                            return res
                # Bison/candidates style
                if 'candidates' in obj and isinstance(obj['candidates'], list):
                    for cand in obj['candidates']:
                        r = find_text(cand)
                        if r:
                            return r
                # GenerateContent response shapes
                if 'output' in obj and isinstance(obj['output'], dict):
                    r = find_text(obj['output'])
                    if r:
                        return r
                if 'results' in obj and isinstance(obj['results'], list):
                    for res_item in obj['results']:
                        r = find_text(res_item)
                        if r:
                            return r
                for v in obj.values():
                    r = find_text(v)
                    if r:
                        return r
                return None
            if isinstance(obj, list):
                for item in obj:
                    r = find_text(item)
                    if r:
                        return r
                return None
            return None

        reply = find_text(body)
        if not reply:
            import json as _json
            reply = _json.dumps(body)
        return (reply, None)
    except Exception as e:
        logging.exception('Error calling external generative API')
        return (None, str(e))


if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=81, debug=True)