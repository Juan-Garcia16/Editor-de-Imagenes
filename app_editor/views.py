import numpy as np
from django.shortcuts import render
from django.http import JsonResponse
from PIL import Image
import io, base64
from django.views.decorators.csrf import csrf_exempt

def index(request):
    return render(request, "index.html")

def bright(img, brillo):
    """
    Altera el brillo de una imagen normalizada [0 , 1].
    """
    img_cop = np.copy(img)
    img_cop = img_cop + brillo
    img_cop = np.clip(img_cop, 0, 1)
    return img_cop


def extract_channel(img, channel):
    """
    Extrae una capa RGB de una imagen normalizada [0,1].
    - img: numpy array H,W,3 con valores en [0,1]
    - channel: 'R', 'G' o 'B' (case-insensitive)

    Devuelve una imagen H,W,3 donde sólo la componente solicitada conserva
    su valor original y las demás quedan en 0. Esto facilita mostrar sólo
    la capa seleccionada manteniendo la estructura RGB para que el navegador
    la renderice correctamente.
    """
    ch = channel.upper() if isinstance(channel, str) else 'R'
    idx_map = {'R': 0, 'G': 1, 'B': 2}
    if ch not in idx_map:
        ch = 'R'
    idx = idx_map[ch]
    out = np.zeros_like(img)
    out[..., idx] = img[..., idx]
    return out


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
                result_np = bright(img_np, brillo)
            elif action == "channel":
                # Esperamos un parámetro 'channel' con 'R'|'G'|'B'
                channel = request.POST.get("channel", "R")
                result_np = extract_channel(img_np, channel)
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
