import streamlit as st
import pandas as pd
from database import inicializar_db, registrar_puntos, obtener_totales

# Se ejecuta una sola vez al abrir la app
inicializar_db()

st.title("🏆 Tablero de Competencia")

# Formulario en el Sidebar
with st.sidebar:
    st.header("Nuevo Registro")
    equipo = st.selectbox("Equipo", ['Escuderos', 'Templarios', 'Capes', 'Herederas', 'Adalies'])
    desc = st.text_input("Descripción")
    pts = st.number_input("Puntos", step=1)
    
    if st.button("Guardar"):
        registrar_puntos(equipo, desc, pts)
        st.success("¡Registrado!")
        st.rerun() # Refresca la app para ver los cambios

# Mostrar Gráfico
datos = obtener_totales()
df = pd.DataFrame(datos, columns=["Equipo", "Puntos"])
st.bar_chart(df.set_index("Equipo"))