# Praetorian Challenge: Machine Learning

### Requirements
* Python Version: 3.6.8

This code is for the [Praetorian Machine Learning Challenge](https://www.praetorian.com/challenges/machine-learning).

### File Summaries
* __MachineLearning.py__ is the main script that will load a pre-trained neural network and complete the challenge.
* __NeuralNetwork.py__ contains the NeuralNet class, which is a simple 3-layer fully-connected neural network build from scratch.
* __Trained_NN.pickle__ is a pre-trained NeuralNet object.
* __unformatted_training_data.npy__ contains 24,000 training samples.
* __unformatted_test_data.npy__ containes 2,000 test samples.

### How To Use
1. Change the email set in __MachineLearning.py__.
2. Run __MachineLearning.py__.

### Model
The pre-trained model has 3 fully connected layers. It was trained using the default function argument values. 
Why did I program a NN from scratch? Because I can.

##### Input Layer
The input layer has 768 nodes. These correspond to the 512 bits of the binary and a 256 multi-hot encoding of the byte values of the binary.

##### Hidden Layer
The hidden layer has 384 nodes.

##### Output Layer
The output layer has 12 nodes (one for each class) and applies a softmax function.

### Training
The update function used is stochastic gradient descent computed via back propagation with a batch size of 1. There is also a very simple implementation of learning rate decay that reduces the learning rate every 5 epochs.

