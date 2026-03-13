import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

# La URL la pondrás en los Secrets de Streamlit
# Formato: postgresql://usuario:password@host/dbname
DB_URL = st.secrets["connections"]["postgresql"]["url"]
engine = create_engine(DB_URL)

def inicializar_db():
    with engine.connect() as conn:
        # Crear tabla equipos
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS equipos (
                nombre TEXT PRIMARY KEY,
                puntos_totales INTEGER DEFAULT 0
            )
        """))
        # Crear tabla historial
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS historial (
                id SERIAL PRIMARY KEY,
                equipo_nombre TEXT,
                descripcion TEXT,
                puntos_cambio INTEGER,
                fecha TIMESTAMP
            )
        """))
        
        # Insertar equipos iniciales si la tabla está vacía
        res = conn.execute(text("SELECT COUNT(*) FROM equipos")).fetchone()
        if res[0] == 0:
            nombres = ['Escuderos', 'Templarios', 'Capes', 'Herederas', 'Adalies']
            for n in nombres:
                conn.execute(text("INSERT INTO equipos (nombre, puntos_totales) VALUES (:n, 0)"), {"n": n})
        conn.commit()

def registrar_puntos(nombre_equipo, descripcion, puntos):
    with engine.begin() as conn:
        # Actualizar total
        conn.execute(text("""
            UPDATE equipos SET puntos_totales = puntos_totales + :p 
            WHERE nombre = :n
        """), {"p": puntos, "n": nombre_equipo})
        
        # Insertar historial
        conn.execute(text("""
            INSERT INTO historial (equipo_nombre, descripcion, puntos_cambio, fecha)
            VALUES (:n, :d, :p, :f)
        """), {
            "n": nombre_equipo, 
            "d": descripcion, 
            "p": puntos, 
            "f": datetime.now()
        })

def obtener_totales():
    with engine.connect() as conn:
        df = pd.read_sql("SELECT nombre, puntos_totales FROM equipos", conn)
        return list(df.itertuples(index=False, name=None))

def obtener_historial_completo():
    with engine.connect() as conn:
        return pd.read_sql("SELECT * FROM historial ORDER BY fecha DESC", conn)

def reiniciar_datos():
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM historial"))
        conn.execute(text("UPDATE equipos SET puntos_totales = 0"))

reiniciar_datos()