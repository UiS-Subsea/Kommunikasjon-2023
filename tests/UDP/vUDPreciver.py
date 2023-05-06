import cv2, socket, numpy, pickle
BUFF_SIZE = 65536
s=socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
con_adr = ('0.0.0.0', 5000)
s.bind(con_adr)
while True:
    x=s.recvfrom(BUFF_SIZE)
    clientip = x[1][0]
    data=x[0]
    data=pickle.loads(data)
    data = cv2.imdecode(data, cv2.IMREAD_COLOR)
    cv2.imshow('server', data) #to open image
    if cv2.waitKey(10) == 13:
        break
cv2.destroyAllWindows()