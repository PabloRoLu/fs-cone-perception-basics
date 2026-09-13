import numpy as np
import matplotlib.pyplot as plt
import cv2
ruta = "images/cono_real.jpg"
#Creamos la ruta para la imagen#
imagen=cv2.imread(ruta)
#Lo que hace la funcion cv2.imread() es leer el archivo, decodificarlo y dejarlo como un array de numpy de 3 dimensiones#
if imagen is None:
    #Hacemos la comprobacion para ver si realmente se puede extraer la foto de nuestra ruta#
    raise FileNotFoundError(f" no se encontro {ruta}")
alto,ancho=imagen.shape[:2]
#La funcion .shape lo que hace es decirnos cuantas casillas hay en cada eje, .shape es una propiedad del array#
#Es decir, nos da el alto de la imagen (Filas), el ancho (columnas) y los canales (B,G,R)#
#Ponemos [:2] para indicar que solo queremos con los 2 primeros terminos#
if ancho>1280:
    #Si el ancho de la imagen supera 1280 pixeles la encogemos sin deformar la imagen#
    escala=1280/ancho
    #Creamos esta escala para ver por cuanto vamos a encoger la altura de la imagen en el caso que su anchura fuera mayor a 1280 pixeles#
    imagen=cv2.resize(imagen,(1280,int(alto*escala)))
    #La funcion cv2.resize() lo que hace es cambiar la escala de la imagen, nosotros lo hacemos para que#
    #La libreria de OpenCV no tarde tanto en hacer sus calculos si es que tenemos una imagen grande#
    #Ponemos int ya que OpenCV nos pide datos enterios, y de ancho ponemos 1280 y de alto (Estan invertido los valores que nos dio la funcion .shape por eso los sacamos por separado)#
    #De alto ponemos el alto conforme a la escala#
hsv=cv2.cvtColor(imagen,cv2.COLOR_BGR2HSV)
kernel=np.ones((7,7),np.uint8)
rango_amarillo=(np.array([20,70,70]),np.array([38,255,255]))
rango_naranja=(np.array([0,100,80]),np.array([12,255,255]))
#Creamos los rangos para los colores, como ya es una imagen real (Hay caucho, luces y demas) ponemos estos parametros para que no tengamos problemas al detectar los colores#
colores={
    "Yellow":{"rango":rango_amarillo,"caja":[0,255,255]},
    "Orange":{"rango":rango_naranja,"caja":[0,140,255]}
}
#Creamos el diccionario de los colores#
def unir_cajas(cajas,max_hueco=200):
     #Creamos una funcion en la que sus inputs son las cajas de los mismos colores y cual deberia de ser su separacion para que se siga considerando el mismo objeto#
     if not cajas:
          return []
     #Si no tenemos cajas regresamos una lista vacia, esto para no tener problemas al usar len() y multiplicar#
     usadas=[False]*len(cajas)
     #Lo que hacemos aqui es crear una lista de False dependiendo de cuantas cajas del mismo color en la zona de proximidad#
     #En nuestro caso vamos a tener usadas=[False,False] ya que len(cajas)=2, de esta forma podemos ver cuales cajas han sido utilizadas y cuales no#
     unidas=[]
     #Creamos una lista para las cajas ya unidas#
     for i,(x1,y1,w1,h1) in enumerate(cajas):
          #Hay que recordar que la funcion enumerate() lo que devuelve es el indice y el valor de lo que le pongamos#
          #En este caso va a devolver por cada caja en nuestro rango de proximidad (200 pixeles)#
          if usadas[i]:
               continue
          #Usamos el if para ver si se cumple la condicion, si es True entonces se salta a la siguiente i (si es que hay)#
          #Y si es False continua ya que el if solo se actua con True#
          izq,arr,der,aba=x1,y1,x1+w1,y1+h1
          #Empezamos definiendo el cuadro#
          usadas[i]=True
          #Le asignamos el valor de True para que no se pueda volver a usar
          cambio=True
          #Creamos una flag#
          while cambio:
               #El while se va a repetir hasta que cambio=False, es decir para si no se solapan cajas#
               cambio=False
               #Asumimos que no se van a solapar cajas, si lod datos pasan las condiciones entonces lo volvemos a cambiar#
               for j,(x2,y2,w2,h2) in enumerate(cajas):
                    #Usamos este for in para comparar con el otro valor de usadas#
                    if usadas[j]:
                         #Volvemos hacer la comprobacion, si es True omitimos los siguientes pasos#
                         #Puede ser True si j=i ya que antes de entrar al while pusimos a i=True#
                         continue
                    izq2,arr2,der2,aba2=x2,y2,x2+w2,y2+h2
                    #Nombramos nuestras nuevas coordenadas#
                    solape_x=min(der,der2)-max(izq,izq2)
                    #Calculamos el solape entre las 2 cajas, de esta forma nos aseguramos que las cajas pertenezcan al mismo cono#
                    if solape_x<=0:
                         #Ya que si fuera negativo significa que el punto de la izquierda de una de las cajas es mayor al punto de la derecha#
                         #Es decir son conos separados, si solape=0 significa que se tocan en un punto, igualmente significa que son conos distintos#
                         #La unica forma que solape>0 significa que comparten o se solapan o hay una dentro de la otra#
                         #Aun no sabemos si son el mismo cono pero con esto ya podemos omitir los que realmente sabemos que no son el mismo cono#
                         continue
                    #Si no se cumple que son cajas del mismo cono omitimos el resto de pasos y pasamos a comparar las cajas que siguen con estatus de False#
                    hueco=max(arr,arr2)-min(aba,aba2)
                    #Ahora al ver que pueden ser del mismo cono, verificamos si realmente lo son, porque en una imagen pueden pasar el filtro del solape pero ser distintos conos#
                    #Calculamos el hueco entre las 2 cajas#
                    if hueco>max_hueco:
                         #Si excede los 200 pixeles lo descartamos ya que son conos distintos#
                         continue
                    #Si pasa significa que son el mismo cono por lo tanto cambiamos las coordenadas#
                    izq,arr=min(izq,izq2),min(arr,arr2)
                    #El punto mas alto (contraintuitvo pero asi funciona OpenCV) es el que menos valor tiene#
                    der,aba=max(der,der2),max(aba,aba2)
                    #Lo mismo para el punto de abajo, el punto mas bajo en el eje Y es el que tiene un mayor valor#
                    usadas[j]=True
                    #Nos aseguramos que no se use esta caja ya que encontro a su otra parte y esta solapada#
                    cambio=True
                    #Como si hubo un solape cambio=True para buscar si hay mas cajas que unir a esta#

          unidas.append((izq,arr,der-izq,aba-arr))
          #Guardamos los nuevos puntos del bounding box (x,y,w,h)
     return unidas                    
