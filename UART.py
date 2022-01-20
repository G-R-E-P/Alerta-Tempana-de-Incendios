from machine import Pin, UART
from time import sleep
#(BUZZ TX0RX0, VELOCIDAD DE COMUNICACION BAUDIOS)
uart = UART(2,115200)
pin = Pin(2,Pin.OUT)
#INICIALIZAMOS (BAUDIOS, BITS, BIT PARA ERRORES, STOP)
uart.init(115200,bits = 8, parity = None, stop = 1)
#VARIABLE EN BITS
ch=b''
uart.write('UART WORKING!')
while True:
    #si es diferente de 0 es que no tiene informacion
    if uart.any()>0:
        #LO QUE HAYA SE ALMACENA EN VARIABLE
        ch = uart.readline()
        #Identificar lo que entra
        #uart.write('entrada:{}'.format(ch))
        if  ch == b'on\r\n':
            uart.write('Led on!')
            pin.on()
        if ch == b'off\r\n':
            uart.write('Led off!')
            pin.off()