from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import gcsfs

# Parámetros generales del DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 7, 2),
    'retries': 1,
}

# Ruta absoluta del JSON dentro del contenedor Airflow
GCP_KEY_PATH = '/opt/airflow/keys/clave.json'
BUCKET_NAME = 'etl-datos-7364'
DEST_DIR = '/opt/airflow/data'

def descargar_csvs():
    # Asegurar la existencia de la carpeta destino
    os.makedirs(DEST_DIR, exist_ok=True)

    # Conectar al bucket usando gcsfs y credenciales
    fs = gcsfs.GCSFileSystem(token=GCP_KEY_PATH)

    # Listar todos los archivos en el bucket
    archivos = fs.ls(BUCKET_NAME)

    # Filtrar solo CSV
    csvs = [f for f in archivos if f.endswith('.csv')]

    if not csvs:
        raise ValueError("No se encontraron archivos CSV en el bucket.")

    # Descargar cada archivo
    for ruta in csvs:
        nombre_archivo = ruta.split('/')[-1]
        destino_local = os.path.join(DEST_DIR, nombre_archivo)
        with fs.open(ruta, 'rb') as remote_file, open(destino_local, 'wb') as local_file:
            local_file.write(remote_file.read())
        print(f'Descargado: {ruta} → {destino_local}')

# Crear el DAG
with DAG(
    dag_id='descargar_csvs_desde_gcs',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description='Descarga todos los CSV desde GCS y los guarda localmente',
) as dag:

    descargar_tarea = PythonOperator(
        task_id='descargar_archivos_csv',
        python_callable=descargar_csvs,
    )

    descargar_tarea
