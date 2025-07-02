from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from google.cloud import bigquery
import os

# Ruta del archivo CSV local (modificado desde GCS a local ./data)
ARCHIVO_LOCAL = os.path.join(os.path.dirname(__file__), '..', 'data', 'sri_ventas_2025.csv')
BQ_PROJECT = "sistemas7364"
BQ_DATASET = "dw_etl"

# ========== FUNCIONES DE CARGA DE DIMENSIONES ==========

def cargar_dim_provincia():
    df = pd.read_csv(ARCHIVO_LOCAL)
    print("Dimensión provincia - filas:", df.shape)
    
    df = df[['PROVINCIA', 'CANTON']].drop_duplicates().dropna()
    df['id_provincia'] = df.apply(lambda row: hash((row['PROVINCIA'], row['CANTON'])) % 1000000, axis=1)

    client = bigquery.Client()
    table_id = f"{BQ_PROJECT}.{BQ_DATASET}.dim_provincia"
    job = client.load_table_from_dataframe(df, table_id, job_config=bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"
    ))
    job.result()
    print(f"Filas cargadas en {table_id}: {job.output_rows}")

def cargar_dim_tiempo():
    df = pd.read_csv(ARCHIVO_LOCAL)
    print("Dimensión tiempo - filas:", df.shape)

    df = df[['AÑO', 'MES']].drop_duplicates()
    df['trimestre'] = df['MES'].apply(lambda x: (int(x) - 1) // 3 + 1)
    df['id_tiempo'] = df.apply(lambda row: hash((row['AÑO'], row['MES'])) % 1000000, axis=1)
    df = df.rename(columns={"AÑO": "anio", "MES": "mes"})

    client = bigquery.Client()
    table_id = f"{BQ_PROJECT}.{BQ_DATASET}.dim_tiempo"
    job = client.load_table_from_dataframe(df, table_id, job_config=bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"
    ))
    job.result()
    print(f"Filas cargadas en {table_id}: {job.output_rows}")

def cargar_dim_sector():
    df = pd.read_csv(ARCHIVO_LOCAL)
    print("Dimensión sector - filas:", df.shape)

    df = df[['CODIGO', 'CANTON']].drop_duplicates().dropna()
    df['id_sector'] = df.apply(lambda row: hash((row['CODIGO'], row['CANTON'])) % 1000000, axis=1)
    df = df.rename(columns={"CODIGO": "codigo_sector_n1"})

    client = bigquery.Client()
    table_id = f"{BQ_PROJECT}.{BQ_DATASET}.dim_sector"
    job = client.load_table_from_dataframe(df, table_id, job_config=bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"
    ))
    job.result()
    print(f"Filas cargadas en {table_id}: {job.output_rows}")

# ========== FUNCIÓN PARA CARGAR TABLA DE HECHOS ==========

def cargar_hechos():
    df = pd.read_csv(ARCHIVO_LOCAL)
    print("Tabla de hechos - filas:", df.shape)

    client = bigquery.Client()

    dim_prov = client.query(f"SELECT * FROM `{BQ_PROJECT}.{BQ_DATASET}.dim_provincia`").to_dataframe()
    dim_tiempo = client.query(f"SELECT * FROM `{BQ_PROJECT}.{BQ_DATASET}.dim_tiempo`").to_dataframe()
    dim_sector = client.query(f"SELECT * FROM `{BQ_PROJECT}.{BQ_DATASET}.dim_sector`").to_dataframe()

    df = df.merge(dim_prov, on=['PROVINCIA', 'CANTON'], how='left')
    df = df.merge(dim_tiempo, left_on=['AÑO', 'MES'], right_on=['anio', 'mes'], how='left')
    df = df.merge(dim_sector, left_on=['CODIGO', 'CANTON'], right_on=['codigo_sector_n1', 'canton'], how='left')

    df_hechos = df[[
        'id_provincia', 'id_tiempo', 'id_sector',
        'VENTAS_NETAS_TARIFA_GRAVADA', 'VENTAS_NETAS_TARIFA_0',
        'VENTAS_NETAS_TARIFA_VARIABLE', 'VENTAS_NETAS_TARIFA_5',
        'EXPORTACION', 'COMPRAS_NETAS_TARIFA_GRAVADA',
        'COMPRAS_NETAS_TARIFA_0', 'IMPORTACIONES',
        'COMPRAS_RISE', 'TOTAL_COMPRAS', 'TOTAL_VENTAS'
    ]]

    df_hechos.columns = [
        'id_provincia', 'id_tiempo', 'id_sector',
        'netas_tarifa_gravada', 'netas_tarifa_0',
        'netas_tarifa_variable', 'netas_tarifa_5',
        'exportaciones', 'compras_netas_tarifa_gravada',
        'compras_netas_tarifa_0', 'importaciones',
        'compras_rise', 'total_compras', 'total_ventas'
    ]

    table_id = f"{BQ_PROJECT}.{BQ_DATASET}.hechos_ventas_compras"
    job = client.load_table_from_dataframe(df_hechos, table_id, job_config=bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"
    ))
    job.result()
    print(f"Filas cargadas en {table_id}: {job.output_rows}")

# ========== DEFINICIÓN DEL DAG Y TAREAS ==========

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 7, 1),
    'retries': 1,
}

with DAG(
    dag_id='etl_ventas_local_bigquery',
    default_args=default_args,
    description='ETL desde archivo local en data/ hacia BigQuery',
    schedule=None,
    catchup=False,
    tags=['local', 'bq', 'etl']
) as dag:

    tarea_dim_provincia = PythonOperator(
        task_id='cargar_dim_provincia',
        python_callable=cargar_dim_provincia
    )

    tarea_dim_tiempo = PythonOperator(
        task_id='cargar_dim_tiempo',
        python_callable=cargar_dim_tiempo
    )

    tarea_dim_sector = PythonOperator(
        task_id='cargar_dim_sector',
        python_callable=cargar_dim_sector
    )

    tarea_cargar_hechos = PythonOperator(
        task_id='cargar_hechos_ventas_compras',
        python_callable=cargar_hechos
    )

    # Dependencias
    [tarea_dim_provincia, tarea_dim_tiempo, tarea_dim_sector] >> tarea_cargar_hechos
