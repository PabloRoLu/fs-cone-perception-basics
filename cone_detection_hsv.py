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
#Pasamos la imagen de BGR a HSV#
rango_azul=(np.array([100,80,80]),np.array([130,255,255]))
#Creamos una tupla de 2 extremos para cada color para generar una logica de deteccion de colores#
rango_amarillo=(np.array([20,80,80]),np.array([32,255,255]))
rango_naranja=(np.array([5,80,80]),np.array([18,255,255]))
colores={
    "Blue":{"rango":rango_azul,"caja":(255,0,0)},
    "Yellow":{"rango":rango_amarillo,"caja":(0,255,255)},
    "Orange":{"rango":rango_naranja,"caja":(0,140,255)}
}
#Creamos un diccionario para los colores#
resultado_bgr=imagen.copy()
kernel=np.ones((3,3),np.uint8)
#Utilizamos un kernel pequeño para no deformar tanto la imagen#
for nombre,datos in colores.items():
    #Iteramos sobre las llaves y valores de nuestro diccionario#
    bajo,alto=datos["rango"]
    #Susbtaremos las 2 tuplas que hay en "rango" por separado#
    mascara=cv2.inRange(hsv,bajo,alto)
    #Separamos los pixeles de los colores que queremos de los que no#
    mascara=cv2.morphologyEx(mascara,cv2.MORPH_CLOSE,kernel,iterations=2)
    #Hacemos operaciones morfologicas para cerrar nuestro objeto y eliminar el "ruido"
    mascara=cv2.morphologyEx(mascara,cv2.MORPH_OPEN,kernel,iterations=1)
    contornos,_=cv2.findContours(mascara,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    #Sacamos los puntos del cono# 
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
plt.show()
