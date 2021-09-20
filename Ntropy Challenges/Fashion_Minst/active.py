from tensorflow.keras import datasets, layers, models, losses, optimizers
from tensorflow.keras import backend as K
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import entropy
import random

## Load Dataset
(x_train, y_train), (x_test, y_test) = datasets.fashion_mnist.load_data()

## Format Data
x_train = x_train.reshape(-1, 28, 28, 1) / 255
x_test = x_test.reshape(-1, 28, 28, 1) / 255

## Split into Labeled and Unlabeled Data
x_labeled = x_train[:0]
y_labeled = y_train[:0]
x_unlabeled = x_train
y_unlabeled = y_train

## Label the first 'n' data points in 'x_unlabeled'
def label(n):
    global x_labeled, y_labeled, x_unlabeled, y_unlabeled
    x_labeled = np.concatenate([x_labeled, x_unlabeled[:n]])
    y_labeled = np.concatenate([y_labeled, y_unlabeled[:n]])
    x_unlabeled = x_unlabeled[n:]
    y_unlabeled = y_unlabeled[n:]

## Define Model
def create_model(lr=0.0004, beta1=0.75, beta2=0.95, dropout=0.4):
    model = models.Sequential()
    model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1), padding="same"))
    model.add(layers.Conv2D(64, (3, 3), activation='relu', padding="same"))
    model.add(layers.MaxPooling2D((2, 2), 2))
    model.add(layers.Dropout(dropout))
    
    model.add(layers.Conv2D(64, (3, 3), activation='relu', padding="same"))
    model.add(layers.Conv2D(128, (3, 3), activation='relu', padding="same"))
    model.add(layers.MaxPooling2D((2, 2), 2))
    model.add(layers.Dropout(dropout))
    
    model.add(layers.Flatten())
    model.add(layers.Dense(256, activation='relu'))
    model.add(layers.Dense(10))
    model.add(layers.Activation('softmax'))

    model.summary()
    
    adam = optimizers.Adam(lr, beta1, beta2)
    model.compile(optimizer=adam,
                  loss=losses.SparseCategoricalCrossentropy(),
                  metrics=['accuracy'])

    return model

## =============================================================================
## MAIN
## =============================================================================
        
if __name__ == "__main__":

    ## Create Model
    model = create_model()

    ## Shuffle Data
    p = np.random.permutation(len(x_unlabeled))
    x_unlabeled = x_unlabeled[p]
    y_unlabeled = y_unlabeled[p]

    ## Variables
    rounds = 300
    num_labels_each_round = 10
    
    ## Loop
    ## Label 'num_labels_each_round' samples each round based on sampling strategy
    ## Train 'model' on labeled dataset
    ## Use 'model' ro predict unlabeled data labels
    ## Sort the unlabeled data by decreasing prediction entropy
    ## Repeat (the label function will label the n data points with the highest entropy)
    for i in range(rounds):

        print()
        print("Round {}".format(i+1))
        print()

        label(num_labels_each_round)

        ## Train 'model'
        if (i % (rounds / 10)) == (rounds / 10) - 1:
            history = model.fit(x_labeled, y_labeled, epochs=10,
                                validation_data=(x_test, y_test))
        else:
            history = model.fit(x_labeled, y_labeled, epochs=10)

        ## Predict unlebeled data
        predictions = model.predict(x_unlabeled)

##        ## Least Confidence Sampling
##        pmax = np.amax(predictions, axis=1)

        ## Entropy Sampling (Uncertainty Sampling)
        pmax = np.apply_along_axis(entropy, 1, predictions)
        pidx = np.argsort(pmax)[::-1]

        ## Adversarial Sampling (Deepfool)
        ## Future Work

        ## Sort 'x_unlabeled' based on sampling
        x_unlabeled = x_unlabeled[pidx]
        y_unlabeled = y_unlabeled[pidx]

    ## Plot the sampling parameters.
    pmax = np.apply_along_axis(entropy, 1, predictions)
    pidx = np.argsort(pmax)[::-1]
    plt.plot(pmax[pidx])
    plt.show()

    ## Save Model
    model.save('model/active')




































    
