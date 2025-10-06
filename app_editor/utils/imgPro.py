import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def layer(img, capa):
    """
    Extrae una capa específica (0=Rojo, 1=Verde, 2=Azul) de una imagen RGB.
    """
    img_capa = np.zeros_like(img)
    img_capa[:,:,capa] = img[:,:, capa]
    return img_capa

def cyan(img):
    """
    Extrae la capa cian de una imagen RGB.
    """
    image_cyan = img.copy()
    image_cyan[:,:,0] = 0 # Cancelar capa roja
    return image_cyan

def magenta(img):
    """
    Extrae la capa magenta de una imagen RGB.
    """
    image_magenta = img.copy()
    image_magenta[:,:,1] = 0 # Cancelar capa verde
    return image_magenta

def yellow(img):
    """
    Extrae la capa amarilla de una imagen RGB.
    """
    image_yellow = img.copy()
    image_yellow[:,:,2] = 0 # Cancelar capa azul
    return image_yellow

def remove_layer(img, capa):
    """
    Elimina una capa específica (0=Rojo, 1=Verde, 2=Azul) de una imagen RGB.
    """
    img_copia = np.copy(img)
    img_copia[:,:,capa] = 0
    return img_copia

def extract_layer_rgb(img, capa):
    """
    Extrae una capa específica (0=Rojo, 1=Verde, 2=Azul) de una imagen RGB.
    """
    img_capa = np.zeros_like(img)
    img_capa[:,:,capa] = img[:,:, capa]
    return img_capa

def extract_layer_cmy(img, capa):
    """
    Extrae una capa específica (0=Cian, 1=Magenta, 2=Amarillo) de una imagen RGB.
    
    La imagen se convierte a CMY, se aísla la capa indicada y 
    se devuelve en formato RGB para visualizarla correctamente.
    """
    # Convertir de RGB a CMY
    cmy = 1 - img

    cmy_capa = np.zeros_like(cmy)

    # Conservar solo la capa indicada (C, M o Y)
    cmy_capa[:, :, capa] = cmy[:, :, capa]

    # Convertir de nuevo a RGB para visualizar
    rgb_resultado = 1 - cmy_capa

    return rgb_resultado


def reverse(img):
    """
    Invierte los colores de una imagen.
    """
    image_reverse = 1 - img
    return image_reverse



def image_resize(img1, img2, resize_method, w1, h1, w2, h2):
    """
    Determina el tamaño objetivo para redimensionar dos imágenes según el método especificado.
    """
    if resize_method == 'resize_to_smaller':
        target_size = (min(w1, w2), min(h1, h2))
    elif resize_method == 'resize_to_larger':
        target_size = (max(w1, w2), max(h1, h2))
    else:  # resize_second_to_first
        target_size = (w1, h1)
    return target_size
    
def fusion_images(img1, img2, resize_method='resize_to_smaller'):
    """
    Fusiona dos imágenes promediando sus píxeles.
    
    Parámetros:
    - img1, img2: Las imágenes a fusionar
    - resize_method: 'resize_to_smaller', 'resize_to_larger', 'resize_second_to_first'
    - resize_method por defecto es 'resize_to_smaller'
    """
    # Convertir a PIL si es necesario
    if isinstance(img1, np.ndarray):
        img1_pil = Image.fromarray((img1 * 255).astype(np.uint8))
    else:
        img1_pil = img1
    
    if isinstance(img2, np.ndarray):
        img2_pil = Image.fromarray((img2 * 255).astype(np.uint8))
    else:
        img2_pil = img2
    
    # Obtener dimensiones
    w1, h1 = img1_pil.size
    w2, h2 = img2_pil.size
    
    # Redimensionar solo si es necesario
    if (w1, h1) != (w2, h2):
        target_size = image_resize(img1, img2, resize_method, w1, h1, w2, h2)
        img1_pil = img1_pil.resize(target_size)
        img2_pil = img2_pil.resize(target_size)
    
    # Convertir de vuelta a numpy y fusionar
    img1_np = np.array(img1_pil) / 255.0
    img2_np = np.array(img2_pil) / 255.0
    
    return (img1_np + img2_np) / 2

