import streamlit as st
import pandas as pd
# Importamos la nueva función 'obtener_historial_completo'
from database import inicializar_db, registrar_puntos, obtener_totales, obtener_historial_completo

# Configuración inicial
st.set_page_config(page_title="Operación Estilo Ruca", layout="wide")
inicializar_db()

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
        st.bar_chart(df_totales.set_index("Equipo"))
        st.table(df_totales)

with tab2:
    st.subheader("Historial de movimientos")
    st.write("Aquí puedes verificar cómo se obtuvo cada punto:")
    
    # IMPORTANTE: Ahora usamos la función de database.py en lugar de la local de sqlite
    df_hist = obtener_historial_completo()
    
    if not df_hist.empty:
        # Reordenamos columnas para que se vea como antes si es necesario
        columnas = ["fecha", "equipo_nombre", "descripcion", "puntos_cambio"]
        st.dataframe(df_hist[columnas], use_container_width=True)
    else:
        st.info("Aún no se han registrado movimientos.")

# El botón de pánico requeriría una función nueva en database.py para limpiar el Sheet
# Por seguridad, es mejor manejar el borrado directamente desde el Excel de Google.