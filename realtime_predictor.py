import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from tensorflow.keras.models import load_model


class RealTimePredictor:
    def __init__(self, model=None, scaler=None, label_encoder=None):
        # Load the pre-trained model and scaler once when the class is instantiated
        self.model = model
        self.scaler = scaler
        self.label_encoder = label_encoder
        self.byte_columns = [f'byte_{i}' for i in range(8)]
        print("Model and scaler loaded successfully.")

    def hex_to_bytes(self, hex_str):
        """ Convert hexadecimal data to a list of integers (bytes). """
        return [int(hex_str[i:i + 2], 16) for i in range(0, len(hex_str), 2)]

    def create_sequences(self, df, sequence_length=20):
        """ Create sequences for LSTM model. """
        X = []
        for start_idx in range(0, len(df), sequence_length):
            end_idx = start_idx + sequence_length
            if end_idx > len(df):
                break
            seq = df.iloc[start_idx:end_idx][self.byte_columns].values
            X.append(seq)
        return np.array(X)

    def predict(self, data):
        df = pd.DataFrame([{'data': item['data']} for item in data])
        df['data'] = df['data'].apply(self.hex_to_bytes)
        df[self.byte_columns] = pd.DataFrame(df['data'].tolist(), index=df.index)
        df[self.byte_columns] = self.scaler.transform(df[self.byte_columns])
        X_new = self.create_sequences(df)  # Assuming no need for labels in prediction
        predictions = self.model.predict(X_new)
        predicted_classes = np.argmax(predictions, axis=1)
        predicted_labels = self.label_encoder.inverse_transform(predicted_classes)
        return predicted_labels[0]
