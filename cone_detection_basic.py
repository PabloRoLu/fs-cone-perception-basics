import cv2
import numpy as np
import matplotlib.pyplot as plt
imagen=np.zeros((500,500,3),dtype="uint8")
#Creamos una imagen de 500x500 pixeles con 3 canales (BGR)#
cono_1=np.array([[100,350],[150,200],[200,350]],np.int32)
#Aqui lo que hacemos es un arreglo matricial, ponemos las coordenadas de los 3 puntos de nuestro cono, y ponemos de tipo de dato np.int32 porque para la libreria Opencv necesita 32 bits para que no haya problema#
cv2.fillPoly(imagen,[cono_1],(255,255,255))
#La funcion cv2.fillPoly (Fill Polygon) hace lo que dice su nombre, rellena el poligono que le dimos, su anatmonia es la siguiente, primero se pone la imagen#
#Despues en corchetes se pone el arreglo matricial o los arreglos matriciales y despues el color#
cono_2=np.array([[300,380],[340,220],[380,380]],np.int32)
cv2.fillPoly(imagen,[cono_2],(255,255,255))
cv2.circle(imagen,(50,50),2,(255,255,255),-1)
cv2.circle(imagen,(450,80),2,(255,255,255),-1)
cv2.circle(imagen,(420,450),2,(255,255,255),-1)
#Creamos "ruido" con 3 circulos pequeños blancos de radio 2 ubicados en distintas partes de la imagen#
imagen_gris=cv2.cvtColor(imagen,cv2.COLOR_BGR2GRAY)
#Pasamos la imagen de BGR a una gris#
_,imagen_binaria=cv2.threshold(imagen_gris,127,255,cv2.THRESH_BINARY)
#Pasamos la imagen gris que tiene un rango de 0-255 a una imagen binaria que tiene 2 valores 0 o 255#
#Si el pixel es menor o igual a 127 pasa automaticamente a 0 y si es mayor pasa al umbral mayor que en nuestro caso es 255#
kernel=np.ones((5,5),np.uint8)
imagen_cerrada=cv2.morphologyEx(imagen_binaria,cv2.MORPH_CLOSE,kernel,iterations=2)
#Cerramos cualquier agujero que pueda existir dentro de la pieza#
contornos,_=cv2.findContours(imagen_cerrada,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
#Sacamos una matriz de los contornos, unicamente de los puntos de la figura y no de todo el perimetro para ahorrar memoria RAM#
resultado_bgr=cv2.cvtColor(imagen_cerrada,cv2.COLOR_GRAY2BGR)
#Pasamos la imagemn cerrada de su escala gris a BGR#
for c in contornos:
#Como tenemos "ruido" en la imagen vamos a tener varias coordenadas en contornos asi que iteramos para descartar el "ruido"#
    area=cv2.contourArea(c)
    if area>100:
        M=cv2.moments(c)
        if M["m00"]!=0:
            cx=int(M["m10"]/M["m00"])
            cy=int(M["m01"]/M["m00"])
            #Sacamos los centros de masa del eje x e y#
            cv2.circle(resultado_bgr,(cx,cy),5,(0,0,255),-1)
            #Ponemos un circulo rojo de radio 5 para ver el centro de cada pieza#
        x,y,w,h=cv2.boundingRect(c)
        #Obtenemos las coordenadas del Bounding Box recto#
        cv2.rectangle(resultado_bgr,(x,y),(x+w,y+h),(255,0,0),2)
        #Hacemos el Bounding Box recto (azul)
        rect=cv2.minAreaRect(c)
        #Obtenemos los 3 tipos de datos para el Bounding Box orientado (Centro,Tamaño,Angulo)#
        caja=cv2.boxPoints(rect)
        #Sacamos los 4 puntos del Bounding Box orientado #
        caja=np.int32(caja)
        #Pasamos a int32 ya que de normal arroja float32 y para que no haya problema con la libreria de Opencv necesitamos int32#
        cv2.drawContours(resultado_bgr,[caja],0,(0,255,255),2)
        #Bounding Box amarillo#
        angulo=rect[-1]
        print(f"Area: {area:.2f} px² \n Centro de masa X={cx:.2f}px, Y={cy:.2f}px \n Angulo: {angulo:.2f}º")
imagen_original=cv2.cvtColor(imagen,cv2.COLOR_BGR2RGB)
resultado_rgb=cv2.cvtColor(resultado_bgr,cv2.COLOR_BGR2RGB)
plt.figure(figsize=(12,6))
plt.subplot(1,2,1)
plt.title("Imagen sintetica original (RGB)")
plt.imshow(imagen_original)
plt.axis("off")
plt.subplot(1,2,2)
plt.title("Deteccion de contornos y bounding boxes")
plt.imshow(resultado_rgb)
plt.axis("off")
plt.show()