import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Crear la conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def inicializar_db():
    """
    En Google Sheets, la 'inicialización' consiste en asegurar que 
    existan las pestañas y los equipos base.
    """
    try:
        equipos = conn.read(worksheet="equipos")
    except:
        # Si la pestaña no existe, creamos los equipos iniciales
        nombres = ['Escuderos', 'Templarios', 'Capes', 'Herederas', 'Adalies']
        equipos = pd.DataFrame({
            "nombre": nombres,
            "puntos_totales": [0] * 5
        })
        conn.update(worksheet="equipos", data=equipos)
    
    try:
        conn.read(worksheet="historial")
    except:
        # Si el historial no existe, creamos una tabla vacía con columnas
        historial = pd.DataFrame(columns=["equipo_nombre", "descripcion", "puntos_cambio", "fecha"])
        conn.update(worksheet="historial", data=historial)

def registrar_puntos(nombre_equipo, descripcion, puntos):
    try:
        # 1. Leer datos actuales
        equipos = conn.read(worksheet="equipos")
        historial = conn.read(worksheet="historial")

        # Aseguramos que puntos_totales sea numérico (evita errores de suma)
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
        # Usamos 'ignore_index=True' y verificamos si historial está vacío
        if historial.empty:
            historial_actualizado = nuevo_log
        else:
            historial_actualizado = pd.concat([historial, nuevo_log], ignore_index=True)

        # 5. Guardar cambios en Google Sheets
        conn.update(worksheet="equipos", data=equipos)
        conn.update(worksheet="historial", data=historial_actualizado)
        
    except Exception as e:
        st.error(f"Error detallado: {e}")

def obtener_totales():
    """Retorna los datos para el gráfico de Streamlit"""
    df = conn.read(worksheet="equipos")
    # Limpiamos posibles valores nulos para evitar errores en el gráfico
    df['puntos_totales'] = df['puntos_totales'].fillna(0)
    return list(df.itertuples(index=False, name=None))

def obtener_historial_completo():
    """Función nueva para ver todos los registros"""
    return conn.read(worksheet="historial")