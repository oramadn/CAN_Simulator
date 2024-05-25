import random


def generate_random_frames(frame_count, num_of_random_hex_frames=3, split_ratio=0.7, seed=None, shuffle=False):
    random.seed(seed)

    frames = []
    # Generate static frames
    for _ in range(int(frame_count * (1 - split_ratio))):
        random_id = hex(random.randint(0, 2 ** 11 - 1))[2:].rjust(5, '0')  # 11-bit identifier
        random_data = hex(random.randint(0, 2 ** 64 - 1))[2:].rjust(16, '0')  # 64-bit data (16 hex characters)

        frames.append({'id': random_id, 'data': [random_data], 'dataSize': 1})

    # Generate variable frames
    for _ in range(int(frame_count * split_ratio)):
        random_id = hex(random.randint(0, 2 ** 11 - 1))[2:].rjust(5, '0')  # 11-bit identifier
        hex_values = []
        for _ in range(random.randint(2, num_of_random_hex_frames)):
            random_int = random.getrandbits(64)  # Generate a random 64-bit integer
            random_hex = format(random_int, '016x')  # Format to 16 hex characters
            hex_values.append(random_hex)
        frames.append({'id': random_id, 'data': hex_values, 'dataSize': len(hex_values)})

    if shuffle:
        random.shuffle(frames)
    return frames


def print_frames_for_arduino(frames):
    print("CANMessage messages[] = {")
    for frame in frames:
        data_entries = ', '.join([f'"{d}"' for d in frame['data']])
        print(f'  {{"{frame["id"]}", {{{data_entries}}}, {frame["dataSize"]}}},')
    print("};")


def split_frames_into_batches(frames, batch_count):
    batches = [[] for _ in range(batch_count)]
    for i, frame in enumerate(frames):
        batches[i % batch_count].append(frame)
    return batches


if __name__ == "__main__":
    frame_count = int(input("How many frames would you like to generate (10-100)? "))
    batch_count = int(input("Into how many batches would you like to split the frames? "))

    frames = generate_random_frames(frame_count, shuffle=True)
    batches = split_frames_into_batches(frames, batch_count)

    for i, batch in enumerate(batches):
        print(f"Batch {i + 1}:")
        print_frames_for_arduino(batch)
        print("\n")
