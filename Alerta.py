#V2.0
#ENVIO DE IMAGENES A SERVIDOR CADA DETERMINADO PERIODO DE TIEMPO CON VALORES DE SENSORES, ALTERAR PARA EL USO CON CRON
import RPi.GPIO as GPIO #Control de pines
import bme280 #Control sensor atmosferico
import smbus2
from time import sleep
import math
import cv2
import requests
from datetime import datetime
from os import remove
import Clasificador
#URL SOLICITUD POST
url = 'https://rain.newrcsoft.com/rest/v1/postData.php'

#RUTA CARPETA DE RESPALDO IMAGENES
ruta = '/home/pi/Detector de incendios V3.0/imagenes/'
#TIEMPO DE BUCLE
lapse = 5

#ESTABLECEMOS LOS PINES EN MODO BCM
GPIO.setmode(GPIO.BCM)

#PINES
Hall = 24
norte = 18
sur = 8
oeste = 25
este = 23

#PINES EXTRA
'''
noreste =
noroeste =
sureste =
suroeste =

'''

#Inicializa el sensor atmosferico

port = 1
address = 0x76
bus = smbus2.SMBus(port)
bme280.load_calibration_params(bus, address)


#Variables para el calculo de velocidad del viento cangilometro
global RPM
global Radian
global Lineal
global KMh
value = 0
#FUNCION PARA CONTAR INTERRUPCIONES
def Contar_Interrupciones(pin):
    global interrupcion
    interrupcion = interrupcion + 0.333 #0.333 cambiar segun cantidad de imanes en el sensor

