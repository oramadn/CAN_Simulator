import random

class CANmsg:
    def __init__(self, id, data):
        self.id = id
        self.data = data

def process_messages(messages, indices):
    # Shuffle indices to ensure unique random selection
    random.shuffle(indices)
    
    # Store the result of index mapping
    index_mapping_results = []

    for msg in messages:
        # Remove '0x' from data attribute
        msg.data = msg.data[2:]  # Assumes data always starts with '0x'

        if indices:
            # Get a unique index from the shuffled list of indices
            index = indices.pop(0)
            
            # Ensure the index is within the range of the data string
            if index < len(msg.data):
                # Map the index to the corresponding character in the data string
                index_char = msg.data[index]
                index_mapping_results.append((msg.id, index_char))
            else:
                # Handle the case where index is out of bounds
                index_mapping_results.append((msg.id, None))
        else:
            # No more indices available
            break

    return index_mapping_results

# Example usage:
messages = [
    CANmsg("0x0052b", "0xc0b9e7f85695c43d"),
    CANmsg("0x0052c", "0xc0b95098d595c43d")
]

indices = [19, 15]  # Example indices

results = process_messages(messages, indices)
for result in results:
    print(f"ID: {result[0]}, Data Character at Index: {result[1]}")
