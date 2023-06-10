import cv2
import imutils
import numpy as np
import pytesseract
from PIL import Image, ImageTk
import mysql.connector
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from tkinter import Tk


# Conexión a la base de datos
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="MiBaseDeDatos"
)

# Crear cursor
cursor = db.cursor()

# Función para procesar la foto seleccionada
def procesar_foto():
    # Obtener la ruta de la foto seleccionada
    foto_path = foto_var.get()

    # Cargar la foto seleccionada
    img = cv2.imread(foto_path, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (620, 480))

    # Convertir la imagen a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Aplicar un filtro bilateral para reducir el ruido mientras se conservan los bordes
    gray = cv2.bilateralFilter(gray, 11, 17, 17)

    # Aplicar el algoritmo de detección de bordes de Canny para obtener los contornos
    edged = cv2.Canny(gray, 30, 200)
    
    # Encontrar los contornos en la imagen
    cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    #cv2.drawContours(img,cnts,-1,(0,255,0),2)
    
    # Ordenar los contornos por área en orden descendente y tomar los 10 primeros
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]

    # Creamos la variable para almacenar el contorno de la placa de matrícula
    screenCnt = None
    
    
    
    # Recorrer los contornos encontrados
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)

        # Si el contorno tiene 4 vértices, se considera como el contorno de la placa de matrícula
        if len(approx) == 4:
            screenCnt = approx
            break

    # Verificar si se detectó el contorno de la placa de matrícula
    if screenCnt is None:
        detected = 0
        print("No se detectó contorno")
    else:
        detected = 1

    # Dibujar el contorno de la placa de matrícula en la imagen original si se detectó
    if detected == 1:
        cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)
    
    # Crear una máscara en blanco del mismo tamaño que la imagen en escala de grises
    mask = np.zeros(gray.shape, np.uint8)

    # Dibujar el contorno de la placa de matrícula en la máscara
    new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1)
    
    
    # Aplicar la máscara a la imagen original para obtener solo la región de la placa de matrícula
    new_image = cv2.bitwise_and(img, img, mask=mask)

    # Obtener las coordenadas de los píxeles blancos en la máscara
    (x, y) = np.where(mask == 255)

    # Calcular las coordenadas superior izquierda y la inferior derecha de la región de la placa de matrícula
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))

    # Recortar la región de la placa de matrícula de la imagen en escala de grises
    Cropped = gray[topx:bottomx + 1, topy:bottomy + 1]
    
    # Aplicar OCR a la región recortada para obtener el número de la matrícula
    license_plate = pytesseract.image_to_string(Cropped, config='--psm 11')
    license_plate = license_plate.strip()

    # Imprimir el número de matrícula detectado
    print("Número detectado:", license_plate)

    # Verificar si la matrícula existe en la tabla "Coche"
    query = "SELECT * FROM Coche WHERE matricula = %s"
    values = (license_plate,)
    cursor.execute(query, values)
    result = cursor.fetchone()

    if result:
        # Si la matrícula existe, guardar fecha y hora de entrada
        fecha_entrada = result[1]
        hora_entrada = result[2]

        # Eliminar la matrícula de la tabla "Coche"
        delete_query = "DELETE FROM Coche WHERE matricula = %s"
        cursor.execute(delete_query, values)

        # Obtener la fecha y hora actuales
        now = datetime.now()
        fecha_salida = now.date()
        hora_salida = now.time()

        # Insertar la matrícula en la tabla "CocheSalida" con las fechas y horas correspondientes
        insert_query = "INSERT INTO CocheSalida (matricula, fechaEntrada, horaEntrada, fechaSalida, horaSalida) VALUES (%s, %s, %s, %s, %s)"
        insert_values = (license_plate, fecha_entrada, hora_entrada, fecha_salida, hora_salida)
        cursor.execute(insert_query, insert_values)
    else:
        # Si la matrícula no existe en "Coche", insertarla en la tabla "Coche" con fecha y hora actuales
        now = datetime.now()
        fecha_entrada = now.date()
        hora_entrada = now.time()
        insert_query = "INSERT INTO Coche (matricula, fecha, hora) VALUES (%s, %s, %s)"
        insert_values = (license_plate, fecha_entrada, hora_entrada)
        cursor.execute(insert_query, insert_values)

    # Confirmar los cambios en la base de datos
    db.commit()

# Función para seleccionar una foto
def seleccionar_foto():
    # Abrir el diálogo de selección de archivo
    foto_path = filedialog.askopenfilename(title="Seleccionar foto")

    # Actualizar la variable de la foto seleccionada
    foto_var.set(foto_path)

    # Mostrar una previsualización de la foto seleccionada
    previsualizacion = Image.open(foto_path)
    previsualizacion = previsualizacion.resize((250, 200))
    previsualizacion_tk = ImageTk.PhotoImage(previsualizacion)
    previsualizacion_label.configure(image=previsualizacion_tk)
    previsualizacion_label.image = previsualizacion_tk

# Crear la ventana principal
root = Tk()
root.title("Parking IES Zaidín Vergeles")
root.geometry("400x300")

# Variable para almacenar la ruta de la foto seleccionada
foto_var = tk.StringVar()

# Botón para seleccionar una foto
seleccionar_foto_btn = tk.Button(root, text="Seleccionar foto", command=seleccionar_foto)
seleccionar_foto_btn.pack()

# Etiqueta para mostrar la previsualización de la foto seleccionada
previsualizacion_label = tk.Label(root)
previsualizacion_label.pack()

# Botón para procesar la foto seleccionada
procesar_foto_btn = tk.Button(root, text="Procesar foto", command=procesar_foto)
procesar_foto_btn.pack()

# Ejecutar el bucle principal de la interfaz gráfica
root.mainloop()

