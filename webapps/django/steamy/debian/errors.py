class SPARQLQueryProcessorError(Exception):
    def __init__(self, reason):
        self.reason = reason

class InvalidKeywordError(Exception):
    def __init__(self):
        self.reason = "Invalid keyword"
