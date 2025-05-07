# TO-DO

# obtener los contaminantes de la estacion(...)

# obtener los parametros meteorologicos de la estacion(...)

# definir los links de los contaminantes de la estación

# definir los links de los metereologicos de la estación

# obtener el link de la ficha de cada estación. (x)

# entregarlo en un csv

# crear y mantener una API?

# Entender como cambiar los parámetros de la URL para poder generar el gráfico que se necesita

# Y finalmente obtener el archivo csv

# https://sinca.mma.gob.cl/cgi-bin/APUB-MMA/apub.htmlindico2.cgi?page=pageRight&header={nombreEstacion}&gsize=1495x708&period=specified&from={inicioPeriodo}&to={terminoPeriodo}&macro=./R{codigoReg}/{keyEstacion}/Cal/{parametroCont}//{parametroCont}.diario.{promedioPeriodo}.ic&limgfrom=&limgto=&limdfrom=&limdto=&rsrc=&stnkey="

# Promedios

# diario.diario

# diario.trimestral

# diario.anual

# Una estación tiene:

# https://sinca.mma.gob.cl/index.php/estacion/index/key/F01

# https://sinca.mma.gob.cl/index.php/estacion/index/id/232

# - un nombre

# - un id

# - una key

# - un código de región

The script (scraping-mapeo.py) now stores station information in a structured format:
stations_by_region[region_code] = {
"names": list of station names,
"keys": list of station keys,
"ids": list of station IDs,
"number": total stations count
}
