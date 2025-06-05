# database.py
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from bson import ObjectId

# Configuración de la conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Cambia esto si tu MongoDB está en otro host o puerto
db = client["Tesis_ECG"]  # Nombre de tu base de datos

# Colección de pacientes
collection_pacientes = db["pacientes"]
collection_pacientes.create_index("ID Paciente", unique=True)
collection_pacientes.create_index("CURP", unique=True)

# Colección de registros de ECG
collection_ecg = db["Registros_ECG"]

def obtener_pacientes():
    return collection_pacientes.find()

def agregar_paciente(paciente):
    try:
        collection_pacientes.insert_one(paciente)
        return True
    except DuplicateKeyError:
        return False

def eliminar_paciente(id_paciente):
    """
    Eliminar un paciente y todos sus registros de ECG asociados.
    """
    # Primero eliminar todos los ECGs asociados al paciente
    collection_ecg.delete_many({"id_paciente": id_paciente})

    # Luego elimino el paciente
    result = collection_pacientes.delete_one({"ID Paciente": id_paciente})
    return result.deleted_count > 0

def guardar_ecg_analizado(id_paciente, nombre_paciente, imagen_ecg, anomalias, detalles_picos):
    """
    Guarda el ECG analizado en la colección registro_ECG.
    """
    registro = {
        "id_paciente": id_paciente,
        "nombre_paciente": nombre_paciente,
        "imagen_ecg": imagen_ecg,  # Puede ser un archivo binario o una URL
        "anomalias": anomalias,
        "detalles_picos_del_ECG": detalles_picos,
        "fecha_analisis": datetime.now()
    }
    collection_ecg.insert_one(registro)

def obtener_ecgs_por_paciente(id_paciente):
    """
    Obtiene todos los ECG analizados de un paciente específico.
    """
    return collection_ecg.find({"id_paciente": id_paciente})

def eliminar_ecg_analizado(id_ecg):
    """
    Elimina un ECG analizado por su ID.
    """
    result = collection_ecg.delete_one({"_id": ObjectId(id_ecg)})
    return result.deleted_count > 0