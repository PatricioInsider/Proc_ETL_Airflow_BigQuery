<<<<<<< HEAD
# 📊 ETL Airflow: Ventas SRI de GCS a BigQuery

Este proyecto implementa un flujo ETL (Extract, Transform, Load) con **Apache Airflow**, para procesar archivos de ventas del SRI desde Google Cloud Storage (GCS), transformarlos con `pandas` y cargarlos en un Data Warehouse en **Google BigQuery**.

---

## 📁 Estructura del Proyecto

etl-airflow/
│
├── config/
│ └── airflow.cfg # Configuración personalizada de Airflow
│
├── dags/
│ ├── descargar_csvs_gcs.py # DAG: descarga archivos CSV desde GCS a local
│ └── etl_ventas_gcs_bq.py # DAG: ETL desde CSV local a BigQuery
│
├── data/ # CSV de ventas desde 2017 hasta 2025
│ ├── sri_ventas_2017.csv
│ ├── ...
│ └── sri_ventas_2025.csv
│
├── docker-compose.yaml # Orquestación de Airflow con Docker
├── requirements.txt # Paquetes necesarios para el entorno Airflow
├── .env # Variables de entorno opcionales
├── .gitignore # Archivos ignorados por Git
├── claveCloude.json # 🔒 Clave privada de GCP (NO incluida en el repo)

yaml
Copiar
Editar

---

## 📜 Descripción de los DAGs

### `descargar_csvs_gcs.py`

- Conecta a un bucket de GCS mediante `gcsfs`.
- Descarga automáticamente todos los archivos `.csv` y los guarda en `/opt/airflow/data`.
- Utiliza la credencial JSON localmente montada como volumen (`claveCloude.json`).

### `etl_ventas_gcs_bq.py`

- Lee los CSV desde la carpeta local.
- Realiza limpieza y transformación:
  - Crea dimensiones: `dim_provincia`, `dim_tiempo`, `dim_sector`.
  - Carga hechos: `hechos_ventas_compras`.
- Usa `pandas` y el cliente `google-cloud-bigquery`.

---

## 🔐 Seguridad y acceso

- El archivo `claveCloude.json` **no se incluye en este repositorio** por seguridad.
  - Está listado en `.gitignore`.
  - Debe colocarse manualmente en la ruta `/opt/airflow/claveCloude.json` para que los DAGs funcionen.

- Los archivos `sri_ventas_*.csv` **sí se incluyen** porque son datos de acceso público y sirven para pruebas y validaciones.  

---

## 🔧 Requisitos

En el archivo `requirements.txt` se incluyen las dependencias principales:

```text
apache-airflow
pandas
gcsfs
google-cloud-bigquery
Instálalas con:

bash
Copiar
Editar
pip install -r requirements.txt
🐳 Cómo levantar el entorno con Docker
bash
Copiar
Editar
docker-compose up -d
Accede a Airflow en: http://localhost:8080

Usuario/Contraseña por defecto:

pgsql
Copiar
Editar
admin / admin
▶️ Cómo ejecutar los DAGs
Asegúrate de tener la clave de servicio en la ruta correcta (claveCloude.json).

Ejecuta el DAG descargar_csvs_desde_gcs si necesitas descargar datos desde GCS.

Ejecuta el DAG etl_ventas_gcs_bigquery para transformar y cargar los datos a BigQuery.

📊 Tablas generadas en BigQuery
Tabla	Tipo	Descripción
dim_provincia	Dimensión	Provincia y cantón
dim_tiempo	Dimensión	Año, mes, trimestre
dim_sector	Dimensión	Código de sector económico + cantón
hechos_ventas_compras	Hechos	Métricas de ventas y compras del SRI

🔗 Repositorio del Proyecto
Puedes consultar o clonar el repositorio desde:

https://github.com/tu-usuario/etl-airflow-sri
(Reemplaza este link con el real si es diferente)

=======
# Proc_ETL_Airflow_BigQuery
Construcción de Procesos ETL con Apache Airflow y Google BigQuery
>>>>>>> 2aee45393d86053e092a0431bac6cb858a3a969c
