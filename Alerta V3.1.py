#V3.1
#ENVIO DE IMAGENES A SERVIDOR CADA DETERMINADO PERIODO DE TIEMPO CON VALORES DE SENSORES, ALTERAR PARA EL USO CON CRON

#LIBRERIAS
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

#RUTAS:
#ruta carpeta donde se respaldan las imagenes
ruta = '/home/pi/Detector de incendios V3.0/imagenes/'
#ruta del modelo
ruta_modelo = ''


#TIEMPO DE BUCLE
lapse = 10

#IMAGEN ERROR
img_error ="error.jpg"
encoded_string_error=''
with open(img_error, "rb") as image_file:
    encoded_string_error = image_file.read()

#CONFIGURACION DE PINES
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


#Variables
RPM = 0
Radian = 0
Lineal = 0
KMh = 0
value = 0

#FUNCION PARA CONTAR INTERRUPCIONES
def Contar_Interrupciones(pin):
    global interrupcion
    interrupcion = interrupcion + 0.333 #0.333 cambiar segun cantidad de imanes en el sensor
#CALCULOS DEL ANEMOMETRO
def anemometro():
    cm_x_km = 100000.0 #centimetros en un km
    s_x_hs = 3600 #segundos en una hora
    radio = 8.5 #radio de giro del anemometro expresado en cm
    circunferencia = (2*math.pi)*radio #calculo de la circunferencia de giro
    rotaciones = interrupcion/3.0 #cantidad de rotaciones o vueltas completas
    distancia_km = (rotaciones * circunferencia)/cm_x_km #distancia en km
    km_x_s = distancia_km / lapse #km/s
    km_x_hs = km_x_s * s_x_hs #km/h
    return km_x_hs
    interrupcion = 0

