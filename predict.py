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

def predict(image,username,classroom):

    folder = 'dbmodels/'+username+'/'+classroom
    X = []
    faces = extract_faces_from_image(image)
    for i in faces:
        X.append(i)

    file =  open(folder+'/map','r') 
    map = eval(file.read())
    students = []
    for i in map:
        students.append(i)
    X = np.array(X)
    X128 = Facenet(X)
    X512 = Facenet512(X)

    model128 = Sequential()
    output128 = 128
    model128.add(Dense(128, activation='relu', input_shape=(128,)))
    while len(students) < output128:
        output128 = output128 // 2
        model128.add(Dense(output128, activation='relu'))
    model128.add(Dense(len(students),activation='softmax'))
    model128.load_weights(folder+'/model128.h5')
    result1 = model128.predict(X128)

    model512 = Sequential()
    output512 = 512
    model512.add(Dense(512, activation='relu', input_shape=(512,)))
    while len(students) < output512:
        output512 = output512 // 2
        model512.add(Dense(output512, activation='relu'))
    model512.add(Dense(len(students),activation='softmax'))
    model512.load_weights(folder+'/model512.h5')
    result2 = model512.predict(X512)

    print(result1)
    print(result2)

    return 1