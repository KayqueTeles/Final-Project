# -*- coding: utf-8 -*-
"""projeto-final-03_AutoEnc.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Z4c7cJO7ofbCFw8U6mYBHBTEe2OpOuHg

# Final Project - Indoor Localization with BLE Beacons and RSSI

## Convolutional Neural Network - Auto Encoder Approach

# Setting Workspace
"""

import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from keras.utils import np_utils
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

"""# Euclidian Distance between Two Points (Evaluation Metric)

It will be used to compare the actual position with the predicted position
"""

def l2_dist(p1, p2):
    x1,y1 = p1
    x2,y2 = p2
    x1, y1 = np.array(x1), np.array(y1)
    x2, y2 = np.array(x2), np.array(y2)
    dx = x1 - x2
    dy = y1 - y2
    dx = dx ** 2
    dy = dy ** 2
    dists = dx + dy
    dists = np.sqrt(dists)
    print('MAE: %.3f' % (np.mean(dists)))
    #print('MSE: %.3f' % (np.mean(np.square(dists))))
    return dists

"""# Getting labed Data Ready"""

file = 'drive/My Drive/CBPF/Deep Learning/Projeto/iBeacon_RSSI_Labeled.csv'
data = pd.read_csv(file)

def fix_pos(x_cord):
    x = 87 - ord(x_cord.upper())
    return x

data['x'] = data['location'].str[0]
data['y'] = data['location'].str[1:]
data.drop(["location"], axis = 1, inplace = True)
data["x"] = data["x"].apply(fix_pos)
data["y"] = data["y"].astype(int)

data.head()

# Input
X = data.iloc[:, 1:-2]
# Labels
y = data.iloc[:, -2:]
y = y.astype('float32')

X_img = np.zeros(shape = (X.shape[0], 25, 25, 1, ))
beacon_coords = {"b3001": (5, 9), 
                 "b3002": (9, 14), 
                 "b3003": (13, 14), 
                 "b3004": (18, 14), 
                 "b3005": (9, 11), 
                 "b3006": (13, 11), 
                 "b3007": (18, 11), 
                 "b3008": (9, 8), 
                 "b3009": (2, 3), 
                 "b3010": (9, 3), 
                 "b3011": (13, 3), 
                 "b3012": (18, 3), 
                 "b3013": (22, 3),}

for key, value in beacon_coords.items():
  X_img[:, value[0], value[1], 0] -= X[key].values/200
  print(key, value)

"""# Getting Unlabed Data Ready"""

file = 'drive/MyDrive/CBPF/Deep Learning/Projeto/iBeacon_RSSI_Unlabeled.csv'
data_un = pd.read_csv(file)

data_un.drop(["location", "date"], axis = 1, inplace = True)

data_un.head()

"""Separating the data in Inputs and Labels"""

# Input
X_un = data

"""Tranforming each input in a image"""

X_img = np.zeros(shape = (X_un.shape[0], 25, 25, 1, ))
beacon_coords = {"b3001": (5, 9), 
                 "b3002": (9, 14), 
                 "b3003": (13, 14), 
                 "b3004": (18, 14), 
                 "b3005": (9, 11), 
                 "b3006": (13, 11), 
                 "b3007": (18, 11), 
                 "b3008": (9, 8), 
                 "b3009": (2, 3), 
                 "b3010": (9, 3), 
                 "b3011": (13, 3), 
                 "b3012": (18, 3), 
                 "b3013": (22, 3),}

for key, value in beacon_coords.items():
  X_img[:, value[0], value[1], 0] -= X[key].values/200
  print(key, value)

"""A exaple of how the image looks"""

from PIL import Image

img = Image.fromarray(X_img[500, :, :, 0] * 255)
plt.imshow(img)

"""Splitting the data"""

train_x_un, val_x_un = train_test_split(X_img, test_size = 0.2, shuffle = False)

"""# Building Model"""

from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import Model
from tensorflow.keras import Input
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Conv2DTranspose

