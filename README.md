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

El script trabaja por defecto con el directorio donde se encuentra, recibe parámetros y modificadores opcionales que deben cumplir cierto formato.
En la propia carpeta desde donde se ejecuta el script, se guardan los archivos que se obtienen según los parámetros recibidos en un archivo con el formato:

```
backupsSetUID_D-M-Y_hh-mm-ss.tar.gz
```
### Instrucciones:

Estando ubicados en la carpeta que contiene el script, se llama al ejecutable y opcionalmente se pueden agregar modificadores en orden:
El primer modificador que se puede agregar es -c: crea dentro del .tar un archivo de log con los caminos absolutos de los ejecutables encontrados.

Modificador -b: Busca sólo ejecutables que sean scripts de Bash, es decir, aplica un filtro a los archivos buscados.

El tercer modificador consiste en especificar la ruta en la que se quiere trabajar. Dejando esta opción vacía, se ejecutará el script sobre el directorio corriente.


### Ejemplo de ejecución:

```bash
./ej1_encuentra_SetUID.sh -c -b /root
```

### Script completo:

```bash
#!/bin/bash

#Inicializamos variables de parametros
b=0
c=0
dir=.

# Si la cantidad de parametros es mayor a 3 se sale directamente.

if [ $# -gt 3 ] ; then
	echo "Este script solo puede recibir un máximo de 3 parametros (-c -b y un directorio)"
	exit 2
fi	

# Mientras la cantidad de parametros sea mayor a 0 se evaluan los parametros

while [ $# -gt 0 ]
do
	#Usamos las variables como una "flag" encendida o apagada
	case "$1" in

		-c )
			c=1
			;;
		-b )
			b=1
			;;
		#Si el parametro es -* (Salvo c o b es un parametro invalido)
		-* )
			echo "Error, parámetro inválido"
		        exit 3	
			;;
		#Si se recibe un parametro sin "-" se evalua si es un directorio
		* )
			dir="$1"
			if [ ! -d $dir ] ; then
				echo "$1 No es un directorio válido"
				exit 4
			fi
	esac
	shift
done

#Creamos un archivo temporal en el cual se guardaran los archivos a respaldar.
touch temp.txt

#Se buscan los archivos en en el directorio indicado.
busqueda=`find "$dir" -type f -user root -perm -4000 -executable -perm -0001 2>/dev/null` 

for arch in `echo $busqueda`
do
	#Se evalua si se recibió el parametro -b entonces solo se filtran los que comiencen con "#!/bin/bash"
	if [ "$b" == 1 ]
	then
		if head -n 1 $arch | grep -qE '#!/bin/bash' 
		then
			echo $arch >> temp.txt
		fi
	else
		echo $arch >> temp.txt
	fi
done

#Se evalua si se pasó el parametro -c, en caso de ser asi se recorre el temporal creando el archivo de log.
if [ "$c" == 1 ] 
then
	logfile="logcaminos_$(date +%d-%m-%Y_%H-%M-%S).rep"
	echo "CAMINOS A LOS ARCHIVOS ENCONTRADOS" >> "$logfile"
	echo ""
       `echo realpath \.\/"$logfile"` >> temp.txt
	for linea in `head -n -1 temp.txt`
	do
		`echo realpath "$linea"` >> "$logfile"
	done
	echo "Archivo de Log "$logfile" creado correctamente."
fi

tarname="backupsSetUID_$(date +%d-%m-%Y_%H-%M-%S).tar.gz"

#Se crea el tar con los archivos.
tar -czf "$tarname" -T temp.txt

#Se borra el archivo temporal.
rm temp.txt


echo "Se generó el archivo $tarname"
exit 0

```

---

## Parte 2: Script Python - Carga a S3

Para la ejecución del script fue necesario importar bibliotecas y módulos de Python para el manejo de ciertas funciones. En particular, la biblioteca boto3 de AWS para python (habiéndose instalado previamente con pip install boto3), sys para acceder a funcionalidades del sistema, os para interactuar con el sistema operativo y el módulo datetime que permite trabajar con fechas y horas.

El script busca en el directorio actual y filtra los archivos que comienzan con “backupsSetUID”, que es como comienza el nombre de los archivos .tar que se generan con el script de Bash. Cabe aclarar que se está suponiendo que existe SOLO un archivo comprimido generado por el script de Bash, por lo que no contempla otra posibilidad.

Para su ejecución únicamente es necesario haber ejecutado previamente el script de Bash y por supuesto, que el archivo .tar esté ubicado en el mismo directorio que es script.

El script de Python propuesto es el siguiente:

### Código:

```python
#!/usr/bin/python3

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
    print("Bucket creado correctamente")
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
```

---

## Parte 3: Base de Datos MySQL y EC2

Para que este script se pueda ejecutar, es necesaria la instalación de la librería boto3 (como se menciona en la parte anterior), tener el archivo obli.sql en el mismo directorio que este script. 
Con el comando aws configure, se guardan las credenciales localmente en root/.aws/credentials. Estas credenciales son temporales, por lo que se debe verificar en AWS y cambiarlas en el archivo “credentials” en caso de que se hayan actualizado.
Para este script se cambió el código de la región en la variable ImageId y se estableció la correspondiente a us-east-1, que es que figura en el servidor de Amazon para el usuario.
Como contraseña se dejó la que estaba (password123).
Algo a mencionar es que durante la ejecución se instala mariadb para que se pueda utilizar el comando mysql en la carga de la base.

### Script Python:

