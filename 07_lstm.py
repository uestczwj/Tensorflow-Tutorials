#Inspired by https://github.com/aymericdamien/TensorFlow-Examples/blob/master/examples/3%20-%20Neural%20Networks/recurrent_network.py
import tensorflow as tf

import numpy as np
from tensorflow.examples.tutorials.mnist import input_data   #import input_data

# configuration
#                        O * W + b -> 10 labels for each image, O[? 28], W[28 10], B[10]
#                       ^ (O: output 28 vec from 28 vec input)
#                       |
#      +-+  +-+       +--+
#      |1|->|2|-> ... |28| time_step_size = 28
#      +-+  +-+       +--+
#       ^    ^    ...  ^
#       |    |         |
# img1:[28] [28]  ... [28]
# img2:[28] [28]  ... [28]
# img3:[28] [28]  ... [28]
# ...
# img128 or img256 (batch_size or test_size 256)
#      each input size = input_vec_size=lstm_size=28

# configuration variables
input_vec_size = 28
lstm_size      = 28
time_step_size = 28

batch_size = 128
test_size  = 256

def get_test_index(shape):
    test_indices = np.arange(len(shape))  # Get A Test Batch
    np.random.shuffle(test_indices)
    test_indices = test_indices[0:test_size]
    return test_indices

def init_weights(shape):
    return tf.Variable(tf.random_normal(shape, stddev=0.01))


def model(X, W, B, lstm_size):
    # X, input shape: (batch_size, time_step_size, input_vec_size)
    XT = tf.transpose(X, [1, 0, 2])  # permute time_step_size and batch_size
    # XT shape: (time_step_size, batch_size, input_vec_size)
    XR = tf.reshape(XT, [-1, lstm_size]) # each row has input for each lstm cell (lstm_size=input_vec_size)
    # XR shape: (time_step_size * batch_size, input_vec_size)
    X_split = tf.split(0, time_step_size, XR) # split them to time_step_size (28 arrays)
    # Each array shape: (batch_size, input_vec_size)

    # Make lstm with lstm_size (each input vector size)
    lstm = tf.nn.rnn_cell.BasicLSTMCell(lstm_size, forget_bias=1.0, state_is_tuple=True)

    # Get lstm cell output, time_step_size (28) arrays with lstm_size output: (batch_size, lstm_size)
    outputs, _states = tf.nn.rnn(lstm, X_split, dtype=tf.float32)

    # Linear activation
    # Get the last output
    return tf.matmul(outputs[-1], W) + B, lstm.state_size # State size to initialize the stat

mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
trX, trY, teX, teY = mnist.train.images, mnist.train.labels, mnist.test.images, mnist.test.labels
trX = trX.reshape(-1, 28, 28)
teX = teX.reshape(-1, 28, 28)

X = tf.placeholder("float", [None, 28, 28])
Y = tf.placeholder("float", [None, 10])

# get lstm_size and output 10 labelsd
W = init_weights([lstm_size, 10])
B = init_weights([10])

train_y, state_size = model(X, W, B, lstm_size)

cost     = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(train_y, Y))
train_op = tf.train.RMSPropOptimizer(0.001, 0.9).minimize(cost)

test_indices = get_test_index(teX)
test_check   = tf.equal(tf.argmax(train_y, 1), tf.argmax(teY[test_indices], 1))
test_op      = tf.reduce_mean(tf.cast(test_check, 'float'))

# Launch the graph in a session
with tf.Session() as sess:
    # you need to initialize all variables
    tf.global_variables_initializer().run()

    startRange = range(0, len(trX), batch_size)
    endRange   = range(batch_size, len(trX) + 1, batch_size)

    for i in range(100):
        for (start, end) in zip(startRange, endRange):
            sess.run(train_op, feed_dict={X: trX[start:end], Y: trY[start:end]})

        predict_result = sess.run(test_op, feed_dict={X: teX[test_indices], Y: teY[test_indices]})
        print(i, predict_result)
