import time
import random

class CANmsg:
    def __init__(self, id=None, data=None):
        self.id = id
        self.data = data

def generateFrames(frameCount):
    #Generate random IDs and DATA
    data = []
    for i in range(frameCount):
        random_id = '0x' + hex(random.randint(0, 2**11 - 1))[2:].rjust(5, '0')
        random_data = '0x' + hex(random.randint(0, 2**64 - 1))[2:].rjust(16, '0')

        data.append(CANmsg(random_id,random_data))
        
    data = sorted(data, key=lambda x: x.id)
    return data

def generateTable(frames):
    #Prepare data for making a table
    data = []
    data_row = []
    for frame in frames:
        data_row.append(frame.id)
        for i in range(2, len(frame.data), 2):
            data_row.append("0x" + frame.data[i:i+2])
        data_row_copy = data_row.copy()
        data.append(data_row_copy)
        data_row.clear()

    # Determine the maximum width for each column
    column_widths = [max(len(str(item)) for item in column) for column in zip(*data)]

    # Centered column titles
    for i, column_title in enumerate(data[0]):
        print(f"{column_title.center(column_widths[i])}", end="  ")
    print()

    # Print the table
    for row in data[1:]:
        for i, item in enumerate(row):
            print(f"{item:{'>' if isinstance(item, int) else '<'}{column_widths[i]}}", end="  ")
        print()

def promptUser():
    while(True):
        try:
            frameCount = int(input("How many CAN frames would you like to simulate (10-100): "))
        except ValueError:
            print("\nInvalid input")
            continue   
        if frameCount < 10 or frameCount > 100:
            print("\nInvalid amount of CAN messages requested")
            continue
        break

    return frameCount
    # data = generateFrames(frameCount) #list of CANmsg objects
    # generateTable(data)
    

# if __name__ == '__main__':
#     main()