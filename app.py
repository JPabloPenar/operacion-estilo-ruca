import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

# --- Configuración de Base de Datos (PostgreSQL) ---
# Usamos el secreto que guardamos en el paso anterior
DB_URL = st.secrets["connections"]["postgresql"]["url"]
engine = create_engine(DB_URL)

def ejecutar_query(query, params=None, commit=False):
    with engine.connect() as conn:
        # Ejecutamos la query
        result = conn.execute(text(query), params or {})
        if commit:
            conn.commit()
        
        # Si es un SELECT, devolvemos los datos
        if not commit:
            return result.fetchall()
        return None

def inicializar_db():
    # Creamos las tablas si no existen (Sintaxis Postgres)
    ejecutar_query('''CREATE TABLE IF NOT EXISTS equipos 
                     (id SERIAL PRIMARY KEY, nombre TEXT UNIQUE, puntos_totales INTEGER DEFAULT 0)''', commit=True)
    
    ejecutar_query('''CREATE TABLE IF NOT EXISTS historial 
                     (id SERIAL PRIMARY KEY, equipo_nombre TEXT, descripcion TEXT, 
                      puntos_cambio INTEGER, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''', commit=True)
    
    equipos = ['Escuderos', 'Templarios', 'Capes', 'Adalies', 'Herederas']
    for e in equipos:
        # Usamos :nombre en vez de ? porque SQLAlchemy prefiere parámetros nombrados
        ejecutar_query('INSERT INTO equipos (nombre, puntos_totales) VALUES (:n, 0) ON CONFLICT (nombre) DO NOTHING', 
                       {"n": e}, commit=True)

# --- Interfaz ---
st.set_page_config(page_title="Tablero Realtime", layout="wide")
inicializar_db()

st.title("🏆 Sistema de Puntos (Persistente)")

# --- Sidebar ---
st.sidebar.header("Registrar Nuevo Evento")
equipo_sel = st.sidebar.selectbox("Selecciona Equipo", ['Escuderos', 'Templarios', 'Capes', 'Adalies', 'Herederas'])
desc = st.sidebar.text_input("Descripción")
puntos = st.sidebar.number_input("Puntos", step=1, value=0)

if st.sidebar.button("Registrar"):
    if desc:
        # Registro en historial y actualización
        ejecutar_query("""INSERT INTO historial (equipo_nombre, descripcion, puntos_cambio, fecha) 
                          VALUES (:n, :d, :p, :f)""", 
                       {"n": equipo_sel, "d": desc, "p": puntos, "f": datetime.now()}, commit=True)
        
        ejecutar_query("UPDATE equipos SET puntos_totales = puntos_totales + :p WHERE nombre = :n", 
                       {"p": puntos, "n": equipo_sel}, commit=True)
        
        st.sidebar.success("¡Datos guardados en la nube!")
        st.rerun()

# --- Visualización ---
st.subheader("📊 Puntos Totales")
# Usamos pandas para leer directamente de SQL
with engine.connect() as conn:
    df_equipos = pd.read_sql("SELECT nombre, puntos_totales FROM equipos", conn)
st.bar_chart(df_equipos.set_index("nombre"))

st.divider()
st.subheader("📋 Historial con Fecha")
with engine.connect() as conn:
    df_historial = pd.read_sql("SELECT fecha, equipo_nombre, descripcion, puntos_cambio FROM historial ORDER BY fecha DESC", conn)

if not df_historial.empty:
    df_historial['fecha'] = pd.to_datetime(df_historial['fecha']).dt.strftime('%d/%m/%Y %H:%M')
    st.dataframe(df_historial, use_container_width=True, hide_index=True)