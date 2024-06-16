import eventlet.wsgi
from flask import Flask
import socketio
import eventlet
from keras.models import load_model
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
from keras.optimizers import Adam
from matplotlib import image as npimg
sio = socketio.Server()


app =Flask(__name__)
speed_limit=10


def img_preprocess(img):
  img = img[60:135,:,:]
  img = cv2.cvtColor(img,cv2.COLOR_RGB2YUV)
  img = cv2.GaussianBlur(img,(3,3),0,)
  img = cv2.resize(img, (200,66))
  img = img/255
  return img

@sio.on('telemetry')
def telemetry(sid,data):
    speed = float(data['speed'])
    image = Image.open(BytesIO(base64.b64decode(data['image'])))
    image = np.asarray(image)
    image = img_preprocess(image)
    image = np.array([image])
    steering_angle = float(model.predict(image))
    throttle = 1.0 - speed/speed_limit
    print('{}  {}  {}  '.format(steering_angle,throttle,speed_limit))
    send_control(steering_angle,throttle)

@sio.on('connect')  # connect,message and disconnect are reserved
def connect(sid,environ):
    print('Connected')
    send_control(0,0)

    
def send_control(steering,throttle):
    sio.emit('steer',data={
        'steering_angle' : steering.__str__(),
        'throttle': throttle.__str__() 
    })
    
    
if __name__ == '__main__':
    model = load_model('modelFinal3.h5')
    # model.compile(optimizer = Adam(),loss='mean_squared_error')
    app = socketio.Middleware(sio,app)
    eventlet.wsgi.server(eventlet.listen(('',4567)),app)