#FUNCION PARA SUBIDA DE DATOS
def DataUpload(date,type,value,image):
    if image == 'Null':
        myjson={'action':'insert',
                'date':date,
                'base':'Base01',
                'type':type,
                'value':value,
                'image':encoded_string_error}
        r = requests.post(url, data=myjson )
        print(r.text + 'en {} {}'.format(date,type))
    if image == 0:
        myjson={'action':'insert',
                'date':date,
                'base':'Base01',
                'type':type,
                'value':value}
        r = requests.post(url, data=myjson )
        print(r.text + 'en {} {}'.format(date,type))
    else:
        myjson={'action':'insert',
                'date':date,
                'base':'Base01',
                'type':type,
                'value':value,
                'image':image}
        r = requests.post(url, data=myjson )
        print(r.text + 'en {} {}'.format(date,type))

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
    
    #VARIABLES PARA VELOCIDAD DEL VIENTO
    print('Proxima lecturas en {} segundos:'.format(lapse))
    Direccion_Viento = 0
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
    #PINES EXTRA
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
                
                #OBTENEMOS VALOR DE FECHA DE CADA LINEA
                fecha= '{} {}'.format(content[1],content[2])
                
                #SI NO HAY IMAGENES RESPALDADAS
                if content[0] == 'Null':
                    
                    #RESPUESTA DE MODELO
                    DataUpload(fecha,'sensorFire',content[3],0)
                    #IMAGEN
                    DataUpload(fecha,'photo',0,'Null')
                    #Velocidad del viento
                    DataUpload(dt_string,'windspeedAvg',content[4],0)
                    #DIRECCION DEL VIENTO(SE DEBE MEJORAR MEDICION)
                    DataUpload(fecha,'winddirAvg',content[5],0)
                    #TEMPERATURA
                    DataUpload(fecha,'tempAvg',content[6],0)
                    #PRESION
                    DataUpload(fecha,content[7],0)
                    #HUMEDAD
                    DataUpload(fecha,'humidityAvg',content[8],0)
                    
                #SI HAY IMAGENES RESPALDADAS
                else:
                    img ="{}{}.jpg".format(ruta,content[0])
                    encoded_string = ''
                    with open(img, "rb") as image_file:
                        encoded_string = image_file.read()
                        
                    #RESPUESTA DE MODELO
                    DataUpload(fecha,'sensorFire',content[3],0)
                    #IMAGEN
                    DataUpload(fecha,'photo',100,encoded_string)
                    #Velocidad del viento
                    DataUpload(dt_string,'windspeedAvg',content[4],0)
                    #DIRECCION DEL VIENTO(SE DEBE MEJORAR MEDICION)
                    DataUpload(fecha,'winddirAvg',content[5],0)
                    #TEMPERATURA
                    DataUpload(fecha,'tempAvg',content[6],0)
                    #PRESION
                    DataUpload(fecha,content[7],0)
                    #HUMEDAD
                    DataUpload(fecha,'humidityAvg',content[8],0)
                    remove(img)
                        
            file.close()
            #Borramos registros
            file = open('respaldo','w')
            file.write('')
            file.close()
            print('RESPALDOS SUBIDOS')
    except:
        print('ERROR DE CONEXION')
    finally:
        #Si hay camara
        if ret == True:
            try:
                cv2.imwrite('image.jpg', image)
                cap.release()
                
                #Invoca al modelo
                Clasificador.clasificador('image.jpg',ruta_modelo)
                value = Clasificador.clasificador.labelNoFuego
                
                #ABRIMOS IMAGEN PARA SUBIR
                encoded_string = ''
                img ="image.jpg"
                with open(img, "rb") as image_file:
                    encoded_string = image_file.read()
                    
                print('SUBIENDO DATOS...')
                
                #RESPUESTA DE MODELO
                DataUpload(dt_string,'sensorFire',value,0)
                #IMAGEN
                DataUpload(dt_string,'photo',100,encoded_string)
                #Velocidad del viento
                DataUpload(dt_string,'windspeedAvg','{:05.2f}'.format(KMh),0)
                #DIRECCION DEL VIENTO(SE DEBE MEJORAR MEDICION)
                DataUpload(dt_string,'winddirAvg',Direccion_Viento,0)
                #TEMPERATURA
                DataUpload(dt_string,'tempAvg','{:05.2f}'.format(temperatura),0)
                #PRESION
                DataUpload(dt_string,'pressureMax','{:05.2f}'.format(presion),0)
                #HUMEDAD
                DataUpload(dt_string,'humidityAvg','{:05.2f}'.format(humedad),0)
                print('DATOS SUBIDOS')
                print('.................................')
                
            except:
                
                #RESPALDO CUANDO NO HAY CONEXION
                print('NO HAY CONEXIÓN')
                
                #BUSCAMOS EN LOS RESPALDOS EL ULTIMO ID DE FOTOS
                file = open('respaldo','r')
                content = file.readlines()
                file.close()
                FOTO_ID = len(content)
                
                #REGISTRAMOS LA INFORMACION EN EL ARCHIVO
                #Hay que agregar los demas valores
                
                #sensorFire [3] - windspeedAvg [4] - winddirAvg [5] - tempAvg[6] - pressureMax[7] - humidityAvg[8]
                data = '{} {} {} {:05.2f} {} {:05.2f} {:05.2f} {:05.2f}\n'.format(FOTO_ID,dt_string,value,KMh,Direccion_Viento,temperatura,presion,humedad)
                
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
                print('..................................')
                
        #Si no hay camara
        else:
            try:
                print('NO SE DETECTA CAMARA')
                print('SUBIENDO DATOS SIN IMAGEN...')
                
                #RESPUESTA DE MODELO
                DataUpload(dt_string,'sensorFire',0,0)
                #IMAGEN
                DataUpload(dt_string,'photo',0,encoded_string_error)
                #Velocidad del viento
                DataUpload(dt_string,'windspeedAvg','{:05.2f}'.format(KMh),0)
                #DIRECCION DEL VIENTO(SE DEBE MEJORAR MEDICION)
                DataUpload(dt_string,'winddirAvg',Direccion_Viento,0)
                #TEMPERATURA
                DataUpload(dt_string,'tempAvg','{:05.2f}'.format(temperatura),0)
                #PRESION
                DataUpload(dt_string,'pressureMax','{:05.2f}'.format(presion),0)
                #HUMEDAD
                DataUpload(dt_string,'humidityAvg','{:05.2f}'.format(humedad),0)
                print('DATOS SUBIDOS')
                print('.................................')
                
            #RESPALDO SIN CONEXION NI CAMARA
            except:
                
                print('NO HAY CONEXION')
                data = 'Null {} 0 {:05.2f} {} {:05.2f} {:05.2f} {:05.2f}\n'.format(FOTO_ID,dt_string,KMh,Direccion_Viento,temperatura,presion,humedad)
                file = open('respaldo','r+')
                content=file.read()
                long = len(content)
                file.seek(long)
                file.write(data)
                file.close()
                print('DATOS GUARDADOS')
                print('.................................')

