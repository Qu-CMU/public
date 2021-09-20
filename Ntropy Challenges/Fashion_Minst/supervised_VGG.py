from tensorflow.keras import datasets, layers, models, losses, optimizers
import matplotlib.pyplot as plt

## Load Dataset
##(x_train, y_train), (x_test, y_test) = datasets.mnist.load_data()
(x_train, y_train), (x_test, y_test) = datasets.fashion_mnist.load_data()

train_data = x_train.reshape(-1, 28, 28, 1) / 255
train_labels = y_train
test_data = x_test.reshape(-1, 28, 28, 1) / 255
test_labels = y_test

if __name__ == "__main__":
    model = models.Sequential()
    model.add(layers.Conv2D(32, (3, 3), padding='same', activation='relu', input_shape=(28, 28, 1)))
    model.add(layers.Conv2D(32, (3, 3), padding='same', activation='relu'))
    model.add(layers.Dropout(0.3))
    model.add(layers.MaxPooling2D(pool_size=(2, 2)))
    
    model.add(layers.Conv2D(64, (3, 3),activation='relu', padding='same'))
    model.add(layers.Conv2D(64, (3, 3),activation='relu'))
    model.add(layers.Dropout(0.3))
    model.add(layers.MaxPooling2D(pool_size=(2, 2)))
    
    model.add(layers.Conv2D(128, (3, 3),activation='relu', padding='same'))
    model.add(layers.Dropout(0.2))
    model.add(layers.MaxPooling2D(pool_size=(2, 2))) 

    model.add(layers.Flatten())
    model.add(layers.Dense(256, activation='relu'))
    model.add(layers.Dense(256, activation='relu'))
    model.add(layers.Dense(10))

    model.summary()

    adam = optimizers.Adam(0.0005, 0.8, 0.99)
    model.compile(optimizer=adam,
                  loss=losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    history = model.fit(train_data, train_labels, epochs=15, 
                        validation_data=(test_data, test_labels))
    
    ## Plot Results
    plt.plot(history.history['accuracy'], label='accuracy')
    plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.ylim([0.5, 1])
    plt.legend(loc='lower right')
    plt.show()

    test_loss, test_acc = model.evaluate(test_data, test_labels, verbose=2)
    print(test_acc)







































    
