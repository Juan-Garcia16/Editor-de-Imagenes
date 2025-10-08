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
            # action determina la operación a aplicar. Por defecto 'bright' para que se presente la imagen.
            action = request.POST.get("action", "bright")

            # Abrir imagen y normalizar 
            image = Image.open(request.FILES["image"]).convert("RGB")
            img_np = np.asarray(image, dtype=np.float32) / 255.0

            # Dispatch simple: elegir la función según action
            if action == "bright":
                brillo = float(request.POST.get("brillo", 0))
                result_np = imgPro.bright(img_np, brillo)
                
            elif action == 'R_channel':
                valor = float(request.POST.get("R_channel", 0))
                result_np = imgPro.bright_layer(img_np, valor, 0)
            elif action == 'G_channel':
                valor = float(request.POST.get("G_channel", 0))
                result_np = imgPro.bright_layer(img_np, valor, 1)
            elif action == 'B_channel':
                valor = float(request.POST.get("B_channel", 0))
                result_np = imgPro.bright_layer(img_np, valor, 2)
                
            elif action == "log_contrast":
                contraste = float(request.POST.get("log_contrast", 0))
                result_np = imgPro.contrast_dark(img_np, contraste)

            elif action == "exp_contrast":
                contraste = float(request.POST.get("exp_contrast", 0))
                result_np = imgPro.contrast_light(img_np, contraste)


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
                
            elif action == "negative":
                result_np = imgPro.negative(img_np)

            elif action == "grayscale":
                # leer parámetro 'tipo' (string)
                tipo = request.POST.get("tipo", "")
                # empezar con la imagen normalizada
                result_np = img_np.copy()

                if tipo == 'average':
                    result_np = imgPro.average(result_np)
                elif tipo == 'luminosity':
                    result_np = imgPro.luminosity(result_np)
                elif tipo == 'midgray':
                    result_np = imgPro.midgray(result_np)
                else:
                    result_np = img_np #no aplicar nada
                    
                    
            # --- FUSION: promedio simple ---
            elif action == 'merge':
                # requiere ambos archivos
                if not request.FILES.get('image') or not request.FILES.get('image2'):
                    return JsonResponse({'error': 'Se requieren dos imágenes para fusionar.'}, status=400)

                resize_method = request.POST.get('resize_method', 'resize_to_smaller') #opciones: resize_to_smaller, resize_to_larger, resize_second_to_first, por defecto resize_to_smaller

                # abrir ambas con PIL
                img1_pil = Image.open(request.FILES['image']).convert('RGB')
                img2_pil = Image.open(request.FILES['image2']).convert('RGB')


                try:
                    result_np = imgPro.fusion_images(img1_pil, img2_pil, resize_method=resize_method)
                except Exception as e:
                    return JsonResponse({'error': f'Error fusionando: {e}'}, status=500)

                # Asegurar rango y devolver
                result_np = np.clip(result_np, 0, 1)
                data_url = _to_data_url(result_np)
                return JsonResponse({'image': data_url})

            # --- FUSION ECUALIZADA: factor entre 0..1 ---
            elif action == 'merge_eq': #slider factor
                if not request.FILES.get('image') or not request.FILES.get('image2'):
                    return JsonResponse({'error': 'Se requieren dos imágenes para fusionar.'}, status=400)

                # parsear factor
                try:
                    factor = float(request.POST.get('factor', 0.5))
                except ValueError:
                    return JsonResponse({'error': 'factor invalido'}, status=400)
                factor = max(0.0, min(1.0, factor))

                resize_method = request.POST.get('resize_method', 'resize_to_smaller')

                # Abrir ambas imágenes
                img1_pil = Image.open(request.FILES['image']).convert('RGB')
                img2_pil = Image.open(request.FILES['image2']).convert('RGB')

                # Verificar si son del mismo tamaño: calcular target con image_resize y redimensionar
                w1, h1 = img1_pil.size
                w2, h2 = img2_pil.size
                target_size = imgPro.image_resize(img1_pil, img2_pil, resize_method, w1, h1, w2, h2)
                if (w1, h1) != target_size:
                    img1_pil = img1_pil.resize(target_size)
                if (w2, h2) != target_size:
                    img2_pil = img2_pil.resize(target_size)

                # Convertir a numpy normalizado
                img1_np = np.asarray(img1_pil, dtype=np.float32) / 255
                img2_np = np.asarray(img2_pil, dtype=np.float32) / 255

                try:
                    result_np = imgPro.fusion_images_ecualized(img1_np, img2_np, factor)
                except Exception as e:
                    return JsonResponse({'error': f'Error fusionando ecualizadas: {e}'}, status=500)

                result_np = np.clip(result_np, 0, 1)
                data_url = _to_data_url(result_np)
                return JsonResponse({'image': data_url})
                                
                    
                    
                    
                    

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
