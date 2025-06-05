import streamlit as st
from conexion import obtener_ecgs_por_paciente, eliminar_ecg_analizado
import pandas as pd
import io
import time
from datetime import datetime
import base64

def mostrar_imagen_interactiva(imagen_bytes, expander_id):
    """
    Muestra la imagen con zoom y desplazamiento usando OpenSeadragon.
    """
    imagen_base64 = base64.b64encode(imagen_bytes).decode()

    html_code = f"""
    <div id="openseadragon_{expander_id}" style="width: 100%; height: 500px;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/openseadragon/2.4.2/openseadragon.min.js"></script>
    <script>
        var viewer = OpenSeadragon({{
            id: "openseadragon_{expander_id}",
            prefixUrl: "https://cdnjs.cloudflare.com/ajax/libs/openseadragon/2.4.2/images/",
            tileSources: {{
                type: "image",
                url: "data:image/png;base64,{imagen_base64}"
            }},
            showNavigator: true,
            animationTime: 0.3,
            zoomPerScroll: 1.5,
            minZoomLevel: 0.5,
            maxZoomLevel: 1.5,
            defaultZoomLevel: 0,
        }});
    </script>
    """
    
    st.components.v1.html(html_code, height=550)

def mostrar_detalles_picos(detalles_picos, diagnostico):
    """Función para mostrar detalles de picos con descripción diagnóstica en formato de tabla"""
    if not detalles_picos or detalles_picos == "No se detectaron picos anormales en este ECG.":
        st.info("🌟 ECG completamente normal - No se detectaron anomalías")
        return
    
    # Limpiar el título principal
    if detalles_picos.startswith("###"):
        detalles_picos = detalles_picos.replace("###", "").strip()

    # Eliminar específicamente el encabezado no deseado
    if "🔴 Detalles de Picos Anormales" in detalles_picos:
        detalles_picos = detalles_picos.replace("🔴 Detalles de Picos Anormales", "").strip()
    elif "Detalles de Picos Anormales" in detalles_picos:
        detalles_picos = detalles_picos.replace("Detalles de Picos Anormales", "").strip()
    
    # Mostrar descripción diagnóstica
    if "Hipertrofia ventricular" in diagnostico:
        st.markdown("""
        <div style='background-color: #f0f7ff; padding: 15px; border-radius: 10px; border-left: 4px solid #2b5876; margin-bottom: 20px;'>
            <h4 style='color: #2b5876; margin-top: 0;'>🩺 Análisis Diagnóstico</h4>
            <p style='color: #4a4a4a;'>La <strong style='color: #2b5876;'>hipertrofia ventricular</strong> fue diagnosticada debido a los valores anormales del pico QRS 
            en múltiples derivaciones, consistentes con un aumento del voltaje eléctrico característico 
            de esta condición, las siguientes derivaciones tuvo ese aumento:</p>
        </div>
        """, unsafe_allow_html=True)
    elif "Arritmia cardiaca" in diagnostico:
        st.markdown("""
        <div style='background-color: #f0f7ff; padding: 15px; border-radius: 10px; border-left: 4px solid #4caf50; margin-bottom: 20px;'>
            <h4 style='color: #2e7d32; margin-top: 0;'>🩺 Análisis Diagnóstico</h4>
            <p style='color: #4a4a4a;'>La <strong style='color: #2b5876;>arritmia cardiaca</strong> fue identificada por anomalías en el pico P en varias derivaciones, 
            indicando irregularidades en la despolarización auricular.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Dividir por picos anormales
    secciones = [s for s in detalles_picos.split('🔴') if s.strip()]
    
    for seccion in secciones:
        lineas = [l.strip() for l in seccion.split('\n') if l.strip()]
        if not lineas:
            continue
            
        # Encabezado del pico
        header = lineas[0]
        with st.container():
            st.markdown(f"""
            <div style='background-color: #f5f5f5; padding: 10px; border-radius: 5px; margin: 10px 0 20px 0;'>
                <h4 style='color: #d32f2f; margin: 0;'>🔴 {header}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Preparar datos para la tabla
            tabla_data = []
            for i in range(1, len(lineas), 4):
                if i+3 >= len(lineas):
                    break
                    
                derivacion = lineas[i].replace("**", "").replace(":", "").strip()
                valor_str = lineas[i+1].split("`")[1]
                valor = float(valor_str.split()[0])
                rango = lineas[i+2].split("`")[1]
                rango_min = float(rango.split('-')[0])
                rango_max = float(rango.split('-')[1].split()[0])
                desviacion = lineas[i+3].split("`")[1]
                
                # Determinar dirección y color
                if valor > rango_max:
                    direccion = "↑"  # Valor por encima del rango máximo
                    color = "color: #d32f2f;"  # Rojo
                elif valor < rango_min:
                    direccion = "↓"  # Valor por debajo del rango mínimo
                    color = "color: #1976d2;"  # Azul
                else:
                    direccion = ""   # No debería ocurrir para valores anormales
                    color = ""
                
                tabla_data.append({
                    "Derivación": derivacion,
                    "Valor Extraido": f"{valor:.3f} mV",
                    "Rango Normal": rango,
                    "Diferencia": f"{desviacion} {direccion}",
                    "_style": color
                })
            # Nueva implementación de estilo de tabla
            df = pd.DataFrame(
                tabla_data,
                columns=["Derivación", "Valor Extraido", "Rango Normal", "Diferencia"]
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
                        styles.loc[idx, 'Valor Extraido'] = 'background-color: #f0f8ff;'
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
                
            """
                # Mostrar la tabla con estilo
                st.table(
                    pd.DataFrame(
                        tabla_data,
                        columns=["Derivación", "Valor Obtenido", "Rango Normal", "Diferencia"]
                    ).style.set_properties(**{
                        'background-color': '#f8f9fa',
                        'border': '1px solid #dee2e6',
                        'color': '#212529'
                    })
                )"""

def historial_medico(pacientes_ordenados):
    st.header("📋 Historial Médico Completo")
    st.divider()

    # Estilos CSS personalizados
    st.markdown("""
    <style>
        .historial-header {
            color: #2b5876;
            border-bottom: 2px solid #4b79a1;
            padding-bottom: 5px;
        }
        .anomalia-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .derivacion-item {
            background-color: #ffffff;
            border-left: 4px solid #4b79a1;
            padding: 10px;
            margin: 8px 0;
            border-radius: 0 8px 8px 0;
        }
        .fecha-text {
            color: #5a5a5a;
            font-weight: bold;
        }
        .delete-btn {
            background-color: #ff6b6b !important;
            color: white !important;
            border-radius: 50% !important;
            width: 30px !important;
            height: 30px !important;
            padding: 0 !important;
        }
        .delete-btn:hover {
            background-color: #ff5252 !important;
        }
        .ecg-expander {
            background-color: #e9f5ff !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Selección de paciente
    id_historial = st.selectbox(
        "👨‍⚕️ Seleccionar Paciente", 
        pacientes_ordenados["Nombre Paciente"],
        key="historial_select_paciente"
    )

    if id_historial:
        id_paciente = pacientes_ordenados[pacientes_ordenados["Nombre Paciente"] == id_historial]["ID Paciente"].values[0]
        ecgs_analizados = obtener_ecgs_por_paciente(id_paciente)
        ecgs_analizados = list(ecgs_analizados)

        if ecgs_analizados:
            st.subheader(f"📊 ECG Analizados de {id_historial}", divider="blue")

            # Ordenar ECG por fecha (más reciente primero)
            ecgs_analizados.sort(key=lambda x: x['fecha_analisis'], reverse=True)

            for idx, ecg in enumerate(ecgs_analizados):
                # Formatear fecha
                fecha_formateada = (
                    ecg['fecha_analisis'].strftime("%Y-%m-%d %H:%M:%S")
                    if isinstance(ecg['fecha_analisis'], datetime)
                    else datetime.fromisoformat(ecg['fecha_analisis']).strftime("%Y-%m-%d %H:%M:%S")
                    if isinstance(ecg['fecha_analisis'], str)
                    else "Fecha no disponible"
                )

                # Tarjeta principal
                with st.container():
                    col1, col2, col3 = st.columns([3, 5, 1])
                    
                    with col1:
                        st.markdown(f"<p class='fecha-text'>🗓 {fecha_formateada}</p>", unsafe_allow_html=True)
                    
                    with col2:
                        # Mostrar diagnóstico principal con estilo
                        if "Sin Anomalías" in ecg['anomalias'] or "Normal" in ecg['anomalias']:
                            st.success(f"✅ {ecg['anomalias']}")
                        else:
                            st.warning(f"{ecg['anomalias']}")
                    
                    with col3:
                        # Botón de eliminar con estilo
                        if st.button("🗑", 
                                   key=f"eliminar_{idx}", 
                                   help="Eliminar este ECG",
                                   use_container_width=True,
                                   on_click=lambda: st.session_state.update({'to_delete': ecg['_id']})):
                            pass

                    # Expander para la imagen ECG
                    with st.expander("🖼️ Ver ECG", expanded=False):
                        mostrar_imagen_interactiva(io.BytesIO(ecg['imagen_ecg']).getvalue(), idx)

                    # Expander para detalles de picos
                    with st.expander("📈 Analisis Detallado", expanded=False):
                        detalles_picos = ecg['detalles_picos_del_ECG']
                        
                        mostrar_detalles_picos(detalles_picos, ecg['anomalias'])

                # Manejar eliminación después de renderizar todo
                if 'to_delete' in st.session_state:
                    if eliminar_ecg_analizado(st.session_state.to_delete):
                        st.success("Registro eliminado correctamente")
                        time.sleep(1)
                        st.rerun()
                    del st.session_state['to_delete']

        else:
            st.warning(f"⚠️ El paciente {id_historial} no tiene análisis ECG registrados.")
            st.image("https://cdn-icons-png.flaticon.com/512/4076/4076478.png", width=150)

    else:
        st.info("👈 Por favor, selecciona un paciente para ver su historial médico.")