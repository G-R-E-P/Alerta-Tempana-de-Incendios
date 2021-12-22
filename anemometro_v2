#MEDIR LA VELOCIDAD DEL VIENTO V2.

import RPi.GPIO as GPIO
from time import sleep
import math

GPIO.setmode(GPIO.BCM)
Hall = 24

def Contar_interrupciones(pin): #funcion de interrupcion para contar las vueltas del anemonmetro
	global interrupcion
	interrupcion=interrupcion+1 #0.333 "con tres imanes"
	sleep(0.1)
	
GPIO.setup(Hall, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(Hall, GPIO.RISING, callback=Contar_interrupciones)

while True:
	cm_x_km = 100000.0 #centimetros en un km
	s_x_hs = 3600 #segundos en una hora
	radio = 8.5 #radio de giro del anemometro expresado en cm
	interrupcion = 0
	tiempo = 10 #segundos
	sleep(10)
	circunferencia = (2*math.pi)*radio #calculo de la circunferencia de giro
	rotaciones = interrupcion/3.0 #cantidad de rotaciones o vueltas completas 
	distancia_km = (rotaciones * circunferencia)/cm_x_km #distancia en km
	km_x_s = distancia_km / tiempo #km/s
	km_x_hs = km_x_s * s_x_hs #km/h
	print('Viento a: {:05.2f} km/h' .format(km_x_hs)) #imprime la velocidad del viento enuun formato de dos cifras decimales

