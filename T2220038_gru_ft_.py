# -*- coding: utf-8 -*-
"""T2220038_GRU-FT .ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tbZ7AMtPfRCN2MLUSxSuIrGWxfkRRq37
"""

import numpy as np
import pandas as pd

!pip install gensim

!pip install scikeras

import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

"""Import Libraries


"""

from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords 
from nltk.stem import WordNetLemmatizer
from numpy import array

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import pydot

import os
import re
import shutil
import string
from collections import Counter

import tensorflow as tf
from tensorflow.keras import regularizers
from tensorflow.keras import layers
from tensorflow.keras import losses
from tensorflow.keras import preprocessing

from tensorflow.keras.preprocessing.text import Tokenizer,one_hot

from tensorflow.keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers.core import Activation, Dropout, Dense
from tensorflow.keras.constraints import MaxNorm
from tensorflow.keras.utils import to_categorical
from keras.layers import Flatten, GlobalMaxPooling1D, Embedding, Conv1D, LSTM, GRU

import sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix

import gensim.downloader as api

from tensorflow.keras.layers import Bidirectional

"""LOAD DATA

"""

data = pd.read_csv("/content/sample_data/augmented_fewshot_new.csv")

data

data.tail()

data.shape

label_map = {
    1:'positive',
    0:'neutral',
    -1:'negative',
    -2:'very negative'
    }

data['predicted'] = data['intensity'].map(label_map)
data.head()

data.head(10582)

#checks for missing value 
data.isna().sum()
data.isnull().sum()

data.dropna(inplace=True)

data.isna().sum()
data.isnull().sum()

data.shape

"""DATA PRE-PROCESSING"""

!pip install text_hammer 
import text_hammer as th

def text_preprocessing(data,col_name):
    column = col_name
    data[column] = data[column].progress_apply(lambda x:str(x).lower())
    data[column] = data[column].progress_apply(lambda x: th.cont_exp(x))
    data[column] = data[column].progress_apply(lambda x: th.remove_emails(x))
    data[column] = data[column].progress_apply(lambda x: th.remove_html_tags(x))
    data[column] = data[column].progress_apply(lambda x: th.remove_special_chars(x))
    data[column] = data[column].progress_apply(lambda x: th.remove_accented_chars(x))
    data[column] = data[column].progress_apply(lambda x: th.make_base(x)) #ran -> run,
    return(data)

data['posts'] = data['posts'].astype(str)

data_clean = text_preprocessing(data, 'posts')
#data_clean = text_preprocessing(data.decode('utf-8'), 'Posts')
#data['Posts_clean'] = data['Posts'].apply(lambda x: text_preprocessing(x.decode('utf-8'), 'Posts'))

data_clean.to_csv('Preprocessed_multiclass.csv', index=False)

#check num of unique word
from collections import Counter
unique_words = Counter(" ".join(data_clean['posts'].values.tolist()).split(" ")).most_common(50)
results = pd.DataFrame(unique_words, columns=['Word', 'Frequency']) 
print(results)

#check num of words in column
data_clean['num_words_post'] = data_clean['Posts'].apply(lambda x:len(str(x).split()))

data_clean.head()

data_clean.shape

"""LEBEL ENCODING"""

def get_intensity(predicted):
  if predicted == 'very negative':
    return -2
  elif predicted == 'positive':
    return 1
  elif predicted == 'neutral':
    return 0
  elif predicted == 'negative':
    return -1
  else:
    return 


data_clean["intensity"] = data_clean['predicted'].apply(get_intensity)
data_clean.head()

data_clean['intensity'].dtypes

data_clean.head(10)

data_clean.tail()

# converting string labels to int labels

label_map = {
    'positive': 1,
    'very negative': -2,
    'negative': -1,
    'neutral': 0
}

data_clean['intensity'] = data_clean['predicted'].map(label_map)
data_clean.head()

#total distribution of data based on sentiment
data_clean['intensity'].value_counts()

data_clean['predicted'].value_counts()

#data_clean.Sentiments = data_clean.Sentiments.replace({'Very Negative':-2, 'Negative':-1, 'Neutral' :0, 'Positive':1, 'Very Positive':2})

"""DATA ANALYSIS"""

max_num_content = data_clean['num_words_post'].max()
print(max_num_content)

data_clean['num_words_post'].describe()

sns.set(style="whitegrid")
sns.boxplot(x = data_clean['num_words_post'])

import seaborn as sns
import matplotlib.pyplot as plt

categories = ["negative", "positive", "very negative", "neutral"]
values = [4259, 1150, 1155 , 4315]

sns.barplot(x=categories, y=values)
plt.title("Bar Chart")
plt.xlabel("valence")
plt.ylabel("arousa")
sns.set_palette("pastel")
plt.show()

"""SPLIT DATASET"""

data_clean = pd.read_csv('/content/Preprocessed_multiclass.csv')

data_clean['predicted'].dtypes

from operator import length_hint
#Split the data into 90% training and 10% testing
X_train, X_test, y_train, y_test = train_test_split(data_clean['posts'].tolist(), data_clean['intensity'].tolist(), train_size = 0.9 , random_state = 42, stratify = data_clean['intensity'])

print(length_hint(X_train)), print(length_hint(y_train))
print(length_hint(X_test)), print(length_hint(y_test))

print(pd.DataFrame(y_train).value_counts())

print(pd.DataFrame(y_test).value_counts())

"""SET CATEGORY VALUE"""

