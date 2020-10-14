import numpy as np
import gensim, logging
import csv, string
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
import pandas as pd
import tensorflow as tf
import os
from focal_loss import BinaryFocalLoss
import random

import tensorflow as tf
tf.executing_eagerly()
testing_arr = np.load("test_arr.npy")
print(testing_arr.shape)
testing_arr_labels = np.load("test_arr_labels.npy")
print(testing_arr_labels.shape)
training_arr = np.load("training_arr.npy")
print(testing_arr.shape)
training_arr_labels = np.load("training_arr_labels.npy")
print(testing_arr_labels.shape)
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        # Currently, memory growth needs to be the same across GPUs
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
    except RuntimeError as e:
        # Memory growth must be set before GPUs have been initialized
        print(e)

labels_parsed_dataset = np.load("parsed_labels.npy", allow_pickle=True)
all_labels = {"A01B","A01C","A01D","A01F","A01G","A01H","A01J","A01K","A01L","A01M","A01N","A21B","A21C","A21D","A22B","A22C","A23B","A23C","A23D","A23F","A23G","A23J","A23K","A23L","A23N","A23P","A23V","A23Y","A24B","A24C","A24D","A24F","A41B","A41C","A41D","A41F","A41G","A41H","A42B","A42C","A43B","A43C","A43D","A44B","A44C","A44D","A45B","A45C","A45D","A45F","A46B","A46D","A47B","A47C","A47D","A47F","A47G","A47H","A47J","A47K","A47L","A61B","A61C","A61D","A61F","A61G","A61H","A61J","A61K","A61L","A61M","A61N","A61P","A61Q","A62B","A62C","A62D","A63B","A63C","A63D","A63F","A63G","A63H","A63J","A63K","A99Z","B01B","B01D","B01F","B01J","B01L","B02B","B02C","B03B","B03C","B03D","B04B","B04C","B05B","B05C","B05D","B06B","B07B","B07C","B08B","B09B","B09C","B21B","B21C","B21D","B21F","B21G","B21H","B21J","B21K","B21L","B22C","B22D","B22F","B23B","B23C","B23D","B23F","B23G","B23H","B23K","B23P","B23Q","B24B","B24C","B24D","B25B","B25C","B25D","B25F","B25G","B25H","B25J","B26B","B26D","B26F","B27B","B27C","B27D","B27F","B27G","B27H","B27J","B27K","B27L","B27M","B27N","B28B","B28C","B28D","B29B","B29C","B29D","B29K","B29L","B30B","B31B","B31C","B31D","B31F","B32B","B33Y","B41B","B41C","B41D","B41F","B41G","B41J","B41K","B41L","B41M","B41N","B41P","B42B","B42C","B42D","B42F","B42P","B43K","B43L","B43M","B44B","B44C","B44D","B44F","B60B","B60C","B60D","B60F","B60G","B60H","B60J","B60K","B60L","B60M","B60N","B60P","B60Q","B60R","B60S","B60T","B60V","B60W","B60Y","B61B","B61C","B61D","B61F","B61G","B61H","B61J","B61K","B61L","B62B","B62C","B62D","B62H","B62J","B62K","B62L","B62M","B63B","B63C","B63G","B63H","B63J","B64B","B64C","B64D","B64F","B64G","B65B","B65C","B65D","B65F","B65G","B65H","B66B","B66C","B66D","B66F","B67B","B67C","B67D","B68B","B68C","B68F","B68G","B81B","B81C","B82B","B82Y","B99Z","C01B","C01C","C01D","C01F","C01G","C01P","C02F","C03B","C03C","C04B","C05B","C05C","C05D","C05F","C05G","C06B","C06C","C06D","C06F","C07B","C07C","C07D","C07F","C07G","C07H","C07J","C07K","C08B","C08C","C08F","C08G","C08H","C08J","C08K","C08L","C09B","C09C","C09D","C09F","C09G","C09H","C09J","C09K","C10B","C10C","C10F","C10G","C10H","C10J","C10K","C10L","C10M","C10N","C11B","C11C","C11D","C12C","C12F","C12G","C12H","C12J","C12L","C12M","C12N","C12P","C12Q","C12R","C12Y","C13B","C13K","C14B","C14C","C21B","C21C","C21D","C22B","C22C","C22F","C23C","C23D","C23F","C23G","C25B","C25C","C25D","C25F","C30B","C40B","C99Z","D01B","D01C","D01D","D01F","D01G","D01H","D02G","D02H","D02J","D03C","D03D","D03J","D04B","D04C","D04D","D04G","D04H","D05B","D05C","D05D","D06B","D06C","D06F","D06G","D06H","D06J","D06L","D06M","D06N","D06P","D06Q","D07B","D10B","D21B","D21C","D21D","D21F","D21G","D21H","D21J","D99Z","E01B","E01C","E01D","E01F","E01H","E02B","E02C","E02D","E02F","E03B","E03C","E03D","E03F","E04B","E04C","E04D","E04F","E04G","E04H","E05B","E05C","E05D","E05F","E05G","E05Y","E06B","E06C","E21B","E21C","E21D","E21F","E99Z","F01B","F01C","F01D","F01K","F01L","F01M","F01N","F01P","F02B","F02C","F02D","F02F","F02G","F02K","F02M","F02N","F02P","F03B","F03C","F03D","F03G","F03H","F04B","F04C","F04D","F04F","F05B","F05C","F05D","F15B","F15C","F15D","F16B","F16C","F16D","F16F","F16G","F16H","F16J","F16K","F16L","F16M","F16N","F16P","F16S","F16T","F17B","F17C","F17D","F21H","F21K","F21L","F21S","F21V","F21W","F21Y","F22B","F22D","F22G","F23B","F23C","F23D","F23G","F23H","F23J","F23K","F23L","F23M","F23N","F23Q","F23R","F24B","F24C","F24D","F24F","F24H","F24S","F24T","F24V","F25B","F25C","F25D","F25J","F26B","F27B","F27D","F27M","F28B","F28C","F28D","F28F","F28G","F41A","F41B","F41C","F41F","F41G","F41H","F41J","F42B","F42C","F42D","F99Z","G01B","G01C","G01D","G01F","G01G","G01H","G01J","G01K","G01L","G01M","G01N","G01P","G01Q","G01R","G01S","G01T","G01V","G01W","G02B","G02C","G02F","G03B","G03C","G03D","G03F","G03G","G03H","G04B","G04C","G04D","G04F","G04G","G04R","G05B","G05D","G05F","G05G","G06C","G06D","G06E","G06F","G06G","G06J","G06K","G06M","G06N","G06Q","G06T","G07B","G07C","G07D","G07F","G07G","G08B","G08C","G08G","G09B","G09C","G09D","G09F","G09G","G10B","G10C","G10D","G10F","G10G","G10H","G10K","G10L","G11B","G11C","G12B","G16B","G16C","G16H","G16Z","G21B","G21C","G21D","G21F","G21G","G21H","G21J","G21K","G99Z","H01B","H01C","H01F","H01G","H01H","H01J","H01K","H01L","H01M","H01P","H01Q","H01R","H01S","H01T","H02B","H02G","H02H","H02J","H02K","H02M","H02N","H02P","H02S","H03B","H03C","H03D","H03F","H03G","H03H","H03J","H03K","H03L","H03M","H04B","H04H","H04J","H04K","H04L","H04M","H04N","H04Q","H04R","H04S","H04T","H04W","H05B","H05C","H05F","H05G","H05H","H05K","H99Z","Y02A","Y02B","Y02C","Y02D","Y02E","Y02P","Y02T","Y02W","Y04S","Y10S","Y10T"}
def convert_labels(first_half):
    return tuple([ord(first_half[0])-65, int(first_half[1:3]), ord(first_half[3])-65])
