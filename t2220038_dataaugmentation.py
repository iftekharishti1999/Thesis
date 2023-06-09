# -*- coding: utf-8 -*-
"""T2220038_DataAugmentation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1trUFnZjD3o9gaP9o7cTuUZCMWdS6t3mJ
"""

import re
import string
import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from collections import Counter


import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
from nltk.corpus import stopwords

from sklearn.utils import shuffle
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report

d = pd.read_csv('/content/sample_data/Fewshot.csv')
print(d.shape)
d.head()

d['predicted'].value_counts()

d.isnull().sum()

d['posts'] = d['posts'].astype(str)
d.head()

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

data_clean = text_preprocessing(d, 'posts')

data_clean.to_csv('Preprocessed_multiclass.csv', index=False)

#check num of unique word
from collections import Counter
unique_words = Counter(" ".join(data_clean['posts'].values.tolist()).split(" ")).most_common(50)
results = pd.DataFrame(unique_words, columns=['Word', 'Frequency']) 
print(results)

data_clean.shape

data_clean.dropna(inplace=True)

data_clean.shape

data_clean.isna().sum()
data_clean.isnull().sum()

data_clean.drop_duplicates()

data_clean['posts'].describe()

data_clean['predicted'].dtypes

tf_without_balancing = TfidfVectorizer()
X_tf_wob = tf_without_balancing.fit_transform(data_clean['posts'])
X_tf_wob = X_tf_wob.toarray()

print(X_tf_wob.shape)
print(X_tf_wob)

data_clean

# converting string labels to int labels

label_map = {
    'positive': 1,
    'very negative': -2,
    'negative': -1,
    'neutral': 0
}

data_clean['intensity'] = data_clean['predicted'].map(label_map)
data_clean.head()

# splitting dataset
X_train_tf_wob, X_test_tf_wob, y_train_tf_wob, y_test_tf_wob = train_test_split(X_tf_wob, data_clean['intensity'].values, test_size=0.2)

# initializing model
naiveBayes_wob = GaussianNB()

naiveBayes_wob.fit(X_train_tf_wob, y_train_tf_wob)

y_pred_tf_wob = naiveBayes_wob.predict(X_test_tf_wob)

print(accuracy_score(y_test_tf_wob, y_pred_tf_wob))

print(classification_report(y_test_tf_wob, y_pred_tf_wob))

"""# Data Augmentation"""

!pip install transformers
!pip install nlpaug

import nlpaug.augmenter.word.context_word_embs as aug

"""# **Increasing 'Positive' sample**



"""

sample_text = data_clean['posts'].iloc[13]

sample_text

augmenter = aug.ContextualWordEmbsAug(model_path='bert-base-uncased', action="insert")

augmented_sample_text = augmenter.augment(sample_text)

augmented_sample_text

for i in range(5):
    print(augmenter.augment(sample_text))

data_clean['intensity'].value_counts()

def augmentMyData(df, augmenter, repetitions=1, samples=100):
    augmented_texts = []
    # select only the minority class samples
    spam_df = data_clean[data_clean['intensity'] == 1].reset_index(drop=True) # removes unecessary index column
    for i in tqdm(np.random.randint(0, len(spam_df), samples)):
        # generating 'n_samples' augmented texts
        for _ in range(repetitions):
            augmented_text = augmenter.augment(spam_df['posts'].iloc[i])
            augmented_texts.append(augmented_text)
    
    data = {
        'intensity': 1,
        'posts': augmented_texts
    }
    aug_df = pd.DataFrame(data)
    df = shuffle(data_clean.append(aug_df).reset_index(drop=True))
    return df

#new_df = data_clean.drop(labels=['length', 'length_after_cleaning'], axis=1)
data_clean.head()

"""# **Sample Increasing **"""

aug_df = augmentMyData(data_clean, augmenter, samples=400)

aug_df['intensity'].value_counts()

