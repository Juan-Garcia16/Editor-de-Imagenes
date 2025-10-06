from django.shortcuts import render
from django.core.files.storage import FileSystemStorage # Importa FileSystemStorage para manejar archivos
from .utils import imgPro
import numpy as np
from PIL import Image
from django.core.files.base import ContentFile # Importa ContentFile para manejar archivos en memoria
from io import BytesIO # Importa BytesIO para manejar buffers en memoria

# Create your views here.

def extract_layer(request, imagen_url, procesada_url, fs, capa, canal, tipo_grises=None):
  
   ruta_original = request.POST.get('imagen_actual')  # ruta recibida del formulario
   if ruta_original:
       # abrir la imagen original desde MEDIA_ROOT
      
       ruta_completa = fs.path(ruta_original.replace('/media/', '')) #convierte la url publica a una relativa
       img = Image.open(ruta_completa).convert('RGB') # abre la imagen en disco en RGB
       arr = np.array(img) / 255 # normalizada para uso correcto de la libreria
      
       # transformacion con la libreria
       if canal == "rgb":
           nueva = imgPro.extract_layer_rgb(arr, capa) #para RGB
       elif canal == "cmy":
           nueva = imgPro.extract_layer_cmy(arr, capa) #para CMY
       elif capa is None and canal is None and tipo_grises is None:
           nueva = imgPro.reverse(arr)
       elif tipo_grises:
           if tipo_grises == "average":
               nueva = imgPro.average(arr)
           elif tipo_grises == "luminosity":
               nueva = imgPro.luminosity(arr)
           elif tipo_grises == "midgray":
               nueva = imgPro.midgray(arr)
       else:
           nueva = arr
      
       nueva = np.clip(nueva, 0, 1)

       print("Tipo:", tipo_grises)
       print("Shape de nueva:", nueva.shape)
       print("Min:", np.min(nueva), "Max:", np.max(nueva), "Media:", np.mean(nueva))
      
       procesada = Image.fromarray((np.clip(nueva, 0, 1) * 255).astype(np.uint8), mode="RGB")
       # procesada = Image.fromarray((nueva[:, :, 0] * 255).astype(np.uint8), mode="L")
    #    procesada = Image.fromarray((nueva * 255).astype(np.uint8))
      
       # guardar la imagen procesada en memoria temporal
       buffer = BytesIO() # crea un buffer en memoria
       procesada.save(buffer, format='PNG') # guarda la imagen procesada en png dentro del buffer
       buffer.seek(0) # va al inicio del buffer para leer la imagen
      
       # guardar la imagen procesada en el sistema de archivos
       nombre_resultado = f'{request.POST.get("accion")}_{ruta_original.split("/")[-1]}' # nombre para la nueva imagen
       fs.save(nombre_resultado, ContentFile(buffer.read())) # lee los butes del buffer y los envuelve en un ContentFile para escribir en fisco con fs
       buffer.close()
      
       imagen_url = ruta_original
       procesada_url = fs.url(nombre_resultado)
      
   return [imagen_url, procesada_url]

            
def index(request):
   imagen_url = request.POST.get('imagen_actual') if request.method == 'POST' else None # obtiene la imagen actual si es POST
   procesada_url = None
   fs = FileSystemStorage()  # usa MEDIA_ROOT y MEDIA_URL automáticamente, están definidos en settings.py
  
   # subir una imagen
   if request.method == 'POST' and request.FILES.get('imagen'): # comprueba si contiene un archivo con clave imagen
       imagen = request.FILES['imagen'] # obtiene el archivo subido
       nombre_archivo = fs.save(imagen.name, imagen) # guarda el archivo en el almacenamiento (MEDIA_ROOT) y devuelve el nombre de guardado
       imagen_url = fs.url(nombre_archivo)  # genera /media/nombre.png
          
   #=====RGB=======
   # EXTRACT R
   elif request.method == 'POST' and request.POST.get('accion') == 'extract_R':
       result = extract_layer(request, imagen_url, procesada_url, fs, 0, "rgb")
       imagen_url = result[0]
       procesada_url = result[1]
   # EXTRACT G
   elif request.method == 'POST' and request.POST.get('accion') == 'extract_G':
       result = extract_layer(request, imagen_url, procesada_url, fs, 1, "rgb")
       imagen_url = result[0]
       procesada_url = result[1]
   # EXTRACT B
   elif request.method == 'POST' and request.POST.get('accion') == 'extract_B':
       result = extract_layer(request, imagen_url, procesada_url, fs, 2, "rgb")
       imagen_url = result[0]
       procesada_url = result[1]
      
   #=====CMY=======
   elif request.method == 'POST' and request.POST.get('accion') == 'extract_C':
       result = extract_layer(request, imagen_url, procesada_url, fs, 0, "cmy")
       imagen_url = result[0]
       procesada_url = result[1]
   # EXTRACT G
   elif request.method == 'POST' and request.POST.get('accion') == 'extract_M':
       result = extract_layer(request, imagen_url, procesada_url, fs, 1, "cmy")
       imagen_url = result[0]
       procesada_url = result[1]
   # EXTRACT B
   elif request.method == 'POST' and request.POST.get('accion') == 'extract_Y':
       result = extract_layer(request, imagen_url, procesada_url, fs, 2, "cmy")
       imagen_url = result[0]
       procesada_url = result[1]
      
   #=====NEGATIVO=======
   elif request.method == 'POST' and request.POST.get('accion') == 'negativo':
       result = extract_layer(request, imagen_url, procesada_url, fs, None, None)
       imagen_url = result[0]
       procesada_url = result[1]
    #=====GRISES=======  
   elif request.method == 'POST' and request.POST.get('accion') == 'grayscale':
       tipo = request.POST.get('tipo_grises')
       result = extract_layer(request, imagen_url, procesada_url, fs, None, None, tipo)
       imagen_url = result[0]
       procesada_url = result[1]
       
   context = {
       'imagen_url': imagen_url,
       'procesada_url': procesada_url
   }
   return render(request, 'index.html', context)

