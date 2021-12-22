#ANEMOMETRO V3.0
import RPi.GPIO as GPIO
from time import sleep
import math

GPIO.setmode(GPIO.BCM)
Hall = 24

tiempo = 10 #segundos

def Contar_interrupciones(pin): #funcion de interrupcion para contar las vueltas del anemonmetro
    global interrupcion
    interrupcion=interrupcion+1 #0.333 "con tres imanes"
    sleep(0.1) #HAY QUE REVISAR

GPIO.setup(Hall, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(Hall, GPIO.RISING, callback=Contar_interrupciones)

def anemometro():
    cm_x_km = 100000.0 #centimetros en un km
    s_x_hs = 3600 #segundos en una hora
    radio = 8.5 #radio de giro del anemometro expresado en cm
    circunferencia = (2*math.pi)*radio #calculo de la circunferencia de giro
    rotaciones = interrupcion/3.0 #cantidad de rotaciones o vueltas completas
    distancia_km = (rotaciones * circunferencia)/cm_x_km #distancia en km
    km_x_s = distancia_km / tiempo #km/s
    km_x_hs = km_x_s * s_x_hs #km/h
    return km_x_hs
    interrupcion = 0
    
while True:
    sleep(tiempo)
    velocidad = anemometro()
    print('Viento a: {:05.2f} km/h' .format(velocidad)) #imprime la velocidad del viento en un formato de dos cifras decimales