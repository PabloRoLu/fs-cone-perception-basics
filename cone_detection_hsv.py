import cv2
import matplotlib.pyplot as plt
import numpy as np
imagen=np.zeros((500,500,3),dtype="uint8")
cono_azul=np.array([[80,360],[130,180],[180,360]],np.int32)
cv2.fillPoly(imagen,[cono_azul],(255,0,0))
cono_amarillo=np.array([[210,370],[260,190],[310,370]],np.int32)
cv2.fillPoly(imagen,[cono_amarillo],(0,255,255))
cono_naranja=np.array([[340, 380], [390, 200], [440, 380]],np.int32)
cv2.fillPoly(imagen,[cono_naranja],(0,140,255))
#Creamos 3 tipos de conos con colores distintos#
cv2.circle(imagen,(40,40),3,(255,255,255),-1)
cv2.circle(imagen,(460,60),3,(255,255,255),-1)
cv2.circle(imagen,(430,460),3,(255,255,255),-1)
#Creamos circulos blancos que van a servir como ruido#
hsv=cv2.cvtColor(imagen,cv2.COLOR_BGR2HSV)
#Pasamos la imagen de BGR a HSV, HSV lo que hace es separar el tono (color)-H, su saturacion -S#
#Y su brillo-V#
rango_azul=(np.array([100,80,80]),np.array([130,255,255]))
#Creamos una tupla de 2 extremos, usamos 2 np.array() el primero marca el limite inferior del HSV, siendo el primer caracter H despues S y despues V#
#H (hue/tono) en OpenCV tiene un valor de 0 a 179, S (Saturation) tiene un valor de 0 (gris) a 255 (color muy vivo) y V (Value/brillo) cuan claro u obscuro es 0 (negro) y 255 (muy brillante)#
#En este caso en el primer np.array utilizamos los limites inferiores de HSV y en el segundo los limites superiores de HSV#
#En este caso usamos el np.array() ya que OpenCV es lo que espera, es una lista de 3 vectores y la conversion la hace OpenCV pero tiene que ser mediante un arreglo de numpy#
#Entonces el motivo de hacer este rango es en un futuro va a escanear la imagen y si cumple con estos requisitos#
#Entre 100 y 130 se encuentra el azul (H), despues de 80 a 255 es que no acepta colores grises (S), y de 80 a 255 es que este medio brillante el color (V)#
#Simplificando lo que hacemos es crear una logica de deteccion de estos colores#
rango_amarillo=(np.array([20,80,80]),np.array([32,255,255]))
#Hacemos lo mismo àra el rango amarillo la saturacion y brillo siempre van del 0 al 255 pero en H lo ponemos de 20 a 32 que es el rango de amarillo#
rango_naranja=(np.array([5,80,80]),np.array([18,255,255]))
#Lo mismo en el naranja, su rango de naranja (H) se encuentra de 5 a 18#
colores={
    "Blue":{"rango":rango_azul,"caja":(255,0,0)},
    "Yellow":{"rango":rango_amarillo,"caja":(0,255,255)},
    "Orange":{"rango":rango_naranja,"caja":(0,140,255)}
}
#Creamos un diccionario para los colores, en este caso "caja" no es para detectar colores, es para que una vez detectados estos colores se dibuje el rectangulo con el valor asignado#
resultado_bgr=imagen.copy()
kernel=np.ones((3,3),np.uint8)
for nombre,datos in colores.items():
    #Nosotros tenemos un diccionario de colores y un diccionario tiene llaves y valores, la funcion .items() nos da ambos valores#
    #Las llaves en este caso serian "Blue","Yellow" y "Orange" y los valores son el rango y la caja#
    #Le asignamos el valor de nombre a las llaves y de datos a los valores e iteramos sobre estos#
    bajo,alto=datos["rango"]
    #Para el valor de "rango" hay que recordar que son los limites de HSV que marcamos anteriormente#
    #Como creamos una tupla de 2 extremos con bajo y alto susbtaremos estas 2 tuplas por separado#
    mascara=cv2.inRange(hsv,bajo,alto)
    #La funcion cv2.inRange() responde a la pregunta, de la imagen (en HSV obligatoriamente) que pixeles caen entre este color minimo y este color maximo#
    #Por eso el orden de la funcion es primero la imagen en HSV (Donde mirar), despues el limite inferior (desde que color) y el limite superior (hasta que color)
    #De esta forma esta funcion devuelve una "mascara" de un tono, es decir si cumple las caracteristicas devuelve 0 o 255 (255 si cae en las especificaciones 0 de lo contrario)#
    #De esta forma cv2.inRange() separa los pixeles de los colores que queremos de los que no, nos devuelve una imagen unicamente con los pixeles que cumplen nuestros requisitos#
    #De esta forma al hacer cv2.findContours() solo estan los pixeles del color que buscamos y no se "confunde"#
    mascara=cv2.morphologyEx(mascara,cv2.MORPH_CLOSE,kernel,iterations=2)
    #Usamos la funcion cv2.morphologyEx() porque la imagen que nos devuelve cv2.inRange() no es perfecta, puede que haya pixeles dentro del objeto que no hayan cumplido el requerimiento#
    #O pixeles fuera del objeto que por accidente hayan cumplido el requerimiento, por eso usamos primero cv2.MORPH_CLOSE#
    #Recordemos que cv2.MORPH_CLOSE lo que hace es dilatar y luego erosionar, logrando de esta forma rellenar los huecos del objeto sin cambiar mucho su diseño original#
    mascara=cv2.morphologyEx(mascara,cv2.MORPH_OPEN,kernel,iterations=1)
    #Volvemos a usar la funcion cv2.morphologyEx() pero ahora para eliminar el "ruido" exterior, usamos la funcion cv2.MORPH_OPEN#
    #Lo que hace esta funcion es erosionar y luego dilatar, lo que consigue con esto es eliminar el "ruido" exterior logrando quedarnos con la version mas cercana de la imagen#
    ##
    contornos,_=cv2.findContours(mascara,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    #Ya con la imagen limpia para cada color sacamos los ejes de los conos, usamos la funcion cv2.RETR_EXTERNAL para solo sacar los puntos de fuera del objeto, es decir su perimetro#
    #Y la funcion cv2.CHAIN_APPROX_SIMPLE para solo obtener los 3 ejes de los conos y no todas las coordenadas, es decir no todo el perimetro# 
    for c in contornos:
        #Iteramos por cada vector del contorno#
        area=cv2.contourArea(c)
        #Obtenemos el area#
        if area>100:
            M=cv2.moments(c)
            #Sacamos su momento#
            if M!=0:
                cx=int(M["m10"]/M["m00"])
                cy=int(M["m01"]/M["m00"])
                #Sacamos su centro de masa dentro de x e y#
            x,y,w,h=cv2.boundingRect(c)
            #Obtenemos las coordenadas de la caja que delimita nuestro cono#
            cv2.rectangle(resultado_bgr,(x,y),(x+w,y+h),datos["caja"],2)
            #Dibujamos el rectangulo para el cono, de color le ponemos el de su caja en ese momento (Azul, Amarillo o Naranja)#
            cv2.circle(resultado_bgr,(cx,cy),5,(0,0,255),-1)
            #Hacemos un circulo rojo de radio 5 pixeles en su centro de masa#
            cv2.putText(resultado_bgr,nombre,(x,y-8),cv2.FONT_HERSHEY_SIMPLEX,0.6,datos["caja"],2)
            #Al poner el texto le ponemos y-8 de esta forma estamos "subiendo" el texto ya que y va de arriba hacia abajo#
            print(f"{nombre} \n Área:{area}px^2 \n Centro de masa X={cx} Y={cy}")
original_rgb=cv2.cvtColor(imagen,cv2.COLOR_BGR2RGB)
resultado_rgb=cv2.cvtColor(resultado_bgr,cv2.COLOR_BGR2RGB)
plt.figure(figsize=(12,6))
plt.subplot(1,2,1)
plt.title("Imagen original")
plt.imshow(original_rgb)
plt.axis("off")
plt.subplot(1,2,2)
plt.title("Detección HSV + Bounding Boxes")
plt.imshow(resultado_rgb)
plt.axis("off")
plt.tight_layout()
#Lo que hace la funcion plt.tight_layout() es recalcular los margenes de separacion de la imagen para que se vean bien#
plt.show()
