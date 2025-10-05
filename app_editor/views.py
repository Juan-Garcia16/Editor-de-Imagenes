from django.shortcuts import render
from django.core.files.storage import FileSystemStorage # Importa FileSystemStorage para manejar archivos

# Create your views here.
def index(request):
    imagen_url = None
    # Si se envió un formulario
    if request.method == 'POST' and request.FILES.get('imagen'):
        imagen = request.FILES['imagen']
        fs = FileSystemStorage()  # usa MEDIA_ROOT automáticamente
        nombre_archivo = fs.save(imagen.name, imagen)
        imagen_url = fs.url(nombre_archivo)  # genera /media/nombre.png
        
    return render(request, 'index.html', {'imagen_url': imagen_url})