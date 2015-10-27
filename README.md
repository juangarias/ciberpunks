# Colectivo Dominio Público
## Instalación ciberpunks

###Dependencias
Instalar pip (para poder instalar fácilmente todas las otras dependencias)

* cv2 (2.4.11 http://opencv.org/)
  * Instalar los binarios, para poder usar la librería
  * Descargar los archivos HAAR (xml para detección de objetos) que vienen con los fuentes
* numpy (Debería venir junto con cv2)
* pyinotify (https://github.com/seb-m/pyinotify) para Linux
* watchdog para Mac OS X
* urllib2
* pyttsx
* BeautifulSoup
* paramiko

###Uso

#####window_input.py
Es la interfaz de consola que permite ingresar un nombre y un e-mail. Luego toma una foto del sujeto.
Finalmente, guarda la foto con el nombre del sujeto en una carpeta de salida.

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