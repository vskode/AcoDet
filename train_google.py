#%%
import pandas as pd
import numpy as np
from pathlib import Path
import os

from utils.funcs import *
from utils.tfrecord_funcs import *
from utils.google_funcs import GoogleMod

params = {
    "sr" : 10000,
    "cntxt_wn_hop": 39124,
    "cntxt_wn_sz": 39124,
    "fft_window_length" : 2**11,
    "n_freq_bins": 2**8,
    "freq_cmpr": 'linear',
    "fmin":  50,
    "fmax":  1000,
    "nr_noise_samples": 100,
    "sequence_len" : 39124,
    "fft_hop": 300,
}

TFRECORDS_DIR = 'Daten/tfrecords'


def prepare_sample(features):
    return features["audio"], features["label"]

def get_dataset(filenames, batch_size):
    dataset = (
        tf.data.TFRecordDataset(filenames, num_parallel_reads=AUTOTUNE)
        .map(parse_tfrecord_fn, num_parallel_calls=AUTOTUNE)
        .map(prepare_sample, num_parallel_calls=AUTOTUNE)
        # .shuffle(batch_size)
        # .batch(batch_size)
    )
    return dataset

#%% init

filenames = tf.io.gfile.glob(f"{TFRECORDS_DIR}*/*.tfrec")
filenames_trial_run = filenames
unfreeze = 3
batch_size = 30
epochs = 100
steps_per_epoch = 20
AUTOTUNE = tf.data.AUTOTUNE



data = get_dataset(filenames_trial_run, batch_size)
num_arrays = len(list(data))

data = data.shuffle(num_arrays)
train_data = data.take(int (num_arrays * 0.7) )
test_data = data.skip(int (num_arrays * 0.7) )
val_data = test_data.skip(int (num_arrays * 0.15) )
test_data = test_data.take(int (num_arrays * 0.15) )

# train_data = train_data.shuffle(int (num_arrays * 0.7) )
train_data = train_data.batch(batch_size)
train_data = train_data.prefetch(AUTOTUNE)

test_data = test_data.batch(batch_size)
test_data = test_data.prefetch(AUTOTUNE)
# train_data = train_data.shuffle(int (num_arrays * 0.7))

#%% freeze layers
G = GoogleMod(params)
model = G.model
for layer in model.layers[:-unfreeze]:
    layer.trainable = False


#%% define training


# Include the epoch in the file name (uses `str.format`)
checkpoint_path = f"unfreeze_{unfreeze}_" + "test1/cp-{epoch:04d}.ckpt"
checkpoint_dir = os.path.dirname(checkpoint_path)


# Create a callback that saves the model's weights every 5 epochs
cp_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_path, 
    verbose=1, 
    save_weights_only=True,
    save_freq=steps_per_epoch*epochs//2)

# Save the weights using the `checkpoint_path` format
model.save_weights(checkpoint_path.format(epoch=0))

# Train the model with the new callback
model.fit(train_data, 
          epochs = epochs, 
          steps_per_epoch=steps_per_epoch, 
          validation_data = test_data,
          callbacks=[cp_callback],
          )

#%% Evaluate the model


# Create a new model instance
# model = GoogleMod(params).model


# data = get_dataset(filenames, batch_size)

# dset = tf.data.TFRecordDataset(f"{TFRECORDS_DIR}/file_01.tfrec").map(parse_tfrecord_fn)
# ll = list()
# for features in dset:
#     ll.append(list(features["audio"].numpy()))
# e = model.predict(np.array(ll, dtype='float32'))


# model.evaluate(data, batch_size = batch_size, verbose =2)
# model.predict(x = get_dataset(filenames, batch_size))