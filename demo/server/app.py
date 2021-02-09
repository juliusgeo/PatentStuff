from flask import Flask, request, jsonify
app = Flask(__name__)
#############
#SETUP MODEL#
#############
import numpy as np
import gensim, logging
import csv, string
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
import pandas as pd
import tensorflow as tf
import os
import pickle

num_words_abstract = 200
num_words_claims = 500
num_words_label_description = num_words_abstract+num_words_claims
directory_prefix = "../../"
label_depth = 3
import random
#import gensim.downloader as api
from nltk.corpus import stopwords
from gensim.parsing.preprocessing import remove_stopwords


import tensorflow_hub as hub

embed = hub.load("https://tfhub.dev/google/tf2-preview/nnlm-en-dim128-with-normalization/1")
#embed = hub.load("https://tfhub.dev/google/Wiki-words-500/2")

embeddings = embed(["cat is on the mat", "dog is in the fog"])
embedding_dim = embeddings.shape[1]
#print(embeddings)
def get_sentence_vector(words, num_words):
    words = word_tokenize(remove_stopwords(words))
    #words = list(filter(lambda w: len(w)>2, words))
    ret = embed(words)
    ret = tf.pad(ret, tf.constant([[0, max(0, num_words-ret.shape[0]),], [0, 0]]), "CONSTANT")
    ret = ret[:num_words]
    return ret
 
with open(directory_prefix+"/class_descriptions/class_descriptions_from_patents.pickle", 'rb') as f:
    label_dict = pickle.load(f)
label_dict = {k[:label_depth]: get_sentence_vector(val.lower(), num_words_label_description) for k, val in label_dict.items()}
#label_dict = {k[:label_depth]: get_sentence_vector(val.lower(), num_words_description) for k, val in label_dict.items()}

label_dict_keys = set(label_dict.keys())
description_shape = tf.TensorShape([num_words_abstract, embedding_dim])
claims_shape = tf.TensorShape([num_words_claims, embedding_dim])
label_shape = tf.TensorShape([num_words_label_description, embedding_dim])




input_abstract = tf.keras.Input(shape=(num_words_abstract, embedding_dim), name='input_abstract')
input_claims = tf.keras.Input(shape=(num_words_claims, embedding_dim), name='input_claims')
input_label = tf.keras.Input(shape=(num_words_label_description, embedding_dim), name='input_label')

abstract_mask = tf.keras.layers.Masking(mask_value=0., input_shape=(num_words_abstract, embedding_dim))(input_abstract)
claims_mask = tf.keras.layers.Masking(mask_value=0., input_shape=(num_words_claims, embedding_dim))(input_claims)
label_mask = tf.keras.layers.Masking(mask_value=0., input_shape=(num_words_label_description, embedding_dim))(input_label)

layer_size = embedding_dim*4
abstract = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(embedding_dim, return_sequences=True))(abstract_mask)
claims = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(embedding_dim, return_sequences=True))(claims_mask)
label = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(embedding_dim, return_sequences=True))(label_mask)

#


abstract = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(layer_size))(abstract)
abstract = tf.keras.layers.GlobalAveragePooling1D()(abstract)

claims = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(layer_size))(claims)
claims = tf.keras.layers.GlobalAveragePooling1D()(claims)

label = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(layer_size))(label)
label = tf.keras.layers.GlobalAveragePooling1D()(label)
#patent = tf.keras.layers.Dense(layer_size//2)(patent)
#label =  tf.keras.layers.Dense(layer_size//2)(label)

#subtract = tf.keras.layers.Subtract()([patent, label])
#multiply = tf.keras.layers.Multiply()([patent, label])

concat = tf.keras.layers.Concatenate(axis=1)([abstract, claims, label])
dense = tf.keras.layers.Dense(int(layer_size)*2)(concat)
dense = tf.keras.layers.Dense(int(layer_size)*2)(dense)
dense = tf.keras.layers.Dense(int(layer_size)*2, activation='relu')(dense)
dense = tf.keras.layers.Dense(int(layer_size)*2, activation='relu')(dense)
dense = tf.keras.layers.Dense(int(layer_size)*2, activation='relu')(dense)

output_binary = tf.keras.layers.Dense(1, name='output_binary')(dense)


#lstm_enforce_1 = tf.keras.layers.Dense(200, activation='relu')(patent_lstm)
#lstm_enforce_2 = tf.keras.layers.Dense(1000, name='output_2')(lstm_enforce_1)
#model = tf.keras.Model(inputs={'input_1':input_lstm, 'input_2':input_label}, outputs={'output_1':output_binary, 'output_2':lstm_enforce_2})
model = tf.keras.Model(inputs={'input_abstract':input_abstract, 'input_claims':input_claims,  'input_label':input_label}, outputs=[output_binary])
print(model)

#saver = tf.train.Saver(max_to_keep=4, keep_checkpoint_every_n_hours=2)
#del model

model.load_weights(directory_prefix+"checkpoints/LSTMWithoutAttention-V1NewDataset.h5")


model.summary()
opt = tf.optimizers.Adam(1e-5)
model.compile(loss=['binary_crossentropy'],
              optimizer=opt,
              metrics=['accuracy'], experimental_run_tf_function=False)


# Create a callback that saves the model's weights
cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=directory_prefix+"checkpoints/LSTMWithoutAttention-V1NewDataset.h5",
                                                 save_weights_only=False,
                                                 verbose=1)

class CustomCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        generate_prc()
prc_callback = CustomCallback()


@app.route('/getprediction', methods=["POST"])
def hello_world():
	print(request.json())
	label_len = len(label_dict_keys)
    #print(label_len)
    left = [label_dict[i] for i in label_dict_keys]
    predictions = []
    left_vectors = np.array(list(label_dict_keys))


    lstm_input_patent = get_sentence_vector(abstract.lower(), num_words_abstract)
    lstm_input_claims = get_sentence_vector(claims.lower(), num_words_claims)
    for i in left:
        yield ({'input_abstract':lstm_input_patent, 'input_claims':lstm_input_claims, 'input_label':i})



    for prediction, label_vectors in zip(predictions, label_vectors_vector):
        indices = np.flip(np.argsort(prediction, axis=0))
        #print(indices)
        e = [1 if i in label_vectors else 0 for i in left_vectors[indices]]
    return 'Hello, World!'