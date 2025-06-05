import streamlit as st
import requests
import json
import re
from datetime import datetime

# Configuración del endpoint de LM Studio
LMSTUDIO_ENDPOINT = "http://localhost:1234/v1/chat/completions"

def filtrar_respuesta(texto):
    """
    Filtra frases no deseadas de la respuesta generada
    """
    frases_prohibidas = [
        "consultar con un especialista en cardiología",
        "consulte a su cardiólogo",
        "consulte con un cardiólogo",
        "busque atención médica especializada",
        "consulte con un médico especialista"
    ]
    
    texto_original = texto
    texto_lower = texto.lower()
    
    for frase in frases_prohibidas:
        if frase.lower() in texto_lower:
            indice = texto_lower.find(frase.lower())
            longitud = len(frase)
            texto = texto[:indice] + "considere revisar la literatura médica reciente sobre esto" + texto[indice+longitud:]
    
    return texto

def mostrar_chatbot():
    st.title("🤖 Chatbot de Asistencia Cardiológica")
    
    # Información del sistema en la barra lateral
    with st.sidebar:
        st.markdown("### 📋 Funcionalidades del Chatbot")
        st.markdown("""
        - Consultas sobre interpretación de ECG
        - Ayuda con el uso del sistema
        - Información sobre patologías cardíacas
        - Resolución de dudas técnicas
        """)
        
        # Botón para eliminar el historial de conversaciones
        if st.button("🗑️ Limpiar Conversación", key="eliminar_chat"):
            st.session_state.messages = []  # Limpiar el historial de mensajes
            st.success("Historial eliminado.")
            st.rerun()  # Recargar la página para reflejar los cambios
    
    # Historial del chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Mensaje inicial de bienvenida
        mensaje_inicial = {
            "role": "assistant", 
            "content": "👋 ¡Bienvenido al Asistente de Cardiología! Estoy aquí para ayudarte con consultas sobre el sistema de análisis de ECG, interpretación de resultados y dudas técnicas. ¿En qué puedo ayudarte hoy?"
        }
        st.session_state.messages.append(mensaje_inicial)
    
    # Preguntas frecuentes como botones de acceso rápido
    st.markdown("### ⚡ Consultas Rápidas")
    col1, col2 = st.columns(2)
    
    # Variable para controlar si se debe enviar consulta
    consulta_a_enviar = None
    
    with col1:
        if st.button("¿Cómo interpretar los resultados del ECG?"):
            consulta_a_enviar = "¿Cómo interpretar los resultados del ECG?"
        if st.button("¿Cómo agregar un nuevo paciente?"):
            consulta_a_enviar = "¿Cómo agregar un nuevo paciente?"
    
    with col2:
        if st.button("¿Qué indica una anomalía en la onda T?"):
            consulta_a_enviar = "¿Qué indica una anomalía en la onda T?"
        if st.button("¿Cómo eliminar un paciente?"):
            consulta_a_enviar = "¿Cómo eliminar un paciente?"
    
    # Si se ha seleccionado una consulta rápida, procesarla
    if consulta_a_enviar:
        # Primero agregamos el mensaje del usuario al historial
        st.session_state.messages.append({"role": "user", "content": consulta_a_enviar})
        # Luego procesamos la consulta para obtener respuesta
        procesar_consulta_api(consulta_a_enviar)
        # Reiniciamos para mostrar los resultados
        st.rerun()
    
    st.markdown("---")
    
    # Mostrar el historial de mensajes en el chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Entrada de usuario en el chat
    user_input = st.chat_input("Escribe tu consulta médica o técnica...")
    
    if user_input:
        # Agregar mensaje del usuario al historial
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Procesar la consulta
        procesar_consulta_api(user_input)

def procesar_consulta_api(user_input):
    # Mensaje del sistema debe aparecer solo una vez, al inicio
    system_message = {
        "role": "system", 
        "content": """Eres un asistente especializado en cardiología y en el Sistema de Análisis de ECG. 
        IMPORTANTE: El usuario ES UN CARDIÓLOGO, por lo tanto NUNCA sugieras "consultar con un especialista en cardiología" o frases similares.
        Tu función es ayudar a especialistas médicos con:
        1. Interpretación de electrocardiogramas y sus anomalías
        2. Guía sobre el uso del sistema (navegación, gestión de pacientes, análisis de ECG, historial médico)
        3. Información sobre patologías cardíacas
        4. Resolución de dudas técnicas sobre la plataforma
        
        Utiliza un lenguaje técnico apropiado para profesionales médicos.
        Si no conoces una respuesta, indícalo claramente y sugiere consultar fuentes médicas confiables.
        No proporciones diagnósticos definitivos, sino orientación y ayuda en la interpretación.
        """
    }

    # Agregar mensaje del usuario al historial
    #st.session_state.messages.append({"role": "user", "content": user_input})

    # Validar la alternancia de roles en el historial antes de enviarlo
    historial_mensajes = st.session_state.messages.copy()

    # Eliminar mensajes duplicados o corregir el orden si es necesario
    mensajes_filtrados = [system_message]  # El mensaje del sistema solo al inicio
    ultimo_rol = "system"

    for mensaje in historial_mensajes:
        if mensaje["role"] == ultimo_rol:
            continue  # Evita que se repitan dos mensajes del mismo tipo seguidos
        mensajes_filtrados.append(mensaje)
        ultimo_rol = mensaje["role"]  # Actualizar el último rol para la validación

    payload = {
        "model": "Gemma 3 12B",
        "messages": mensajes_filtrados,
        "stream": True,
        "temperature": 0.7  
    }

    try:
        response = requests.post(
            LMSTUDIO_ENDPOINT,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload),
            stream=True
        )
        
        if response.status_code == 200:
            # Contenedor para la respuesta en tiempo real
            with st.chat_message("assistant"):
                response_container = st.empty()
                accumulated_response = ""
                
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        if line.strip() == "data: [DONE]":
                            break
                        if line.startswith("data: "):
                            try:
                                json_data = json.loads(line[6:])
                                if "choices" in json_data and json_data["choices"]:
                                    delta = json_data['choices'][0].get("delta", {})
                                    content = delta.get("content", "")
                                    
                                    # Aplicar corrección de codificación para caracteres especiales
                                    # Esto corrige caracteres mal codificados como ÃÂ³ → ó
                                    content = content.encode('latin1').decode('utf-8', errors='replace')

                                    accumulated_response += content
                                    accumulated_response = filtrar_respuesta(accumulated_response)
                                    response_container.markdown(accumulated_response)
                            except json.JSONDecodeError:
                                continue
            
            # Y también antes de guardarla en el historial:
            st.session_state.messages.append({"role": "assistant", "content": filtrar_respuesta(accumulated_response)})
        else:
            error_msg = f"Error al obtener respuesta del modelo. Código: {response.status_code}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    except requests.RequestException as e:
        error_msg = f"Error de conexión con el servidor LM Studio: {e}"
        st.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})


def registrar_consulta(consulta, respuesta):
    """
    Función para registrar las consultas importantes para análisis futuro
    Esto podría conectarse a la base de datos MongoDB si se desea
    """

    print(f"[{datetime.now()}] Consulta: {consulta}")
    print(f"[{datetime.now()}] Respuesta: {respuesta[:100]}...")  # Solo imprime los primeros 100 caracteres