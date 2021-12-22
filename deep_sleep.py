import machine
from machine import Pin
from time import sleep

count = 1
milimetros = 0
sleep(1)
milimetros = (count * 1.17)
print(milimetros , "mm")
datos = open("cangilometro_datos", "w")
datos.write("{:02}".format (milimetros) + " mm\n")
datos.close()

"""led = Pin (2, Pin.OUT) 
#blink LED
led.value(0)
sleep(1)
led.value(1)
sleep(1)
led.value(0)
sleep(1)
led.value(1)
sleep(1)
led.value(0)
sleep(1)
led.value(1)
sleep(1)"""

# wait 5 seconds so that you can catch the ESP awake to establish a serial communication later
# you should remove this sleep line in your final script
sleep(5)
print('Estoy despierto, pero me volvere a dormir')
sleep(1)

#sleep for indefinite time
machine.deepsleep()