#INICIALIZAMOS LOS PINES COMO ENTRADAS Y PUD_UP PARA DETECTAR PULSO COMO 0
GPIO.setup(Hall, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(norte, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(sur, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(oeste, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(este, GPIO.IN, pull_up_down = GPIO.PUD_UP)

#PINES EXTRA
'''
GPIO.setup(noreste, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(noroeste, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(sureste, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(suroeste, GPIO.IN, pull_up_down = GPIO.PUD_UP)

'''

#METODO PARA DETECTAR EVENTOS CANGILOMETRO
GPIO.add_event_detect(Hall, GPIO.RISING, callback = Contar_Interrupciones)


#Bucle
while True:
    #FECHA
    now = datetime.now()
    dt_string = now.strftime("%Y/%m/%d %H:%M:%S")

    Direccion_Viento = 0
    print('Proxima lecturas en {} segundos:'.format(lapse))
    interrupcion = 0
    RPM = 0
    Radian = 0
    Lineal = 0
    KMh = 0
    sleep(lapse)
    #Calculo de velocidad del viento
    RPM = interrupcion*6
    Radian=RPM * (2 * math.pi)/60
    Lineal=Radian*0.15
    #print('Velocidad del viento: {:05.2f}m/s' .format(Lineal))
    KMh=Lineal*3.6
    #Datos del  sensor
    bme280_data = bme280.sample(bus,address)
    temperatura = bme280_data.temperature
    presion = bme280_data.pressure
    humedad = bme280_data.humidity
    #imprimir valores en formato de dos cifras decimales y agrega el signo correspondiente.
    print('TEMP: {:05.2f}C PRES: {:05.2f}hPa HUME: {:05.2f}%' .format(temperatura, presion, humedad))
    print('Velocidad Viento {:05.2f} km/h'.format(KMh))
    #DIRECCION DEL VIENTO
    if (GPIO.input(norte) == False):
        print('VIENTO NORTE: {:05.2f} km/h' .format(KMh))
        Direccion_Viento = 0
    elif (GPIO.input(sur) == False):
        print('VIENTO SUR: {:05.2f} km/h' .format(KMh))
        Direccion_Viento = 180
    elif (GPIO.input(oeste) == False):
        print('VIENTO OESTE: {:05.2f} km/h' .format(KMh))
        Direccion_Viento = 90
    elif (GPIO.input(este) == False):
        print('Viento ESTE: {:05.2f} km/h' .format(KMh))
        Direccion_Viento = 270
    else:
        print('ERROR EN VELETA')

    """elif (GPIO.input(noroeste) == False):
	print('Viento del Noroeste a: {:05.2f} m/s' .format(Lineal))
    elif (GPIO.input(noreste) == False):
	print('Viento del Noreste a: {:05.2f} m/s' .format(Lineal))
    elif (GPIO.input(suroeste) == False):
	print('Viento del Suroeste a: {:05.2f} m/s' .format(Lineal))
    elif (GPIO.input(sureste) == False):
	print('Viento del Sureste a: {:05.2f} m/s' .format(Lineal))"""
    
    #Pequeña interrupcion para controlar error de conexion de camara
    sleep(0.15)
    cap = cv2.VideoCapture(0)
    ret,image = cap.read()
    
    #BUSQUEDA Y SUBIDA DE RESPALDO
    try:
        #REVISAR SI HAY RESPALDO
        file = open('respaldo','r')
        content = file.read()
        long = len(content)
        file.close()
        if long != 0:
            print('RESPALDOS PENDIENTES')
            file = open('respaldo','r')
            #BUCLE PARA SUBIDA DE RESPALDOS
            for line in file.readlines():
                #CONVERTIR CADA LINEA EN VECTOR
                content = line.split()
                fecha= '{} {}'.format(content[1],content[2])
                #escribimos el json
                #SI NO HAY IMAGENES RESPALDADAS
                if content[0] == 'Null':
                    img ="error.jpg"
                    encoded_string=''
                    with open(img, "rb") as image_file:
                        encoded_string = image_file.read()
                    #MOdelo
                    myjson={'action':'insert',
                            'date':fecha,
                            'base':content[3],
                            'type':content[10],
                            'value':content[11],
                            'image':encoded_string}
                    r = requests.post(url, data=myjson )
                    print(r.text)
                    #IMAGEN
                    myjson={'action':'insert',
                            'date':fecha,
                            'base':content[3],
                            'type':content[4],
                            'value':content[5],
                            'image':encoded_string}
                    r = requests.post(url, data=myjson )
                    print(r.text)
                        
                    #Velocidad del viento
                    myjson={'action':'insert',
                            'date':fecha,
                            'base':content[3],
                            'type':content[6],
                            'value':content[7]}
                    r = requests.post(url, data=myjson )
                    print(r.text)
                    #DIRECCION DEL VIENTO(SE DEBE MEJORAR MEDICION)
                    myjson={'action':'insert',
                            'date':fecha,
                            'base':content[3],
                            'type':content[8],
                            'value':content[9]}
                    r = requests.post(url, data=myjson )
                    print(r.text)
                #SI HAY IMAGENES RESPALDADAS
                else:
                    img ="{}{}.jpg".format(ruta,content[0])
                    encoded_string = ''
                    with open(img, "rb") as image_file:
                        encoded_string = image_file.read()
                    #MODELO
                    myjson={'action':'insert',
                            'date':fecha,
                            'base':content[3],
                            'type':content[10],
                            'value':content[11],
                            'image':encoded_string}
                    r = requests.post(url, data=myjson )
                    print(r.text)
                    #CARGA DE DATOS AL SERVIDOR
                    myjson={'action':'insert',
                        'date':fecha,
                        'base':content[3],
                        'type':content[4],
                        'value':content[5],
                        'image':encoded_string}
                    r = requests.post(url, data=myjson )
                    print(r.text)
                    #DATOS SENSORES
                    #VELOCIDAD DEL VIENTO
                    myjson={'action':'insert',
                         'date':fecha,
                         'base':content[3],
                         'type':content[6],
                         'value':content[7]}
                    r = requests.post(url, data=myjson )
                    print(r.text)
                    remove(img)
                    #DIRECCION DEL VIENTO(SE DEBE MEJORAR MEDICION)
                    myjson={'action':'insert',
                            'date':dt_string,
                            'base':content[3],
                            'type':content[8],
                            'value':content[9]}
                    r = requests.post(url, data=myjson )
                    print(r.text)
            file.close()
            #Borramos registros
            file = open('respaldo','w')
            file.write('')
            file.close()
            print('RESPALDOS SUBIDOS')
    except:
        print('ERROR')
    finally:
        #Si hay camara
        if ret == True:
            try:
                cv2.imwrite('image.jpg', image)
                cap.release()
                #Invoca al modelo
                Clasificador.clasificador('image.jpg', "/home/pi/Detector de incendios V3.0/modelfile.eim")
                value = Clasificador.clasificador.labelNoFuego
                #ABRIMOS IMAGEN PARA SUBIR
                encoded_string = ''
                img ="image.jpg"
                with open(img, "rb") as image_file:
                    encoded_string = image_file.read()
                    
                print('SUBIENDO DATOS...')
                myjson={'action':'insert',
                       'date':dt_string,
                       'base':'Base01',
                       'type':'sensorFire',
                       'value': value,
                       'image':encoded_string}
                r = requests.post(url, data=myjson )
                print(r.text)
                #IMAGEN
                myjson={'action':'insert',
                        'date':dt_string,
                        'base':'Base01',
                        'type':'photo',
                        'value':'100',
                        'image':encoded_string}
                r = requests.post(url, data=myjson )
                print("1°" + r.text)
                    
                #Velocidad del viento
                myjson={'action':'insert',
                        'date':dt_string,
                        'base':'Base01',
                        'type':'windspeedAvg',
                        'value':'{:05.2f}'.format(KMh)}
                r = requests.post(url, data=myjson )
                print("2°" + r.text)
                #DIRECCION DEL VIENTO(SE DEBE MEJORAR MEDICION)
                myjson={'action':'insert',
                        'date':dt_string,
                        'base':'Base01',
                        'type':'winddirAvg',
                        'value':Direccion_Viento}
                r = requests.post(url, data=myjson )
                print("3°" + r.text)
                '''
                #TEMPERATURA
                myjson={'action':'insert',
                        'date':dt_string,
                        'base':'Base01',
                        'type':'tempAvg',
                        'value':'{:05.2f}'.format(temperatura)}
                r = requests.post(url, data=myjson )
                print("4°" + r.text)
                
                #PRESION
                myjson={'action':'insert',
                        'date':dt_string,
                        'base':'Base01',
                        'type':'pressureMax',
                        'value':'{:05.2f}'.format(presion)}
                r = requests.post(url, data=myjson )
                print("5°" + r.text)
                
                #HUMEDAD
                myjson={'action':'insert',
                        'date':dt_string,
                        'base':'Base01',
                        'type':'humidityAvg',
                        'value':'{:05.2f}'.format(humedad)}
                r = requests.post(url, data=myjson )
                print("6°" + r.text)
                '''
                print('DATOS SUBIDOS')
                print('.................................')
            except:
                #RESPALDO CUANDO NO HAY CONEXI0N
                print('NO HAY CONEXIÓN')
                #BUSCAMOS EN LOS RESPALDOS EL ULTIMO ID DE FOTOS
                file = open('respaldo','r')
                content = file.readlines()
                file.close()
                FOTO_ID = len(content)
                #REGISTRAMOS LA INFORMACION EN EL ARCHIVO
                #Hay que agregar los demas valores
                data = '{} {} Base01 photo 100 windspeedAvg {:05.2f} winddirAvg {} sensorFire {}\n'.format(FOTO_ID,dt_string,KMh,Direccion_Viento, value)
                file = open('respaldo','r+')
                content=file.read()
                long = len(content)
                file.seek(long)
                file.write(data)
                file.close()
                #REGISTRAMOS LA IMAGEN CON ID
                cv2.imwrite('{}{}.jpg'.format(ruta,FOTO_ID), image)
                cap.release()
                
                print('DATOS GUARDADOS')
                print('......................................')
        #Si no hay camara
        else:
            try:
                print('NO SE DETECTA CAMARA')
                print('SUBIENDO DATOS SIN IMAGEN...')
                img ="error.jpg"
                encoded_string=''
                with open(img, "rb") as image_file:
                    encoded_string = image_file.read()
                
                #IMAGEN
                myjson={'action':'insert',
                        'date':dt_string,
                        'base':'Base01',
                        'type':'photo',
                        'value':'0',
                        'image':encoded_string}
                r = requests.post(url, data=myjson )
                print("1°" + r.text)
                #modelo
                myjson={'action':'insert',
                        'date':dt_string,
                        'base':'Base01',
                        'type':'sensorFire',
                        'value':'0',
                        'image':encoded_string}
                r = requests.post(url, data=myjson )
                print("1°" + r.text)
                       
                #Velocidad del viento
                myjson={'action':'insert',
                        'date':dt_string,
                        'base':'Base01',
                        'type':'windspeedAvg',
                        'value':'{:05.2f}'.format(KMh)}
                r = requests.post(url, data=myjson )
                print("2°" + r.text)
                #DIRECCION DEL VIENTO(SE DEBE MEJORAR MEDICION)
                myjson={'action':'insert',
                        'date':dt_string,
                        'base':'Base01',
                        'type':'winddirAvg',
                        'value':Direccion_Viento}
                r = requests.post(url, data=myjson )
                print("3°" + r.text)
                '''
                #TEMPERATURA
                myjson={'action':'insert',
                        'date':dt_string,
                        'base':'Base01',
                        'type':'tempAvg',
                        'value':'{:05.2f}'.format(temperatura)}
                r = requests.post(url, data=myjson )
                print("4°" + r.text)
                
                #PRESION
                myjson={'action':'insert',
                        'date':dt_string,
                        'base':'Base01',
                        'type':'pressureMax',
                        'value':'{:05.2f}'.format(presion)}
                r = requests.post(url, data=myjson )
                print("5°" + r.text)
                
                #HUMEDAD
                myjson={'action':'insert',
                        'date':dt_string,
                        'base':'Base01',
                        'type':'humidityAvg',
                        'value':'{:05.2f}'.format(humedad)}
                r = requests.post(url, data=myjson )
                print("6°" + r.text)
                '''
                print('................................')
            #RESPALDO SIN CONEXION NI CAMARA
            except:
                print('NO HAY CONEXION')
                data = 'Null {} Base01 photo 0 windspeedAvg {:05.2f} winddirAvg {} sensorFire 0\n'.format(dt_string,KMh,Direccion_Viento)
                file = open('respaldo','r+')
                content=file.read()
                long = len(content)
                file.seek(long)
                file.write(data)
                file.close()
                print('DATOS GUARDADOS')
                print('................................')
  

