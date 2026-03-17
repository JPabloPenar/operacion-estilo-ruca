import streamlit as st
import pandas as pd
import altair as alt
from database import inicializar_db, registrar_puntos, obtener_totales, obtener_historial_completo

st.set_page_config(
    page_title="Operación Estilo Ruca",
    page_icon="logo.png",
    layout="wide"
)

# Inicializar DB
try:
    inicializar_db()
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# Título
st.title("🏆 Operación Estilo Ruca")
st.markdown("---")

# Sidebar mejorado
with st.sidebar:
    st.title("⚙️ Panel de control")

    with st.expander("🔐 Acceso"):
        password = st.text_input("Contraseña", type="password")

    with st.expander("➕ Registrar puntos"):
        equipo = st.selectbox("Equipo", ['Escuderos', 'Templarios', 'Capes', 'Herederas', 'Adalies'])
        desc = st.text_input("Descripción")
        pts = st.number_input("Puntos", step=1, value=0)

        if st.button("Guardar"):
            if password != "SoyDeFORDOC":
                st.error("Contraseña incorrecta")
            elif not desc:
                st.warning("Debes escribir una descripción")
            elif pts == 0:
                st.warning("Los puntos no pueden ser 0")
            else:
                registrar_puntos(equipo, desc, pts)
                st.toast("Puntos registrados 🚀")
                st.rerun()

# Obtener datos
res = obtener_totales()

# Tabs
t1, t2 = st.tabs(["📊 Gráfico", "📋 Historial"])

with t1:
    if res:
        df = pd.DataFrame(res, columns=["Equipo", "Puntos"])

    # Layout en columnas
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📊 Puntajes por equipo")

        chart = alt.Chart(df).mark_bar().encode(
            x='Equipo',
            y='Puntos',
            color='Equipo'
        )

        st.altair_chart(chart, use_container_width=True)

    with col2:
        st.subheader("🏅 Equipo líder")
        top = df.sort_values("Puntos", ascending=False).iloc[0]
        st.metric(label=top["Equipo"], value=top["Puntos"])

    st.markdown("---")

    # Ranking
    st.subheader("👑 Ranking")
    df_sorted = df.sort_values("Puntos", ascending=False).reset_index(drop=True)

    medals = ["🥇", "🥈", "🥉"]

    for i, row in df_sorted.iterrows():
        icon = medals[i] if i < 3 else "🏅"
        st.write(f"{icon} {row['Equipo']} — {row['Puntos']} pts")
with t2:
    st.subheader("Historial de movimientos")
    df_h = obtener_historial_completo()

    if not df_h.empty:
        df_h['fecha'] = pd.to_datetime(df_h['fecha']).dt.strftime('%d/%m/%Y %H:%M')
        st.dataframe(df_h, use_container_width=True, hide_index=True)
    else:
        st.info("No hay datos todavía")
