import cv2 as cv
from PIL import Image
import os
import numpy as np
from mtcnn.mtcnn import MTCNN
from Facenet import Facenet
from Facenet512 import Facenet512
import tensorflow as tf
from keras.layers import Dense,Activation,Flatten,Convolution2D,MaxPooling2D,Dropout,BatchNormalization ,ZeroPadding2D
from keras.models import Sequential 
from keras.optimizers import Adam
from keras.utils import to_categorical
from keras.losses import CategoricalCrossentropy
import keras
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split

def extract_faces_from_image(image):
  detector = MTCNN()
  faces = detector.detect_faces(image)
  image_array = []
  for result in faces:
    x, y, w, h = result['box']
    face = image[y:y+h, x:x+w]
    face_img_resized = cv.resize(face, (160,160))
    image_array.append(face_img_resized)
  return image_array


def trainmodel(username, classroom):
    X = []
    Y = []

    folder = 'upload/'+username+'/'+classroom
    students = []
    for i in os.listdir(folder):
        students.append(i.split('.')[0])
    
    number_of_students = len(students)
    print(students)
    for j in range(len(students)):
        cap = cv.VideoCapture(folder+'/'+students[j]+'.mp4')
        count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if count % 500 == 0:
                faces = extract_faces_from_image(frame)
                for i in faces:
                    X.append(i)
                    Y.append(j)
                    #cv.imwrite(folder+'/'+PERSON+'/image_'+str(count)+'.jpg',i)
            count += 1
    
    map = {}
    for i in range(len(students)):
        map[students[i]] = i

    X = np.array(X)
    Y = np.array(Y)
    X = tf.convert_to_tensor(X, dtype=tf.float32)
    Y = to_categorical(Y)
    print(Y)
    X128 = Facenet(X)
    X512 = Facenet512(X)

    x_train128,x_test128,y_train128,y_test128=train_test_split(X128,Y,test_size=0.1, random_state=42)
    x_train512,x_test512,y_train512,y_test512=train_test_split(X512,Y,test_size=0.1, random_state=42)

    model128 = Sequential()
    output128 = 128
    model128.add(Dense(128, activation='relu', input_shape=(128,)))
    while len(students) < output128:
        output128 = output128 // 2
        model128.add(Dense(output128, activation='relu'))
    model128.add(Dense(len(students),activation='softmax'))
    model128.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    print(model128.summary())
    history128 = model128.fit(x_train128, y_train128, epochs=10, batch_size=32, validation_data=(x_test128, y_test128))


    model512 = Sequential()
    output512 = 512
    model512.add(Dense(512, activation='relu', input_shape=(512,)))
    while len(students) < output512:
        output512 = output512 // 2
        model512.add(Dense(output512, activation='relu'))
    model512.add(Dense(len(students),activation='softmax'))
    model512.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    print(model512.summary())
    history512 = model512.fit(x_train512, y_train512, epochs=10, batch_size=32, validation_data=(x_test512, y_test512))


    # write the code for saving the list, the models
    os.makedirs('dbmodels/'+username+'/'+classroom+'/', exist_ok=True)
    mapfile = open('dbmodels/'+username+'/'+classroom+'/map', 'x')
    mapfile.write(str(map))
    mapfile.close()
    model128.save('dbmodels/'+username+'/'+classroom+'/'+'model128.h5')
    model512.save('dbmodels/'+username+'/'+classroom+'/'+'model512.h5')
    return 1
    

    


    
        
    
    
    

    
    