all_labels = [convert_labels(i) for i in all_labels]
def convert_label_to_vector(label):
    first_half, second_half = label.split(" ")
    return tuple([ord(first_half[0])-65, int(first_half[1:3]), ord(first_half[3])-65])
#label_dict = {k: [] for k in all_labels}
#for label, vector in zip(training_arr_labels, training_arr):
#    label_vectors = [convert_label_to_vector(z.strip().strip('\'\"')) for z in label[0].split(',')]
#    for l in label_vectors:
#        if l not in all_labels:
#            continue
#        label_dict[tuple(l)].append(vector)
#label_dict = {k: np.mean(np.vstack(label_dict[k]), axis=0) for k in label_dict.keys() if label_dict[k] != []}
import pickle
with open("binary_label_dict.pickle", 'rb') as f:
    label_dict = pickle.load(f)
#with open("binary_label_dict.pickle", 'wb') as f:
#   pickle.dump(label_dict, f)
label_dict_keys = set(label_dict.keys())

occurences = {k: 0 for k in label_dict.keys()}

def random_data_generator():
    indices = np.argsort(np.random.choice(317974, 10000))
    #indices = indices[:(len(indices)//4)*3]
    n = 0
    for label, vector in zip(training_arr_labels[indices], training_arr[indices]):
        n = n+1
        label_vectors = [convert_label_to_vector(z.strip().strip('\'\"')) for z in label[0].split(',')]
        label_vectors = set([i for i in label_vectors if i in label_dict_keys])
        #non_true_vectors = [i for i in random.sample(label_dict_keys, 4*len(label_vectors)) if i not in label_vectors]
        non_true_vectors = [i for i in random.sample(label_dict_keys, 4*len(label_vectors)) if i not in label_vectors]
        for i in label_vectors:
            occurences[i] = occurences[i]+1
        for l in [label_dict[i] for i in label_vectors]:
            yield ({'input_1':vector, 'input_2':l}, [1])
        for l in [label_dict[i] for i in non_true_vectors]:
            yield ({'input_1':vector, 'input_2':l}, [0])
