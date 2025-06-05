import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from conexion import obtener_ecgs_por_paciente
from datetime import datetime
import numpy as np

def evolucion_cardiaca(pacientes_ordenados):
    st.header("📈 Evolución Cardíaca del Paciente")
    st.markdown("""
    <style>
        .evolucion-header {
            color: #2b5876;
            border-bottom: 2px solid #4b79a1;
            padding-bottom: 5px;
        }
        .metric-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border-left: 4px solid #4b79a1;
        }
        .plot-container {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .data-table {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .anomaly-count {
            background-color: #fff8e1;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            border-left: 4px solid #ffc107;
        }
        .highlight {
            background-color: #ffeb3b !important;
            font-weight: bold;
        }
        .viz-card {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid #e0e0e0;
        }
        .viz-header {
            color: #2c3e50;
            border-bottom: 1px solid #ecf0f1;
            padding-bottom: 8px;
            margin-bottom: 15px;
            font-size: 1.1em;
        }
        .viz-tooltip {
            background-color: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid #bdc3c7 !important;
            border-radius: 5px !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='metric-card'>
        <h3 class='evolucion-header'>Análisis de Evolución Temporal</h3>
        <p>Se visualiza cómo han evolucionado los parámetros cardíacos del paciente a lo largo del tiempo, 
        comparando múltiples análisis de ECG.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Selección de paciente
    paciente_seleccionado = st.selectbox(
        "👨‍⚕️ Seleccionar Paciente", 
        pacientes_ordenados["Nombre Paciente"],
        key="evolucion_select_paciente"
    )

    if paciente_seleccionado:
        id_paciente = pacientes_ordenados[pacientes_ordenados["Nombre Paciente"] == paciente_seleccionado]["ID Paciente"].values[0]
        ecgs_analizados = obtener_ecgs_por_paciente(id_paciente)
        ecgs_analizados = list(ecgs_analizados)

        if len(ecgs_analizados) >= 2:
            # Procesamiento de datos para gráficos
            datos_evolucion, pico_principal = procesar_datos_evolucion(ecgs_analizados)
            
            # Mostrar información sobre el pico principal
            st.markdown(f"""
            <div class='metric-card'>
                <h4>🔍 Pico Principal</h4>
                <p>El análisis se centra en el <strong>{pico_principal}</strong> ya que presenta la mayor cantidad de anomalías 
                a lo largo de los registros ECG del paciente.</p>
            </div>
            """, unsafe_allow_html=True)

             # Mostrar métricas resumen
            mostrar_metricas_resumen(datos_evolucion, pico_principal)
            
            # Mostrar tabla completa de datos
            mostrar_tabla_datos(datos_evolucion)
            
            # Mostrar gráficos de evolución
            mostrar_graficos_evolucion(datos_evolucion, pico_principal)
            
            # Análisis de tendencias
            mostrar_analisis_tendencias(datos_evolucion, pico_principal)
            
            # Sección de gráficos mejorados
            with st.expander("📊 Visualización Avanzada de Datos", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    agregar_grafico_radar(datos_evolucion, pico_principal)
                
                agregar_grafico_calor(datos_evolucion, pico_principal)
                agregar_grafico_anomalias_apiladas(ecgs_analizados)
            
        else:
            st.warning(f"⚠️ Se necesitan al menos 2 análisis ECG para mostrar la evolución. El paciente {paciente_seleccionado} tiene {len(ecgs_analizados)} análisis.")
            st.info("Realiza más análisis ECG para este paciente para habilitar las funciones de evolución.")

# ==============================================
# FUNCIONES PARA LOS NUEVOS GRÁFICOS MEJORADOS
# ==============================================

def agregar_grafico_radar(df, pico_principal):
    """Muestra un gráfico de radar comparando el primer y último registro"""
    st.markdown("<div class='viz-card'>", unsafe_allow_html=True)
    st.markdown("<h4 class='viz-header'>🔵 Comparación Radial de Parámetros</h4>", unsafe_allow_html=True)
    
    # Seleccionar parámetros relevantes
    parametros = ['P_avg', 'QRS_avg', 'T_avg', 'PR_avg', 'QT_avg']
    parametros = [p for p in parametros if p in df.columns and not df[p].isnull().all()]
    
    if len(parametros) >= 3:  # Mínimo 3 parámetros para radar
        # Normalizar datos para comparación (0-1)
        df_norm = df[parametros].apply(lambda x: (x - x.min()) / (x.max() - x.min()), axis=0)
        
        fig = go.Figure()
        
        # Agregar primer registro
        fig.add_trace(go.Scatterpolar(
            r=df_norm.iloc[0].values,
            theta=[p.split('_')[0] for p in parametros],
            fill='toself',
            name=f"Inicio ({df['Fecha'].iloc[0].strftime('%Y-%m-%d')}",
            line_color='#3498db',
            opacity=0.8
        ))
        
        # Agregar último registro
        fig.add_trace(go.Scatterpolar(
            r=df_norm.iloc[-1].values,
            theta=[p.split('_')[0] for p in parametros],
            fill='toself',
            name=f"Actual ({df['Fecha'].iloc[-1].strftime('%Y-%m-%d')}",
            line_color='#e74c3c',
            opacity=0.8
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            height=500,
            margin=dict(l=50, r=50, b=50, t=50),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Se necesitan al menos 3 parámetros válidos para generar el gráfico de radar")
    
    st.markdown("</div>", unsafe_allow_html=True)

def agregar_grafico_calor(df, pico_principal):
    """Muestra un heatmap de cambios en los parámetros"""
    st.markdown("<div class='viz-card'>", unsafe_allow_html=True)
    st.markdown("<h4 class='viz-header'>🔥 Mapa de Calor de Evolución</h4>", unsafe_allow_html=True)
    
    # Seleccionar columnas numéricas relevantes para el pico principal
    pico_key = pico_principal.split()[0].upper()
    numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns 
                   if pico_key in col and not df[col].isnull().all()]
    
    # Si no hay suficientes columnas específicas, usar todas las numéricas
    if len(numeric_cols) < 3:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) > 0:
        # Calcular cambios porcentuales entre registros consecutivos
        cambios = df[numeric_cols].pct_change() * 100
        
        # Agregar fecha como índice y eliminar primera fila (siempre NaN)
        cambios['Fecha'] = df['Fecha'].dt.strftime('%m-%Y')
        cambios = cambios.set_index('Fecha').iloc[1:]  # Eliminar primera fila en lugar de dropna()
        
        if len(cambios) >= 1:  # Cambiado a >=1 en lugar de >1
            # Configurar nombres legibles
            nombres_columnas = {
                col: col.replace('_avg', ' (Prom)').replace('_min', ' (Mín)').replace('_max', ' (Máx)')
                for col in cambios.columns
            }
            
            # Crear el heatmap
            fig = px.imshow(cambios.rename(columns=nombres_columnas),
                            labels=dict(x="Fecha", y="Parámetro", color="Cambio %"),
                            color_continuous_scale='RdBu',
                            color_continuous_midpoint=0,
                            aspect="auto",
                            title=f"Cambios en {pico_principal}")
            
            fig.update_layout(
                xaxis_nticks=min(10, len(cambios)),
                height=400 + len(cambios.columns)*20,
                margin=dict(l=100, r=20, b=50, t=80),  # Aumentado espacio superior para título
                coloraxis_colorbar=dict(
                    title="Cambio %",
                    thicknessmode="pixels",
                    thickness=15,
                    lenmode="pixels",
                    len=300,
                    yanchor="top",
                    y=1,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Se necesitan al menos 2 mediciones para mostrar cambios porcentuales. Actualmente hay datos de 1 medición.")
    else:
        st.warning("No hay suficientes datos numéricos para generar el mapa de calor")
    
    st.markdown("</div>", unsafe_allow_html=True)

def agregar_grafico_anomalias_apiladas(ecgs_analizados):
    """Muestra anomalías por tipo como área apilada"""
    st.markdown("<div class='viz-card'>", unsafe_allow_html=True)
    st.markdown("<h4 class='viz-header'>📈 Evolución de Anomalías por Tipo</h4>", unsafe_allow_html=True)
    
    # Procesar datos para contar anomalías por fecha
    datos_anomalias = []
    for ecg in ecgs_analizados:
        fecha = ecg['fecha_analisis']
        _, anomalias = extraer_valores_picos(ecg['detalles_picos_del_ECG'])
        anomalias['Fecha'] = fecha
        datos_anomalias.append(anomalias)
    
    df_anomalias = pd.DataFrame(datos_anomalias)
    df_anomalias['Fecha'] = pd.to_datetime(df_anomalias['Fecha'])
    df_anomalias = df_anomalias.sort_values('Fecha')
    
    # Configurar nombres legibles
    nombres = {
        'P': 'Onda P',
        'QRS': 'Complejo QRS',
        'T': 'Onda T',
        'PR': 'Intervalo PR',
        'QT': 'Intervalo QT'
    }
    
    # Filtrar columnas con datos
    columnas_validas = [col for col in nombres.keys() if col in df_anomalias.columns and df_anomalias[col].sum() > 0]
    
    if len(columnas_validas) > 0:
        fig = px.area(df_anomalias.set_index('Fecha')[columnas_validas].rename(columns=nombres),
                     title="",
                     labels={'value': 'Número de Anomalías', 'variable': 'Tipo de Anomalía'},
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        
        fig.update_layout(
            hovermode="x unified",
            legend_title="Tipo de Anomalía",
            height=400,
            margin=dict(l=50, r=50, b=50, t=50),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No se detectaron anomalías en los registros analizados")
    
    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================
# FUNCIONES ORIGINALES (MANTENIDAS)
# ==============================================

def contar_anomalias_por_pico(ecgs_analizados):
    """Cuenta las anomalías por tipo de pico en todos los ECG analizados de manera precisa"""
    contador_anomalias = {
        'P': 0,      # Anomalías en onda P
        'QRS': 0,    # Anomalías en complejo QRS
        'T': 0,      # Anomalías en onda T
        'U': 0,      # Anomalías en onda U
        'PR': 0,     # Anomalías en intervalo PR
        'QT': 0      # Anomalías en intervalo QT
    }
    
    for ecg in ecgs_analizados:
        detalles_picos = ecg.get('detalles_picos_del_ECG', '')
        
        if not detalles_picos or "No se detectaron" in detalles_picos:
            continue
        
        # Dividir por secciones de picos anormales
        secciones = [s.strip() for s in detalles_picos.split('🔴') if s.strip()]
        
        for seccion in secciones:
            lineas = [l.strip() for l in seccion.split('\n') if l.strip()]
            if not lineas:
                continue
                
            # Determinar tipo de pico exacto
            header = lineas[0].lower()
            pico_key = None
            
            # Detección exacta del tipo de pico
            if 'pico qrs' in header or 'complejo qrs' in header:
                pico_key = 'QRS'
            elif ('pico p' in header or 'onda p' in header) and 'intervalo pr' not in header:
                pico_key = 'P'
            elif 'pico t' in header or 'onda t' in header:
                pico_key = 'T'
            elif 'pico u' in header or 'onda u' in header:
                pico_key = 'U'
            elif 'intervalo pr' in header:
                pico_key = 'PR'
            elif 'intervalo qt' in header:
                pico_key = 'QT'
            
            # Solo contar si identificamos claramente el tipo de pico
            if pico_key:
                # Contar cada derivación con anomalía (cada 4 líneas = 1 derivación)
                num_anomalias = 0
                for i in range(1, len(lineas), 4):
                    if i + 3 < len(lineas):
                        # La línea de diferencia (i+3) contiene ↑ o ↓ si hay anomalía
                        diferencia_linea = lineas[i+3]
                        if '↑' in diferencia_linea or '↓' in diferencia_linea:
                            num_anomalias += 1
                
                contador_anomalias[pico_key] += num_anomalias
    
    return contador_anomalias

def procesar_datos_evolucion(ecgs_analizados):
    # Ordenar ECG por fecha
    ecgs_analizados.sort(key=lambda x: x['fecha_analisis'] if isinstance(x['fecha_analisis'], datetime) 
                         else datetime.fromisoformat(x['fecha_analisis']))
    
    # Contar anomalías en TODOS los ECG de manera precisa
    contador_anomalias = contar_anomalias_por_pico(ecgs_analizados)
    
    # Mostrar conteo de anomalías con verificación
    st.markdown("<div class='anomaly-count'>", unsafe_allow_html=True)
    st.write("### Conteo Exacto de Anomalías por Pico")
    
    # Crear DataFrame ordenado descendente
    anomaly_df = pd.DataFrame.from_dict(contador_anomalias, orient='index', columns=['Anomalías'])
    anomaly_df = anomaly_df.sort_values('Anomalías', ascending=False)
    
    # Función para resaltar el máximo
    def highlight_max(s):
        return ['background-color: #ffeb3b' if v == s.max() else '' for v in s]
    
    # Mostrar tabla con el pico principal resaltado
    st.dataframe(
        anomaly_df.style.apply(highlight_max).background_gradient(cmap='YlOrBr'),
        use_container_width=True
    )
    
    # Verificación adicional
    max_pico = anomaly_df.idxmax()[0]
    max_anomalias = anomaly_df.max()[0]
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Mapeo a nombres legibles
    nombres_picos = {
        'P': 'Onda P',
        'QRS': 'Complejo QRS',
        'T': 'Onda T',
        'U': 'Onda U',
        'PR': 'Intervalo PR',
        'QT': 'Intervalo QT'
    }
    
    # Procesar datos para cada ECG
    datos = []
    for ecg in ecgs_analizados:
        fecha = (ecg['fecha_analisis'] if isinstance(ecg['fecha_analisis'], datetime) 
                else datetime.fromisoformat(ecg['fecha_analisis']))
        diagnostico = ecg['anomalias']
        detalles_picos = ecg['detalles_picos_del_ECG']
        valores_picos, _ = extraer_valores_picos(detalles_picos)
        
        datos.append({
            'Fecha': fecha,
            'Diagnóstico': diagnostico,
            **valores_picos
        })
    
    return pd.DataFrame(datos), nombres_picos.get(max_pico, 'Complejo QRS')

def extraer_valores_picos(detalles_picos):
    valores = {
        'P_avg': np.nan, 'P_min': np.nan, 'P_max': np.nan,
        'QRS_avg': np.nan, 'QRS_min': np.nan, 'QRS_max': np.nan,
        'T_avg': np.nan, 'T_min': np.nan, 'T_max': np.nan,
        'U_avg': np.nan, 'U_min': np.nan, 'U_max': np.nan,
        'PR_avg': np.nan, 'PR_min': np.nan, 'PR_max': np.nan,
        'QT_avg': np.nan, 'QT_min': np.nan, 'QT_max': np.nan
    }
    
    anomalias_pico = {'P': 0, 'QRS': 0, 'T': 0, 'U': 0, 'PR': 0, 'QT': 0}
    
    if not detalles_picos or "No se detectaron" in detalles_picos:
        return valores, anomalias_pico
    
    try:
        secciones = [s.strip() for s in detalles_picos.split('🔴') if s.strip()]
        
        for seccion in secciones:
            lineas = [l.strip() for l in seccion.split('\n') if l.strip()]
            if not lineas:
                continue
                
            tipo_pico = lineas[0].lower()
            pico_key = None
            
            if 'pico qrs' in tipo_pico or 'complejo qrs' in tipo_pico:
                pico_key = 'QRS'
            elif ('pico p' in tipo_pico or 'onda p' in tipo_pico) and 'intervalo pr' not in tipo_pico:
                pico_key = 'P'
            elif 'pico t' in tipo_pico or 'onda t' in tipo_pico:
                pico_key = 'T'
            elif 'pico u' in tipo_pico or 'onda u' in tipo_pico:
                pico_key = 'U'
            elif 'intervalo pr' in tipo_pico:
                pico_key = 'PR'
            elif 'intervalo qt' in tipo_pico:
                pico_key = 'QT'
            
            valores_pico = []
            for i in range(1, len(lineas), 4):
                if i + 3 >= len(lineas):
                    break
                
                try:
                    valor_str = lineas[i + 1].split("`")[1].split()[0]
                    valor = float(valor_str)
                    valores_pico.append(valor)
                    
                    # Contar anomalías
                    if '↑' in lineas[i + 3] or '↓' in lineas[i + 3]:
                        if pico_key in anomalias_pico:
                            anomalias_pico[pico_key] += 1
                except:
                    continue
            
            if pico_key and valores_pico:
                avg_key = f"{pico_key}_avg"
                min_key = f"{pico_key}_min"
                max_key = f"{pico_key}_max"
                
                valores[avg_key] = np.mean(valores_pico)
                valores[min_key] = min(valores_pico)
                valores[max_key] = max(valores_pico)
                
    except Exception as e:
        st.error(f"Error al extraer valores: {str(e)}")
    
    return valores, anomalias_pico

def mostrar_metricas_resumen(df, pico_principal):
    st.subheader("📊 Métricas Clave de Evolución", divider="blue")
    
    # Determinar las métricas a mostrar basadas en el pico principal
    if "QRS" in pico_principal:
        metric_cols = ['QRS_avg', 'QRS_min', 'QRS_max']
        unidad = 'mV'
    elif "P" in pico_principal and "PR" not in pico_principal:
        metric_cols = ['P_avg', 'P_min', 'P_max']
        unidad = 'mV'
    elif "T" in pico_principal:
        metric_cols = ['T_avg', 'T_min', 'T_max']
        unidad = 'mV'
    elif "PR" in pico_principal:
        metric_cols = ['PR_avg']
        unidad = 'ms'
    elif "QT" in pico_principal:
        metric_cols = ['QT_avg']
        unidad = 'ms'
    else:
        metric_cols = ['QRS_avg']
        unidad = 'mV'
    
    # Filtrar columnas existentes
    metric_cols = [col for col in metric_cols if col in df.columns and not df[col].isnull().all()]
    
    # Crear columnas dinámicamente
    cols = st.columns([1, 1, 1, 2, 1])  # Métricas + Diagnóstico + Total ECG
    
    # Mostrar métricas del pico principal
    for i, col_name in enumerate(metric_cols):
        with cols[i]:
            current_val = df[col_name].iloc[-1]
            initial_val = df[col_name].iloc[0]
            delta_val = current_val - initial_val
            
            # Formatear valores para mostrar
            current_fmt = f"{current_val:.2f} {unidad}"
            delta_fmt = f"{delta_val:+.2f} {unidad}"
            
            # Determinar color del delta
            delta_color = "normal"
            if "avg" in col_name:
                if abs(delta_val) > 0.5:
                    delta_color = "inverse" if delta_val < 0 else "normal"
            
            st.metric(
                label=f"{col_name.split('_')[0]} {col_name.split('_')[1]}",
                value=current_fmt,
                delta=delta_fmt,
                delta_color=delta_color
            )
    
    # Mostrar diagnóstico actual
    with cols[-2]:
        ultimo_dx = df['Diagnóstico'].iloc[-1]
        if " - " in ultimo_dx:
            dx_principal = ultimo_dx.split(" - ")[1]
            icono = "⚠️" if "⚠️" in ultimo_dx else "✅"
            st.metric("Diagnóstico Actual", f"{icono} {dx_principal}")
        else:
            icono = "✅" if "Normal" in ultimo_dx else "⚠️"
            st.metric("Diagnóstico Actual", f"{icono} {ultimo_dx}")
    
    # Mostrar total de ECG
    with cols[-1]:
        num_ecgs = len(df)
        st.metric("Total ECG Analizados", num_ecgs)

def mostrar_tabla_datos(df):
    st.subheader("📋 Datos Completo de Evolución", divider="blue")
    
    # Crear copia para no modificar el original
    df_display = df.copy()
    
    # Formatear fecha para mejor visualización
    df_display['Fecha'] = df_display['Fecha'].dt.strftime('%Y-%m-%d %H:%M')
    
    # Seleccionar columnas relevantes para mostrar
    columns_to_show = ['Fecha', 'Diagnóstico']
    for col in df.columns:
        if col not in ['Fecha', 'Diagnóstico'] and not pd.isna(df[col]).all():
            columns_to_show.append(col)
    
    # Función para aplicar estilo condicional
    def style_table(row):
        styles = [''] * len(row)
        
        # Resaltar diagnósticos anormales
        if "⚠️" in str(row['Diagnóstico']) or "Anomalía" in str(row['Diagnóstico']):
            styles[columns_to_show.index('Diagnóstico')] = 'background-color: #ffebee;'
        
        # Resaltar valores extremos en QRS
        if 'QRS_avg' in columns_to_show and not pd.isna(row['QRS_avg']):
            qrs_idx = columns_to_show.index('QRS_avg')
            if row['QRS_avg'] > 2.5:  # Valor alto
                styles[qrs_idx] = 'background-color: #ffebee; color: #c62828;'
            elif row['QRS_avg'] < 0.5:  # Valor bajo
                styles[qrs_idx] = 'background-color: #e3f2fd; color: #1565c0;'
        
        return styles
    
    # Aplicar estilo a la tabla
    styled_df = df_display[columns_to_show].style.apply(
        style_table, axis=1
    ).format(
        na_rep="N/A", 
        precision=2,
        subset=[col for col in columns_to_show if col not in ['Fecha', 'Diagnóstico']]
    ).set_properties(**{
        'text-align': 'center',
        'font-size': '0.9em',
        'border': '1px solid #dee2e6'
    }).set_table_styles([
        {'selector': 'th', 'props': [
            ('background-color', '#2c3e50'),
            ('color', 'white'),
            ('font-weight', 'bold'),
            ('text-align', 'center')
        ]},
        {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f8f9fa')]},
        {'selector': 'tr:hover', 'props': [('background-color', '#e8f4f8')]}
    ])
    
    st.markdown("<div class='data-table'>", unsafe_allow_html=True)
    st.dataframe(styled_df, use_container_width=True, height=400)
    st.markdown("</div>", unsafe_allow_html=True)

def mostrar_graficos_evolucion(df, pico_principal):
    st.subheader("📈 Gráficos de Evolución Temporal", divider="blue")
    
    # Gráfico 1: Evolución del pico principal
    with st.container():
        st.markdown("<div class='plot-container'>", unsafe_allow_html=True)
        
        # Determinar qué métricas mostrar según el pico principal
        if "QRS" in pico_principal:
            y_cols = ['QRS_max', 'QRS_avg', 'QRS_min']
            title = f'Evolución del {pico_principal}'
            y_title = "Voltaje (mV)"
        elif "P" in pico_principal and "PR" not in pico_principal:
            y_cols = ['P_max', 'P_avg', 'P_min']
            title = f'Evolución del {pico_principal}'
            y_title = "Voltaje (mV)"
        elif "T" in pico_principal:
            y_cols = ['T_max', 'T_avg', 'T_min']
            title = f'Evolución del {pico_principal}'
            y_title = "Voltaje (mV)"
        elif "PR" in pico_principal:
            y_cols = ['PR_avg']
            title = f'Evolución del {pico_principal}'
            y_title = "Duración (ms)"
        elif "QT" in pico_principal:
            y_cols = ['QT_avg']
            title = f'Evolución del {pico_principal}'
            y_title = "Duración (ms)"
        else:
            y_cols = ['QRS_avg']
            title = 'Evolución del Parámetro Principal'
            y_title = "Valor"
        
        # Filtrar columnas que existen y tienen datos
        y_cols = [col for col in y_cols if col in df.columns and not df[col].isnull().all()]
        
        if y_cols:
            fig = px.line(df, x='Fecha', y=y_cols,
                         title=title,
                         labels={'value': y_title},
                         markers=True)
            
            # Personalizar hover data
            fig.update_traces(
                hovertemplate="<b>Fecha:</b> %{x|%Y-%m-%d}<br><b>Valor:</b> %{y:.2f}<extra></extra>"
            )
            
            fig.update_layout(
                xaxis_title="Fecha de Análisis",
                hovermode="x unified",
                legend_title="Métricas"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Gráfico 2: Histograma de diagnósticos - SOLO SI HAY MÁS DE UN DIAGNÓSTICO
    with st.container():
        # Simplificar diagnóstico para visualización
        df_dx = df.copy()
        df_dx['Diagnóstico Simple'] = df_dx['Diagnóstico'].apply(
            lambda x: x.split(" - ")[1] if " - " in x else x
        )
        
        # Verificar si hay más de un diagnóstico único
        diagnosticos_unicos = df_dx['Diagnóstico Simple'].unique()
        
        if len(diagnosticos_unicos) > 1:
            st.markdown("<div class='plot-container'>", unsafe_allow_html=True)
            
            # Contar frecuencias de diagnóstico
            dx_counts = df_dx['Diagnóstico Simple'].value_counts().reset_index()
            dx_counts.columns = ['Diagnóstico', 'Cantidad']
            
            fig = px.bar(dx_counts, 
                        x='Diagnóstico', 
                        y='Cantidad',
                        title='Distribución de Diagnósticos',
                        color='Diagnóstico',
                        text='Cantidad')
            
            fig.update_layout(
                showlegend=False,
                xaxis_title="Diagnóstico",
                yaxis_title="Número de ECG"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Gráfico 3: Evolución temporal de diagnósticos - SOLO SI HAY MÁS DE UN DIAGNÓSTICO
    with st.container():
        if len(diagnosticos_unicos) > 1:
            st.markdown("<div class='plot-container'>", unsafe_allow_html=True)
            
            # Crear variable numérica para el eje Y (solo para visualización)
            df_dx['Orden'] = range(len(df_dx))
            
            fig = px.scatter(df_dx, 
                            x='Fecha', 
                            y='Orden',
                            color='Diagnóstico Simple',
                            title='Línea de Tiempo de Diagnósticos',
                            hover_name='Diagnóstico Simple',
                            labels={'Orden': ''})
            
            fig.update_layout(
                showlegend=True,
                xaxis_title="Fecha de Análisis",
                yaxis={'visible': False, 'showticklabels': False},
                hovermode="closest"
            )
            
            # Conectar puntos en orden cronológico
            for dx in df_dx['Diagnóstico Simple'].unique():
                dx_df = df_dx[df_dx['Diagnóstico Simple'] == dx]
                if len(dx_df) > 1:
                    fig.add_trace(px.line(dx_df, x='Fecha', y='Orden', color_discrete_sequence=[px.colors.qualitative.Plotly[0]]).data[0])
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

def mostrar_analisis_tendencias(df, pico_principal):
    st.subheader("🔍 Análisis de Tendencias", divider="blue")
    
    # Determinar la columna a analizar según el pico principal
    if "QRS" in pico_principal:
        col_analisis = 'QRS_avg'
        nombre_parametro = "voltaje QRS"
        unidad = "mV"
        umbral = 0.5  # mV de cambio significativo por año
    elif "P" in pico_principal and "PR" not in pico_principal:
        col_analisis = 'P_avg'
        nombre_parametro = "voltaje de la onda P"
        unidad = "mV"
        umbral = 0.1  # mV de cambio significativo por año
    elif "T" in pico_principal:
        col_analisis = 'T_avg'
        nombre_parametro = "voltaje de la onda T"
        unidad = "mV"
        umbral = 0.2  # mV de cambio significativo por año
    elif "PR" in pico_principal:
        col_analisis = 'PR_avg'
        nombre_parametro = "intervalo PR"
        unidad = "ms"
        umbral = 20   # ms de cambio significativo por año
    elif "QT" in pico_principal:
        col_analisis = 'QT_avg'
        nombre_parametro = "intervalo QT"
        unidad = "ms"
        umbral = 30   # ms de cambio significativo por año
    else:
        col_analisis = 'QRS_avg'
        nombre_parametro = "parámetro principal"
        unidad = ""
        umbral = 0.5
    
    # Verificar que tenemos datos para analizar
    if col_analisis not in df.columns or df[col_analisis].isnull().all():
        st.warning(f"No hay datos suficientes para analizar la tendencia del {pico_principal}")
        return
    
    # Calcular tendencias (regresión lineal simple)
    try:
        dates_num = pd.to_numeric(pd.to_datetime(df['Fecha'])) / 10**9
        valores = df[col_analisis].values
        
        if len(dates_num) > 1 and not any(np.isnan(valores)):
            coeff = np.polyfit(dates_num, valores, 1)
            slope = coeff[0] * (3600*24*365)  # Convertir a cambio por año
            
            # Determinar el mensaje según la pendiente
            if abs(slope) > umbral:
                if slope > 0:
                    st.warning(f"⚠️ Tendencia significativamente ascendente en {nombre_parametro}")
                    st.markdown(f"""
                    <div class='metric-card'>
                        <p>El {nombre_parametro} muestra un aumento significativo a lo largo del tiempo 
                        (≈{abs(slope):.2f} {unidad} por año). Esto podría indicar:</p>
                        <ul>
                            <li>Posible desarrollo de hipertrofia ventricular (si es QRS)</li>
                            <li>Cambios en la masa muscular cardíaca</li>
                            <li>Evolución de condiciones subyacentes</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning(f"⚠️ Tendencia significativamente descendente en {nombre_parametro}")
                    st.markdown(f"""
                    <div class='metric-card'>
                        <p>El {nombre_parametro} muestra una disminución significativa a lo largo del tiempo 
                        (≈{abs(slope):.2f} {unidad} por año). Esto podría indicar:</p>
                        <ul>
                            <li>Cambios en la conducción eléctrica</li>
                            <li>Posible desarrollo de bloqueos</li>
                            <li>Efectos de medicación</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success(f"✅ {pico_principal} estable sin tendencias significativas (cambio de {slope:.2f} {unidad}/año)")
                
            # Mostrar gráfico de tendencia
            with st.container():
                st.markdown("<div class='plot-container'>", unsafe_allow_html=True)
                
                # Crear DataFrame para Plotly
                plot_df = pd.DataFrame({
                    'Fecha': df['Fecha'],
                    'Valor': df[col_analisis],
                    'Tendencia': np.polyval(coeff, dates_num)
                })
                
                fig = px.line(plot_df, x='Fecha', y=['Valor', 'Tendencia'],
                             title=f'Tendencia del {pico_principal}',
                             labels={'value': f'Valor ({unidad})'},
                             markers=True)
                
                fig.update_layout(
                    hovermode="x unified",
                    legend_title=""
                )
                
                # Personalizar línea de tendencia
                fig.data[1].line.color = 'red'
                fig.data[1].line.dash = 'dash'
                fig.data[1].name = 'Tendencia lineal'
                
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"No se pudo calcular la tendencia: {e}")
    
    # Análisis de diagnóstico cambiante
    if len(df['Diagnóstico'].unique()) > 1:
        st.markdown("""
        <div class='metric-card'>
            <h4>📌 Evolución del Diagnóstico</h4>
            <p>El diagnóstico ha cambiado a lo largo del tiempo:</p>
        """, unsafe_allow_html=True)
        
        # Crear tabla de cambios de diagnóstico
        cambios = []
        for i in range(len(df)):
            if i == 0:
                cambios.append("Primer registro")
            else:
                if df['Diagnóstico'].iloc[i] != df['Diagnóstico'].iloc[i-1]:
                    cambios.append("Cambio significativo")
                else:
                    cambios.append("Sin cambio")
        
        dx_df = pd.DataFrame({
            'Fecha': df['Fecha'].dt.strftime('%Y-%m-%d'),
            'Diagnóstico': df['Diagnóstico'],
            'Cambio': cambios
        })
        
        # Aplicar estilo a la tabla
        def highlight_changes(row):
            if row['Cambio'] == "Cambio significativo":
                return ['background-color: #fff3cd'] * len(row)
            elif row['Cambio'] == "Primer registro":
                return ['background-color: #e2f0d9'] * len(row)
            return [''] * len(row)
        
        st.table(
            dx_df.style.apply(highlight_changes, axis=1)
        )
        
        st.markdown("</div>", unsafe_allow_html=True)