# FS Cone Perception Basics
Proyecto básico de detección de conos para Formula Student Driverless usando OpenCV.
## Descripción
Este repositorio contiene un pipeline sencillo de percepción que permite:
- Detectar formas que simulan conos en una imagen sintética
- Calcular el centroide de cada cono
- Generar Bounding Boxes (rectos y orientados)
- Filtrar ruido mediante operaciones morfológicas
El objetivo es construir una base sólida de visión por computador orientada a la detección de conos, que es uno de los primeros pasos en el stack de Autonomous de Formula Student.
## Librerías utilizadas
- Python
- OpenCV
- NumPy
- Matplotlib
## Cómo ejecutarlo
1. Clonar el repositorio
2. Instalar las dependencias:
```bash
pip install opencv-python numpy matplotlib
```
3. Ejecutar el script:
```bash
python cone_detection_basic.py
```
## Estado actual
- [x] Creación de imagen sintética con conos
- [x] Preprocesamiento (threshold + morfología)
- [x] Detección de contornos
- [x] Cálculo de centroides
- [x] Bounding Boxes (recto y orientado)
- [ ] Detección por color (HSV) en imágenes reales
- [ ] Integración con ROS2
## Próximos pasos
- Mejorar la forma de los conos sintéticos
- Probar el pipeline con imágenes reales de conos
- Añadir clasificación por color (azul / amarillo / naranja)
- Empezar a estructurar el código como nodos de ROS2
---
Desarrollado como parte de mi preparación para entrar en el área de Autonomous de UVigo Motorsport.
