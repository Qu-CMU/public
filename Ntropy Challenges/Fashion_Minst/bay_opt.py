from tensorflow.keras import datasets, layers, models, losses, optimizers
from skopt import gp_minimize
from skopt.plots import plot_convergence
from skopt.space.space import Real
from skopt.utils import use_named_args
from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras import backend as K
import matplotlib.pyplot as plt

## Load Dataset
## (x_train, y_train), (x_test, y_test) = datasets.mnist.load_data()
(x_train, y_train), (x_test, y_test) = datasets.fashion_mnist.load_data()

train_data = x_train.reshape(-1, 28, 28, 1) / 255
train_labels = y_train
test_data = x_test.reshape(-1, 28, 28, 1) / 255
test_labels = y_test

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

    adam = optimizers.Adam(lr, beta1, beta2)
    model.compile(optimizer=adam,
                  loss=losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    return model
        
if __name__ == "__main__":
    dim_lr = Real(low=1e-4, high=5e-3, prior='log-uniform', name='lr')
    dim_b1 = Real(low=0.7, high=0.99, name='beta1')
    dim_b2 = Real(low=0.9, high=0.999, name='beta2')
    dim_drop = Real(low=0.25, high=0.75, name='dropout')
    dimensions = [dim_lr, dim_b1, dim_b2, dim_drop]
    default_param = [0.0005, 0.75, 0.95, 0.4]
    best_accuracy = 0

    @use_named_args(dimensions=dimensions)
    def fitness(lr, beta1, beta2, dropout):
        model = create_model(lr, beta1, beta2, dropout)

        history = model.fit(train_data, train_labels, epochs=5, 
                            validation_data=(test_data, test_labels))

        accuracy = history.history['val_accuracy'][-1]

        print()
        print("Accuracy: {0:.2%}".format(accuracy))
        print()

        global best_accuracy

        if accuracy > best_accuracy:
            model.save("best_model.tf")
            best_accuracy = accuracy

        del model
        K.clear_session()

        return -accuracy
    
    search_result = gp_minimize(func=fitness,
                                dimensions=dimensions,
                                acq_func='EI',
                                n_calls=32,
                                x0=default_param)

    plot_convergence(search_result)

    print(search_result.x)
    
    









































    
