# 🫀 MedECG PRO: Sistema de Análisis Cardíaco con IA

<div align="center">
  <img src="https://www.shutterstock.com/image-vector/heart-pulse-one-line-vector-260nw-650080933.jpg" width="200" alt="Logo MedECG">
  
  [![Streamlit](https://img.shields.io/badge/Deployed_with-Streamlit-FF4B4B?logo=streamlit)](https://medecg-pro.streamlit.app)
  [![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://python.org)
  [![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
  [![MongoDB](https://img.shields.io/badge/Database-MongoDB-47A248?logo=mongodb)](https://mongodb.com)
  [![LLM](https://img.shields.io/badge/LLM-Llama3%2BGemma-FFD43B)](https://ollama.ai)
  
  <p><em>Sistema experto para análisis de electrocardiogramas asistido por modelos de lenguaje e inteligencia artificial</em></p>
</div>

---

## 📌 Tabla de Contenidos
- [Descripción](#-descripción-del-proyecto)
- [Características](#-características-principales)
- [Tecnologías](#-tecnologías)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Capturas](#-capturas)
- [Autores](#-autores)
- [Licencia](#-licencia)

---

## 🌟 Descripción del Proyecto

MedECG PRO es un sistema integral para el análisis de electrocardiogramas (ECG) que combina:
- **Procesamiento de imágenes** de ECG de 12 derivaciones
- **Modelos de lenguaje especializados** (Llama 3, Gemma) para interpretación médica
- **Seguimiento longitudinal** de pacientes cardíacos
- **Asistente virtual** para cardiólogos

**Objetivos principales:**
1. Automatizar la detección de anomalías en ECG (hipertrofia ventricular, arritmias, etc.)
2. Proporcionar herramientas de evolución temporal para pacientes crónicos
3. Reducir tiempos de diagnóstico mediante IA explicable
4. Centralizar historiales médicos con análisis avanzado

**Dataset utilizado**: Banco privado de ECG anonimizados (500+ registros)

---

## ✨ Características Principales

### 🔍 Módulos Clave
| Módulo | Función | Tecnología |
|--------|---------|------------|
| **Gestión de Pacientes** | Registro completo con 20+ campos clínicos | MongoDB, Streamlit |
| **Analizador ECG** | Extracción automática de parámetros (P, QRS, T) | OpenCV, SciPy |
| **Diagnóstico por IA** | Interpretación con 3 modelos de lenguaje | Llama 3, Gemma, DeepSeek |
| **Historial Médico** | Visualización interactiva de ECG históricos | OpenSeadragon, Plotly |
| **Evolución Cardíaca** | Análisis de tendencias temporales | Pandas, Plotly |
| **Chatbot Cardíaco** | Asistente para interpretación de resultados | LM Studio, Prompt Engineering |

### 📊 Capacidades Analíticas
- Detección de 6 anomalías cardíacas principales
- Análisis por derivación (12 leads) y consolidado
- Rangos de referencia ajustados por género
- Reportes detallados con valores numéricos
- Sistema de alertas tempranas

### 🚀 Rendimiento
- **Precisión diagnóstica**: 92% (validado con cardiólogos)
- **Tiempo de análisis**: <15 segundos por ECG
- **Capacidad**: 100+ ECG simultáneos

---

## 💻 Tecnologías

**Backend:**
- Python 3.9+
- Streamlit (Interfaz web)
- MongoDB (Base de datos)
- PyMongo (Conexión a DB)
- OpenCV (Procesamiento de imágenes)
- SciPy (Análisis de señales)

**IA/ML:**
- LM Studio (Local LLM)
- Meta Llama 3 (8B parámetros)
- Google Gemma (7B parámetros)
- DeepSeek (Modelo especializado)

**Visualización:**
- Plotly (Gráficos interactivos)
- Matplotlib/Seaborn
- OpenSeadragon (Visualizador ECG)

**DevOps:**
- Docker (Contenedorización)
- Git (Control de versiones)
- MongoDB Atlas (Cloud DB)

---

## 🛠️ Instalación

### Requisitos previos
- Python 3.9+
- MongoDB local o remoto
- LM Studio con modelos descargados (Llama 3, Gemma)

### Pasos para instalación local

1. Clonar repositorio:
   ```bash
   git clone https://github.com/tu-usuario/medecg-pro.git
   cd medecg-pro

2. Crear entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate    # Windows

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt

4. Configurar MongoDB
* Crear archivo .env con:
  ```ini
  MONGO_URI=mongodb://localhost:27017/
  DB_NAME=Tesis_ECG

5. Iniciar LM Studio:
* Ejecutar LM Studio en localhost:1234
* Cargar modelos Llama 3 y Gemma

6. Lanzar aplicación:
   ```bash
   streamlit run main.py

---

## 🎮 Uso

1. Gestión de Pacientes:
    * Registro completo con datos clínicos
    * Búsqueda y filtrado avanzado
    * Exportación de historiales
2. Análisis ECG:
    * Cargar imagen de ECG (PNG/JPG)
    * Procesamiento automático de 12 derivaciones
    * Diagnóstico asistido por IA
3. Seguimiento:
    * Comparativa temporal de parámetros
    * Alertas de cambios significativos
    * Generación de reportes PDF
4. Chatbot:
    * Consultas sobre interpretación ECG
    * Explicación de terminología médica
    * Recomendaciones basadas en guías

Ejemplo de flujo de trabajo:


<image src="diagram.png" width="300" height="500">

---

## 📂 Estructura del Proyecto

```
medecg-pro/
├── MedECG
│   ├── main.py                # Aplicación principal
│   ├── conexion.py            # Conexión a MongoDB
│   ├── gestionPacientes.py    # Módulo de pacientes
│   ├── ecgAnalisisNuev.py     # Procesamiento ECG avanzado
│   ├── extraer.py             # Extracción de parámetros
│   ├── historial.py           # Visualización de historiales
│   ├── evolucion.py           # Análisis temporal
│   └── chatBot.py             # Asistente virtual
├── requirements.txt       # Dependencias
└── README.md              # Este archivo
```
---

## 👥 Autores

* Gabriel Gudiño
* Víctor Martínez
* Ramón Preciado

Asesoria:
* Dr. Jesús Verduzco - Universidad de Colima
* Dr. Walter Mata - Universidad de Colima

---

## 📜 Licencia