random_dataset = tf.data.Dataset.from_generator(random_data_generator, ({'input_1':tf.float32, 'input_2':tf.float32}, tf.float32), ({'input_1':tf.TensorShape([1000]), 'input_2':tf.TensorShape([1000])}, tf.TensorShape([1]))).repeat()
random_dataset = random_dataset.batch(256, drop_remainder=True).prefetch(1000)
def data_generator_test():
    n = 0
    for label, vector in zip(testing_arr_labels, testing_arr):
        label_vectors = [convert_label_to_vector(z.strip().strip('\'\"')) for z in label[0].split(',')]
        label_vectors = set([i for i in label_vectors if i in label_dict_keys])
        non_true_vectors = [i for i in label_dict_keys if i not in label_vectors]
        for l in [label_dict[i] for i in label_vectors]:
            yield ({'input_1':vector, 'input_2':l}, [1])
        for l in [label_dict[i] for i in non_true_vectors]:
            yield ({'input_1':vector, 'input_2':l}, [0])


wv = gensim.models.KeyedVectors.load("patents.wv", mmap='r')
porter = PorterStemmer()
ret = []
ret_labels = []
placeholder_vec = [0 for _ in range(1000)]

def get_sentence_vector(sentence):
    for word in sentence:
        try:
            ret.append(wv[porter.stem(word)])
        except:
            pass
    return np.mean(np.vstack(ret), axis=0)
def new_data_generator():
    #last_state = np.load("state.npy")[0]
    for row in pd.read_csv('../dataset.csv',sep=',', header = None, chunksize=1):
        label, description=row[0].values[0], row[1].values[0]
        lstm_input_patent = get_sentence_vector(word_tokenize(description.lower()))
        label_vectors = [convert_label_to_vector(z.strip().strip('\'\"')) for z in label.split(',')]
        label_vectors = set([i for i in label_vectors if i in label_dict_keys])
        non_true_vectors = [label_dict[i] for i in random.sample(label_dict_keys, len(label_vectors)) if i not in label_vectors]
        for l in (label_dict[i] for i in label_vectors):
            yield ({'input_1':lstm_input_patent, 'input_2':l}, [1])
        for l in non_true_vectors:
            yield ({'input_1':lstm_input_patent, 'input_2':l}, [0])

test_dataset = tf.data.Dataset.from_generator(data_generator_test, ({'input_1':tf.float64, 'input_2':tf.float64}, tf.float64), ({'input_1':tf.TensorShape([1000]), 'input_2':tf.TensorShape([1000])}, tf.TensorShape([1]))).repeat()
test_dataset = test_dataset.batch(32, drop_remainder=True).prefetch(1000).repeat()
print(test_dataset)

new_dataset = tf.data.Dataset.from_generator(new_data_generator, ({'input_1':tf.float64, 'input_2':tf.float32}, tf.float64), ({'input_1':tf.TensorShape([1000]), 'input_2':tf.TensorShape([1000])}, tf.TensorShape([1]))).repeat().batch(128, drop_remainder=True).repeat()
def string_to_label(s):
    s = tf.strings.split(s, sep=" ")[0]
    arr = [i for i in tf.strings.unicode_decode(s, input_encoding="UTF-8").numpy() if i not in [34, 39]]
    return np.array([arr[0]-65, (arr[1]-48)*10+(arr[2]-48), arr[3]-65])