from keras.layers import GaussianNoise, AveragePooling2D, SpatialDropout2D

def create_deep():
  seed = 7
  np.random.seed(seed)
  inputs = Input(shape=(train_x_un.shape[1], train_x_un.shape[2], 1))

  # a layer instance is callable on a tensor, and returns a tensor
  x = Conv2D(24, kernel_size=(3,3), activation='relu', padding = "valid", 
             data_format="channels_last")(inputs)
  x = MaxPooling2D(2)(x)
  x = Conv2D(24, kernel_size=(3,3), activation='relu', padding = "valid", 
             data_format="channels_last")(x)
  x = MaxPooling2D(2)(x)
  x = Conv2D(24, kernel_size=(3,3), activation='relu', padding = "valid", 
             data_format="channels_last")(x)
  x = Conv2DTranspose(24, kernel_size=(3,3),strides = (2,2), activation='relu',
                      padding = "valid", data_format="channels_last")(x)
  x = Conv2DTranspose(16, kernel_size=(3,3),strides = (2,2), activation='relu',
                      padding = "valid", data_format="channels_last")(x)
  x = Conv2DTranspose(8, kernel_size=(3,3),strides = (2,2), activation='relu', 
                      padding = "valid", data_format="channels_last")(x)
  x = Conv2DTranspose(1, kernel_size=(3,3), activation='relu', padding = "valid",
                      data_format="channels_last")(x)

  # This creates a model that includes
  # the Input layer and three Dense layers
  model = Model(inputs=inputs, outputs=x)
  model.compile(optimizer=Adam(0.001),
                loss='mse')
  return model

model2 = create_deep()
model2.summary()

early_stopping = EarlyStopping(monitor='val_loss', patience=100, verbose=0, 
                               mode='auto', restore_best_weights=True)

out = model2.fit(x = train_x_un, y = train_x_un, 
                 validation_data = (val_x_un, val_x_un),
                 epochs=15, 
                 batch_size=10, 
                 #batch_size=200, 
                 verbose=1, 
                 callbacks = [early_stopping])

"""Getting the encoder part of the auto encoder and then add on a new dense layer to make predictions."""

predictions = Dense(8, activation='relu')(Flatten()(model2.layers[5].output))
predictions = Dense(2, activation = 'relu')(predictions)

model3 = Model(inputs=model2.input, outputs=predictions)
model3.summary()

"""Training only the last layer to start. This will help prevent the auto encoders being immediately being washed out because the last layer is uninitialized"""

for layer in model3.layers[:-2]:
    layer.trainable = False
model3.compile(optimizer=Adam(.001, clipnorm = .5, clipvalue = .5),
              loss='mse')

seed = 7
np.random.seed(seed)

# Training and Test
X_train, X_test, y_train, y_test = train_test_split(X_img, y, test_size = 0.4, shuffle = False)
# Trainig and Validation
X_train_2, X_val, y_train_2, y_val = train_test_split(X_train, y_train, test_size = 0.2, shuffle = True)

hist = model3.fit(x = X_train_2, y = y_train_2, validation_data = (X_val,y_val), epochs=500, batch_size=50,  verbose=0, callbacks = [early_stopping])

