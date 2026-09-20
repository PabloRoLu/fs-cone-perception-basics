import cv2
import numpy as np
ruta="images/cono_real.jpg"
imagen=cv2.imread(ruta)
#Decodificamos la ruta para la imagen#
if imagen is None:
    raise FileNotFoundError(f"No se encontro {ruta}")
alto,ancho=imagen.shape[:2]
if ancho>900:
    escala=900/ancho
    imagen=cv2.resize(imagen,(900,int(alto*escala)))
    #Creamos una condicion de ancho para la imagen, si se cumple la condicion modificamos la imagen#
hsv=cv2.cvtColor(imagen,cv2.COLOR_BGR2HSV)
def nada(_):
    pass
#Creamos esta funcion ya que OpenCV nos lo pide al momento de usar la funcion "cv2.createTrackbar()"#
cv2.namedWindow("HSV tuner",cv2.WINDOW_NORMAL)
#Creamos el marco y el tipo de ventana#
cv2.createTrackbar("H min","HSV tuner",20,179,nada)
cv2.createTrackbar("H max","HSV tuner",38,179,nada)
cv2.createTrackbar("S min","HSV tuner",70,255,nada)
cv2.createTrackbar("S max","HSV tuner",255,255,nada)
cv2.createTrackbar("V min","HSV tuner",70,255,nada)
cv2.createTrackbar("V max","HSV tuner",255,255,nada)
#Creamos 6 barras cada uno con los maximos y minmos junto a un valor default de HSV en la ventana "HSV tuner"#
print(f"q=Salir | p=Imprimir rango actual")
while True:
    #Creamos el while para que cada vez que movamos la barra la imagen se vea afectada por los nuevos valores#
    h_min=cv2.getTrackbarPos("H min","HSV tuner")
    h_max=cv2.getTrackbarPos("H max","HSV tuner")
    s_min=cv2.getTrackbarPos("S min","HSV tuner")
    s_max=cv2.getTrackbarPos("S max","HSV tuner")
    v_min=cv2.getTrackbarPos("V min","HSV tuner")
    v_max=cv2.getTrackbarPos("V max","HSV tuner")
    #Obtenemos los valores de las barras en cada instante#
    bajo=np.array([h_min,s_min,v_min])
    alto=np.array([h_max,s_max,v_max])
    #Formamos los limites inferiores y superiores para la mascara#
    mascara=cv2.inRange(hsv,bajo,alto)
    recorte=cv2.bitwise_and(imagen,imagen,mask=mascara)
    #Generamos otra imagen pero a diferencia de la original y de la imagen de mascara (Blanco y negro)#
    #Guardamos unicamente como se veria la imagen original si le aplicaramos la mascara es decir como se veria a color la imagen con la mascara aplicada#
    mascara_bgr=cv2.cvtColor(mascara,cv2.COLOR_GRAY2BGR)
    #Pasamos la mascara a BGR para que al juntarlas con las otras 2 imagenes no haya problemas con las dimensiones#
    panel=np.hstack([imagen,mascara_bgr,recorte])
    #Pegamos las 3 imagenes juntas#
    cv2.imshow("HSV tuner",panel)
    #Mostramos la ventana donde estan las barras junto a las imagenes (la original, la blanco y negro y la tercera que es como se veria la original con esos filtros#
    tecla=cv2.waitKey(30) & 0xFF
    #Creamos una pausa de 30 milisegundos para que las imagenes puedan cambiar respecto a los valores de las barras#
    if tecla==ord("q"):
        break
    if tecla==ord("p"):
        print("bajo=np.array([{},{},{}])".format(h_min,s_min,v_min))
        print("alto=np.array([{},{},{}])".format(h_max,s_max,v_max))
cv2.destroyAllWindows()
#Si se pulsa la tera q borramos las ventanas del programa#
