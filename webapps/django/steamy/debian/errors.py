class SPARQLQueryProcessorError(Exception):
    def __init__(self, reason):
        self.reason = reason

class UnexpectedSituationError(Exception):
    pass
