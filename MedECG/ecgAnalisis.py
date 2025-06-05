import streamlit as st
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from conexion import guardar_ecg_analizado
from extraer import extract_ecg_values
import requests
import json
import re
from googletrans import Translator
import time

def traducir_texto(texto, idioma_destino="es"):
    translator = Translator()
    traduccion = translator.translate(texto, dest=idioma_destino)
    return traduccion.text

def obtener_diagnostico_lmstudio(valores_ecg, sexo_paciente, modelo="Meta Llama 3.1"):
    url = "http://localhost:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}

    # Modificar el prompt para dejar claro que el Pico QRS debe ser validado correctamente.
    prompt = f"""
    Analiza los siguientes valores de ECG de un paciente {sexo_paciente}:
    - Pico P: {valores_ecg['Pico P']} mV
    - Pico QRS: {valores_ecg['Pico QRS']} mV
    - Pico T: {valores_ecg['Pico T']} mV
    - Pico U: {valores_ecg['Pico U']} mV

    Si los valores están dentro del rango normal para un {sexo_paciente} los cuales son: 
    - Pico P: Debe ser entre 0.05 mV y 0.25 mV. VALORES COMO 0.397 mV, 0.04, 0.4 Y ESOS VALORES SON ANOMALIAS
    - Pico QRS: Debe ser entre 0.6 mV y 1.2 mV. quiero que te quede claro, valores dentro del rango como: 0.958, 0.800, 1.157 mV, 1.050 y esos valores NO DEBEN SER CONSIDERADOS COMO ANOMALIAS**  
    por otro lado valores mayores a 1.2 como 1.3, 1.4, 1.5, 1.25 SI SON CONSIDERADOS COMO ANOMALIAS Y SI CUENTA COMO Hipertrofia ventricular ya sea para HOMBRES Y MUJERES
    - Pico T: Debe ser entre 0.1 mV y 0.5 mV. quiero que te quede claro, valores dentro del rango como: 0.291 mV, 0.45, 0.12, y esos valores NO DEBEN SER CONSIDERADOS COMO ANOMALIAS**  
    por otro lado valores mayores a 0.5 como 0.6, 0.55, 0.7, 0.65 SI SON CONSIDERADOS COMO ANOMALIAS ya sea para HOMBRES Y MUJERES
    - Pico U: Debe ser entre 0.0 mV y 0.2 mV. valores como: 0.012 mV, 0.15, 0.19 entre esos valores NO DEBEN SER CONSIDERADOS COMO ANOMALIAS

    **Si cualquier valor no está dentro de estos rangos, se considera una anomalía.**

    Si los valores están dentro del rango normal para un {sexo_paciente}, responde con:  
    ✅ Sin Anomalias ECG Normal  

    Si hay anomalías (es decir, los valores están por encima o por debajo de los rangos de valores de Pico P, Pico QRS, Pico T y Pico U), responde con:  
    ⚠️ ECG Anormal - en qué valor se encuentra la anomalía y responde exactamente con una de las siguientes opciones acorde con los valores obtenidos y el sexo del paciente:  
    **Arritmia cardiaca**  
    **Bradicardia**  
    **Taquicardia**  
    **Bloqueo AV**  
    **Hipertrofia ventricular (si el valor del Pico QRS es mayor a 1.2 mV o por debajo de 0.6 mV), quiero que te quede claro, valores dentro del rango como, 0.958, 0.800, 1.157 mV, 1.050 y esos valores NO DEBEN SER CONSIDERADOS COMO ANOMALIAS**  
    por otro lado valores mayores a 1.2 como 1.3, 1.4, 1.5, 1.25 SI SON CONSIDERADOS COMO ANOMALIAS Y SI CUENTA COMO Hipertrofia ventricular ya sea para HOMBRES Y MUJERES  
    **Onda T invertida**  

    No des explicaciones adicionales. Solo responde en qué valor está la anomalía y con una de las opciones de anomalías.
    """

    data = {
        "model": modelo,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    }

    # 📌 Inicia el cronómetro
    tiempo_inicio = time.time()

    response = requests.post(url, headers=headers, data=json.dumps(data))

    # 📌 Calcula el tiempo transcurrido
    tiempo_respuesta = time.time() - tiempo_inicio

    if response.status_code == 200:
        resultado = response.json()["choices"][0]["message"]["content"]
        return resultado, tiempo_respuesta
    else:
        return "⚠️ Error al obtener el diagnóstico", tiempo_respuesta

