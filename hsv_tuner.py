import cv2
import numpy as np
ruta=r"C:\Users\pablo\Pictures\cono_real.jpg"
imagen=cv2.imread(ruta)
if imagen is None:
    raise FileNotFoundError(f"No se encontro {ruta}")
alto,ancho=imagen.shape[:2]
if ancho>900:
    escala=900/ancho
    imagen=cv2.resize(imagen,(900,int(alto*escala)))
hsv=cv2.cvtColor(imagen,cv2.COLOR_BGR2HSV)
def nada(_):
    pass
#Creamos esta funcion ya que OpenCV nos lo pide al momento de usar la funcion "cv2.createTrackbar()"#
#Lo hacemos para que no pete, es decir esta funcion no devuele nada, por eso ponemos _#
cv2.namedWindow("HSV tuner",cv2.WINDOW_NORMAL)
#Creamos el marco de la ventana usando la funcion cv2.namedWindow() #
#El primer valor es el titulo y el segundo que tipo de ventana vamos a utilizar#
#En nuestro caso utilizamos cv2.WINDOW_NORMAL, es decir como se va a comportar esa ventana que acabamos de crear
cv2.createTrackbar("H min","HSV tuner",20,179,nada)
#La funcion cv2.createTrackbar() lo que hacemos es crear las barras que se utilizan para mover#
#Le ponemos el titulo, despues ponemos en que ventana se va a poner, en nuestro caso la que acabamos de crear#
#Despues el primer valor numerico es el valor default con el que va a salir en la ventana#
#Despues ponemos el valor maximo y al final como se va a mover la barra, le ponemos la funcion nada#
#Ya que la funcion cv2.createTrackbar() pide un argumento final donde se le tiene que indicar una funcion cada vez que muevan el slider#
#createTrackbar( nombre , ventana , valor_inicial , valor_máximo , callback )#
cv2.createTrackbar("H max","HSV tuner",38,179,nada)
cv2.createTrackbar("S min","HSV tuner",70,255,nada)
cv2.createTrackbar("S max","HSV tuner",255,255,nada)
cv2.createTrackbar("V min","HSV tuner",70,255,nada)
cv2.createTrackbar("V max","HSV tuner",255,255,nada)
#Creamos 6 barras cada uno con los maximos y minmos de HSV en la ventana "HSV tuner"#
#Les ponemos valores maximos y un valor default#
print(f"q=Salir | p=Imprimir rango actual")
while True:
    #Creamos el while para que cada vez que movamos la barra la imagen se vea afectada por los nuevos valores#
    h_min=cv2.getTrackbarPos("H min","HSV tuner")
    #La funcion cv2.getTrackbarPos() devuelve un entero, dice donde esta la barra#
    #Sigue la siguiente anatomia cv2.getTrackbarPos(nombre_slider,nombre_ventana)
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
    #La funcion cv2.bitwise_and() esta diseñada para mezlar 2 fotos, sigue la siguiente anatomia#
    #cv2.bitwise_and(foto_A, foto_B, mask=), nuestro caso lo que queremos hacer con esta funcion es#
    #Generar otra imagen pero a diferencia de la original y de la imagen de mascara (Blanco y negro)
    #Nosotros vamos a guardar unicamente como se veria la imagen original si le aplicaramos la mascara#
    #Es decir como se veria a color la imagen con la mascara aplicada#
    mascara_bgr=cv2.cvtColor(mascara,cv2.COLOR_GRAY2BGR)
    #Pasamos la mascara a BGR para que al juntarlas con las otras 2 imagenes no haya problemas con las dimensiones#
    panel=np.hstack([imagen,mascara_bgr,recorte])
    #La funcion np.hstack (horizontal stack) pega unos arrays uno a lado de otro#
    cv2.imshow("HSV tuner",panel)
    #Mostramos la ventana donde estan las barras junto a las imagenes (la original, la blanco y negro y la tercera que es como se veria la original con esos filtros#
    tecla=cv2.waitKey(30) & 0xFF
    #La funcion cv2.waitkey() lo que hace es ver cada tiempo (milisegundos) si se pulso una tecla#
    #Le añadimos & OxFF (255 en hexadecimal) ya que cv2.waitkey() devuelve un numero de 32 bits con bits basura en los bits altos#
    #Asi que para que no haya error ponemos ese & 0xFF que le dice que solo se quede con los 8 bits de la derecha#
    #Tambien la funcion cv2.waitKey() pone el reloj del while, es decir cada 30 milisegundos el while da una vuelta#
    if tecla==ord("q"):
        #Como cv2.waitkey() devuelve un numero (codigo ASCII) para que no tengamos problemas#
        #En igualar un numero con un caracter utilizamos la funcion ord(), ya que esta funcion nos devuelve el numero del caracter#
        break
    if tecla==ord("p"):
        print("bajo=np.array([{},{},{}])".format(h_min,s_min,v_min))
        print("alto=np.array([{},{},{}])".format(h_max,s_max,v_max))
        #Imprimimos los limites de la deteccion del HSV, pudimos haberlo hecho con f string pero es lo mismo#
cv2.destroyAllWindows()
#Si se pulsa la tera q borramos las ventanas del programa#