import json

class Decoder:
    def __init__(self, path):
        self.path = path

    def decode(self, file):
        decodeFile = open(self.path + file)
        decodeString = decodeFile.read()
        return json.loads(decodeString)