def obtener_diagnostico_deepseek(valores_ecg, sexo_paciente):
    url = "http://localhost:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}

    prompt = f"""
    Evalúa los valores de ECG de un paciente {sexo_paciente} y determina si hay anomalías.
    Responde solo con el diagnóstico sin explicaciones y no me digas que estas haciendo, que pasos estas haciendo y como lo estas razonando, solo dame una respuestas corta y sencilla.  
    Si los valores están dentro del rango, responde exactamente:  
    ✅ Sin anomalías  

    Si hay anomalías, indica solo el pico afectado y el diagnóstico en este formato:  
    ⚠️ ECG Anormal - Pico X: [Diagnóstico]  

    **Valores del paciente:**  
    - Pico P: {valores_ecg['Pico P']} mV  
    - Pico QRS: {valores_ecg['Pico QRS']} mV  
    - Pico T: {valores_ecg['Pico T']} mV  
    - Pico U: {valores_ecg['Pico U']} mV  

    **Rangos normales:**  
    - Pico P: 0.05 - 0.25 mV  
    - Pico QRS: 0.6 - 1.2 mV  
    - Pico T: 0.1 - 0.5 mV  
    - Pico U: 0.0 - 0.2 mV  NO PUEDE PASAR DE 0.2 VALORES ARRIBA COMO 0.3, 0.4, 0.5, 0.6 Y VALORES DENTRO DE LOS MISMOS YA SON ANOMALIAS

    **Condiciones según anomalías:**  
    - Pico QRS fuera de rango → Hipertrofia ventricular  
    - Pico T invertido → Onda T invertida  
    - Pico P fuera de rango → Arritmia Cardiaca
    - Pico U fuera de rango → Alteración en la repolarización
    - Otros valores fuera de rango → Bloqueo AV / Bradicardia / Taquicardia según corresponda  

    ⚠ **Ejemplo de respuesta esperada:**  
    - ✅ Sin anomalías  
    - ⚠️ ECG Anormal - Pico QRS: Hipertrofia ventricular  
    - ⚠️ ECG Anormal - Pico T: Onda T invertida  
    - ⚠️ ECG Anormal - Pico P: Arritmia cardiaca
    - ⚠️ ECG Anormal - Pico U: Alteración en la repolarización

    Responde solo en español y de forma directa.
    """

    data = {
        "model": "DeepSeek R1 Distill Llama 8B",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    # 📌 Inicia el cronómetro
    tiempo_inicio = time.time()

    response = requests.post(url, headers=headers, data=json.dumps(data))

    # 📌 Calcula el tiempo transcurrido
    tiempo_respuesta = time.time() - tiempo_inicio


    if response.status_code == 200:
        resultado = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")

        # Eliminar cualquier etiqueta HTML o texto adicional
        resultado_limpio = re.sub(r"<[^>]+>", "", resultado).strip()

        # Traducir si la respuesta no está en español
        resultado_final = traducir_texto(resultado_limpio)

        return resultado_final, tiempo_respuesta
    else:
        return "⚠️ Error al obtener el diagnóstico", tiempo_respuesta

def obtener_diagnostico_gemma(valores_ecg, sexo_paciente):
    url = "http://localhost:1234/v1/chat/completions"  # Reemplaza con la URL correcta para el modelo Gemma
    headers = {"Content-Type": "application/json"}

    prompt = f"""
    Evalúa los siguientes valores de ECG para un paciente {sexo_paciente} y determina si hay anomalías. 
    Responde con solo el diagnóstico indicando si hay alguna anomalía y especifica el pico afectado con el diagnóstico. 
    Si no hay anomalías, responde con '✅ Sin Anomalías'. 

    **Valores del paciente:**  
    - Pico P: {valores_ecg['Pico P']} mV  
    - Pico QRS: {valores_ecg['Pico QRS']} mV  
    - Pico T: {valores_ecg['Pico T']} mV  
    - Pico U: {valores_ecg['Pico U']} mV  

    **Rangos normales:**  
    - Pico P: 0.05 - 0.25 mV  
    - Pico QRS: 0.6 - 1.2 mV  
    - Pico T: 0.1 - 0.5 mV  
    - Pico U: 0.0 - 0.2 mV  

    Si Hay algun rango anormal en un pico muestra el valor y pico anormal, asi como de que anomalia se trata como arritmia, taquicardia, entre otras

    Responde solo con la anomalía detectada o '✅ ECG Sin Anomalías'.  
    No expliques ni detalles el razonamiento.
    """

    data = {
        "model": "Gemma 3 12B Instruct",  # Aquí especificas el nombre del modelo
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3  # Controla la aleatoriedad de la respuesta
    }

    # 📌 Inicia el cronómetro
    tiempo_inicio = time.time()

    response = requests.post(url, headers=headers, data=json.dumps(data))

    # 📌 Calcula el tiempo transcurrido
    tiempo_respuesta = time.time() - tiempo_inicio

    if response.status_code == 200:
        resultado = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        
        # Limpiar cualquier posible etiqueta HTML y traducir la respuesta si no está en español
        resultado_limpio = re.sub(r"<[^>]+>", "", resultado).strip()

        return resultado_limpio, tiempo_respuesta
    else:
        return "⚠️ Error al obtener el diagnóstico", tiempo_respuesta

def analizar_ecg(pacientes_ordenados):
    st.header("Analizador de ECG")

    # Seleccionar paciente
    opciones_pacientes = [f"{row['ID']} - {row['Nombre']} ({row['Género']})" for _, row in pacientes_ordenados.iterrows()]
    paciente_seleccionado = st.selectbox("Seleccionar paciente para análisis", opciones_pacientes)

    # Modelo a usar
    modelo_a_usar = "Meta Llama 3.1"  # Puedes cambiarlo a otro modelo si es necesario

    if paciente_seleccionado != "Seleccionar paciente":
        archivo_ecg = st.file_uploader("Cargar Imagen del ECG", type=["jpg", "png", "jpeg"])

        if archivo_ecg is not None:
            # Procesar la imagen y extraer valores
            imagen = Image.open(archivo_ecg)
            
            # Mostrar la imagen original
            st.subheader("Imagen ECG Original:")
            st.image(imagen, caption="ECG Cargado", use_column_width=True)
            
            #Extraer valores del ECG
            with st.spinner("Extrayendo valores del ECG..."):
                valores_ecg, fig_analisis = extract_ecg_values(imagen)
            
            # Mostrar gráfico de análisis
            st.subheader("Análisis de la Señal ECG:")
            st.pyplot(fig_analisis)

            # Mostrar los valores extraídos
            st.subheader("Valores Extraídos del ECG:")
            for clave, valor in valores_ecg.items():
                st.write(f"- **{clave}:** {valor} mV")
            
             # Obtener sexo del paciente
            id_paciente, nombre_paciente, sexo_paciente = paciente_seleccionado.split(" - ")[0], paciente_seleccionado.split(" - ")[1].split(" (")[0], paciente_seleccionado.split("(")[1].strip(")")

            # Botón para realizar análisis con el modelo definido
            if st.button("Realizar Diagnóstico"):
                with st.spinner(f"Obteniendo diagnóstico con {modelo_a_usar}..."):
                    diagnostico, tiempo = obtener_diagnostico_lmstudio(valores_ecg, sexo_paciente, modelo_a_usar)

                # Mostrar resultado del diagnóstico
                st.subheader("Diagnóstico del modelo:")
                if "Sin Anomalías" in diagnostico or "Normal" in diagnostico:
                    st.success(diagnostico)
                else:
                    st.warning(diagnostico)
                    
                st.subheader("Tiempo de Respuesta:")
                st.write(f"{round(tiempo, 2)} segundos")

                # Guardar el ECG analizado en la base de datos
                imagen_bytes = archivo_ecg.getvalue()
                guardar_ecg_analizado(id_paciente, nombre_paciente, imagen_bytes, diagnostico)

                st.success("✅ ECG analizado y guardado correctamente.")

