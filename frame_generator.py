import random


def generate_random_frames(frame_count, num_of_random_hex_frames=5, split_ratio=0.5, seed=None):
    random.seed(seed)

    frames = []
    # Generate static frames
    for _ in range(int(frame_count * (1 - split_ratio))):
        random_id = hex(random.randint(0, 2 ** 11 - 1))[2:].rjust(5, '0')
        random_data = hex(random.randint(0, 2 ** 64 - 1))[2:].rjust(16, '0')

        frames.append({'id': random_id, 'data': random_data})

    # Generate variable frames
    for _ in range(int(frame_count * split_ratio)):
        random_id = hex(random.randint(0, 2 ** 11 - 1))[2:].rjust(5, '0')
        hex_values = []
        for _ in range(random.randint(2, num_of_random_hex_frames)):
            # Generate a random integer with the right number of bits (8 bits per byte)
            random_int = random.getrandbits(64)
            # Convert integer to a hexadecimal string, and format to ensure correct length
            random_hex = format(random_int, '0{}x'.format(16))
            # Append the formatted hex string to the list
            hex_values.append(random_hex)
        frames.append({'id': random_id, 'data': hex_values})
    # random.shuffle(frames)
    return frames


if __name__ == "__main__":
    frame_count = int(input("How many frames would you like to generate (10-100)?"))
    generate_random_frames(frame_count)
