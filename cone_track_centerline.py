import cv2
import matplotlib.pyplot as plt
import numpy as np
def dibujar_cono(imagen,cima,base_izq,base_der,color_bgr):
    puntos=np.array([cima,base_izq,base_der],np.int32)
    #Cambiamos los puntos que se van a insertar despues a un array de numpy y que sean int32 bits para que sea compatible con OpenCV#
    cv2.fillPoly(imagen,[puntos],color_bgr)
    #Creamos una funcion para dibujar cada cono#
def detectar_centrodies(hsv,rango,kernel,area_min=150):
    bajo,alto=rango
    mascara=cv2.inRange(hsv,bajo,alto)
    mascara=cv2.morphologyEx(mascara,cv2.MORPH_CLOSE,kernel,iterations=2)
    mascara=cv2.morphologyEx(mascara,cv2.MORPH_OPEN,kernel,iterations=1)
    contornos,_=cv2.findContours(mascara,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    centros=[]
    #Creamos una lista para ir guardando los centros del cono y sus valores importantes#
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
    #Hay que recordar que la funcion .sort() lo que hace es ordenar numericamente los datos de la lista o en nuestro caso los datos de nuestro diccionario#
    #key es la regla "mira esta propiedad para decidir el orden", es decir como tenemos un diccionario con valores del centro de masa en x en y, cajas delimitadoras y contornos .sort() no sabe como arreglarlo#
    #Por eso usamos key que le indica a .sort() como ordenar el diccionario que tenemos#
    #def sacar_altura(p):
    #    return p["cy"]#
    #Es decir, estamos ordenando el diccionario en base a la altura de cada cono, de esta forma estan emparejados (a la misma altura) los conos azules y amarillos#
    #lambda en si es una funcion de un argumento, en vez de poner#
    #def sacar_altura(p):
        #    return p["cy"]#
    #Ponemos lambda, que sigue la siguiente anatomia, lambda "argumento":"expresion"#
    #En si lambda puede hacer varias cosas, sumar, multiplicar, usar if, siempre y cuando se trate de un solo argumento#
    #En este caso utilizamos lambda para ordenar los conos del eje y, lo que hace lambda en este caso es para cada cono vamos solo a seleccionar los conos en el eje Y#
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
#Lo que hace la funcion len() aqui es contar cuantas fichas tenemos en el diccionario#
#Como tenemos un diccionario, cada columna arroja datos diferentes, arroja el centro de masa en x, el centro de masa en y y asi sucesivamente#
#Lo que hace len() en este caso es contar el numero de las filas#
resultado_bgr=imagen.copy()
puntos_centro=[]
#Creamos una lista para los puntos que esten entre los conos#
n_pares=min(len(azules),len(amarillos))
#Para buscar el numero de pares buscamos el numero menor de esta tupla#
for i in range(n_pares):
    #Iteramos sobre cada par de conos#
    izq=azules[i]
    der=amarillos[i]
    #Asignamos cada cono, si es izquierdo es azul, y como ya esta ordenado por lo que hicimos con lo de .sorted(key=lambda cono:cono["cy"])#
    mx=int((izq["cx"]+der["cx"])/2)
    #Tomamos las coordenadas de los conos que estan en la misma fila ya que estan ordenadas y para sacar el centro entre estas 2 sumamos sus coordenadas en x y lo dividimos entre 2#
    my=int((izq["cy"]+der["cy"])/2)
    #Lo mismo pero para las coordenadas del eje Y#
    puntos_centro.append((mx,my))
    #Guardamos los puntos#
    x,y,w,h=izq["box"]
    #Volvemos a tomar los puntos de la caja delimitadora, pero en este caso del cono azul#
    cv2.rectangle(resultado_bgr,(x,y),(x+w,y+h),Azul,2)
    cv2.circle(resultado_bgr,(izq["cx"],izq["cy"]),5,[0,0,255],-1)
    #Hacemos el bounding box del cono azul junto a un circulo rojo en su centro de masas#
    x,y,w,g=der["box"]
    cv2.rectangle(resultado_bgr,(x,y),(x+w,y+h),Amarillo,2)
    cv2.circle(resultado_bgr,(der["cx"],der["cy"]),5,[0,0,255],-1)
    #Hacemos lo mismo pero para los conos amarillos#
    cv2.line(resultado_bgr,(izq["cx"],izq["cy"]),(der["cx"],der["cy"]),(180,180,180),1)
    #La funcion cv2.line() sigue la siguiente anatomia (imagen, punto inical, punto final, color, grosor)#
    #En nuestro caso el punto inicial es el centro de masa del cono azul y el punto final es el centro de masa del cono amarillo#
    #La funcion como lo dice el nombre es hacer una linea entre esos 2 puntos#
    cv2.circle(resultado_bgr,(mx,my),6,[0,255,0],-1)
    #Hacemos un circulo verde en el centro de los centros de masas del cono azul y amarillo#
    print(f"Par {i+1}: \n azul=({izq["cx"]},{izq["cy"]}) \n amarillo=({der["cx"]},{der["cy"]}) \n centro=({mx},{my})")
    #Imprimimos los centros de masas para cada cono junto al centro de ambos#
if len(puntos_centro)>=2:
    #Comprobamos que haya mas de 2 centros para poder hacer las lineas#
    for i in range(len(puntos_centro)-1):
        #Si tenemos n puntos vamos a tener n-1 lineas, por eso usamos el len() esa funcion nos va a dar cuantos puntos tenemos#
        #y el range hay que recordar que da lo siguiente, si len=2 su range es 0,1#
        #Por eso al len() le restamos -1 ya que vamos a tener n-1 lineas# 
        cv2.line(resultado_bgr,puntos_centro[i],puntos_centro[i+1],(0,255,0),3)
        #Por eso aqui el punto inicial es el i y el final es el i+1, es decir, el que le sigue#
        #De esta forma hacemos una linea verde entre los centros de los conos#
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