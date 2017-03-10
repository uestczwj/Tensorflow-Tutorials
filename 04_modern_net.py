#!/usr/bin/env python

import tensorflow as tf
import numpy as np
from tensorflow.examples.tutorials.mnist import input_data   #import input_data

batch_size = 128

def init_weights(shape):
    return tf.Variable(tf.random_normal(shape, stddev=0.01))


def model(X, w_h, w_h2, w_o, p_keep_input, p_keep_hidden): # this network is the same as the previous one except with an extra hidden layer + dropout
    X = tf.nn.dropout(X, p_keep_input)
    h = tf.nn.relu(tf.matmul(X, w_h))

    h = tf.nn.dropout(h, p_keep_hidden)
    h2 = tf.nn.relu(tf.matmul(h, w_h2))

    h2 = tf.nn.dropout(h2, p_keep_hidden)

    return tf.matmul(h2, w_o)


mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
trX, trY, teX, teY = mnist.train.images, mnist.train.labels, mnist.test.images, mnist.test.labels

X = tf.placeholder("float", [None, 784])
Y = tf.placeholder("float", [None, 10])

w_h  = init_weights([784, 625])
w_h2 = init_weights([625, 625])
w_o  = init_weights([625, 10])

p_keep_input = tf.placeholder("float")
p_keep_hidden = tf.placeholder("float")

train_y = model(X, w_h, w_h2, w_o, p_keep_input, p_keep_hidden)
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(train_y, Y))
train_op = tf.train.RMSPropOptimizer(0.001, 0.9).minimize(cost)

test_y      = model(X, w_h, w_h2, w_o, p_keep_input, p_keep_hidden)
test_check  = tf.equal(tf.argmax(test_y, 1), tf.argmax(teY, 1))
test_op     = tf.reduce_mean(tf.cast(test_check, 'float'))

# Launch the graph in a session
with tf.Session() as sess:
    # you need to initialize all variables
    tf.global_variables_initializer().run()

    startRange = range(0, len(trX), batch_size)
    endRange   = range(batch_size, len(trX) + 1, batch_size)

    for i in range(100):
        for (start, end) in zip(startRange, endRange):
            sess.run(train_op, feed_dict={X: trX[start:end], Y: trY[start:end], p_keep_input: 0.8, p_keep_hidden: 0.5})

        test_result = sess.run(test_op, feed_dict={X: teX, Y: teY, p_keep_input: 1.0, p_keep_hidden: 1.0})
        print(i, test_result)
