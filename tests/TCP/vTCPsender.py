import cv2, socket, pickle, os
import numpy as np
s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF,1000000)
server_ip = "10.0.0.12"
server_port = 5000

cap = cv2.VideoCapture(2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)
while True:
	ret,photo = cap.read()
	ret,buffer = cv2.imencode(".jpg",photo,[int(cv2.IMWRITE_JPEG_QUALITY),30])
	x_as_bytes = pickle.dumps(buffer)
	s.sendto((x_as_bytes),(server_ip,server_port))
	if cv2.waitKey(10)==13:
		break
cv2.destroyAllWindows()
cap.release()