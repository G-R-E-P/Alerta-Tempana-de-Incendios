import Clasificador
import cv2
cap = cv2.VideoCapture(0)
ret,image = cap.read()
        
Clasificador.clasificador(image, "/home/pi/Detector de incendios V3.0/modelfile.eim")
value = Clasificador.clasificador.labelNoFuego