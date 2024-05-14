import pandas as pd


def load_data(file_path):
    """ Load CAN data from a CSV file. """
    return pd.read_csv(file_path)


def preprocess_data(df, action):
    """ Filter data for specific action transitions and preprocess if necessary. """
    # This example assumes that data preprocessing is done outside this function
    return df[df['action'] == action].reset_index(drop=True)


def byte_and_frame_id_change_frequencies(df1, df2, num_frame_ids):
    """ Compute frequency of byte differences between two dataframes of CAN frames, tracking total changes by byte and by frame ID. """
    byte_change_counts = {i: 0 for i in range(8)}  # Count changes for each byte position
    frame_id_change_counts = {row.id: 0 for row in
                              df1[:num_frame_ids].itertuples()}  # Initialize with the first block of unique frame IDs

    for (idx1, row1), (idx2, row2) in zip(df1.iterrows(), df2.iterrows()):
        if row1['id'] != row2['id']:
            continue  # Ensure matching frame IDs are compared
        data1 = row1['data']
        data2 = row2['data']
        frame_change_detected = False

        for byte_pos in range(8):
            byte1 = int(data1[2 * byte_pos:2 * byte_pos + 2], 16)
            byte2 = int(data2[2 * byte_pos:2 * byte_pos + 2], 16)
            if byte1 != byte2:
                byte_change_counts[byte_pos] += 1
                frame_change_detected = True

        if frame_change_detected:
            frame_id_change_counts[row1['id']] += 1

    return byte_change_counts, frame_id_change_counts


def analyze_changes(change_dict):
    """ Analyze changes to determine the most significant byte positions. """
    significance = {key: len(value) for key, value in change_dict.items()}
    return significance


# Main execution
if __name__ == "__main__":
    df = load_data('data/temp.csv')
    df_idle = preprocess_data(df, 'Idle')
    df_throttle = preprocess_data(df, 'Throttle')

    byte_frequencies, frame_id_frequencies = byte_and_frame_id_change_frequencies(df_idle, df_throttle, 20)

    # Convert to DataFrame
    byte_freq_df = pd.DataFrame(list(byte_frequencies.items()), columns=['Byte Position', 'Change Frequency'])
    frame_id_freq_df = pd.DataFrame(list(frame_id_frequencies.items()), columns=['Frame ID', 'Change Frequency'])

    # Filter out rows where 'Change Frequency' is 0
    byte_freq_df = byte_freq_df[byte_freq_df['Change Frequency'] > 0]
    frame_id_freq_df = frame_id_freq_df[frame_id_freq_df['Change Frequency'] > 0]

    # Display the DataFrames
    print("Byte Change Frequencies:")
    print(byte_freq_df)
    print("\nFrame ID Change Frequencies:")
    print(frame_id_freq_df)
