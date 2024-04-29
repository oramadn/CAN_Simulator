from can_message import CANmsg


class VariableFrame(CANmsg):
    def __init__(self, id=None, data=None, idx=None, random_hex_numbers=None):
        super().__init__(id=id, data=data)  # Pass id and data to the superclass constructor
        if random_hex_numbers is None:
            random_hex_numbers = []  # Initialize a new list if none provided
        self.idx = idx
        self.random_hex_numbers = random_hex_numbers
