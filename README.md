# Colectivo Dominio Público
## Instalación ciberpunks

###Dependencias
Instalar pip (para poder instalar fácilmente todas las otras dependencias)

* cv2
* numpy
* pyinotify (https://github.com/seb-m/pyinotify)
* urllib2
* pyttsx
* BeautifulSoup

###Uso

#####face_collector.py
Permite detectar caras de una entrada (video o webcam) y guardarlas en una carpeta destino.
Las guarda recortadas y estandarizadas para luego poder compararlas.

#####face_id_ui.py
Detecta nuevos archivos creados en una carpeta de entrada y dispara una secuencia de imagenes leídas de una carpeta.
Esta carpeta es la "base de datos" de caras.
Simula la búsqueda de un rostro en una base de datos.

###Bases de datos de rostros

* Labeled faces in the wild (http://vis-www.cs.umass.edu/lfw/)
* AT&T face database (http://www.cl.cam.ac.uk/research/dtg/attarchive/facedatabase.html)
* Face Recognition Database (http://www.face-rec.org/databases/)