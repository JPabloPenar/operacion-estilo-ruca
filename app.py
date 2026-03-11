import streamlit as st
import sqlite3
import pandas as pd

# --- Configuración de Base de Datos ---
def ejecutar_query(query, params=(), commit=False):
    with sqlite3.connect('competencia.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if commit:
            conn.commit()
        return cursor.fetchall()

def inicializar_db():
    ejecutar_query('''CREATE TABLE IF NOT EXISTS equipos 
                     (id INTEGER PRIMARY KEY, nombre TEXT UNIQUE, puntos_totales INTEGER DEFAULT 0)''', commit=True)
    ejecutar_query('''CREATE TABLE IF NOT EXISTS historial 
                     (id INTEGER PRIMARY KEY, equipo_nombre TEXT, descripcion TEXT, puntos_cambio INTEGER)''', commit=True)
    
    equipos = ['Escuderos', 'Templarios', 'Vikingos', 'Espartanos', 'Samuráis']
    for e in equipos:
        ejecutar_query('INSERT OR IGNORE INTO equipos (nombre, puntos_totales) VALUES (?, 0)', (e,), commit=True)

# --- Interfaz de Streamlit ---
st.set_page_config(page_title="Tablero de Competencia", layout="wide")
inicializar_db()

st.title("🏆 Sistema de Puntos de Competencia")

# Sidebar para entradas
st.sidebar.header("Registrar Nuevo Evento")
equipo_sel = st.sidebar.selectbox("Selecciona Equipo", ['Escuderos', 'Templarios', 'Vikingos', 'Espartanos', 'Samuráis'])
desc = st.sidebar.text_input("Descripción del logro/falta")
puntos = st.sidebar.number_input("Puntos", step=1, value=0)

if st.sidebar.button("Registrar"):
    if desc:
        # 1. Insertar en historial
        ejecutar_query("INSERT INTO historial (equipo_nombre, descripcion, puntos_cambio) VALUES (?, ?, ?)", 
                       (equipo_sel, desc, puntos), commit=True)
        # 2. Actualizar total
        ejecutar_query("UPDATE equipos SET puntos_totales = puntos_totales + ? WHERE nombre = ?", 
                       (puntos, equipo_sel), commit=True)
        st.sidebar.success("¡Puntos registrados!")
    else:
        st.sidebar.error("Por favor agrega una descripción")

# --- Visualización de Datos ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Puntos Totales")
    df_equipos = pd.DataFrame(ejecutar_query("SELECT nombre, puntos_totales FROM equipos"), 
                              columns=["Equipo", "Puntos"])
    st.bar_chart(df_equipos.set_index("Equipo"))

with col2:
    st.subheader("📜 Historial Reciente")
    hist_data = ejecutar_query("SELECT equipo_nombre, descripcion, puntos_cambio FROM historial ORDER BY id DESC LIMIT 10")
    df_hist = pd.DataFrame(hist_data, columns=["Equipo", "Motivo", "Puntos"])
    st.table(df_hist)

# Botón para reiniciar (opcional)
if st.button("Limpiar todo el historial"):
    ejecutar_query("DELETE FROM historial", commit=True)
    ejecutar_query("UPDATE equipos SET puntos_totales = 0", commit=True)
    st.rerun()