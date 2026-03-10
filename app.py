import streamlit as st
import pandas as pd
from database import inicializar_db, registrar_puntos, obtener_totales
import sqlite3

# Configuración inicial
st.set_page_config(page_title="Operación Estilo Ruca", layout="wide")
inicializar_db()

def consultar_historial_completo():
    """Función auxiliar para leer todos los movimientos"""
    conn = sqlite3.connect('competencia.db')
    cursor = conn.cursor()
    # Traemos los datos uniendo con el nombre del equipo para que sea claro
    cursor.execute('''
        SELECT h.fecha, e.nombre, h.descripcion, h.puntos_cambio 
        FROM historial h
        JOIN equipos e ON h.equipo_id = e.id
        ORDER BY h.id DESC
    ''')
    datos = cursor.fetchall()
    conn.close()
    return datos

st.title("🏆 Competencia: Operación Estilo Ruca")

# --- SIDEBAR: REGISTRO ---
with st.sidebar:
    st.header("Registrar Puntos")
    equipo = st.selectbox("Equipo", ['Escuderos', 'Templarios', 'Capes', 'Herederas', 'Adalies'])
    desc = st.text_input("Descripción del logro o falta")
    pts = st.number_input("Puntos a asignar", step=1, value=0)
    
    if st.button("Guardar Registro"):
        if desc:
            registrar_puntos(equipo, desc, pts)
            st.success(f"¡Puntos para {equipo} registrados!")
            st.rerun()
        else:
            st.error("Por favor, escribe una descripción.")

# --- CUERPO PRINCIPAL: PESTAÑAS ---
tab1, tab2 = st.tabs(["📊 Tablero de Puntos", "📋 Auditoría de Registros"])

with tab1:
    st.subheader("Puntaje Actual")
    datos_totales = obtener_totales()
    if datos_totales:
        df_totales = pd.DataFrame(datos_totales, columns=["Equipo", "Puntos"])
        # Mostramos el gráfico de barras
        st.bar_chart(df_totales.set_index("Equipo"))
        
        # También mostramos una tabla simple con los totales
        st.table(df_totales)

with tab2:
    st.subheader("Historial de movimientos")
    st.write("Aquí puedes verificar cómo se obtuvo cada punto:")
    
    historial = consultar_historial_completo()
    if historial:
        df_hist = pd.DataFrame(historial, columns=["Fecha", "Equipo", "Descripción", "Puntos"])
        # Mostramos el historial completo
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("Aún no se han registrado movimientos.")

# Botón de pánico (opcional, solo para el administrador)
if st.expander("Configuración Avanzada"):
    if st.button("Reiniciar Competencia (BORRAR TODO)"):
        conn = sqlite3.connect('competencia.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM historial")
        cursor.execute("UPDATE equipos SET puntos_totales = 0")
        conn.commit()
        conn.close()
        st.warning("Datos borrados correctamente.")
        st.rerun()