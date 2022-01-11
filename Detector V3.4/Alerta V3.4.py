#V3.4
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
ruta = '/home/pi/Detector de Incendios V 3.4/imagenes/'
#ruta del modelo
ruta_modelo = '/home/pi/Detector de Incendios V 3.4/modelfile.eim'


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

#INICIALIZAMOS LOS PINES COMO ENTRADAS Y PUD_UP PARA DETECTAR PULSO COMO 0
GPIO.setup(Hall, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(norte, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(sur, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(oeste, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(este, GPIO.IN, pull_up_down = GPIO.PUD_UP)

#Inicializa el sensor atmosferico
try:
    port = 1
    address = 0x76
    bus = smbus2.SMBus(port)
    bme280.load_calibration_params(bus,address)
except:
    print('El programa no se puede ejecutar sin sensor BME280')
    exit()

#FUNCION PARA CONTAR INTERRUPCIONES PARA ANEMOMETRO
def Contar_Interrupciones(pin):
    global interrupcion
    interrupcion = interrupcion + 1
#METODO PARA DETECTAR EVENTOS ANEMOMETRO
GPIO.add_event_detect(Hall, GPIO.RISING, callback = Contar_Interrupciones)
    
#CALCULOS DE ANEMOMETRO
def anemometro(interrup):
    cm_x_km = 100000.0 #centimetros en un km
    s_x_hs = 3600 #segundos en una hora
    radio = 8.5 #radio de giro del anemometro expresado en cm
    circunferencia = (2*math.pi)*radio #calculo de la circunferencia de giro
    #rotaciones = interrupcion/3.0 #cantidad de rotaciones o vueltas completas
    distancia_km = (interrup * circunferencia)/cm_x_km #distancia en km
    km_x_s = distancia_km / lapse #km/s
    km_x_hs = km_x_s * s_x_hs #km/h
    print('Viento a: {:05.2f} km/h' .format(km_x_hs))
    interrupcion = 0
    return km_x_hs
    
#SENSOR BME280
def BME280():
    #Datos del  sensor
    bme280_data = bme280.sample(bus,address)
    temperatura = bme280_data.temperature
    presion = bme280_data.pressure
    humedad = bme280_data.humidity
    print('TEMP: {:05.2f}C PRES: {:05.2f}hPa HUME: {:05.2f}%' .format(temperatura, presion, humedad))
    return temperatura,presion,humedad

#VELETA
def veleta(): #La direccion del viento tiene que ser mas precisa
    if (GPIO.input(norte) == False):
        print('VIENTO NORTE')
        return 0
    elif (GPIO.input(sur) == False):
        print('VIENTO SUR')
        return 180
    elif (GPIO.input(oeste) == False):
        print('VIENTO OESTE')
        return 90
    elif (GPIO.input(este) == False):
        print('Viento ESTE')
        return 270
    else:
        print('NO SE DETECTA VELETA')
        return 333
#FUNCION PARA SUBIDA DE DATOS
def DataUpload(date,Type,value,image):
    #Tiempo de espera para cancelar la subida de archivos
    Timeout = 10
    if image == 'Null':
        myjson={'action':'insert',
                'date':date,
                'base':'Base01',
                'type':Type,
                'value':value,
                'image':encoded_string_error}
        r = requests.post(url, data=myjson, timeout = Timeout)
        print(r.text + ' in {} {}'.format(date,Type))
    if image == 0:
        myjson={'action':'insert',
                'date':date,
                'base':'Base01',
                'type':Type,
                'value':value}
        r = requests.post(url, data=myjson,timeout = Timeout)
        print(r.text + ' in {} {}'.format(date,Type))
    else:
        myjson={'action':'insert',
                'date':date,
                'base':'Base01',
                'type':Type,
                'value':value,
                'image':image}
        r = requests.post(url, data=myjson, timeout = Timeout)
        print(r.text + ' in {} {}'.format(date,Type))
 

#Bucle
while True:
    interrupcion = 0
    print('Proxima lecturas en {} segundos:'.format(lapse))
    sleep(lapse)
    
    #FECHA
    now = datetime.now()
    dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
    
    #VELOCIDAD DEL VIENTO
    KMh = anemometro(interrupcion)
    #CONTROL DE ERROR BME280
    temperatura = 0
    presion = 0
    humedad = 0
    try:
        #TEMPERATURA PRESION HUMEDAD
        temperatura,presion,humedad = BME280()
    except:
        print('ERROR EN SENSOR BME280')
    
    #DIRECCION DEL VIENTO
    Direccion_Viento = veleta()
    
    #interrupcion para controlar error de conexion de camara
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
                    DataUpload(fecha,'pressureMax',content[7],0)
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
                    DataUpload(fecha,'pressureMax',content[7],0)
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
        print('NO SE PUDO SUBIR DATOS')
    finally:
        #Si hay camara
        if ret == True:
            value = 0
            try:
                cv2.imwrite('image.jpg', image)
                cap.release()
                
                #Invoca al modelo
                Clasificador.clasificador('image.jpg',ruta_modelo)
                value = Clasificador.clasificador.labelNoFuego
                print('value = {}'.format(value))
                
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
                data = 'Null {} 0 {:05.2f} {} {:05.2f} {:05.2f} {:05.2f}\n'.format(dt_string,KMh,Direccion_Viento,temperatura,presion,humedad)
                file = open('respaldo','r+')
                content=file.read()
                long = len(content)
                file.seek(long)
                file.write(data)
                file.close()
                print('DATOS GUARDADOS')
                print('.................................')
