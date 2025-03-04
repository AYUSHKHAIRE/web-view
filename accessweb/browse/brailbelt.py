class BrailBelt:
    def __init__(self):
        self.braille_dict = {
            "a": "1",
            "b": "12",
            "c": "14",
            "d": "145",
            "e": "15",
            "f": "124",
            "g": "1245",
            "h": "125",
            "i": "24",
            "j": "245",
            "k": "13",
            "l": "123",
            "m": "134",
            "n": "1345",
            "o": "135",
            "p": "1234",
            "q": "12345",
            "r": "1235",
            "s": "234",
            "t": "2345",
            "u": "136",
            "v": "1236",
            "w": "2456",
            "x": "1346",
            "y": "13456",
            "z": "1356",
            "1": "3456 1",
            "2": "3456 12",
            "3": "3456 14",
            "4": "3456 145",
            "5": "3456 15",
            "6": "3456 124",
            "7": "3456 1245",
            "8": "3456 125",
            "9": "3456 24",
            "0": "3456 245"
        }

        self.utf_8_dict = {}
        for key, value in self.braille_dict.items():
            self.utf_8_dict[value] = key  # Reverse mapping

    def encode_string(self, to_encode):
        if not isinstance(to_encode, str):
            raise ValueError(f'{to_encode} should be in string format, not {type(to_encode)}')
        string_to_return = ''
        for a_letter in to_encode.lower():  
            if a_letter in self.braille_dict:
                string_to_return += self.braille_dict[a_letter] + ' '  
            else:
                string_to_return += a_letter + ' '  
        return string_to_return.strip()  

    def decode_string(self, to_decode):
        if not isinstance(to_decode, str):
            raise ValueError(f'{to_decode} should be in string format, not {type(to_decode)}')
        string_to_return = ''
        num_detected_flag = False
        for a_seq in to_decode.split(' '):
            if a_seq == "3456":  # Number indicator detected
                num_detected_flag = True
                continue  # Skip to next iteration
            if num_detected_flag:
                key = f"3456 {a_seq}"
                num_detected_flag = False  # Reset flag
            else:
                key = a_seq
            utf_8_seq = self.utf_8_dict.get(key, '?')  
            string_to_return += utf_8_seq
        return string_to_return.strip()  

# braille = BrailBelt()
# encoded = braille.encode_string("hello123")
# print(f"Encoded: {encoded}")
# decoded = braille.decode_string(encoded)
# print(f"Decoded: {decoded}")
