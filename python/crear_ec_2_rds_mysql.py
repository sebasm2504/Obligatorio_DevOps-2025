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