num_classes = 4

y_train = to_categorical(y_train, num_classes, dtype= 'int64')
y_test = to_categorical(y_test, num_classes, dtype= 'int64')

print(y_train)

"""TOKENIZATION"""

#Parameter
num_words = 10580 
max_length = 600
pad_type = 'post'

#initialize the tokenizer class
tokenizer = Tokenizer(num_words, lower=True)

#generate word index dictionary
tokenizer.fit_on_texts(X_train)
word_index = tokenizer.word_index

print(len(word_index))

type(X_train)

"""WORD EMBEDDING"""

# Generate and padding to the sequences
x_train = tokenizer.texts_to_sequences(X_train) 
x_train_pad = pad_sequences(x_train, padding= pad_type, maxlen = max_length)

x_test = tokenizer.texts_to_sequences(X_test) 
x_test_pad = pad_sequences(x_test, padding= pad_type, maxlen = max_length)

x_train_pad[0]

"""FASTTEXT"""

pip install fasttext

import fasttext
#import fasttext.util

#model = fasttext.train_unsupervised("/content/Preprocessed_multiclass.csv")

#model.get_nearest_neighbors("cancer")

#model.get_nearest_neighbors("scream")

import fasttext.util

# Load FastText model
fasttext.util.download_model('en', if_exists='ignore')  # Download the English model if needed
#fasttext_model_path = 'cc.en.100.bin'
fasttext_model = fasttext.load_model("cc.en.300.bin")
 #cc.en.300.bin
vector_size = 300

fasttext_weight_matrix = np.zeros((num_words, vector_size))
fasttext_weight_matrix.shape

for word_index in range(1, num_words):
    if word_index in tokenizer.index_word:
        word = tokenizer.index_word[word_index]
        if word in fasttext_model.words:
            fasttext_weight_matrix[word_index] = fasttext_model.get_word_vector(word)
        else:
            fasttext_weight_matrix[word_index] = np.zeros(300)
    else:
         #Handle missing key however you wish
        pass

"""GRU"""

#Hyper parameters
embedding_dim = 300   #embedding layer will create a vector in 300 dimensions
class_num = num_classes #we have 4 categories to classify

model3 = Sequential()
model3.add(Embedding(input_dim = num_words, output_dim = embedding_dim, input_length= x_train_pad.shape[1], weights = [fasttext_weight_matrix], trainable = False))
model3.add(Dropout(0.2))
model3.add(GRU(200, return_sequences = True))
model3.add(Dropout(0.2))
model3.add(GRU(300, return_sequences = True))
model3.add(Dropout(0.2))
model3.add(GRU(200, return_sequences = True))
model3.add(Dropout(0.2))
model3.add(Flatten())
model3.add(tf.keras.layers.Dense(100, activation='relu'))
model3.add(tf.keras.layers.Dense(64, activation='relu'))
model3.add(Dense(class_num, activation = 'softmax'))

model3.summary()

# Set the training parameters
model3.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

NUM_EPOCHS = 20

history = model3.fit(x_train_pad, y_train, epochs=NUM_EPOCHS)

model3.evaluate(x_test_pad, y_test)

y_predicted = model3.predict(x_test_pad)

#get all predicted value
y_predicted_labels = [np.argmax(i) for i in y_predicted]

y_pred =   np.argmax(model3.predict(x_test_pad), axis  =  1)
y_true = np.argmax(y_test, axis = 1) 
from sklearn import metrics
print(metrics.classification_report(y_pred, y_true))

class_names = ['neutral', 'positive', 'very negative', 'negative']

print(metrics.classification_report(y_pred, y_true, target_names=class_names))

report = metrics.classification_report(y_pred, y_true, target_names=class_names)
with open('classification_report.txt', 'w') as f:
    print(report, file=f)

#import itertools

# #def plot_confusion_matrix(cm, classes,
#                           #normalize=False,
#                           #title='Confusion matrix',
#                           #cmap=plt.cm.Blues):
#   #  
#     #plt.imshow(cm, interpolation='nearest', cmap=cmap)
#     #plt.title(title)
#     #plt.colorbar()
#     #tick_marks = np.arange(len(classes))
#     #plt.xticks(tick_marks, classes, rotation=45)
#     #plt.yticks(tick_marks, classes)

#     #if normalize:
#         #cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
#         #print("Normalized confusion matrix")
#     #else:
#         #print('Confusion matrix, without normalization')

#     thresh = cm.max() / 2.
#     for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
#         plt.text(j, i, cm[i, j],
#                  horizontalalignment="center",
#                  color="white" if cm[i, j] > thresh else "black")

#     plt.tight_layout()
#     plt.ylabel('True label')
#     plt.xlabel('Predicted label')

#cm = confusion_matrix(y_true, y_predicted_labels)
cm = confusion_matrix(y_pred, y_true)

# Print confusion matrix
print("Confusion Matrix:")
print(cm)
#disp = ConfusionMatrixDisplay(confusion_matrix=cm)

# disp = ConfusionMatrixDisplay(confusion_matrix=cm)
# disp.plot ()

# from sklearn.metrics import classification_report
# print(classification)

model3.save('model3.h5')

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

cm = confusion_matrix(y_true, y_pred)

#disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['neutral', 'positive', 'very negative', 'negative'])

disp.plot()
plt.savefig('Confusion_matrix_GRU.png')

print(pd.DataFrame(y_pred).value_counts())

print(pd.DataFrame(y_true).value_counts())

