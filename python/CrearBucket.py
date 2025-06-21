import boto3
import sys
import os
from datetime import datetime


# Directorio actual
directorio = os.getcwd()

# Lista los archivos y filtra los que comienzan con "backupsSetUID"
archivos = [
    os.path.join(directorio, f)
    for f in os.listdir(directorio)
    if f.startswith("backupsSetUID") and os.path.isfile(os.path.join(directorio, f))
]

# Muestra la lista
for archivo in archivos:
    file_name = archivo

s3_client = boto3.client('s3')
bucket_name = 'el-maligno-327041-325301'
object_name = "Log_"+datetime.now().strftime("%d-%m-%Y")
try:
    boto3.client('s3').create_bucket(Bucket=bucket_name)
except boto3.exceptions.S3CreateError as e:
    print(f"Error creating bucket: {e}")
    exit(1)
try:
    s3_client.upload_file(file_name, bucket_name, object_name)
    print(f"Archivo {file_name} subido a {bucket_name}/{object_name}")
except FileNotFoundError:
    print(f"El archivo {file_name} no fue encontrado")
except ClientError as e:
    print(f"Error al subir archivo: {e}")