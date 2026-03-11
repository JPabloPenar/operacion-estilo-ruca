import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

# --- Conexión Persistente (Neon/Postgres) ---
# Esto evita el error de la imagen al buscar en tus secrets
try:
    DB_URL = st.secrets["connections"]["postgresql"]["url"]
    engine = create_engine(DB_URL)
except Exception:
    st.error("❌ No se encontró la configuración en Secrets. Asegúrate de configurar 'connections.postgresql'.")
    st.stop()

def ejecutar_query(query, params=None, commit=False):
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        if commit:
            conn.commit()
        if not commit and result.returns_rows:
            return result.fetchall()
        return None

def inicializar_db():
    # Tablas en Postgres
    ejecutar_query('''CREATE TABLE IF NOT EXISTS equipos 
                     (id SERIAL PRIMARY KEY, nombre TEXT UNIQUE, puntos_totales INTEGER DEFAULT 0)''', commit=True)
    ejecutar_query('''CREATE TABLE IF NOT EXISTS historial 
                     (id SERIAL PRIMARY KEY, equipo_nombre TEXT, descripcion TEXT, 
                      puntos_cambio INTEGER, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''', commit=True)
    
    equipos = ['Escuderos', 'Templarios', 'Capes', 'Adalies', 'Herederas']
    for e in equipos:
        # ON CONFLICT es el 'INSERT OR IGNORE' de Postgres
        ejecutar_query('INSERT INTO equipos (nombre, puntos_totales) VALUES (:n, 0) ON CONFLICT (nombre) DO NOTHING', 
                       {"n": e}, commit=True)

# --- Interfaz ---
st.set_page_config(page_title="Tablero Realtime", layout="wide")
inicializar_db()

st.title("🏆 Operación Estilo Ruca")

# Sidebar
st.sidebar.header("Registrar Nuevo Evento")
equipo_sel = st.sidebar.selectbox("Selecciona Equipo", ['Escuderos', 'Templarios', 'Capes', 'Adalies', 'Herederas'])
desc = st.sidebar.text_input("Descripción")
puntos = st.sidebar.number_input("Puntos", step=1, value=0)

if st.sidebar.button("Registrar"):
    if desc:
        # Guardamos historial con fecha y actualizamos total
        ahora = datetime.now()
        ejecutar_query("INSERT INTO historial (equipo_nombre, descripcion, puntos_cambio, fecha) VALUES (:n, :d, :p, :f)", 
                       {"n": equipo_sel, "d": desc, "p": puntos, "f": ahora}, commit=True)
        ejecutar_query("UPDATE equipos SET puntos_totales = puntos_totales + :p WHERE nombre = :n", 
                       {"p": puntos, "n": equipo_sel}, commit=True)
        st.sidebar.success("¡Registrado!")
        st.rerun()

# --- Visualización ---
st.subheader("📊 Puntos Totales")
res_equipos = ejecutar_query("SELECT nombre, puntos_totales FROM equipos")
df_equipos = pd.DataFrame(res_equipos, columns=["Equipo", "Puntos"])
st.bar_chart(df_equipos.set_index("Equipo"))

st.divider()
st.subheader("📋 Historial con Fecha")
res_hist = ejecutar_query("SELECT fecha, equipo_nombre, descripcion, puntos_cambio FROM historial ORDER BY fecha DESC")

if res_hist:
    df_hist = pd.DataFrame(res_hist, columns=["Fecha", "Equipo", "Descripción", "Puntos"])
    # Formato de fecha legible
    df_hist['Fecha'] = pd.to_datetime(df_hist['Fecha']).dt.strftime('%d/%m/%Y %H:%M')
    st.dataframe(df_hist, use_container_width=True, hide_index=True)
else:
    st.info("No hay registros.")

if st.button("Limpiar todo"):
    ejecutar_query("DELETE FROM historial", commit=True)
    ejecutar_query("UPDATE equipos SET puntos_totales = 0", commit=True)
    st.rerun()