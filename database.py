import sqlite3

def inicializar_db():
    conn = sqlite3.connect('competencia.db')
    cursor = conn.cursor()
    
    # Tabla para los equipos y su puntaje total
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            puntos_totales INTEGER DEFAULT 0
        )
    ''')
    
    # Tabla para el registro detallado (logs)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipo_id INTEGER,
            descripcion TEXT NOT NULL,
            puntos_cambio INTEGER NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (equipo_id) REFERENCES equipos (id)
        )
    ''')
    
    # Insertar los 5 equipos iniciales si no existen
    equipos = ['Escuderos', 'Templarios', 'Capes', 'Herederas', 'Adalies']
    for equipo in equipos:
        cursor.execute('INSERT OR IGNORE INTO equipos (nombre) VALUES (?)', (equipo,))
    
    conn.commit()
    conn.close()

def registrar_puntos(nombre_equipo, descripcion, puntos):
    conn = sqlite3.connect('competencia.db')
    cursor = conn.cursor()
    
    try:
        # 1. Registrar en el historial
        cursor.execute('''
            INSERT INTO historial (equipo_id, descripcion, puntos_cambio)
            SELECT id, ?, ? FROM equipos WHERE nombre = ?
        ''', (descripcion, puntos, nombre_equipo))
        
        # 2. Actualizar el total del equipo
        cursor.execute('''
            UPDATE equipos 
            SET puntos_totales = puntos_totales + ? 
            WHERE nombre = ?
        ''', (puntos, nombre_equipo))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.close()


def obtener_totales():
    """Función extra para facilitar la lectura en Streamlit"""
    conn = sqlite3.connect('competencia.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, puntos_totales FROM equipos")
    datos = cursor.fetchall()
    conn.close()
    return datos