print("Original: ", data_clean.shape)
print("Augmented: ", aug_df.shape)

data_clean['intensity'].value_counts()

aug_df.to_csv('augmented_fewshot.csv', index=False)

"""# **Increasing "Very Positive" sample**"""

data_clean = pd.read_csv('')

sample_text = data_clean['Posts'].iloc[7756]

sample_text

augmenter = aug.ContextualWordEmbsAug(model_path='bert-base-uncased', action="insert")

augmented_sample_text = augmenter.augment(sample_text)

augmented_sample_text

for i in range(5):
    print(augmenter.augment(sample_text))

data_clean['intensity'].value_counts()

def augmentMyData(df, augmenter, repetitions=1, samples=200):
    augmented_texts = []
    # select only the minority class samples
    spam_df = data_clean[data_clean['intensity'] == 2].reset_index(drop=True) # removes unecessary index column
    for i in tqdm(np.random.randint(0, len(spam_df), samples)):
        # generating 'n_samples' augmented texts
        for _ in range(repetitions):
            augmented_text = augmenter.augment(spam_df['Posts'].iloc[i])
            augmented_texts.append(augmented_text)
    
    data = {
        'intensity': 2,
        'Posts': augmented_texts
    }
    aug_df = pd.DataFrame(data)
    df = shuffle(data_clean.append(aug_df).reset_index(drop=True))
    return df

data_clean.head()

aug_df = augmentMyData(data_clean, augmenter, samples=4300)

aug_df['intensity'].value_counts()

data_clean['intensity'].value_counts()

aug_df.to_csv('augmented_fewshot.csv', index=False)

"""# **Increasing "Positive" sample**"""

data_clean = pd.read_csv('')

sample_text = data_clean['Posts'].iloc[200]

sample_text

augmenter = aug.ContextualWordEmbsAug(model_path='bert-base-uncased', action="insert")

augmented_sample_text = augmenter.augment(sample_text)

augmented_sample_text

for i in range(5):
    print(augmenter.augment(sample_text))

data_clean['intensity'].value_counts()

def augmentMyData(df, augmenter, repetitions=1, samples=200):
    augmented_texts = []
    # select only the minority class samples
    spam_df = data_clean[data_clean['intensity'] == 2].reset_index(drop=True) # removes unecessary index column
    for i in tqdm(np.random.randint(0, len(spam_df), samples)):
        # generating 'n_samples' augmented texts
        for _ in range(repetitions):
            augmented_text = augmenter.augment(spam_df['Posts'].iloc[i])
            augmented_texts.append(augmented_text)
    
    data = {
        'intensity': 2,
        'Posts': augmented_texts
    }
    aug_df = pd.DataFrame(data)
    df = shuffle(data_clean.append(aug_df).reset_index(drop=True))
    return df

data_clean.head()

aug_df = augmentMyData(data_clean, augmenter, samples=3000)

aug_df['intensity'].value_counts()

print("Original: ", df.shape)
print("Augmented: ", aug_df.shape)

df['intensity'].value_counts()

aug_df.to_csv('augmented_fewshot.csv', index=False)

# split the dataset before augmenting to avoid augmented data in valid set
X_train, _, y_train, _ = train_test_split(aug_df['text'], aug_df['label'].values, test_size=0.1)
_, X_test, _, y_test = train_test_split(df['text'], df['label'].values, test_size=0.5)

tf_with_aug = TfidfVectorizer()
X_train_tf = tf_with_aug.fit_transform(X_train)
X_train_tf = X_train_tf.toarray()

nb = GaussianNB()
nb.fit(X_train_tf, y_train)

X_test_tf = tf_with_aug.transform(X_test)
X_test_tf = X_test_tf.toarray()

X_train_tf.shape, X_test_tf.shape

y_preds = nb.predict(X_test_tf)

print(confusion_matrix(y_test, y_preds))
print(accuracy_score(y_test, y_preds))
print(classification_report(y_test, y_preds))