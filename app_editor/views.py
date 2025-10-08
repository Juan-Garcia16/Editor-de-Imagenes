import numpy as np
from django.shortcuts import render
from django.http import JsonResponse
from PIL import Image
import io, base64
from django.views.decorators.csrf import csrf_exempt
from .utils import imgPro

def index(request):
    return render(request, "index.html")

def _to_data_url(img_array):
    """
    Convierte un numpy array normalizado [0,1] a una data URL PNG (base64).
    Retorna la string completa: "data:image/png;base64,..."
    """
    result = (img_array * 255).astype(np.uint8)
    img_out = Image.fromarray(result)
    buffer = io.BytesIO()
    img_out.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"

@csrf_exempt
def process_image(request):
    try:
        # Este endpoint soporta varias 'actions' (por ejemplo 'bright' o 'channel').
        # El frontend envía un multipart/form-data con al menos el campo 'image'.
        if request.method == "POST" and request.FILES.get("image"):
            # action determina la operación a aplicar. Por defecto 'bright'.
            action = request.POST.get("action", "bright")

            # Abrir imagen y normalizar a float en [0,1]
            image = Image.open(request.FILES["image"]).convert("RGB")
            img_np = np.asarray(image, dtype=np.float32) / 255.0

            # Dispatch simple: elegir la función según action
            if action == "bright":
                brillo = float(request.POST.get("brillo", 0))
                result_np = imgPro.bright(img_np, brillo)

            elif action == "rgb_layer":
                # 'capa' puede venir como '0','1','2' o 'R','G','B'
                capa_raw = request.POST.get("capa", "0")
                try:
                    capa = int(capa_raw)
                except ValueError:
                    map_chr = {'R':0,'G':1,'B':2}
                    capa = map_chr.get(capa_raw.upper(), 0)
                if capa not in (0,1,2):
                    return JsonResponse({"error":"capa invalida"}, status=400)
                result_np = imgPro.extract_layer_rgb(img_np, capa)

            elif action == "cmy_layer":
                # 'capa' puede venir como '0','1','2' o 'C','M','Y'
                capa_raw = request.POST.get("capa", "0")
                try:
                    capa = int(capa_raw)
                except ValueError:
                    map_chr = {'C':0,'M':1,'Y':2}
                    capa = map_chr.get(capa_raw.upper(), 0)
                if capa not in (0,1,2):
                    return JsonResponse({"error":"capa invalida"}, status=400)
                result_np = imgPro.extract_layer_cmy(img_np, capa)

            else:
                return JsonResponse({"error": f"Operacion no soportada: {action}"}, status=400)

            # Convertir el resultado a data URL y devolver JSON
            data_url = _to_data_url(result_np)
            return JsonResponse({"image": data_url})
        else:
            return JsonResponse({"error": "No se recibió imagen"}, status=400)
    except Exception as e:
        # En caso de error, mostramos mensaje en consola y devolvemos JSON
        print("Error al procesar la imagen:", e)
        return JsonResponse({"error": str(e)}, status=500)
