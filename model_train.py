import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import SimpleRNN, LSTM, GRU, Dense, Dropout
from tensorflow.keras.utils import to_categorical


def hex_to_bytes(hex_str):
    """ Convert hexadecimal data to a list of integers (bytes). """
    return [int(hex_str[i:i + 2], 16) for i in range(0, len(hex_str), 2)]


def load_and_preprocess_data(filepath):
    """ Load and preprocess data from CSV. """
    df = pd.read_csv(filepath)
    # print(f"Loaded CSV with shape {df.shape}")
    df['data_bytes'] = df['data'].apply(hex_to_bytes)
    max_bytes = max(df['data_bytes'].apply(len))
    byte_columns = [f'byte_{i}' for i in range(max_bytes)]
    df[byte_columns] = pd.DataFrame(df['data_bytes'].tolist(), index=df.index)
    scaler = MinMaxScaler()
    df[byte_columns] = scaler.fit_transform(df[byte_columns])
    return df, scaler, byte_columns


def create_sequences(df, byte_columns, sequence_length):
    """ Create sequences for LSTM model. """
    X, y = [], []
    for start_idx in range(0, len(df), sequence_length):
        end_idx = start_idx + sequence_length
        if end_idx > len(df):
            break
        seq = df.iloc[start_idx:end_idx][byte_columns].values
        label = df.iloc[start_idx]['label']
        X.append(seq)
        y.append(label)
    return np.array(X), np.array(y)


def train_model(X, y, byte_columns, save=False, epochs=100, batch_size=16):
    """ Train the LSTM model. """
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    # model = Sequential([
    #     SimpleRNN(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
    #     Dropout(0.2),
    #     SimpleRNN(50, return_sequences=True),
    #     Dropout(0.2),
    #     SimpleRNN(50),
    #     Dropout(0.2),
    #     Dense(y_train.shape[1], activation='softmax')
    # ])
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
        Dropout(0.2),
        LSTM(50, return_sequences=True),
        Dropout(0.2),
        LSTM(50),
        Dropout(0.2),
        Dense(y_train.shape[1], activation='softmax')
    ])
    # model = Sequential([
    #     GRU(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
    #     Dropout(0.2),
    #     GRU(50, return_sequences=True),
    #     Dropout(0.2),
    #     GRU(50),
    #     Dropout(0.2),
    #     Dense(y_train.shape[1], activation='softmax')
    # ])
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_val, y_val))

    # # Evaluate the model
    evaluation = model.evaluate(X_val, y_val)
    print("Loss:", evaluation[0], "Accuracy:", evaluation[1])
    if save:
        model.save('model.keras')

    # Plot accuracy
    plt.figure()
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('Model accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    plt.grid(True)
    plt.show()

    # Plot loss
    plt.figure()
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Model loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    plt.grid(True)
    plt.show()

    return model, history


def load_and_predict(model, new_data_path, scaler, byte_columns):
    """ Load new data and make predictions with the loaded model. """
    new_df = pd.read_csv(new_data_path)
    new_df['data_bytes'] = new_df['data'].apply(hex_to_bytes)
    new_df[byte_columns] = pd.DataFrame(new_df['data_bytes'].tolist(), index=new_df.index)
    new_df[byte_columns] = scaler.transform(new_df[byte_columns])
    X_new, _ = create_sequences(new_df, byte_columns)  # Assuming no need for labels in prediction
    predictions = model.predict(X_new)
    return predictions


def train(sequence_length, save=False):
    # Load data
    df, scaler, byte_columns = load_and_preprocess_data('data/combined_file.csv')

    # Encode labels
    label_encoder = LabelEncoder()
    X, y = create_sequences(df, byte_columns, sequence_length)
    y_encoded = label_encoder.fit_transform(y)
    y_categorical = to_categorical(y_encoded)

    model, history = train_model(X, y_categorical, byte_columns, save, 100)  # save, Epochs, Batchsize
    return model, scaler, label_encoder


if __name__ == "__main__":
    train()
