import numpy as np

import tensorflow as tf
import keras

INPUT_FILE = r"data\alice-in-wonderland.txt"

print("Extracting text from input")
file = open(INPUT_FILE, 'rb')
lines = []
for line in file:
    line = line.strip().lower()
    line = line.decode("ascii", "ignore")
    if len(line) == 0:
        continue
    lines.append(line)
file.close()
text = " ".join(lines)

chars = set([c for c in text])
nb_chars = len(chars)
char2index = dict((c, i) for i, c in enumerate(chars))
index2char = dict((i, c) for i, c in enumerate(chars))

#print(index2char)

print("Creating input and label")
SEQ_LEN = 10 #we define the size of the character sequence in one time step
STEP = 1
print("The table is ready")

input_chars = []
label_chars = []
for i in range(0, len(text) - SEQ_LEN, STEP):
    input_chars.append(text[i:i + SEQ_LEN])
    label_chars.append(text[i + SEQ_LEN])

print(input_chars)

print("Vectorizing input and label text...")
X = np.zeros((len(input_chars), SEQ_LEN, nb_chars), dtype=np.bool_)
y = np.zeros((len(input_chars), nb_chars), dtype=np.bool_)
for i, input_char in enumerate(input_chars):
    for j, ch in enumerate(input_char):
        X[i, j, char2index[ch]] = 1
    y[i, char2index[label_chars[i]]] = 1

HIDDEN_SIZE = 128
BATCH_SIZE = 128
NUM_ITERATIONS = 25
NUM_EPOCHS_PER_ITERATION = 1
NUM_PREDS_PER_EPOCH = 100

model = keras.Sequential()
model.add(keras.layers.SimpleRNN(HIDDEN_SIZE, return_sequences=False,
                    input_shape=(SEQ_LEN, nb_chars),
                    unroll=True))
model.add(keras.layers.Dense(nb_chars))
model.add(keras.layers.Activation("softmax"))

model.compile(loss="categorical_crossentropy", optimizer="rmsprop")

for iteration in range(NUM_ITERATIONS):
    print("=" * 50)
    print("Iteration #: %d" % (iteration))
    model.fit(X, y, batch_size=BATCH_SIZE, epochs=NUM_EPOCHS_PER_ITERATION)

    # testing model
    # randomly choose a row from input_chars, then use it to 
    # generate text from model for next 100 chars
    test_idx = np.random.randint(len(input_chars))
    test_chars = input_chars[test_idx]
    print("Generating from seed: %s" % (test_chars))
    print(test_chars, end="")
    for i in range(NUM_PREDS_PER_EPOCH):
        Xtest = np.zeros((1, SEQ_LEN, nb_chars))
        for i, ch in enumerate(test_chars):
            Xtest[0, i, char2index[ch]] = 1
        pred = model.predict(Xtest, verbose=0)[0]
        ypred = index2char[np.argmax(pred)]
        print(ypred, end="")
        # move forward with test_chars + ypred
        test_chars = test_chars[1:] + ypred
    print()