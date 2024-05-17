import pandas as pd
import numpy as np
import statsmodels.api as sm


def analyze_linear_relationship_per_frame(csv_file, num_frames):
    df = pd.read_csv(csv_file)
    num_bytes = 8  # Assuming 8 bytes per frame

    # Dictionary to store regression results with keys as (frame_id, byte_position)
    regression_results = {}

    # Retrieve frame IDs for the first block of data to associate frame indexes with frame IDs
    frame_ids = df['id'].iloc[:num_frames].tolist()

    # Process each frame using its ID for better identification
    for frame_index in range(num_frames):
        frame_id = frame_ids[frame_index]
        # Filter data for the current frame across all blocks and explicitly copy it
        frame_data = df.iloc[frame_index::num_frames].copy()

        for byte_pos in range(num_bytes):
            # Extract bytes for current position from each frame's data and handle data manipulation properly
            frame_data[f'byte_{byte_pos}'] = frame_data['data'].apply(lambda x: int(x[2 * byte_pos:2 * byte_pos + 2],
                                                                                    16))

            # Prepare the data for regression
            X = np.arange(len(frame_data))  # Independent variable: block index
            y = frame_data[f'byte_{byte_pos}']  # Dependent variable: byte value

            # Check if there is any variance in y, if not, skip to next byte
            if np.var(y) == 0:
                continue

            # Add a constant to the model (intercept)
            X = sm.add_constant(X)

            # Fit the linear regression model
            try:
                model = sm.OLS(y, X).fit()
                # Store the R-squared value along with frame ID and byte position
                regression_results[(frame_id, byte_pos)] = model.rsquared
            except Exception as e:
                print(f"Error fitting model for frame {frame_id}, byte {byte_pos}: {e}")
                continue

    # Determine the byte and frame with the highest R-squared value
    best_frame_byte = max(regression_results, key=regression_results.get, default=(None, None))
    best_frame_id, best_byte = best_frame_byte
    best_r_squared = regression_results.get(best_frame_byte, 0)

    return best_frame_id, best_byte, best_r_squared


if __name__ == "__main__":
    best_frame_id, best_byte, best_r_squared = analyze_linear_relationship_per_frame('data/brake_data.csv')
    print(f"The frame ID {best_frame_id} and byte position {best_byte} has the most linear relationship with an R-squared of {best_r_squared:.2f}")
