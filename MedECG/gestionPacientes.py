# pacientes.py
import streamlit as st
import pandas as pd
from conexion import obtener_pacientes, agregar_paciente, eliminar_paciente
import time
import uuid
from datetime import datetime, date

def calcular_edad(fecha_nacimiento):
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year
    return edad

def gestion_pacientes():
    st.header("Gestión de Pacientes")

    # Estilos mejorados para el formulario
    st.markdown("""
    <style>
    .paciente-form {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 30px;
    }
    
    .form-section {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
        background-color: #f9f9f9;
    }
    
    .section-title {
        color: #2e86c1;
        margin-bottom: 15px;
        font-size: 1.2em;
        display: flex;
        align-items: center;
    }
    
    .section-title .icon {
        margin-right: 10px;
    }
    
    .paciente-form .stTextInput input,
    .paciente-form .stNumberInput input,
    .paciente-form .stDateInput input,
    .paciente-form .stSelectbox select {
        border: 1px solid #1a6fc4;
        border-radius: 6px;
        padding: 8px 12px;
    }
    
    .paciente-form .stTextArea textarea {
        border: 1px solid #1a6fc4;
        border-radius: 6px;
    }
    
    .required-field {
        color: #e74c3c;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state for pacientes if it doesn't exist
    if 'pacientes' not in st.session_state:
        st.session_state.pacientes = pd.DataFrame()

    # Mostrar los pacientes desde MongoDB
    pacientes = obtener_pacientes()
    pacientes_lista = []
    for paciente in pacientes:
        paciente_data = {
            "ID Paciente": paciente.get("ID Paciente"),
            "Nombre Paciente": paciente.get("Nombre Paciente"),
            "Telefono Paciente": paciente.get("Telefono Paciente"),
            "Edad": paciente.get("Edad"),
            "Género": paciente.get("Género"),
            "CURP": paciente.get("CURP"),
            "NSS": paciente.get("NSS"),
            "Fecha Nacimiento": paciente.get("Fecha Nacimiento"),
            "Direccion": paciente.get("Direccion"),
            "Colonia": paciente.get("Colonia"),
            "Codigo Postal": paciente.get("Código Postal"),
            "Municipio": paciente.get("Municipio"),
            "Estado": paciente.get("Estado"),
            "Datos de Referencia": paciente.get("Datos de Referencia"),
            "Persona de Contacto": paciente.get("Persona de Contacto"),
            "Parentesco": paciente.get("Parentesco"),
            "Domicilio Persona de Contacto": paciente.get("Domicilio Persona de Contacto"),
            "Telefono Persona de Contacto": paciente.get("Telefono Persona de Contacto"),
            "Celular Persona de Contacto": paciente.get("Celular Persona de Contacto"),
            "Correo de Contacto": paciente.get("Correo de Contacto"),
            "Observaciones": paciente.get("Observaciones")
        }
        pacientes_lista.append(paciente_data)

    if 'limpiar_formulario' not in st.session_state:
        st.session_state.limpiar_formulario = False

    def generar_id_unico():
        if not st.session_state.pacientes.empty:
            try:
                ids_numericos = [int(id.replace('PAC', '')) for id in st.session_state.pacientes['ID Paciente'] if id.startswith('PAC')]
                if ids_numericos:
                    nuevo_numero = max(ids_numericos) + 1
                    return f"PAC{nuevo_numero:03d}"
                else:
                    return "PAC001"
            except:
                return f"PAC{uuid.uuid4().hex[:6].upper()}"
        else:
            return "PAC001"

    # Contenedor del formulario con estilo
    with st.container():
        st.markdown('<div class="paciente-form">', unsafe_allow_html=True)
        
        with st.form("agregar_paciente", clear_on_submit=True):
            st.subheader("📝 Agregar Nuevo Paciente")
            id_generado = generar_id_unico()
            
            # SECCIÓN 1: DATOS PERSONALES
            with st.container():
                st.markdown('<div class="form-section">', unsafe_allow_html=True)
                st.markdown('<div class="section-title"><span class="icon">👤</span> Datos Personales</div>', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns([2, 2, 3, 2])
                with col1:
                    apellido_paterno = st.text_input("Apellido Paterno*", max_chars=30)
                with col2:
                    apellido_materno = st.text_input("Apellido Materno", max_chars=30)
                with col3:
                    nombres = st.text_input("Nombre(s)*", max_chars=50, help="Nombre o Nombres del paciente")
                with col4:
                    telefono = st.text_input("Numero de Telefono", max_chars=15)
                
                # Campos más pequeños en una sola fila
                col_datos1, col_datos2, col_datos3, col_datos4, col_datos5 = st.columns([0.5, 1, 1, 1, 1])  # Ajusta estos valores
           
                with col_datos1:
                    fecha_nacimiento = st.date_input("Fecha Nacimiento*", 
                                                     value=None,
                                                min_value=date(1900, 1, 1), 
                                                max_value=date.today(),
                                            )
                with col_datos2:
                    edad = st.number_input("Edad", max_value=100, min_value=0)
                with col_datos3:
                    genero = st.selectbox("Género*", ["Masculino", "Femenino", "Otro", "Prefiero no decirlo"])
                with col_datos4:
                    curp = st.text_input("CURP*", max_chars=30)
                with col_datos5:
                    nss = st.text_input("NSS*", max_chars=30, help="Numero de Seguro Social del paciente")
                    
                st.markdown('</div>', unsafe_allow_html=True)

            # SECCIÓN 2: DATOS DE DOMICILIO
            with st.container():
                st.markdown('<div class="form-section">', unsafe_allow_html=True)
                st.markdown('<div class="section-title"><span class="icon">🏠</span> Datos Domiciliarios</div>', unsafe_allow_html=True)
            
                estados_mexico = [
                "Aguascalientes", "Baja California", "Baja California Sur", "Campeche",
                "Chiapas", "Chihuahua", "Coahuila", "Colima", "Durango", "Guanajuato",
                "Guerrero", "Hidalgo", "Jalisco", "México", "Michoacán", "Morelos",
                "Nayarit", "Nuevo León", "Oaxaca", "Puebla", "Querétaro", "Quintana Roo",
                "San Luis Potosí", "Sinaloa", "Sonora", "Tabasco", "Tamaulipas", "Tlaxcala",
                "Veracruz", "Yucatán", "Zacatecas"
                ]
                
                col6, col7, col8, col9, col10 = st.columns([3, 2, 2, 2, 3])
                with col6:
                    direccion = st.text_input("Calle*", max_chars=100, help="Calle y Numero de la vivienda del paciente")
                with col7:
                    colonia = st.text_input("Colonia*", max_chars=50, help="Colonia de la vivienda del paciente")
                with col8:
                    codigo_postal = st.text_input("C.P *", max_chars=10, help="Codigo postal de la vivienda del paciente")
                with col9:
                    municipio = st.text_input("Municipio*", max_chars=50, help="Municipio en el que radica el paciente")
                with col10:
                    estado = st.selectbox("Estado*", estados_mexico, help="Estado donde radica el paciente")
                datos_referencia = st.text_area("Datos de referncia (opcional)", max_chars=100, help="Datos de referencias para ubicar el domicilio, ejempla escuela X")
                st.markdown('</div>', unsafe_allow_html=True)

            # SECCIÓN 3: DATOS DE CONTACTO
            with st.container():
                st.markdown('<div class="form-section">', unsafe_allow_html=True)
                st.markdown('<div class="section-title"><span class="icon">📱</span> Datos de Contacto</div>', unsafe_allow_html=True)
                
                nombre_contacto, parentesco, domicilio_contacto = st.columns([1, 1, 1.5])
                with nombre_contacto:
                    nombre_contacto = st.text_input("Nombre de la persona de contacto*", max_chars=50, help="Nombre Completo de la persona de contacto")
                with parentesco:
                    parentesco = st.text_input("Parentesco con el paciente*", max_chars=15)
                with domicilio_contacto:
                    domicilio_contacto = st.text_input("Domicilio del dato de contacto*", max_chars=100, help="Domicilio Completo del dato de contacto")
                
                col_tel1, col_tel2, correo = st.columns([1, 1, 1])
                with col_tel1:
                    telefono_contacto = st.text_input("Teléfono Fijo", max_chars=15)
                with col_tel2:
                    celular_contacto = st.text_input("Celular*", max_chars=15)
                with correo:
                    correo = st.text_input("Correo Electrónico",max_chars=30)
                st.markdown('</div>', unsafe_allow_html=True)

            # SECCIÓN 4: OBSERVACIONES
            with st.container():
                st.markdown('<div class="form-section">', unsafe_allow_html=True)
                st.markdown('<div class="section-title"><span class="icon">📝</span> Información Adicional</div>', unsafe_allow_html=True)
                
                observaciones = st.text_area("Observaciones", height=100, 
                                          help="Antecedentes médicos relevantes o notas importantes del paciente")
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<small>* Campos obligatorios</small>", unsafe_allow_html=True)
            
            agregar = st.form_submit_button("➕ Agregar Paciente", type="primary")

            if agregar:
                if any(not campo for campo in [apellido_paterno, nombres, edad, curp, nss, fecha_nacimiento, genero,
                        direccion, colonia, codigo_postal, municipio, estado, datos_referencia,
                        nombre_contacto, parentesco, domicilio_contacto,
                        telefono_contacto, celular_contacto]):
                    st.error("Por favor complete todos los campos obligatorios (*)")
                    time.sleep(3)
                else:
                    dni_repetido = any(paciente["CURP"] == curp for paciente in pacientes_lista)
                    if dni_repetido:
                        st.error("❌ Error: El DNI ya existe en la base de datos.")
                    else:
                        paciente = {
                            "ID Paciente": id_generado,
                            "Nombre Paciente": f"{apellido_paterno} {apellido_materno} {nombres}".strip(),
                            "Telefono Paciente": telefono,
                            "Edad": edad,
                            "Género": genero,
                            "CURP": curp,
                            "NSS": nss,
                            "Fecha Nacimiento": datetime.combine(fecha_nacimiento, datetime.min.time()),
                            "Direccion": direccion,
                            "Colonia": colonia,
                            "Codigo Postal": codigo_postal,
                            "Municipio": municipio,
                            "Estado": estado,
                            "Datos de Referencia": datos_referencia,
                            "Persona de Contacto": nombre_contacto,
                            "Parentesco": parentesco,
                            "Domicilio Persona de Contacto": domicilio_contacto,
                            "Telefono Persona de Contacto": telefono_contacto,
                            "Celular Persona de Contacto": celular_contacto,
                            "Correo de Contacto": correo,
                            "Observaciones": observaciones
                        }

                        if agregar_paciente(paciente):
                            st.success(f"✅ Paciente {nombres} {apellido_paterno} agregado correctamente.")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("❌ ID o CURP ya existen.")
                            time.sleep(2)
                    
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # Si no hay pacientes, usar un DataFrame vacío
    if not pacientes_lista:
        st.session_state.pacientes = pd.DataFrame()
    else:
        st.session_state.pacientes = pd.DataFrame(pacientes_lista)

    # --- Checkbox para mostrar la lista de pacientes ---
    ver_pacientes = st.checkbox("¿Desea ver la lista de pacientes?")
    if ver_pacientes:
        # Contenedor principal con estilo
        with st.container():
            st.markdown("""
            <style>
                .lista-pacientes-container {
                    margin-top: 20px;
                    padding: 15px 0;
                }
                
                .paciente-count {
                    color: #1a6fc4;
                    font-weight: bold;
                    margin-bottom: 15px;
                }
            </style>
            <div class="lista-pacientes-container">
            """, unsafe_allow_html=True)
            
            st.subheader("Lista de Pacientes")
            
            if st.session_state.pacientes.empty:
                st.warning("⚠️ No hay pacientes registrados aún.")
            else:
                # Mostrar conteo de pacientes
                num_pacientes = len(st.session_state.pacientes)
                st.markdown(f'<div class="paciente-count">Total de pacientes: {num_pacientes}</div>', unsafe_allow_html=True)
                
                # Ordenar los pacientes por ID
                pacientes_ordenados = st.session_state.pacientes.sort_values(by="ID Paciente", ascending=True)

                for _, paciente in pacientes_ordenados.iterrows():
                    def format_value(value):
                        if pd.isna(value) or value == "None" or value is None:
                            return "No especificado"
                        return value
        
                    fecha_nac = format_value(pd.to_datetime(paciente['Fecha Nacimiento']).strftime('%d/%m/%Y') 
                                if not pd.isna(paciente['Fecha Nacimiento']) else 'No especificado')
                    st.markdown(
                        f"""
                        <div style="
                            border: 2px solid #2e86c1;
                            border-radius: 10px;
                            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
                            padding: 15px;
                            margin-bottom: 10px;
                            background-color: white;
                            ">
                            <h3 style="color: #2e86c1; border-bottom: 1px solid #2e86c1; padding-bottom: 8px;">👤 {paciente['Nombre Paciente']} - ID: {paciente['ID Paciente']}</h3>
                            <!-- Sección 1: Datos Personales -->
                            <div style="margin-bottom: 15px;">
                                <h4 style="color: #2e86c1; margin-bottom: 5px;">📋 Datos Personales</h4>
                                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                                    <div><strong>Nacimiento:</strong> {fecha_nac}</div>
                                    <div><strong>Edad:</strong> {format_value(paciente['Edad'])} años</div>
                                    <div><strong>Género:</strong> {format_value(paciente['Género'])}</div>
                                    <div><strong>CURP:</strong> {format_value(paciente['CURP'])}</div>
                                    <div><strong>NSS:</strong> {format_value(paciente['NSS'])}</div>
                                    <div><strong>Teléfono:</strong> {format_value(paciente['Telefono Paciente'])}</div>
                                </div>
                            </div>
                            <!-- Sección 2: Datos Domiciliarios -->
                            <div style="margin-bottom: 15px;">
                                <h4 style="color: #2e86c1; margin-bottom: 5px;">🏠 Datos Domiciliarios</h4>
                                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                                    <div><strong>Dirección:</strong> {format_value(paciente['Direccion'])}</div>
                                    <div><strong>Código Postal:</strong> {format_value(paciente['Codigo Postal'])}</div>
                                    <div><strong>Colonia:</strong> {format_value(paciente['Colonia'])}</div>
                                    <div><strong>Municipio:</strong> {format_value(paciente['Municipio'])}</div>
                                    <div><strong>Estado:</strong> {format_value(paciente['Estado'])}</div>
                                    <div><strong>Referencias:</strong> {format_value(paciente['Datos de Referencia'])}</div>
                                </div>
                            </div>
                            <!-- Sección 3: Datos de Contacto -->
                            <div style="margin-bottom: 15px;">
                                <h4 style="color: #2e86c1; margin-bottom: 5px;">📱 Datos de Contacto</h4>
                                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                                    <div><strong>Contacto:</strong> {format_value(paciente['Persona de Contacto'])}</div>
                                    <div><strong>Parentesco:</strong> {format_value(paciente['Parentesco'])}</div>
                                    <div><strong>Domicilio Contacto:</strong> {format_value(paciente['Domicilio Persona de Contacto'])}</div>
                                    <div><strong>Teléfono:</strong> {format_value(paciente['Telefono Persona de Contacto'])}</div>
                                    <div><strong>Celular:</strong> {format_value(paciente['Celular Persona de Contacto'])}</div>
                                    <div><strong>Correo:</strong> {format_value(paciente['Correo de Contacto'])}</div>
                                </div>
                            </div>
                            <!-- Sección 4: Observaciones -->
                            <div>
                                <h4 style="color: #2e86c1; margin-bottom: 5px;">📝 Observaciones</h4>
                                <div style="background-color: #f5f5f5; padding: 10px; border-radius: 5px;">
                                    {format_value(paciente['Observaciones'])}
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        st.markdown("</div>", unsafe_allow_html=True)  # Cierre del contenedor principal

    # Checkbox para mostrar la opción de eliminar paciente
    eliminar_opcion = st.checkbox("¿Desea eliminar un paciente?")

    if eliminar_opcion:
        if not st.session_state.pacientes.empty:
            with st.form("eliminar_paciente"):
                st.write("Eliminar Paciente")

                pacientes_ordenados = st.session_state.pacientes.sort_values(by="ID Paciente", ascending=True)
                opciones_pacientes = [f"{row['ID Paciente']} - {row['Nombre Paciente']}" for _, row in pacientes_ordenados.iterrows()]
            
                paciente_eliminar = st.selectbox(
                    "Seleccionar Paciente a Eliminar",
                    options=opciones_pacientes
                )
                eliminar = st.form_submit_button("Eliminar Paciente")

                if eliminar:
                    id_eliminar = paciente_eliminar.split(" - ")[0]

                    if eliminar_paciente(id_eliminar):
                        st.success(f"Paciente {paciente_eliminar} eliminado correctamente.")
                        time.sleep(3)
                    else:
                        st.error("Error al eliminar el paciente.")

                    st.rerun()
        else:
            st.warning("⚠️ No hay pacientes registrados en el sistema.")