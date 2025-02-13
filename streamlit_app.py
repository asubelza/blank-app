import streamlit as st


import streamlit as st
import openai
import pandas as pd
from io import StringIO
import requests
import os # Import the os module

# Clave de API de OpenAI (reemplaza con tu clave)
openai.api_key = "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"

# Base de datos de juegos de mesa (ejemplo en CSV, puedes cargar tu propio archivo)

@st.cache_data
def cargar_juegos():
    url = "/media/TEMP/juegos_mesa.csv"

    # Check if file exists
    if not os.path.exists(url):
        st.error(f"File not found at: {url}")
        return pd.DataFrame()  # Return empty DataFrame if file not found

    try:
        # Explicitly specify the encoding as 'latin-1'
        df_juegos = pd.read_csv(url, encoding='latin-1')  # Try reading with default header and specified encoding
    except pd.errors.EmptyDataError:
        # If EmptyDataError, try reading without header
        try:
            df_juegos = pd.read_csv(url, header=None, encoding='latin-1')  # Try reading without header and specified encoding
            # Optionally, assign column names if needed
            # df_juegos.columns = ['column_1', 'column_2', ...] 
            st.warning("CSV file loaded without header. Column names may need to be assigned manually.")
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            return pd.DataFrame()  # Return empty DataFrame if still fails
    return df_juegos

df_juegos = cargar_juegos()

def obtener_sugerencia(prompt):
    respuesta = openai.Completion.create(
        engine="text-davinci-003",  # Ajusta el modelo
        prompt=prompt,
        max_tokens=250,  # Más tokens para respuestas más completas
        n=1,
        stop=None,
        temperature=0.7,  # Aumenta la creatividad si es necesario
    )
    return respuesta.choices[0].text.strip()

def generar_imagen(descripcion):
    response = openai.Image.create(
        prompt=descripcion,
        n=1,
        size="1024x1024"
    )
    imagen_url = response['data'][0]['url']
    return imagen_url

def buscar_juegos(criterios):
    # Aquí va la lógica para buscar juegos en df_juegos según los criterios
    juegos_encontrados = df_juegos[df_juegos.apply(lambda row: criterios.lower() in row.to_string().lower(), axis=1)]
    return juegos_encontrados

# Título y descripción
st.title("Generador de Juegos de Mesa Personalizados")

st.write("""
    Esta aplicación te ayudará a generar ideas para juegos de mesa personalizados según tus preferencias.
    Puedes ingresar detalles como el tipo de evento, el grupo de personas, las mecánicas preferidas, etc.
""")

# Formulario para ingresar criterios
evento = st.text_input("¿Para qué tipo de evento o grupo es el juego?")
tema = st.text_input("¿Qué tema o género prefieres? (Ej: Fantasía, Ciencia Ficción, Historia)")
mecanicas = st.text_input("¿Qué mecánicas te gustaría incluir? (Ej: cartas, dados, construcción de mazos)")
interacciones = st.text_input("¿Qué tipo de interacciones quieres entre jugadores? (Ej: cooperativo, competitivo, etc.)")

# Botón para obtener la sugerencia de juego
if st.button("Generar Idea de Juego"):
    prompt = f"Genera una idea para un juego de mesa personalizado para un evento '{evento}', con tema '{tema}', que incluya mecánicas como '{mecanicas}' y con interacciones '{interacciones}'."
    sugerencia = obtener_sugerencia(prompt)
    st.write("### Sugerencia Generada:")
    st.write(sugerencia)

    # Generar imagen de la idea de juego
    st.write("### Visualización del Juego:")
    imagen_url = generar_imagen(sugerencia)
    st.image(imagen_url, caption="Posible visualización del juego")

# Buscando juegos existentes en la base de datos
st.write("### Buscar Juegos de Mesa Existentes")
criterio_busqueda = st.text_input("Ingresa un término para buscar en la base de datos de juegos (Ej: temática, mecánica, etc.)")

if st.button("Buscar Juegos"):
    juegos_encontrados = buscar_juegos(criterio_busqueda)
    if not juegos_encontrados.empty:
        st.write("### Juegos Encontrados:")
        st.dataframe(juegos_encontrados)
    else:
        st.write("No se encontraron juegos que coincidan con tu búsqueda.")