# summarize history for loss
plt.plot(hist.history['loss'])
plt.plot(hist.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper right')
plt.show()

mse = model3.evaluate(X_val, y_val, verbose=0)
print(mse)

"""Training all the layers"""

for layer in model3.layers[:-2]:
    layer.trainable = True
model3.compile(optimizer=Adam(.001, clipnorm = .5, clipvalue = .5),
              loss='mse',)
hist = model3.fit(x = X_train_2, y = y_train_2, validation_data = (X_val,y_val), epochs=500, batch_size=50,  verbose=0, callbacks = [early_stopping])
#preds = model3.predict(X_val)
# l2dists_mean, l2dists = l2_dist((preds[:, 0], preds[:, 1]), (val_y["x"], val_y["y"]))
# print(l2dists_mean)

# summarize history for loss
plt.plot(hist.history['loss'])
plt.plot(hist.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper right')
plt.show()

mse = model3.evaluate(X_val, y_val, verbose=0)
print(mse)

"""## Training with full dataset"""

model3 = Model(inputs=model2.input, outputs=predictions)
model3.summary()

for layer in model3.layers[:-2]:
    layer.trainable = False
model3.compile(optimizer=Adam(.001, clipnorm = .5, clipvalue = .5),
              loss='mse')

y_frames = [y_train_2, y_val]

X_train_shuffled = np.concatenate((X_train_2, X_val), axis=0)
y_train_shuffled = pd.concat(y_frames)

hist = model3.fit(x = X_train_shuffled, y = y_train_shuffled, epochs=500, batch_size=50,  verbose=0, callbacks = [early_stopping])

for layer in model3.layers[:-2]:
    layer.trainable = True
model3.compile(optimizer=Adam(.001, clipnorm = .5, clipvalue = .5),
              loss='mse',)
hist = model3.fit(x = X_train_shuffled, y = y_train_shuffled, epochs=500, batch_size=50,  verbose=0, callbacks = [early_stopping])
#preds = model3.predict(X_val)
# l2dists_mean, l2dists = l2_dist((preds[:, 0], preds[:, 1]), (val_y["x"], val_y["y"]))
# print(l2dists_mean)

# summarize history for loss
plt.plot(hist.history['loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train'], loc='upper right')
plt.show()

mse = model3.evaluate(X_val, y_val, verbose=0)
print(mse)

"""Calculating euclidian error"""

preds = model3.predict(X_test)
l2dists = l2_dist((preds[:, 0], preds[:, 1]), (y_test["x"], y_test["y"]))

df = y_test 
df['error'] = l2dists
df.head()

"""Heatmap of average euclidian error"""

import seaborn as sns

heatmap_data = pd.pivot_table(df, values='error', 
                              index='y', 
                              columns='x', 
                              aggfunc='mean',)
                              #fill_value=0)
#heatmap_data.head()

#sns.clustermap(heatmap_data, cmap="mako", row_cluster=False, col_cluster=False , cbar_pos=(0, .2, .03, .4))
#plt.savefig('heatmap_with_Seaborn_clustermap_python.jpg',
#            dpi=150, figsize=(8,12))

fig, ax = plt.subplots(figsize=(20,10))

heatmap_data.sort_index(level=0, ascending=False, inplace=True)
sns.heatmap(heatmap_data, annot=True, linewidths=0.4, cmap="YlOrRd", ax=ax)
#sns.heatmap(heatmap_data, linewidths=0.4, cmap="YlOrRd")

"""Adjust the metric to meters"""

preds_real = preds * 3.0
y_test_real = y_test * 3.0
l2dists_real = l2_dist((preds_real[:, 0], preds_real[:, 1]), (y_test_real["x"], y_test_real["y"]))

sortedl2 = np.sort(l2dists)
prob = 1.0 * np.arange(len(sortedl2)) / (len(sortedl2) - 1) 
fig, ax = plt.subplots()
lg1 = ax.plot(sortedl2, prob, color='black')

plt.title('CDF of Euclidean distance error')
plt.xlabel('Distance')
plt.ylabel('Probability')
plt.grid(True)
gridlines = ax.get_xgridlines() + ax.get_ygridlines()
for line in gridlines:
    line.set_linestyle('-.')

#######################

sortedl2 = np.sort(l2dists_real)
prob = 1.0 * np.arange(len(sortedl2)) / (len(sortedl2) - 1) 
fig, ax = plt.subplots()
lg1 = ax.plot(sortedl2, prob, color='black')

plt.title('CDF of Euclidean distance error')
plt.xlabel('Distance (m)')
plt.ylabel('Probability')
plt.grid(True)
gridlines = ax.get_xgridlines() + ax.get_ygridlines()
for line in gridlines:
    line.set_linestyle('-.')

#plt.savefig('Figure_CDF_error.png', dpi=300)
plt.show()
plt.close()