#import machine
#from machine import Pin
from time import sleep

data = open('registro','r+')
content = data.readline()
if content == '':
    data.write('1.17')
else:
    number_float = float(content)
    number = number_float + 1.17
    number_str = str(number)
    data.seek(0)
    data.write(number_str)
data.close()


sleep(5)
print('Registre con exito, volvere a dormir')
sleep(1)

#sleep for indefinite time
#machine.deepsleep()