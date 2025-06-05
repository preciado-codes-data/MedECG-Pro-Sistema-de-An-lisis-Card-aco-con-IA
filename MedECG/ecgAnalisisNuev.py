import streamlit as st
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from conexion import guardar_ecg_analizado
from extraer import analyze_all_leads
import requests
import json
import re
from googletrans import Translator
import time
import pandas as pd

def traducir_texto(texto, idioma_destino="es"):
    translator = Translator()
    traduccion = translator.translate(texto, dest=idioma_destino)
    return traduccion.text

def obtener_diagnostico_lmstudio(valores_ecg, valores_por_derivacion, sexo_paciente, modelo="Meta Llama 3.1 8B"):
    url = "http://localhost:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}

    # Create a compact representation of all lead values
    leads_info = ""
    for lead, valores in valores_por_derivacion.items():
        leads_info += f"""
        Derivación {lead}:
        - Pico P: {valores['Pico P']} mV
        - Pico QRS: {valores['Pico QRS']} mV
        - Pico T: {valores['Pico T']} mV
        - Pico U: {valores['Pico U']} mV
        """

    prompt = f"""
    Analiza los siguientes valores de ECG de un paciente {sexo_paciente}:

    **Valores promedio:**
    - Pico P: {valores_ecg['Pico P']} mV
    - Pico QRS: {valores_ecg['Pico QRS']} mV
    - Pico T: {valores_ecg['Pico T']} mV
    - Pico U: {valores_ecg['Pico U']} mV

    **Valores por derivación:**
    {leads_info}

    **Rangos normales:**
    - Pico P: 0.05 - 0.25 mV (VALORES COMO 0.397, 0.04, 0.4 SON ANOMALÍAS)
    - Pico QRS: 0.6 - 1.2 mV (VALORES >1.2 COMO 1.3, 1.4 SON HIPERTROFIA VENTRICULAR)
    - Pico T: 0.1 - 0.5 mV (VALORES >0.5 COMO 0.6, 0.7 SON ANOMALÍAS)
    - Pico U: 0.0 - 0.2 mV (VALORES >0.2 SON ANOMALÍAS)

    **Reglas estrictas:**
    1. Si TODOS los valores están dentro del rango → ✅ ECG Normal
    2. Si hay anomalías → Escoge SOLO UN diagnóstico basado en:
    - Pico QRS fuera de rango → Hipertrofia ventricular
    - Pico T fuera de rango → Onda T invertida
    - Pico P fuera de rango → Arritmia cardiaca
    - Pico U fuera de rango → Alteración en la repolarización

    **Formato de respuesta EXACTO:**
    - Si es normal: "✅ Sin Anomalías - ECG Normal"
    - Si hay anomalías: "⚠️ ECG Anormal - [DIAGNÓSTICO]"

    Ejemplos válidos:
    ⚠️ ECG Anormal - Hipertrofia ventricular
    ⚠️ ECG Anormal - Arritmia cardiaca

    ¡NO DES EXPLICACIONES! Solo responde con el formato exacto especificado.
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

def obtener_diagnostico_deepseek(valores_ecg, valores_por_derivacion, sexo_paciente ,modelo="DeepSeek R1 Distill"):
    url = "http://localhost:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}

    # Create a compact representation of all lead values
    leads_info = ""
    for lead, valores in valores_por_derivacion.items():
        leads_info += f"""
        Derivación {lead}:
        - Pico P: {valores['Pico P']} mV
        - Pico QRS: {valores['Pico QRS']} mV
        - Pico T: {valores['Pico T']} mV
        - Pico U: {valores['Pico U']} mV
        """

    prompt = f"""
    Evalúa estos valores de ECG (promedio + derivaciones) para un {sexo_paciente}:

    **Promedios:**
    - Pico P: {valores_ecg['Pico P']} mV (Normal: 0.05-0.25)
    - Pico QRS: {valores_ecg['Pico QRS']} mV (Normal: 0.6-1.2)
    - Pico T: {valores_ecg['Pico T']} mV (Normal: 0.1-0.5)
    - Pico U: {valores_ecg['Pico U']} mV (Normal: 0.0-0.2)

    **Derivaciones:**
    {leads_info}

    Responde SOLO con:
    ✅ Sin anomalías  
    ⚠️ ECG Anormal - Hipertrofia ventricular (QRS>1.2)  
    ⚠️ ECG Anormal - Onda T invertida (T>0.5)  
    ⚠️ ECG Anormal - Arritmia cardiaca (P fuera de rango)  
    ⚠️ ECG Anormal - Alteración en la repolarización (U>0.2)

    **Prioridad:** QRS → T → P → U.  
    ¡No agregues texto extra!
    """

    data = {
        "model": modelo,
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

def obtener_diagnostico_gemma(valores_ecg, valores_por_derivacion, sexo_paciente, modelo="Gemma 3 12B"):
    url = "http://localhost:1234/v1/chat/completions"  # Reemplaza con la URL correcta para el modelo Gemma
    headers = {"Content-Type": "application/json"}

    # Create a compact representation of all lead values
    leads_info = ""
    for lead, valores in valores_por_derivacion.items():
        leads_info += f"""
        Derivación {lead}:
        - Pico P: {valores['Pico P']} mV
        - Pico QRS: {valores['Pico QRS']} mV
        - Pico T: {valores['Pico T']} mV
        - Pico U: {valores['Pico U']} mV
        """

    prompt = f"""
    Evalúa los siguientes valores de ECG para un paciente {sexo_paciente} y determina si hay anomalías.
    Debes analizar tanto los valores promedio como los valores de cada derivación individual.

    **Valores promedio:**  
    - Pico P: {valores_ecg['Pico P']} mV  
    - Pico QRS: {valores_ecg['Pico QRS']} mV  
    - Pico T: {valores_ecg['Pico T']} mV  
    - Pico U: {valores_ecg['Pico U']} mV  

    **Valores por derivación:**
    {leads_info}

    **Rangos normales:**  
    - Pico P: 0.05 - 0.25 mV  
    - Pico QRS: 0.6 - 1.2 mV  
    - Pico T: 0.1 - 0.5 mV  
    - Pico U: 0.0 - 0.2 mV  

    **Instrucciones:**
    1. Analiza todos los valores (promedio y por derivación)
    2. Identifica qué picos están fuera de los rangos normales
    3. Proporciona UN SOLO DIAGNÓSTICO GENERAL basado en la anomalía más significativa encontrada
    
    **Diagnósticos posibles basados en anomalías:**  
    - Si el Pico P está fuera de rango → Arritmia Cardiaca  
    - Si el Pico QRS está fuera de rango → Hipertrofia ventricular  
    - Si el Pico T está fuera de rango → Onda T invertida  
    - Si el Pico U está fuera de rango → Alteración en la repolarización  

    **Formato de respuesta:**
    Si no hay anomalías:
    ✅ Sin Anomalías - ECG Normal
    
    Si hay anomalías, proporciona un único diagnóstico general y menciona los picos anormales:
    ⚠️ ECG Anormal - [DIAGNÓSTICO PRINCIPAL]
    
    Por ejemplo:
    ⚠️ ECG Anormal - Hipertrofia ventricular
    
    No incluyas información sobre derivaciones específicas en el diagnóstico final.
    No proporciones más de un diagnóstico. Escoge el más significativo.
    No des explicaciones adicionales.
    Responde solo en español y de forma directa.
    """

    data = {
        "model": modelo, 
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3  # Control de la aleatoriedad de la respuesta
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

def obtener_picos_anormales(valores_ecg):
    RANGOS_NORMALES = {
        'Pico P': {'min': 0.05, 'max': 0.25, 'unidad': 'mV'},
        'Pico QRS': {'min': 0.6, 'max': 1.2, 'unidad': 'mV'},
        'Pico T': {'min': 0.1, 'max': 0.5, 'unidad': 'mV'},
        'Pico U': {'min': 0.0, 'max': 0.2, 'unidad': 'mV'}
    }
    
    picos_anormales = {}
    
    for lead, valores in valores_ecg.items():
        for pico, valor in valores.items():
            rango = RANGOS_NORMALES[pico]
            if valor < rango['min'] or valor > rango['max']:
                if pico not in picos_anormales:
                    picos_anormales[pico] = {
                        'derivaciones': [],
                        'rango_normal': f"{rango['min']}-{rango['max']} {rango['unidad']}"
                    }
                
                # Calcular desviación y dirección correctamente
                if valor > rango['max']:
                    desviacion = f"{(valor - rango['max']):.3f}"
                    direccion = '↑'  # Por encima del máximo
                else:
                    desviacion = f"{(rango['min'] - valor):.3f}"
                    direccion = '↓'  # Por debajo del mínimo
                
                picos_anormales[pico]['derivaciones'].append({
                    'derivacion': lead,
                    'valor': valor,
                    'desviacion': desviacion,
                    'direccion': direccion,
                    'unidad': rango['unidad']
                })
    
    return picos_anormales

def mostrar_analisis_detallado(picos_anormales):
    if picos_anormales:
        st.subheader("📊 Análisis Detallado de Anomalías")

        st.divider()  # Barra divisoria bajo el título
        
        for pico, datos in picos_anormales.items():
            with st.expander(f"🔴 {pico} - {len(datos['derivaciones'])} derivaciones anormales (Rango normal: {datos['rango_normal']})"):
                # Crear una tabla con los datos
                table_data = []
                
                for d in datos['derivaciones']:
                    table_data.append([
                        d['derivacion'],
                        f"{d['valor']} {d['unidad']}",
                        datos['rango_normal'],
                        f"{d['desviacion']} {d['unidad']} {d['direccion']}"
                    ])
                
                """
                # Mostrar la tabla con estilo
                st.table(
                    pd.DataFrame(
                        table_data,
                        columns=["Derivación", "Valor Obtenido", "Rango Normal", "Diferencia"]
                    ).style.set_properties(**{
                        'background-color': '#f8f9fa',
                        'border': '1px solid #dee2e6',
                        'color': '#212529'
                    })
                )"""
                # Nueva implementación de estilo de tabla
                df = pd.DataFrame(
                    table_data,
                    columns=["Derivación", "Valor Obtenido", "Rango Normal", "Diferencia"]
                )
                # Función de estilo personalizado
                def color_abnormal(df):
                    """
                    Color-code the rows based on abnormal values
                    - Red for values above range
                    - Blue for values below range
                    """
                    # Crear un DataFrame de estilos inicialmente vacío
                    styles = pd.DataFrame('', index=df.index, columns=df.columns)
                        
                    # Aplicar estilo a la columna de Diferencia
                    for idx, val in df['Diferencia'].items():
                        is_above = '↑' in str(val)
                        is_below = '↓' in str(val)
                            
                        if is_above:
                            styles.loc[idx, 'Diferencia'] = 'background-color: #ffdddd; color: #d32f2f;'
                        elif is_below:
                            styles.loc[idx, 'Diferencia'] = 'background-color: #e6f2ff; color: #1976d2; font-weight: bold;'
                            styles.loc[idx, 'Derivación'] = 'background-color: #f0f8ff;'
                            styles.loc[idx, 'Valor Obtenido'] = 'background-color: #f0f8ff;'
                            styles.loc[idx, 'Rango Normal'] = 'background-color: #f0f8ff;'
                        
                    return styles

                # Aplicar estilo avanzado
                styled_df = df.style.apply(
                    color_abnormal, 
                    axis=None
                ).set_properties(**{
                    # Estilo de tabla médica
                    'border': '1px solid #b0c4de',  # Borde azul claro
                    'border-collapse': 'collapse',
                    'text-align': 'center',
                    'font-family': 'Arial, sans-serif',
                    'font-size': '0.9em',
                }).set_table_styles([
                    # Estilo de encabezado
                    {'selector': 'th', 
                    'props': [
                        ('background-color', '#2c3e50'),  # Azul marino oscuro
                        ('color', 'white'),  # Texto blanco
                        ('font-weight', 'bold'),
                        ('padding', '12px'),
                        ('text-transform', 'uppercase'),
                        ('letter-spacing', '1px'),
                        ('border-bottom', '2px solid #34495e')
                    ]},
                    # Estilo de filas
                    {'selector': 'tr:nth-child(even)', 
                    'props': [('background-color', '#f4f6f7')]},
                    {'selector': 'tr:nth-child(odd)', 
                    'props': [('background-color', '#ffffff')]},
                    # Hover effect
                    {'selector': 'tr:hover', 
                    'props': [('background-color', '#e8f4f8')]}
                ]).set_caption(
                    "🫀 Análisis Detallado de Pico QRS - 12 Derivaciones", 
                )

                # Renderizar la tabla con estilo
                st.dataframe(styled_df, use_container_width=True)
                
    
    return picos_anormales

def analizar_ecg(pacientes_ordenados):
    with st.container():
        st.header("Analizador de ECG")
        st.divider()

        # Seleccionar paciente
        opciones_pacientes = [f"{row['ID Paciente']} - {row['Nombre Paciente']} ({row['Género']})" for _, row in pacientes_ordenados.iterrows()]
        paciente_seleccionado = st.selectbox("Seleccionar paciente para análisis", opciones_pacientes)

        # Modelo a usar
        modelo_a_usar = "Gemma 3 12B"

        if paciente_seleccionado != "Seleccionar paciente":
            archivo_ecg = st.file_uploader("Cargar Imagen del ECG", type=["jpg", "png", "jpeg"])

            if archivo_ecg is not None:
                # Procesar la imagen y extraer valores
                imagen = Image.open(archivo_ecg)
                
                # Mostrar la imagen original
                #st.subheader("Imagen ECG Original:")
                #st.image(imagen, caption="ECG Cargado", use_container_width=True, width=700)
                
                # Extraer valores del ECG
                with st.spinner("Extrayendo valores del ECG..."):
                    valores_ecg = analyze_all_leads(imagen)
                
                # Mostrar los valores extraídos
                #st.subheader("Valores Extraídos del ECG:")
                #for lead, valores in valores_ecg.items():
                    #st.write(f"**Derivación {lead}:**")
                    #for pico, valor in valores.items():
                        #st.write(f"- **{pico}:** {valor} mV")

                # Obtener datos del paciente
                id_paciente, nombre_paciente, sexo_paciente = paciente_seleccionado.split(" - ")[0], paciente_seleccionado.split(" - ")[1].split(" (")[0], paciente_seleccionado.split("(")[1].strip(")")

                # Valores consolidados para diagnóstico general
                valores_consolidados = {
                    "Pico P": np.mean([valores["Pico P"] for valores in valores_ecg.values()]),
                    "Pico QRS": np.mean([valores["Pico QRS"] for valores in valores_ecg.values()]),
                    "Pico T": np.mean([valores["Pico T"] for valores in valores_ecg.values()]),
                    "Pico U": np.mean([valores["Pico U"] for valores in valores_ecg.values()]),
                }

                # Botón para realizar análisis
                if st.button("Realizar Diagnóstico"):
                    with st.spinner("Realizando Diagnóstico..."):
                        diagnostico, tiempo = obtener_diagnostico_deepseek(valores_consolidados, valores_ecg, sexo_paciente, modelo_a_usar)

                    st.divider()
                    # Mostrar diagnóstico general
                    st.subheader("Diagnóstico General:")
                    if "Sin Anomalías" in diagnostico or "Normal" in diagnostico:
                        st.success(diagnostico)
                    else:
                        st.warning(diagnostico)
                    st.write(f"Tiempo de respuesta: {round(tiempo, 2)} segundos")

                    # Detectar y mostrar picos anormales
                    picos_anormales = obtener_picos_anormales(valores_ecg)
                    
                    # Mostrar análisis detallado y obtener el formato para guardar
                    analisis_detallado = mostrar_analisis_detallado(picos_anormales)
                    
                    # Modificar la parte donde preparas los detalles para guardar:
                    if picos_anormales:
                        detalle_texto = "Detalles de Picos Anormales\n\n"
                        for pico, datos in picos_anormales.items():
                            detalle_texto += f"🔴 **{pico}** - {len(datos['derivaciones'])} derivaciones anormales (Rango normal: {datos['rango_normal']}):\n\n"
                            for d in datos['derivaciones']:
                                flecha = '↑' if float(d['desviacion']) > 0 else '↓'
                                detalle_texto += f"""
                                **Derivación {d['derivacion']}:**  
                                - Valor Extraido: `{d['valor']} {d['unidad']}`  
                                - Rango normal: `{datos['rango_normal']}`  
                                - Desviación: `{d['desviacion']} {d['unidad']}` {flecha}  
                                \n"""
                    else:
                        detalle_texto = "No se detectaron picos anormales en este ECG."

                    # Guardar el ECG analizado
                    imagen_bytes = archivo_ecg.getvalue()
                    guardar_ecg_analizado(id_paciente, nombre_paciente, imagen_bytes, diagnostico, detalle_texto)

                    st.success("✅ ECG analizado y guardado correctamente.")