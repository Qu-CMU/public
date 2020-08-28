import time
import pickle
import numpy as np
import pdb

## Sigmoid Function
def sigmoid(mat):
    return 1 / (1 + np.exp(-mat))

## Softmax Function (Vector)
def softmax(mat):
    exp = np.exp(mat)
    return exp / np.sum(exp)

## Softmax Function (matrix row-wise)
def softmax_all(mat):
    exp = np.exp(mat)
    return exp.T / np.sum(exp, 0)[0,:,None]

## Calculate loss
def calc_loss(y, yhat):
    return -np.sum(np.multiply(y, np.log(yhat)))

## Calculate Error
def calc_error(y, yhat):
    return np.count_nonzero(np.subtract(y, yhat)) / len(y)

## Convert integer to 1-hot vector
def convert_to_one_hot(y):
    vect = np.array(y.T)
    one_hot = np.zeros((vect.size, 12))
    one_hot[np.arange(vect.size), vect] = 1

    return one_hot

## Return index with the largest value
def convert_from_one_hot(y):
    return np.reshape(np.argmax(y, axis=0), (-1, 1))

## Load a model
def load_nn(filename):
    with open(filename, 'rb') as f:
        nn = pickle.load(f)

    return nn

##----------------------------------------------------------------------------------

## Simple Neural Network
## 1 input layer
## 1 hidden layer
## 1 output layer

class NeuralNet:
    def __init__(self, _input, hidden):
        self.A, self.B = self._init_weights(_input, hidden)

    ## Initialize weights randomly between -0.1 and 0.1
    def _init_weights(self, _input, numHidden):
        ## Randomize weight matricies
        alphaStar = (np.random.rand(numHidden, _input) / 5) - 0.1
        betaStar = (np.random.rand(12, numHidden) / 5) - 0.1

        ## Add column of 0's (bias term)
        alpha = np.concatenate((np.zeros((numHidden, 1)), alphaStar), 1)
        beta = np.concatenate((np.zeros((12, 1)), betaStar), 1)
            
        return alpha, beta          

    ## Predict Y given X.
    ## Function also returns a, z, b which are used to calculate gradients during back propagation
    def predict(self, _X):
        ## Add bias term
        X = np.insert(_X, 0, 1, axis=1)

        ## Calculate neural network output
        a = np.matmul(self.A,X.T)
        z = np.insert(sigmoid(a), 0, 1, axis=0)
        b = np.matmul(self.B,z)
        yhat = softmax(b)

        return a, z, b, yhat

    ## Calculate gradients via back propagation
    def back_prop(self, X, Y, a, z, b, yhat):
        dldb = yhat - Y.T
        gradB = np.matmul(dldb, z.T)
        dldz = np.matmul((self.B[:,1:]).T, dldb)
        dlda = np.multiply(np.multiply(dldz, z[1:]), (1-z[1:]))
        gradA = np.matmul(dlda, X)

        return gradA, gradB

    ## Train neural network
    ## Saves a copy of the model to 'temp.backup' after every epoch
    def train_network(self, _xtrain, _ytrain, xtest, ytest, epoch=15, lr=0.1, decay=True):
        ## Add bias term
        xtrain = np.insert(_xtrain, 0, 1, axis=1)
        xtrain = np.reshape(xtrain, (xtrain.shape[0], 1, -1))
        
        ## Encode labels as one-hot vectors
        ytrain = convert_to_one_hot(_ytrain)
        ytrain = np.reshape(ytrain, (ytrain.shape[0], 1, -1))
            
        startTime = time.time()
        
        for i in range(0, epoch):
            ## Crude implementation of learning rate decay
            if decay == True:
                if i >= 10:
                    lr = 0.001
                elif i >= 5:
                    lr = 0.01
                else:
                    lr = 0.1

            ## Batch size of 1
            for X, Y in zip(xtrain, ytrain):
                a    = np.matmul(self.A,X.T)
                z    = np.insert(sigmoid(a), 0, 1, axis=0)
                b    = np.matmul(self.B,z)
                yhat = softmax(b)
                
                gradA, gradB = self.back_prop(X, Y, a, z, b, yhat)

                self.A = self.A - (lr * gradA)
                self.B = self.B - (lr * gradB)
                
            ## Calculate some error metrics
            _, _, _, yhat = self.predict(_xtrain)
            yhat = convert_from_one_hot(yhat)
            trainError = calc_error(_ytrain, yhat)
            
            _, _, _, yhat = self.predict(xtest)
            yhat = convert_from_one_hot(yhat)
            testError = calc_error(ytest, yhat)

            ## Print metrics
            print('Epoch: ' + str(i))
            print('Time Elapsed: ' + str(time.time() - startTime))
            print('Train Error: ' + str(trainError))
            print('Test Error:  ' + str(testError))
            print(' ')

            self.save('train.backup')

    ## Calculate and print confusion matrix over test dataset
    def print_confusion_matrix(self, X, Y, verbose=False):
        predictionMatrix = np.zeros((12,12), 'uint8')
        
        ## Make Predictions
        _, _ , _, yhat = self.predict(X)
        pred = convert_from_one_hot(yhat)

        actual = list(Y.flat)
        pred   = list(pred.flat)

        ## Generate Matrix Counts
        for index, (a, p) in enumerate(zip(actual, pred)):
            predictionMatrix[a][p] += 1

            if a != p and verbose:
                print('Find {a} {p}'.format(a=a, p=p))
                print('{b:.3f} {d:.3f}'.format(b=yhat[a,index], d=yhat[p,index]))

        ## Pretty print confusion matrix
        for i in predictionMatrix:
            string = ''
            for j in i:
                string += '{0:0=3d}'.format(j) + ' '
            print(string)

    ## Save model
    def save(self, fileName):
        with open(fileName, 'wb') as f:
            pickle.dump(self, f)
