import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Definimos la URL de manera explícita para evitar el error 404
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1VTHKI7cL78RIdiGD43WEdIEYEhghNShJe3shMvqq1Xw/edit"

# Crear la conexión especificando la URL directamente
conn = st.connection("gsheets", type=GSheetsConnection)

def inicializar_db():
    """Asegura que existan las pestañas y los equipos base."""
    try:
        # Intentamos leer usando la URL explícita
        equipos = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="equipos")
    except Exception as e:
        st.warning(f"Configurando pestaña 'equipos' por primera vez...")
        nombres = ['Escuderos', 'Templarios', 'Capes', 'Herederas', 'Adalies']
        equipos = pd.DataFrame({
            "nombre": nombres,
            "puntos_totales": [0] * 5
        })
        conn.update(spreadsheet=SPREADSHEET_URL, worksheet="equipos", data=equipos)
    
    try:
        conn.read(spreadsheet=SPREADSHEET_URL, worksheet="historial")
    except Exception as e:
        st.warning(f"Configurando pestaña 'historial' por primera vez...")
        historial = pd.DataFrame(columns=["equipo_nombre", "descripcion", "puntos_cambio", "fecha"])
        conn.update(spreadsheet=SPREADSHEET_URL, worksheet="historial", data=historial)

def registrar_puntos(nombre_equipo, descripcion, puntos):
    try:
        # 1. Leer datos actuales especificando el spreadsheet
        equipos = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="equipos")
        historial = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="historial")

        # Aseguramos que puntos_totales sea numérico
        equipos['puntos_totales'] = pd.to_numeric(equipos['puntos_totales']).fillna(0)

        # 2. Actualizar el total del equipo
        equipos.loc[equipos['nombre'] == nombre_equipo, 'puntos_totales'] += puntos
        
        # 3. Preparar el nuevo registro
        nuevo_log = pd.DataFrame([{
            "equipo_nombre": str(nombre_equipo),
            "descripcion": str(descripcion),
            "puntos_cambio": int(puntos),
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        
        # 4. Combinar con el historial existente
        if historial.empty:
            historial_actualizado = nuevo_log
        else:
            historial_actualizado = pd.concat([historial, nuevo_log], ignore_index=True)

        # 5. Guardar cambios
        conn.update(spreadsheet=SPREADSHEET_URL, worksheet="equipos", data=equipos)
        conn.update(spreadsheet=SPREADSHEET_URL, worksheet="historial", data=historial_actualizado)
        
    except Exception as e:
        st.error(f"Error al registrar puntos: {e}")

def obtener_totales():
    """Retorna los datos para el gráfico"""
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="equipos")
        df['puntos_totales'] = pd.to_numeric(df['puntos_totales']).fillna(0)
        return list(df.itertuples(index=False, name=None))
    except Exception as e:
        st.error(f"Error al obtener totales: {e}")
        return []

def obtener_historial_completo():
    """Retorna todo el historial"""
    try:
        return conn.read(spreadsheet=SPREADSHEET_URL, worksheet="historial")
    except Exception as e:
        st.error(f"Error al obtener historial: {e}")
        return pd.DataFrame()