def fusion_images_ecualized(img1, img2, factor):
    """
    Fusiona dos imágenes con un factor específico de ecualización, solo fusiona
    imágenes del mismo tamaño.
    """
    if img1.shape != img2.shape:
        raise ValueError("Las imágenes deben tener el mismo tamaño para fusionarlas.")
    img_fusionada = factor * img1 + (1 - factor) * img2
    return img_fusionada

def average(img):
    """
    Convierte una imagen a escala de grises usando el método del promedio."""
    img_copia = np.copy(img)
    return (img_copia[:,:,0] + img_copia[:,:,1] + img_copia[:,:,2]) / 3

def luminosity(img):
    """
    Convierte una imagen a escala de grises usando el método de luminosidad.
    """
    img_copia = np.copy(img)
    return 0.299*img_copia[:,:,0] + 0.587*img_copia[:,:,1] + 0.114*img_copia[:,:,2]

def midgray(img):
    """
    Convierte una imagen a escala de grises usando el método de gris medio.
    """
    img_copia = np.copy(img)
    midgray = (np.maximum(img_copia[:,:,0], img_copia[:,:,1], img_copia[:,:,2]) +
               np.minimum(img_copia[:,:,0], img_copia[:,:,1], img_copia[:,:,2]))/2
    return midgray

def bright(img, brillo):
    """
    Altera el brillo de una imagen normalizada [-1 , 1].
    """
    img_cop = np.copy(img)
    img_cop = img_cop + brillo
    img_cop = np.clip(img_cop, 0, 1)
    return img_cop

def bright_layer(img, brillo, capa):
    """
    Altera el brillo de una capa específica RGB de una imagen normalizada [-1 , 1].
    """
    img_capa = np.copy(img)
    img_capa[:,:,capa] = img[:,:,capa] + brillo
    return img_capa

def contrast_dark(img, contraste):
    """
    Aplica contraste oscuro usando transformación logarítmica.
    """
    img_cop = np.copy(img)
    img_cop = contraste * np.log10(1 + img_cop)
    img_cop = np.clip(img_cop, 0, 1)
    return img_cop

def contrast_light(img, contraste):
    """
    Aplica contraste claro usando transformación exponencial.
    """
    img_copia = np.copy(img)
    img_copia = contraste * np.exp(img_copia - 1)
    img_copia = np.clip(img_copia, 0, 1) 
    return contraste * np.exp(img_copia - 1)

def binarize(img, umbral):
    """
    Binariza una imagen normalizada usando un umbral específico.
    """
    img_copia = np.copy(img)
    img_gris = (img_copia[:,:,0] + img_copia[:,:,1] + img_copia[:,:,2]) / 3
    img_binaria = (img_gris > umbral)
    return img_binaria

def crop(img, xIni, yIni, xFin, yFin):
    """
    Deja una sección rectangular de la imagen definida por las coordenadas
    (xIni, yIni) y (xFin, yFin), siendo esquina superior izquierda y esquina inferior derecha respectivamente.
    """
    temp = yIni
    yIni = xIni
    xIni = temp
    
    temp = yFin
    yFin = xFin
    xFin = temp
    
    img_copia = np.copy(img)
    return img_copia[xIni:xFin, yIni:yFin]

def trasnslation(img, dx, dy):
    """
    Traslada una imagen dx píxeles en x y dy píxeles en y.
    Los píxeles que salen del borde se rellenan con negro.
    """
    trasladada = np.zeros_like(img)

    # Calcular límites válidos para el copiado
    h, w = img.shape[:2]
    x_origen_inicio = 0
    x_origen_fin = w - dx
    y_origen_inicio = 0
    y_origen_fin = h - dy

    # Asignar los valores trasladados
    trasladada[dy:h, dx:w] = img[y_origen_inicio:y_origen_fin, x_origen_inicio:x_origen_fin]

    return trasladada

