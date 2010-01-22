class SPARQLQueryProcessorError(Exception):
    def __init__(self, reason):
        self.reason = reason

class UnexpectedSituationError(Exception):
    pass

class SPARQLQueryBuilderError(Exception):
    pass

class UnexpectedFieldValueError(Exception):
    def __init__(self, field):
        self.field = field

    def __str__(self):
        return "Unexpected form value parsing '%s'" % self.field