```python
#!/usr/bin/python3
import boto3
import time
from botocore.exceptions import ClientError
import base64

# Crear el Security Group para la base de datos
ec2 = boto3.client('ec2')
security_group_name_db = 'MySQLSecurityGroup'

try:
    response = ec2.create_security_group(
        GroupName=security_group_name_db,
        Description='Permitir acceso al puerto 3306 para MySQL desde EC2'
    )
    security_group_id_db = response['GroupId']
    print(f"Security Group para la base de datos creado con ID: {security_group_id_db}")
except ClientError as e:
    if 'InvalidGroup.Duplicate' in str(e):
        print(f"Security Group '{security_group_name_db}' ya existe. Obteniendo su ID...")
        response = ec2.describe_security_groups(GroupNames=[security_group_name_db])
        security_group_id_db = response['SecurityGroups'][0]['GroupId']
        print(f"Security Group existente con ID: {security_group_id_db}")
    else:
        raise

# Crear el Security Group para la instancia EC2
security_group_name_ec2 = 'EC2SecurityGroup'

try:
    response = ec2.create_security_group(
        GroupName=security_group_name_ec2,
        Description='Permitir acceso desde la instancia EC2 al Security Group de la base de datos y SSM'
    )
    security_group_id_ec2 = response['GroupId']
    print(f"Security Group para la instancia EC2 creado con ID: {security_group_id_ec2}")

    # Configurar reglas de ingreso para permitir acceso al Security Group de la base de datos
    ec2.authorize_security_group_ingress(
        GroupId=security_group_id_db,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 3306,
                'ToPort': 3306,
                'UserIdGroupPairs': [{'GroupId': security_group_id_ec2}]
            }
        ]
    )
    print("Reglas de ingreso configuradas para permitir acceso desde la instancia EC2.")

    # Configurar reglas de ingreso para permitir acceso a SSM
    ec2.authorize_security_group_ingress(
        GroupId=security_group_id_ec2,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 443,
                'ToPort': 443,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Permitir acceso a SSM (HTTPS)
            }
        ]
    )
    print("Reglas de ingreso configuradas para permitir acceso a SSM.")
except ClientError as e:
    if 'InvalidGroup.Duplicate' in str(e):
        print(f"Security Group '{security_group_name_ec2}' ya existe. Obteniendo su ID...")
        response = ec2.describe_security_groups(GroupNames=[security_group_name_ec2])
        security_group_id_ec2 = response['SecurityGroups'][0]['GroupId']
        print(f"Security Group existente con ID: {security_group_id_ec2}")
    else:
        raise

# Crear la base de datos RDS
rds = boto3.client('rds')
db_instance_identifier = 'Maligno-DB'

try:
    response = rds.create_db_instance(
        DBInstanceIdentifier=db_instance_identifier,
        AllocatedStorage=20,
        DBInstanceClass='db.t3.micro',
        Engine='mysql',
        MasterUsername='admin',
        MasterUserPassword='password123',  # Cambiar por una contraseña segura
        VpcSecurityGroupIds=[security_group_id_db]
    )
    print(f"Base de datos RDS creada con ID: {db_instance_identifier}")

    # Esperar a que la base de datos esté disponible
    print("Esperando a que la base de datos esté disponible...")
    waiter = rds.get_waiter('db_instance_available')
    waiter.wait(DBInstanceIdentifier=db_instance_identifier)
    db_instance = rds.describe_db_instances(DBInstanceIdentifier=db_instance_identifier)
    db_endpoint = db_instance['DBInstances'][0]['Endpoint']['Address']
    print(f"Base de datos disponible en: {db_endpoint}")
except ClientError as e:
    if 'DBInstanceAlreadyExists' in str(e):
        print(f"La base de datos RDS '{db_instance_identifier}' ya existe. Obteniendo su endpoint...")
        db_instance = rds.describe_db_instances(DBInstanceIdentifier=db_instance_identifier)
        db_endpoint = db_instance['DBInstances'][0]['Endpoint']['Address']
        print(f"Base de datos disponible en: {db_endpoint}")
    else:
        raise

with open('obli.sql', 'r') as file:
    sql_content = file.read()

# Crear la instancia EC2
user_data_script = f'''#!/bin/bash
sudo yum update -y
sudo yum install mariadb105-server-utils.x86_64 -y
# Esperar unos segundos por seguridad
sleep 60
# Crear archivo SQL en EC2
cat << EOF > /home/ec2-user/obli.sql
{sql_content}
EOF
# Ejecutar el script SQL en la base de datos RDS
mysql -h {db_endpoint} -u admin -ppassword123 < /home/ec2-user/obli.sql
echo "Conexión a la base de datos RDS: {db_endpoint}" > /home/ec2-user/db_connection_info.txt
'''

try:
    response = ec2.run_instances(
        ImageId='ami-0c101f26f147fa7fd',  # Reemplazar con uno válido para tu región
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        SecurityGroupIds=[security_group_id_ec2],
        UserData=user_data_script,
        IamInstanceProfile={'Name': 'LabInstanceProfile'},
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': 'Maligno-SRV'}]
            }
        ]
    )
    instance_id = response['Instances'][0]['InstanceId']
    print(f"Instancia EC2 creada con ID: {instance_id}")

    # Esperar a que la instancia EC2 esté en estado 'running'
    print("Esperando a que la instancia EC2 esté en estado 'running'...")
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])
    print("Instancia EC2 está en ejecución.")
except ClientError as e:
    if 'InvalidInstanceID.Duplicate' in str(e):
        print("La instancia EC2 ya existe.")
    else:
        raise
```

