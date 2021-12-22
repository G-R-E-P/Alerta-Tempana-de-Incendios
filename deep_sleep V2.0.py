import machine
from machine import Pin
from time import sleep

data = open('registro.txt','r+')
content = data.readline()
if content == '':
    data.write('1.17')
else:
    number = float(content)
    number = number + 1.17
    number = str(number)
    data.seek(0)
    data.write(number)
data.close()


sleep(5)
print('Registre con exito, volvere a dormir')
sleep(1)

#sleep for indefinite time
machine.deepsleep()