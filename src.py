import time
import random


class CANmsg:
    def __init__(self, id=None, data=None):
        self.id = id
        self.data = data


def generate_frames(frame_count):
    # Generate random IDs and DATA
    data = []
    for i in range(frame_count):
        random_id = hex(random.randint(0, 2 ** 11 - 1))[2:].rjust(5, '0')
        random_data = hex(random.randint(0, 2 ** 64 - 1))[2:].rjust(16, '0')

        data.append(CANmsg(random_id, random_data))

    data = sorted(data, key=lambda x: x.id)
    return data


# def generate_table(frames):
#     # Prepare data for making a table
#     data = []
#     data_row = []
#     for frame in frames:
#         data_row.append(frame.id)
#         for i in range(2, len(frame.frames), 2):
#             data_row.append("0x" + frame.frames[i:i + 2])
#         data_row_copy = data_row.copy()
#         data.append(data_row_copy)
#         data_row.clear()
#
#     # Determine the maximum width for each column
#     column_widths = [max(len(str(item)) for item in column) for column in zip(*data)]
#
#     # Centered column titles
#     for i, column_title in enumerate(data[0]):
#         print(f"{column_title.center(column_widths[i])}", end="  ")
#     print()
#
#     # Print the table
#     for row in data[1:]:
#         for i, item in enumerate(row):
#             print(f"{item:{'>' if isinstance(item, int) else '<'}{column_widths[i]}}", end="  ")
#         print()


def prompt_user():
    while (True):
        try:
            frame_count = int(input("How many CAN frames would you like to simulate (10-100): "))
        except ValueError:
            print("\nInvalid input")
            continue
        if frame_count < 10 or frame_count > 100:
            print("\nInvalid amount of CAN messages requested")
            continue
        break

    return frame_count
    # data = generateFrames(frame_count) #list of CANmsg objects
    # generateTable(data)


def split_frames(classList, ratio=0.6):
    random.shuffle(classList)

    split_index = int(len(classList) * ratio)

    variable_frames = classList[:split_index]
    static_frames = classList[split_index:]

    return variable_frames, static_frames


def generate_variable_bytes_idx(frames):
    variable_bytes = len(frames) * 8
    variable_bytes_idx = random.sample(range(variable_bytes), variable_bytes // 2)
    # print(f'Initial variable_bytes_idx: {variable_bytes_idx}')

    variable_bytes_idx, throttle_bytes = generate_unique_subset(variable_bytes_idx, 3)
    variable_bytes_idx, brake_bytes = generate_unique_subset(variable_bytes_idx, 3)
    variable_bytes_idx, steering_bytes = generate_unique_subset(variable_bytes_idx, 4)
    # print(f'throttle_bytes: {throttle_bytes}\nbrake_bytes: {brake_bytes}\nsteering_bytes: {steering_bytes}\n\nFinal variable_bytes_idx: {variable_bytes_idx}')

    return variable_bytes_idx, throttle_bytes, brake_bytes, steering_bytes


def generate_unique_subset(original_list, subset_size):
    # Select a unique subset of specified size from the original list
    unique_subset = random.sample(original_list, subset_size)

    # Create a set from the unique subset for efficient removal
    subset_set = set(unique_subset)

    # Remove the elements of the unique subset from the original list
    original_list = [item for item in original_list if item not in subset_set]

    return original_list, unique_subset
