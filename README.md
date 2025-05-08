# TO-DO

# Obtener las fechas limites (x)

# obtener los contaminantes de la estacion(haciendo)

# obtener los parametros meteorologicos de la estacion(...)

# definir los links de los contaminantes de la estación(funciona para uno estático)

# definir los links de los metereologicos de la estación (...)

# obtener el link de la ficha de cada estación. (x)

# entregarlo en un csv (...)

# crear y mantener una API? (proyecto personal)

# Entender como cambiar los parámetros de la URL para poder generar el gráfico que se necesita (x)

# https://sinca.mma.gob.cl/cgi-bin/APUB-MMA/apub.htmlindico2.cgi?page=pageRight&header={nombreEstacion}&gsize=1495x708&period=specified&from={inicioPeriodo}&to={terminoPeriodo}&macro=./R{codigoReg}/{keyEstacion}/Cal/{parametroCont}//{parametroCont}.diario.{promedioPeriodo}.ic&limgfrom=&limgto=&limdfrom=&limdto=&rsrc=&stnkey="

# Parámetros

# Por cada parámetro contaminante se tiene un promedio diario (diario, trimestral o anual). Por cada unidad de promedio se obtiene un gráfico de serie de tiempo.

# A este promedio se le debe asignar una ventana de tiempo (suelo y techo)

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

# un conjunto de parámetros contaminantes y metereológicos.

# Por cada parámetro existen mediciones, que pueden ser entregadas en promedio diario (anual, trimestral). Se debe definir un periodo para poder calcular este promedio (gráficos de series de tiempo).
