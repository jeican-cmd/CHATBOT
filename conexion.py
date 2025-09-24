import sqlite3
from contextlib import contextmanager

def get_db_connection():
    """
    Establece conexión con la base de datos SQLite
    Retorna el objeto de conexión configurado
    """
    conn = sqlite3.connect("basedatos.db")
    conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
    return conn

@contextmanager
def get_db_cursor():
    """
    Context manager para manejo automático de conexión y cursor
    Garantiza el cierre apropiado de recursos
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    """
    Inicializa todas las tablas necesarias para la aplicación
    """
    with get_db_cursor() as cursor:
        # Tabla de materias
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS materias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            semestre TEXT NOT NULL,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Tabla de usuarios (para futuras funcionalidades)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            mensaje TEXT,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

def insertar_materia(nombre, semestre):
    """
    Inserta una nueva materia en la base de datos
    """
    with get_db_cursor() as cursor:
        cursor.execute(
            "INSERT INTO materias (nombre, semestre) VALUES (?, ?)", 
            (nombre, semestre)
        )
        return cursor.lastrowid

def obtener_materias():
    """
    Obtiene todas las materias registradas
    """
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM materias ORDER BY semestre, nombre")
        return cursor.fetchall()

def obtener_materias_por_semestre(semestre):
    """
    Obtiene materias filtradas por semestre
    """
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM materias WHERE semestre = ? ORDER BY nombre", (semestre,))
        return cursor.fetchall()