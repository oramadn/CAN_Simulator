import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, LSTM, GRU, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
import seaborn as sns


def hex_to_bytes(hex_str):
    """ Convert hexadecimal data to a list of integers (bytes). """
    return [int(hex_str[i:i + 2], 16) for i in range(0, len(hex_str), 2)]


def load_and_preprocess_data(filepath):
    """ Load and preprocess data from CSV. """
    directory = 'Vehicle Action Display experiment datasets/E'

    dfs = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)
            df = pd.read_csv(file_path)
            dfs.append(df)
    combined_df = pd.concat(dfs, ignore_index=True)

    output_path = os.path.join(directory, 'combined_data.csv')  # Specify a filename for the CSV
    combined_df.to_csv(output_path, index=False)
    print(f"Combined CSV created at: {output_path}")

    df = pd.read_csv(output_path)  # Load the combined CSV
    df['data_bytes'] = df['data'].apply(hex_to_bytes)
    max_bytes = max(df['data_bytes'].apply(len))
    byte_columns = [f'byte_{i}' for i in range(max_bytes)]
    df[byte_columns] = pd.DataFrame(df['data_bytes'].tolist(), index=df.index)
    scaler = MinMaxScaler()
    df[byte_columns] = scaler.fit_transform(df[byte_columns])
    return df, scaler, byte_columns


def create_sequences(df, byte_columns, sequence_length):
    """ Create sequences for RNN models. """
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


def build_model(model_type, input_shape):
    """ Build an RNN model based on model_type. """
    if model_type == "SimpleRNN":
        return Sequential([
            SimpleRNN(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            SimpleRNN(50, return_sequences=True),
            Dropout(0.2),
            SimpleRNN(50),
            Dropout(0.2),
            Dense(5, activation='softmax')  # Assuming binary classification
        ])
    elif model_type == "LSTM":
        return Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(5, activation='softmax')
        ])
    elif model_type == "GRU":
        return Sequential([
            GRU(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            GRU(50, return_sequences=True),
            Dropout(0.2),
            GRU(50),
            Dropout(0.2),
            Dense(5, activation='softmax')
        ])
    else:
        raise ValueError("Unsupported model type")


def train_and_evaluate(model_type, X_train, y_train, X_val, y_val, label_encoder, epochs=150, batch_size=16):
    """ Train and evaluate a model. """
    model = build_model(model_type, (X_train.shape[1], X_train.shape[2]))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    callback = EarlyStopping(monitor='loss', patience=15)
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size,
                        validation_data=(X_val, y_val), callbacks=[callback])

    # Predictions for evaluation
    y_pred_prob = model.predict(X_val)
    y_pred = np.argmax(y_pred_prob, axis=1)
    y_true = np.argmax(y_val, axis=1)

    # Calculate metrics
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='weighted')
    recall = recall_score(y_true, y_pred, average='weighted')
    f1 = f1_score(y_true, y_pred, average='weighted')
    auc = roc_auc_score(y_val, y_pred_prob, multi_class='ovr')

    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 7))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
    plt.title(f'Confusion Matrix for {model_type}')
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.show()

    # Plot accuracy and loss
    plt.figure()
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title(f'Model accuracy for {model_type}')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    plt.grid(True)
    plt.show()

    plt.figure()
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title(f'Model loss for {model_type}')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    plt.grid(True)
    plt.show()

    return model, history, accuracy, precision, recall, f1, auc


def train(sequence_length, save=False):
    """ Main training function to handle all models. """
    df, scaler, byte_columns = load_and_preprocess_data('data/combined_file.csv')
    label_encoder = LabelEncoder()
    X, y = create_sequences(df, byte_columns, sequence_length)
    y_encoded = label_encoder.fit_transform(y)
    y_categorical = to_categorical(y_encoded)
    X_train, X_val, y_train, y_val = train_test_split(X, y_categorical, test_size=0.2, random_state=42)

    for model_type in ["SimpleRNN", "LSTM", "GRU"]:
        print(f"Training {model_type}")
        model, history, accuracy, precision, recall, f1, auc = train_and_evaluate(model_type,
                                                                                  X_train,
                                                                                  y_train,
                                                                                  X_val,
                                                                                  y_val,
                                                                                  label_encoder,
                                                                                  150,
                                                                                  16)
        print(f"Results for {model_type}: Accuracy: {accuracy}, Precision: {precision}, Recall: {recall}, F1: {f1}, AUC: {auc}")
        if save:
            model.save(f'model_{model_type}.keras')


if __name__ == "__main__":
    train(30)