def lower_resolution(img, zoom_factor):
    img_copia = np.copy(img)
    return img_copia[::zoom_factor, ::zoom_factor]

# def zoom(img, zoom_factor):
#     """
#     Aplica un zoom a una imagen normalizada.
#     """
#     img_copia = np.copy(img)
#     return np.kron(img_copia, np.ones((zoom_factor, zoom_factor, 1)))

def mhist (RGB, tipo='n', color='gray'):
    """
    Grafica el histograma de una imagen.
    Parámetros:
    - RGB: imagen en escala de grises o un canal (2D array)
    - tipo: 'p' para porcentaje, 'n' para conteo absoluto
    - color: color del histograma (ej. 'red', 'green', 'blue', 'gray')
    """
    formato = tipo.lower()
    filas, columnas = RGB.shape[:2]
    
    if formato == 'p':
        factor = (filas * columnas) / 100 # para mostrar en porcentaje
    else:
        factor = 1 # para mostrar en conteo
    histograma = np.zeros(256)

    for nivel in range(256):
        histograma[nivel] = np.sum(RGB == nivel) / factor
        
    plt.bar(np.arange(256), histograma, color=color, width=1) 
    plt.title("Histograma")
    plt.xlabel("Nivel de Intensidad (0-255)")
    plt.ylabel("Porcentaje" if formato == 'p' else "Frecuencia")
    plt.xlim([0, 255])
    plt.tight_layout() 
    plt.show()

def rotarImg(a, ang):
    """
    Rota una imagen en sentido antihorario por un ángulo dado.
    Parámetros:
    a (numpy.ndarray): Imagen de entrada representada como un arreglo 2D.
    ang (float): Ángulo de rotación en grados. Debe estar en el rango (0, π] radianes.
    Devuelve:
    numpy.ndarray: Imagen rotada con el mismo tipo de datos que la imagen de entrada.
    Excepciones:
    ValueError: Si el ángulo está fuera del rango esperado (0 < ang <= π).
    Notas:
    - La función convierte el ángulo de grados a radianes internamente.
    - La imagen de salida tendrá dimensiones ajustadas para contener la imagen rotada.
    - La rotación se realiza en sentido antihorario.
    """
    ang = np.radians(ang)  # Convertir a radianes
    m, n = a.shape
    cos_ang = np.cos(ang)
    sin_ang = np.sin(ang)

    if ang > 0 and ang <= np.pi / 2:
        c = int(round(m * sin_ang + n * cos_ang)) + 1
        d = int(round(m * cos_ang + n * sin_ang)) + 1
        b = np.zeros((c, d), dtype=a.dtype)
        for i in range(c):
            for j in range(d):
                iii = i - int(n * sin_ang) - 1
                ii = int(round(j * sin_ang + iii * cos_ang))
                jj = int(round(j * cos_ang - iii * sin_ang))
                if 0 <= ii < m and 0 <= jj < n:
                    b[i, j] = a[ii, jj]
    elif ang > np.pi / 2 and ang <= np.pi:
        c = int(round(m * sin_ang - n * cos_ang)) + 1
        d = int(round(m * sin_ang - n * cos_ang)) + 1
        e = -n * cos_ang
        b = np.zeros((c, d), dtype=a.dtype)
        for i in range(c):
            iii = c - i - 1
            for j in range(d):
                jjj = d - j - 1
                ii = int(round(jjj * sin_ang + iii * cos_ang))
                jj = int(round(jjj * cos_ang - iii * sin_ang))
                if 0 <= ii < m and 0 <= jj < n:
                    b[i, j] = a[ii, jj]
    else:
        raise ValueError("Ángulo fuera del rango esperado (0 < ang <= π)")

    return b