resultado=imagen.copy()
for nombre,datos in colores.items():
    #Iteramos sobre cada llave del diccionario#
    bajo,alto=datos["rango"]
    #Obtenemos los rangos inferiores y superiores para obtener una mascara que nos ayude a seleccionar los colores que estamos buscando#
    mascara=cv2.inRange(hsv,bajo,alto)
    #Obtenemos la mascara para separar colores#
    mascara=cv2.morphologyEx(mascara,cv2.MORPH_CLOSE,kernel,iterations=3)
    mascara=cv2.morphologyEx(mascara,cv2.MORPH_OPEN,kernel,iterations=1)
    #Hacemos operaciones morfologicas para limpiar el objeto#
    contornos,_=cv2.findContours(mascara,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    #Obtenemos el contorno#
    cajas=[]
    #Como vamos a tener distintas cajas del mismo color creamos una lista para guardar estos datos#
    for c in contornos:
        area=cv2.contourArea(c)
        #Sacamos el area de cada cono#
        if area>4000:
            #Si el area del objeto es menor a 4000 pixeles cuadrados lo descartamos#
            cajas.append(cv2.boundingRect(c))
            #Guardamos el bounding box de los distintos "conos"#
    cajas=unir_cajas(cajas)
    #Como en la funcion ya habiamos definido max_hueco=200, solo le ponemos el valor de la caja#
    #Ahora el valor de la caja es el return unidas, es decir ya tenemos la caja guardada#
    cajas=sorted(cajas,key=lambda b:b[2]*b[3], reverse=True)[:2]
    #Ahora en vez de usar cajas.sort() usamos la funcion sorted() que nos devuelve otra lista, por eso ponemos de nueco cajas=sorted()#
    #Aqui vamos a acomodar cada caja por su area por eso b[2]*b[3] ya que b[0]=x, b[1]=y, b[2]=w y b[3]=h#
    #Y el area de un rectangulo es ancho por alto, asi que de normal la funcion ordena de menor a mayor, por eso ponemos reverse=True#
    #Para que el orden sea de mayor a menor, y ponemos [:2] para extraer los primeros 2 elementos, es decir las 2 cajas mas grandes#
    #Esto como filtro de seguridad para asegurarnos que no se cuelen conos de atras y solo esten nuestros 2 conos de enfrente#
    for (x,y,w,h) in cajas:
           cx,cy=x+w//2,y+h//2
           #Sacamos su centro de masa#
           cv2.rectangle(resultado,(x,y),(x+w,y+h),datos["caja"],3)
           #Hacemos el bounding box de su respectivo color#
           cv2.circle(resultado,(cx,cy),6,(0,0,255),-1)
           cv2.putText(resultado,nombre,(x,max(20,y-8)),cv2.FONT_HERSHEY_SIMPLEX,0.6,datos["caja"],2)
           #Ponemos el nombre del color del respectivo bounding box
           print(f"{nombre} \n caja unida {w}x{h} \n centro={cx},{cy}")

original_rgb=cv2.cvtColor(imagen,cv2.COLOR_BGR2RGB)
resultado_rgb=cv2.cvtColor(resultado,cv2.COLOR_BGR2RGB)
plt.figure(figsize=(14,6))
plt.subplot(1,2,1)
plt.title("Foto real")
plt.imshow(original_rgb)
plt.axis("off")
plt.subplot(1,2,2)
plt.title("Detecciòn HSV")
plt.imshow(resultado_rgb)
plt.axis("off")
plt.tight_layout()
plt.show()