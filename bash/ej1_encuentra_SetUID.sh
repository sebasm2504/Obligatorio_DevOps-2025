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
