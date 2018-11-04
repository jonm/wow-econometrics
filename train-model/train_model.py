#!/usr/bin/env python

import datetime

import pytz
import tensorflow as tf
from tensorflow.keras import layers
from tf.python.lib.io import file_io

DATASET = 's3://wowecon-training-datasets/thrall/2018-08-28T19:46:19.153638+00:00.csv'

# item_id,year1,month1,day1,weekday1,hour1,minute1,second1,volume1,price1,year2,month2,day2,weekday2,hour2,minute2,second2,volume2,price2
# 3382,2018,8,8,2,0,54,1,40,7500,2018,8,8,2,1,53,0,40,7500

# N.B. CsvDataset only accepts certain DTypes (float32, float64, int32,
# int64, or string) that are valid for CSV files per RFC4180. See also:
# https://www.tensorflow.org/api_docs/python/tf/contrib/data/CsvDataset
CSV_RECORD_DEFAULTS = [ #tf.int64,   # item_id
                       tf.int32,   # year1
                       tf.int32,    # month1
                       tf.int32,    # day1
                       tf.int32,    # weekday1
                       tf.int32,    # hour1
                       tf.int32,    # minute1
                       tf.int32,    # second1
                       tf.int64,   # volume1
                       tf.int64,   # price1
                       tf.int32,   # year2
                       tf.int32,    # month2
                       tf.int32,    # day2
                       tf.int32,    # weekday2
                       tf.int32,    # hour2
                       tf.int32,    # minute2
                       tf.int32,    # second2
                       tf.int64,   # volume2
                       tf.int64]   # price2

def cast_to_more_accurate_types(#t0,
                                t1, t2, t3, t4, t5, t6, t7, t8, t9,
                                t10, t11, t12, t13, t14, t15, t16, t17, t18):
    """Cast to more accurate types, and combine the two outputs into
    a single tensor."""
    features = (#t0                     # item_id
        tf.cast(t1, dtype=tf.float32),  # year1
        tf.cast(t2, dtype=tf.float32),  # month1
        tf.cast(t3, dtype=tf.float32),  # day1
        tf.cast(t4, dtype=tf.float32),  # weekday1
        tf.cast(t5, dtype=tf.float32),  # hour1
        tf.cast(t6, dtype=tf.float32),  # minute1
        tf.cast(t7, dtype=tf.float32),  # second1
        tf.cast(t8, dtype=tf.float32),  # volume1
        tf.cast(t9, dtype=tf.float32),  # price1
        tf.cast(t10, dtype=tf.float32), # year2
        tf.cast(t11, dtype=tf.float32), # month2
        tf.cast(t12, dtype=tf.float32), # day2
        tf.cast(t13, dtype=tf.float32), # weekday2
        tf.cast(t14, dtype=tf.float32), # hour2
        tf.cast(t15, dtype=tf.float32), # minute2
        tf.cast(t16, dtype=tf.float32))                          # second2
    labels = (tf.cast(t17, dtype=tf.float32, name="volume2"),
              tf.cast(t18, dtype=tf.float32, name="price2"))
    return (tf.reshape(features, (16,)), tf.reshape(labels, (2,)))

def train_input_fn(path):
    raw_dataset = tf.contrib.data.CsvDataset([path], CSV_RECORD_DEFAULTS,
                                             header=True)
    typed_dataset = raw_dataset.map(cast_to_more_accurate_types)
    return typed_dataset

def create_model():
    model = tf.keras.Sequential()
    model.add(layers.Dense(16, activation='relu'))
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(2, activation='softmax', name='output'))
    model.compile(optimizer=tf.train.AdamOptimizer(0.01),
                  loss='mse', metrics=['mae'])
    return model