def transform_label(label, vector):
    vector = tf.convert_to_tensor(vector)
    vector.set_shape([1000])
    label_vectors = map(string_to_label, tf.strings.strip(tf.strings.split(label, sep=',')).values)
    label_vectors = set([tuple(i) for i in label_vectors if tuple(i) in label_dict_keys])
    non_true_vectors = [i for i in random.sample(label_dict_keys, len(label_vectors)) if tuple(i) not in label_vectors]
    lens = len(label_vectors)+len(non_true_vectors)
    x = [vector]*lens
    y = [tf.convert_to_tensor(label_dict[tuple(i)]) for i in label_vectors]+[tf.convert_to_tensor(label_dict[tuple(i)]) for i in non_true_vectors]
    z = [tf.convert_to_tensor([1])]*len(label_vectors)+[tf.convert_to_tensor([0])]*len(non_true_vectors)
    return x, y, z
@tf.function
def label_to_dataset(label, vector):
    x, y, z = tf.py_function(func=transform_label, inp=[label, vector], Tout=(tf.float64, tf.float64, tf.float64))
    x.set_shape((None, 1000))
    y.set_shape((None, 1000))
    z.set_shape((None, 1))
    out = tf.data.Dataset.from_tensor_slices(({'input_1':x, 'input_2':y}, z))
    return out

#ds = tf.data.Dataset.from_tensor_slices((training_arr_labels, training_arr))
#print(ds.take(1))
#label = tf.placeholder(tf.string)
#vector = tf.placeholder(tf.float64)
#map_function = tf.py_function(func=transform_label, inp=[label, vector], Tout=(tf.float64, tf.float64, tf.float64))
#ds = ds.map(lambda label, vector: transform_label)
#ds = ds.flat_map(lambda x, y, z: tf.data.Dataset.from_tensor_slices(({'input_1':x, 'input_2':y}, z)))
#ds = ds.batch(256).prefetch(1000)
#ds = ds.interleave(label_to_dataset, cycle_length=4, block_length=16, num_parallel_calls=tf.data.experimental.AUTOTUNE).prefetch(tf.data.experimental.AUTOTUNE).batch(2)
input_patent = tf.keras.Input(shape=(1000), name='input_1')
input_label = tf.keras.Input(shape=(1000), name='input_2')
dense_patent_1 = tf.keras.layers.Dense(1000, activation='relu')(input_patent)
dense_label_1 =  tf.keras.layers.Dense(1000, activation='relu')(input_label)
dense_patent_2 = tf.keras.layers.Dense(1000, activation='relu')(dense_patent_1)
dense_label_2 =  tf.keras.layers.Dense(1000, activation='relu')(dense_label_1)
dense_patent_3 = tf.keras.layers.Dropout(.1)(dense_patent_2)
dense_label_3=  tf.keras.layers.Dropout(.1)(dense_label_2)
concat = tf.keras.layers.Concatenate(axis=1)([dense_patent_3, dense_label_3])
dense_1 = tf.keras.layers.Dense(1800, activation='relu')(concat)
output_binary = tf.keras.layers.Dense(1, activation="sigmoid", name='output_1')(dense_1)

model = tf.keras.Model(inputs={'input_1':input_patent, 'input_2':input_label}, outputs=output_binary)
try:
    pass
    model.load_weights('./binarycheckpoint4.h5')
except:
    print('couldnt load')
    pass
#saver = tf.train.Saver(max_to_keep=4, keep_checkpoint_every_n_hours=2)


model.compile(loss='logcosh',
              optimizer='adam',
              metrics=['accuracy', tf.keras.metrics.Precision(),tf.keras.metrics.Recall()])

import datetime
class MyCustomCallback(tf.keras.callbacks.Callback):
    def __init__(self, test_data):
        self.test_data = test_data

    def on_epoch_end(self, epoch, logs=None):
        print('saving occurences')
        loss, accuracy, precision, recall = self.model.evaluate(self.test_data, verbose=1, steps=9314)
        f1score = 2*(precision*recall)/(precision+recall)
        print("F1 Score: "+str(f1score))
        print("Accuracy: "+str(accuracy))
        with open("occurences.pickle", 'wb') as f:
            pickle.dump(occurences, f)
my_callback = MyCustomCallback(test_dataset)
cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath='./binarycheckpoint4.h5',
                                                 save_weights_only=False,
                                                 verbose=1)
log_dir="logs\\fit\\" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)


history = model.fit(random_dataset, epochs=50, steps_per_epoch=10000, callbacks=[cp_callback, my_callback, tensorboard_callback])

