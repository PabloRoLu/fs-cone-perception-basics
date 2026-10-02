import numpy as np
import cv2

ruta = r"C:\Users\pablo\Downloads\track.MOV"
cap = cv2.VideoCapture(ruta)
if not cap.isOpened():
    raise FileNotFoundError(f"No se pudo abrir {ruta}")

rango_amarillo = (np.array([13, 40, 30]), np.array([35, 255, 255]))
rango_naranja = (np.array([0, 55,75]), np.array([10, 255, 255]))
rango_azul = (np.array([90, 40, 30]), np.array([130, 255, 255]))
colores = {
    "Yellow": {"rango": rango_amarillo, "caja": (0, 255, 255)},
    "Orange": {"rango": rango_naranja, "caja": (0, 140, 255)},
    "Blue": {"rango": rango_azul, "caja": (255, 0, 0)},
}
kernel = np.ones((5, 5), np.uint8)
#Creamos un kernel de 5x5 para que no se deforme los conos lejanos al aplicar las operaciones morfologicas#
cockpit = np.array([
    (0.31, 1.00), (0.36, 0.84), (0.50, 0.74), (0.51, 0.70),
    (0.70, 0.70), (0.76, 0.78), (0.90, 0.84), (0.96, 1.00),
])
#Dividimos el cockpit en 8 puntos
mascara_coche = None
#Creamos la variable para la mascara del cockpit#
anteriores = {nombre: [] for nombre in colores}
#Creamos un diccionario por comprension para los centros de cajas del boundingbox del frame pasado para compararlos con el frame actual
print("q = salir")

while True:
    ok, frame = cap.read()
    if not ok:
        break
    #Cuando ya no haya frames terminamos el while

    alto, ancho = frame.shape[:2]
    if max(alto, ancho) > 900:
        escala = 900 / max(alto, ancho)
        frame = cv2.resize(frame, (int(ancho * escala), int(alto * escala)))
        alto, ancho = frame.shape[:2]
        #Si cada frame es mayor a 900 pixeles lo encogemos

    if mascara_coche is None:
        mascara_coche = np.full((alto, ancho), 255, np.uint8)
        #Creamos una imagen blanca del alto y ancho de los frames
        puntos = (cockpit * [ancho, alto]).astype(np.int32)
        #Definimos los puntos del cockpit de manera que OpenCV los pueda leer
        cv2.fillPoly(mascara_coche, [puntos], 0)
        #Unimos los puntos del cockpit y dentro de esos puntos solo va a ver pixeles negros

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #Pasamos el frame de BGR a HSV
    resultado_bgr = frame.copy()
    actuales = {nombre: [] for nombre in colores}
    #Creamos otro diccionario por comprension, esta vez dentro del while de esta forma los centros de conos van a estar en el frame actual

    for nombre, datos in colores.items():
        #Iteramos sobre el diccionario de colores#
        bajo, alto_hsv = datos["rango"]
        #Asignamos los limites para la mascara
        mascara = cv2.inRange(hsv, bajo, alto_hsv)
        #Creamos la mascara para el frame en HSV
        mascara = cv2.bitwise_and(mascara, mascara_coche)
        #Solo deja el pixel si es blanco en ambas mascaras, que sea blanco en ambas cara significa
        #Que en mascara tiene que estar dentro del rango hsv y en mascara_coche que no este en el cockpit
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel, iterations=2)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel, iterations=1)
        #Hacemos las operaciones morfologicas para limpiar el frame
        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #Obtenemos el contorno del color de los objetos que detecto

        for c in contornos:
            area = cv2.contourArea(c)
            if area < 50:
                continue
            #Si el area es menor a 50 pixeles^2 lo descartamos

            x, y, w, h = cv2.boundingRect(c)
            #Obtenemos los puntos del boundingbox de cada objeto detectado que haya pasado el filtro
            cx = x + w / 2.0
            cy = y + h / 2.0
            #Obtenemos sus centros en cada eje

            if w < 6 or h < 10 or h < 1.03 * w or h > 4.2 * w or w * h > 0.02 * ancho*alto or y+h < alto * 0.54 or  x <= 1 or x + w >= ancho - 1 or area/(w*h)<0.33:
                continue
            #Creamos las condiciones para descartar objetos que no sean los conos
            silueta = np.zeros((h, w), np.uint8)
            #Creamos un lienzo en negro del boundingbox
            cv2.drawContours(silueta, [c], -1, 255, -1, offset=(-x, -y))
            #Convertimos el contorno del cono en pixeles blancos sobre el lienzo negro
            tercio = max(1, h // 3)
            #Usamos max para garantizar que tercio sea como minimo 1
            #Sacamos "un tercio del cono"
            ancho_arriba = np.count_nonzero(silueta[:tercio]) / tercio
            ancho_abajo = np.count_nonzero(silueta[-tercio:]) / tercio
            #Dividimos el valor de los pixeles blancos del numero de filas del tercio inicial o final entre el numero del tercio para saber la media por fila de pixeles blancos
            if ancho_arriba > ancho_abajo:
                #Si tenemos mas pixeles blancos en el ancho de arriba que en el de abajo descartamos ese boundingbox
                continue

            
            actuales[nombre].append((cx, cy))

            if not any(abs(cx - px) < 25 and abs(cy - py) < 25 for px, py in anteriores[nombre]):
                #Creamos una condicion donde descartamos el boundingbox si solo aparece en un frame o en el siguiente tiene una posicion muy alejada
                continue

            cv2.rectangle(resultado_bgr, (x, y), (x + w, y + h), datos["caja"], 2)
            cv2.putText(resultado_bgr,nombre,(x, max(20, y - 8)),cv2.FONT_HERSHEY_SIMPLEX,0.55,datos["caja"],2,)
            #Si pasa todos los filtros dibujamos el boundingbox#

    anteriores = actuales
    #Guardamos los centros de cada boundingbox del actual frame para el siguiente frame y asi podamos comparar
    #Comparar si los centros detectados son parecidos en distancia (<25) a su otro centro
    cv2.imshow("Cone detection video", resultado_bgr)
    if cv2.waitKey(16) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()