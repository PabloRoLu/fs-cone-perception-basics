import cv2
import matplotlib.pyplot as plt
import numpy as np
#Creamos una funcion para hacer los conos#
def dibujar_cono(imagen,cima,base_izq,base_der,color_bgr):
    puntos=np.array([cima,base_izq,base_der],np.int32)
    cv2.fillPoly(imagen,[puntos],color_bgr)
#Creamos una funcion para detectar los centros de masa, el bounding box y los contonros de cada cono#
def detectar_centrodies(hsv,rango,kernel,area_min=150):
    bajo,alto=rango
    mascara=cv2.inRange(hsv,bajo,alto)
    mascara=cv2.morphologyEx(mascara,cv2.MORPH_CLOSE,kernel,iterations=2)
    mascara=cv2.morphologyEx(mascara,cv2.MORPH_OPEN,kernel,iterations=1)
    contornos,_=cv2.findContours(mascara,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    centros=[]
    for c in contornos:
        if cv2.contourArea(c)>area_min:
            M=cv2.moments(c)
            if M!=0:
                cx=int(M["m10"]/M["m00"])
                cy=int(M["m01"]/M["m00"])
            x,y,w,h=cv2.boundingRect(c)
            centros.append({"cx":cx,
                            "cy":cy,
                            "box":(x,y,w,h),
                            "contorno":c})
            #Guardamos el centro de masa en x e y, su caja delimitadora y su contorno en forma de diccionario#
    centros.sort(key=lambda cono:cono["cy"])
    #Ordenamos los centros de forma ascendente#
    return centros

imagen=np.zeros((520,600,3),dtype="uint8")
#Creamos una imagen de 600 pixeles de ancho (x) y de 520 pixeles de alto (y)#
Azul=[255,0,0]
Amarillo=[0,255,255]
#Creamos los valores para los colores#
Filas=[160,280,400]
#Creamos el valor de las filas donde vamos a insertar los conos#
for y in Filas:
    #Iteramos sobre cada valor de las filas#
    dibujar_cono(imagen,(140,y-70),(105,y+20),(175,y+20),Azul)
    dibujar_cono(imagen,(500,y-70),(465,y+20),(535,y+20),Amarillo)
    #Creamos los conos#
cv2.circle(imagen,(30,30),3,(255,255,255),-1)
cv2.circle(imagen,(600,50),3,(255,255,255),-1)
cv2.circle(imagen,(40,490),3,(255,255,255),-1)
#Creamos ruido#
hsv=cv2.cvtColor(imagen,cv2.COLOR_BGR2HSV)
kernel=np.ones((3,3),np.uint8)
rango_azul=(np.array([100,80,80]),np.array([130,255,255]))
rango_amarillo=(np.array([20,80,80]),np.array([35,255,255]))
#Creamos los rangos de deteccion para los colores azules y amarillos#
azules=detectar_centrodies(hsv,rango_azul,kernel)
amarillos=detectar_centrodies(hsv,rango_amarillo,kernel)
#Guardamos los centros de masa, las cajas delimitadoras y los contornos de los conos#
print(f"Conos azules: {len(azules)} \nConos amarillos: {len(amarillos)}")
#Imprimimos la cantidad de conos#
resultado_bgr=imagen.copy()
puntos_centro=[]
#Creamos una lista para los puntos que esten entre los conos#
n_pares=min(len(azules),len(amarillos))
#Para buscar el numero de pares buscamos el numero menor de esta tupla#
for i in range(n_pares):
    #Iteramos sobre cada par de conos#
    izq=azules[i]
    der=amarillos[i]
    #Asignamos cada cono, si es izquierdo es azul y si es derecho amarillo#
    mx=int((izq["cx"]+der["cx"])/2)
    #Obtenemos el punto medio de los centros de masas de cada cono en el eje X#
    my=int((izq["cy"]+der["cy"])/2)
    #Lo mismo pero para las coordenadas del eje Y#
    puntos_centro.append((mx,my))
    #Guardamos los puntos#
    x,y,w,h=izq["box"]
    #Volvemos a tomar los puntos de la caja delimitadora (bounding box), pero en este caso del cono azul#
    cv2.rectangle(resultado_bgr,(x,y),(x+w,y+h),Azul,2)
    cv2.circle(resultado_bgr,(izq["cx"],izq["cy"]),5,[0,0,255],-1)
    #Hacemos el bounding box del cono azul junto a un circulo rojo en su centro de masas#
    x,y,w,g=der["box"]
    cv2.rectangle(resultado_bgr,(x,y),(x+w,y+h),Amarillo,2)
    cv2.circle(resultado_bgr,(der["cx"],der["cy"]),5,[0,0,255],-1)
    #Hacemos lo mismo pero para los conos amarillos#
    cv2.line(resultado_bgr,(izq["cx"],izq["cy"]),(der["cx"],der["cy"]),(180,180,180),1)
    #Hacemos una linea gris que une los centros de masas de los conos#
    cv2.circle(resultado_bgr,(mx,my),6,[0,255,0],-1)
    #Hacemos un circulo verde en el centro de los centros de masas del cono azul y amarillo#
    print(f"Par {i+1}: \n azul=({izq["cx"]},{izq["cy"]}) \n amarillo=({der["cx"]},{der["cy"]}) \n centro=({mx},{my})")
    #Imprimimos los centros de masas para cada cono junto al centro de ambos#
if len(puntos_centro)>=2:
    #Comprobamos que haya mas de 2 centros para poder hacer las lineas#
    for i in range(len(puntos_centro)-1):
        #Iteramos sobre el range de la longitud de los conos (le restamos 1 ya que por n conos tenemos n-1 lineas# 
        cv2.line(resultado_bgr,puntos_centro[i],puntos_centro[i+1],(0,255,0),3)
        #Hacemos una linea verde entre los centros de los conos#
original_rgb=cv2.cvtColor(imagen,cv2.COLOR_BGR2RGB)
resultado_rgb=cv2.cvtColor(resultado_bgr,cv2.COLOR_BGR2RGB)
plt.figure(figsize=(13,6))
plt.subplot(1,2,1)
plt.title("Pista sintetica (azules izq / amarillos der)")
plt.imshow(original_rgb)
plt.axis("off")
plt.subplot(1,2,2)
plt.title("Centro de pista (linea verde)")
plt.imshow(resultado_rgb)
plt.axis("off")
plt.tight_layout()
plt.show()
