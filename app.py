import streamlit as st
import pandas as pd
from database import inicializar_db, registrar_puntos, obtener_totales, obtener_historial_completo

st.set_page_config(page_title="Operación Estilo Ruca", layout="wide")

# Iniciamos la base de datos de Neon
try:
    inicializar_db()
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

st.title("🏆 Operación Estilo Ruca")

# Sidebar
with st.sidebar:

    password = st.text_input("Contraseña", type="password")

    st.header("Registrar Puntos")
    equipo = st.selectbox("Equipo", ['Escuderos', 'Templarios', 'Capes', 'Herederas', 'Adalies'])
    desc = st.text_input("Descripción")
    pts = st.number_input("Puntos", step=1, value=0)
    
    if st.button("Guardar"):
        if password != "SoyDeFORDOC":
            st.error("Contraseña incorrecta")
        elif not desc:
            st.warning("Debes escribir una descripción")
        else:
            registrar_puntos(equipo, desc, pts)
            st.success("¡Registrado!")
            st.rerun()

# Pestañas
t1, t2 = st.tabs(["📊 Gráfico", "📋 Historial"])

with t1:
    res = obtener_totales()
    if res:
        df = pd.DataFrame(res, columns=["Equipo", "Puntos"])
        st.bar_chart(df.set_index("Equipo"))

with t2:
    df_h = obtener_historial_completo()
    if not df_h.empty:
        df_h['fecha'] = pd.to_datetime(df_h['fecha']).dt.strftime('%d/%m/%Y %H:%M')
        st.dataframe(df_h, use_container_width=True, hide_index=True)