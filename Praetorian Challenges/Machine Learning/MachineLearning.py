import time
import pickle
import base64
import logging
import requests
import numpy as np
from NeuralNetwork import *

email = 'johnsmith@email.com'

## Enumerate architectures in alphabetic order
architecture = ['alphaev56', 'arm', 'avr', 'm68k', 'mips', 'mipsel', 'powerpc', 's390', 'sh4', 'sparc', 'x86_64', 'xtensa']

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

## ----------------------------------------------------------------
## Communication Code

class Server(object):
    url = 'https://mlb.praetorian.com'
    log = logging.getLogger(__name__)

    def __init__(self):
        self.session = requests.session()
        self.binary  = None
        self.hash    = None
        self.wins    = 0
        self.targets = []

    def _request(self, route, method='get', data=None):
        while True:
            try:
                if method == 'get':
                    r = self.session.get(self.url + route)
                else:
                    r = self.session.post(self.url + route, data=data)
                if r.status_code == 429:
                    raise Exception('Rate Limit Exception')
                if r.status_code == 500:
                    raise Exception('Unknown Server Exception')

                return r.json()
            except Exception as e:
                self.log.error(e)
                self.log.info('Waiting 60 seconds before next request')
                time.sleep(60)

    def get(self):
        r = self._request("/challenge")
        self.targets = r.get('target', [])
        self.binary  = base64.b64decode(r.get('binary', ''))
        return r

    def post(self, target):
        r = self._request("/solve", method="post", data={"target": target})
        self.wins = r.get('correct', 0)
        self.hash = r.get('hash', self.hash)
        self.ans  = r.get('target', 'unknown')
        return r

    def get_hash(self):
        response = self.session.get('https://mlb.praetorian.com/hash', data={'email':email})
        r = response.json()
        
        if 'error' in r:
            print('Error Message: ' + r.json()['error'])
        elif 'hash' in r:
            self.hash = r['hash']
            
            print('Saving hash to ' + email + '_hash.txt')
            f = open(email + '_hash.txt', 'w')
            f.write('Email: ' + email + '\nHash: ' + r['hash'])

## ----------------------------------------------------------------------------
## Helper functions

## Convert s.binary to an array of bits
def hex_to_bits(raw):
    return np.reshape(np.unpackbits(np.frombuffer(raw, 'uint8')), (1, -1))

## Convert an array of bits to an array bytes
def bits_to_bytes(bits):
    byte = np.empty((bits.shape[0], 0), 'uint8')
    for i in range(0, 512, 8):
        byte = np.append(byte, np.packbits(bits[:, i:i+8], axis=1), axis=1)

    return byte

##  Multi-hot encode an array of bytes
def bytes_to_multi_hot(byte):
    hotBytes = np.zeros((byte.shape[0], 256), 'uint8')
    np.put_along_axis(hotBytes, byte, 1, axis=1)

    return hotBytes

## Format s.binary into neural network input
def format_server_data(raw):
    bits     = hex_to_bits(raw)
    byte     = bits_to_bytes(bits)
    hotBytes = bytes_to_multi_hot(byte)

    x = np.append(bits, hotBytes, axis=1)
      
    return x

## Format datasets to train on.
def format_training_data(data):
    np.random.shuffle(data)
    x = data[:, :-1]
    y = np.reshape(data[:,-1], (-1, 1))
    
    byte     = bits_to_bytes(data)
    hotBytes = bytes_to_multi_hot(byte)
    x        = np.append(x, hotBytes, axis=1)

    return x, y
    
## ----------------------------------------------------------------------------

## Collects (trainSize + testSize) data samples and stores them as binary arrays.
## Labels are appended to the end of each data point and stored as an integer representing the index in the global variable 'architecture' list
def collect_data(trainSize=24000, testSize=2000, trainFile='unformatted_training_data.npy', testFile='unformatted_test_data.npy'):    
    s = Server()
    total = trainSize + testSize

    ## Initialize dataset
    x = np.empty((0,512), 'uint8')
    y = np.empty((0,1), 'uint8')
    uniques = np.array([])

    ## Collect data
    while len(uniques) < total:
        for _ in range(total - len(uniques)):
            ## Get input data
            s.get()
            bits = hex_to_bits(s.binary)

            ## Get label
            s.post(s.targets[0])
            index = architecture.index(s.ans)
            
            ## Append to dataset
            x = np.append(x, bits, axis=0)
            y = np.append(y, [[index]], axis=0)

        ## Remove duplicates
        uniques = np.unique(np.append(x, y, axis=1), axis=0)

    ## Shuffle data and split into training and test sets
    np.random.shuffle(uniques)
    train = uniques[:trainSize]
    test  = uniques[trainSize:]
    
    ## Save datasets
    with open(trainFile, 'wb') as f:
        np.save(f, train)

    with open(testFile, 'wb') as f:
        np.save(f, test)

## Train model
def train(layer1Size=768, layer2Size=384, epoch=15, lr=0.1, trainFile='unformatted_training_data.npy', \
          testFile='unformatted_test_data.npy', saveFile='Trained_NN.pickle', loadFile=None, combine=False, decay=True):
    ## Create or load a model
    if loadFile != None:
        nn = load_nn(loadFile)
    else:
        nn = NeuralNet(layer1Size, layer2Size)
    
    ## Load datasets
    train = np.load(trainFile)
    test  = np.load(testFile)

    ## If true, also train on test data 
    if combine == True:
        train = np.append(train, test, axis=0)

    ## Format training and test data
    xtrain, ytrain = format_training_data(train)
    xtest , ytest  = format_training_data(test)
    
    nn.train_network(xtrain, ytrain, xtest, ytest, epoch, lr, decay)

    ## Save Model
    print('Saving Model')
    nn.save(saveFile)

## Print confusion matrix
def confusion_matrix(loadFile='Trained_NN.pickle', testFile='unformatted_test_data.npy'):
    nn = load_nn(loadFile)

    test = np.load(testFile)
    x, y  = format_training_data(test)
    nn.print_confusion_matrix(x, y)

## Test model on game server.
def play(loadFile='Trained_NN.pickle', verbose=False):
    s = Server()
    nn = load_nn(loadFile)

    ## Play until hash is recieved
    while not s.hash:
        s.get()
        x = format_server_data(s.binary)
        
        ## Make prediction
        _, _ , _, prediction = nn.predict(x)
        prediction = list(prediction.flat)
        
        ## Convert prediction to architecture name
        index  = prediction.index(max(prediction))
        target = architecture[index]

        while target not in s.targets:
            prediction[index] = -1
            index  = prediction.index(max(prediction))
            target = architecture[index]

        ## Send guess
        s.post(target)
        
        if verbose == True:
            if target != s.ans:
                print('Incorrect')
            s.log.info("Guess:[{: >9}]   Answer:[{: >9}]   Wins:[{: >3}]".format(target, s.ans, s.wins))

    ## Print and save hash
    s.log.info("You win! {}".format(s.hash))
    s.get_hash()

## ----------------------------------------------
## Play the game
    
if __name__ == "__main__":
    play(verbose=True)
