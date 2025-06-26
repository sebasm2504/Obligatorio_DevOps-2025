# Obligatorio - Programación para DevOps

## Introducción

Dado un plan de migración de las instalaciones de la empresa **“El Maligno S.A.”**, se busca abandonar el modelo _on-premise_ para adoptar un modelo en la nube, optando por los servicios de **Amazon Web Services (AWS)**.

Para lograr esto, se delegan tareas de **backup** mediante scripts en **Bash** y **Python**, con especificaciones detalladas más adelante. La idea es respaldar información específica almacenada localmente y subirla a servidores de Amazon.

---

## Parte 1: Script Bash - Backups con SetUID

Se necesita un script de **Bash** que respalde todos los ejecutables del usuario `root` que cumplan lo siguiente:

- Tengan el permiso **SetUID**
- El resto de los usuarios tengan **permiso de ejecución**

### Funcionamiento

El script:

- Trabaja por defecto en el directorio actual.
- Recibe modificadores opcionales en este orden:

1. `-c`: Crea un archivo de log con los caminos absolutos de los ejecutables encontrados.
2. `-b`: Filtra solo scripts de Bash (que comiencen con `#!/bin/bash`).
3. Ruta opcional para buscar archivos (por defecto, el directorio actual).

El archivo de respaldo generado se guarda como:

```
backupsSetUID_D-M-Y_hh-mm-ss.tar.gz
```

### Ejemplo de ejecución:

```bash
./ej1_encuentra_SetUID.sh -c -b /root
```

### Script completo:

```bash
#!/bin/bash

b=0
c=0
dir=.

if [ $# -gt 3 ] ; then
    echo "Este script solo puede recibir un máximo de 3 parámetros (-c -b y un directorio)"
    exit 2
fi

while [ $# -gt 0 ]; do
    case "$1" in
        -c ) c=1 ;;
        -b ) b=1 ;;
        -* ) echo "Error, parámetro inválido"; exit 3 ;;
        * )
            dir="$1"
            if [ ! -d $dir ]; then
                echo "$1 No es un directorio válido"
                exit 4
            fi
    esac
    shift
done

touch temp.txt
búsqueda=`find "$dir" -type f -perm -4000 -executable -perm -0001 2>/dev/null`

for arch in $búsqueda; do
    if [ "$b" == 1 ]; then
        if head -n 1 $arch | grep -qE '#!/bin/bash'; then
            echo $arch >> temp.txt
        fi
    else
        echo $arch >> temp.txt
    fi
done

if [ "$c" == 1 ]; then
    logfile="logcaminos_$(date +%d-%m-%Y_%H-%M-%S).rep"
    echo "CAMINOS A LOS ARCHIVOS ENCONTRADOS" >> "$logfile"
    echo "" >> "$logfile"
    realpath ./"$logfile" >> temp.txt
    while read linea; do
        realpath "$linea" >> "$logfile"
    done < temp.txt
    echo "Archivo de Log creado correctamente."
fi

tarname="backupsSetUID_$(date +%d-%m-%Y_%H-%M-%S).tar.gz"
tar -czf "$tarname" -T temp.txt
rm temp.txt

echo "Se generó el archivo $logfile"
exit 0
```

---

## Parte 2: Script Python - Carga a S3

Este script usa **boto3** para:

- Buscar archivos `.tar.gz` generados por el script de Bash.
- Crear un bucket S3 llamado `el-maligno-327041-325301`.
- Subir el archivo `.tar.gz` a S3 con nombre `"Log_D-M-Y"`.

### Código:

```python
import boto3
import sys
import os
from datetime import datetime

directorio = os.getcwd()
archivos = [
    os.path.join(directorio, f)
    for f in os.listdir(directorio)
    if f.startswith("backupsSetUID") and os.path.isfile(os.path.join(directorio, f))
]

for archivo in archivos:
    print(archivo)
    file_name = archivo

s3_client = boto3.client('s3')
bucket_name = 'el-maligno-327041-325301'
object_name = "Log_" + datetime.now().strftime("%d-%m-%Y")

try:
    boto3.client('s3').create_bucket(Bucket=bucket_name)
except boto3.exceptions.S3CreateError as e:
    print(f"Error creating bucket: {e}")
    exit(1)

try:
    s3_client.upload_file(file_name, bucket_name, object_name)
    print(f"File {file_name} uploaded to {bucket_name}/{object_name}")
except FileNotFoundError:
    print(f"The file {file_name} was not found")
```

---

## Parte 3: Base de Datos MySQL y EC2

Este script crea:

1. Un **Security Group** para MySQL y otro para EC2.
2. Una **instancia RDS MySQL**.
3. Una **instancia EC2** que:
   - Se conecta a la base.
   - Ejecuta el script SQL `obli.sql`.

> Requiere tener `boto3` instalado y credenciales válidas (`aws configure`).

### Consideraciones:

- La imagen de AMI es para `us-east-1`: `ami-0c101f26f147fa7fd`
- Contraseña por defecto: `password123`
- Se instala MariaDB en EC2.

### Script Python (resumen):

```python
# Crear security groups, RDS y EC2
# Leer archivo obli.sql
# Crear script de userdata para EC2 que conecte con RDS y cargue la base

# (Código completo omitido aquí por espacio, ver documento original)
```

---

## Requisitos

- Python 3.x
- AWS CLI configurado (`aws configure`)
- Boto3 (`pip install boto3`)
- Script Bash con permisos de ejecución
- Archivo `obli.sql` para la base de datos

---

## Créditos

Trabajo obligatorio - DevOps  
**El Maligno S.A.**
