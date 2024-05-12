import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt


def create_sequences(df, sequence_length=20):
    X = []
    y = []
    start_idx = 0

    # Iterate over the dataframe with a step size of 'sequence_length'
    for start_idx in range(0, len(df), sequence_length):
        end_idx = start_idx + sequence_length

        # Make sure we have a full sequence
        if end_idx > len(df):
            break

        # Extract the sequence and the label
        seq = df.iloc[start_idx:end_idx][byte_columns].values
        label = df.iloc[start_idx]['action']  # Assuming label is same for the whole sequence

        X.append(seq)
        y.append(label)

    return np.array(X), np.array(y)


# Function to convert hexadecimal data to a list of integers (bytes)
def hex_to_bytes(hex_str):
    return [int(hex_str[i:i + 2], 16) for i in range(0, len(hex_str), 2)]


csv_file_path = 'data/combined_file.csv'

# Load CSV file
df = pd.read_csv(csv_file_path)
print(f"Loaded CSV with shape {df.shape}")
# print(df.head())  # Print the head to check the initial rows

# Convert hex to bytes
df['data_bytes'] = df['data'].apply(hex_to_bytes)
print(df.head())

# Assuming 'data_bytes' contains lists of the same length
max_bytes = max(df['data_bytes'].apply(len))  # Get the max length of bytes list
byte_columns = [f'byte_{i}' for i in range(max_bytes)]
df[byte_columns] = pd.DataFrame(df['data_bytes'].tolist(), index=df.index)

print(df.head())
# Check data types and structure after conversion
# print(df.dtypes)
# print(df[byte_columns].head())  # Show the first few rows of byte columns

# Create an instance of MinMaxScaler
scaler = MinMaxScaler()

# List of byte columns
byte_columns = [f'byte_{i}' for i in range(8)]

# Scale the byte columns and update the DataFrame
df[byte_columns] = scaler.fit_transform(df[byte_columns])

print(df.head())

X, y = create_sequences(df)

# Encode labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)
y_categorical = to_categorical(y_encoded)

X_train, X_val, y_train, y_val = train_test_split(X, y_categorical, test_size=0.2, random_state=42)

model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
    Dropout(0.2),
    LSTM(50, return_sequences=True),
    Dropout(0.2),
    LSTM(50),
    Dropout(0.2),
    Dense(y_train.shape[1], activation='softmax')  # Assuming one-hot encoded labels
])

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Plot histograms of the feature distributions to ensure they are as expected
df[byte_columns].hist(figsize=(12, 10))
plt.show()

# Train the model
# history = model.fit(X_train, y_train, epochs=100, batch_size=16, validation_data=(X_val, y_val))
# model.save('model.keras')
#
# # Evaluate the model
# evaluation = model.evaluate(X_val, y_val)
# print("Loss:", evaluation[0], "Accuracy:", evaluation[1])
#
# # Plot training & validation accuracy values
# plt.plot(history.history['accuracy'])
# plt.plot(history.history['val_accuracy'])
# plt.title('Model accuracy')
# plt.ylabel('Accuracy')
# plt.xlabel('Epoch')
# plt.legend(['Train', 'Validation'], loc='upper left')
# plt.show()
#
# # Plot training & validation loss values
# plt.plot(history.history['loss'])
# plt.plot(history.history['val_loss'])
# plt.title('Model loss')
# plt.ylabel('Loss')
# plt.xlabel('Epoch')
# plt.legend(['Train', 'Validation'], loc='upper left')
# plt.show()
# # ------------------------------------------------------------------------

# Loading the model saved in Keras format
model = load_model('model.keras')

new_data_path = 'data/test.csv'
new_df = pd.read_csv(new_data_path)

# Convert hex data to bytes
new_df['data_bytes'] = new_df['data'].apply(hex_to_bytes)

# Create byte columns and scale them
new_df[byte_columns] = pd.DataFrame(new_df['data_bytes'].tolist(), index=new_df.index)
new_df[byte_columns] = scaler.transform(new_df[byte_columns])  # Use the same scaler as before
print(new_df.head())
# Check if new data needs labels for some reason (if not skip labeling steps)
# Assume labels are necessary, repeat label encoding with the same LabelEncoder (if needed)

X_new, _ = create_sequences(new_df)  # No labels if just predicting

predictions = model.predict(X_new)
predicted_classes = np.argmax(predictions, axis=1)  # Convert probabilities to class labels if necessary

# Optionally, convert numeric labels back to original categorical labels
predicted_labels = le.inverse_transform(predicted_classes)
print(predicted_labels)

# If probabilities are meaningful, you might plot them
plt.figure(figsize=(10, 6))
plt.bar(range(len(predictions[0])), predictions[0])  # Example: Plotting class probabilities for the first predicted sequence
plt.title('Predicted Class Probabilities for the First Sequence')
plt.xlabel('Class')
plt.ylabel('Probability')
plt.show()

