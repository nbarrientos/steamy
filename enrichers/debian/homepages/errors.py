class W3CValidatorError(Exception):
    pass

class W3CValidatorUnableToConnectError(W3CValidatorError):
    def __str__(self):
        return "Unable to connect to W3C markup validation service"

class W3CValidatorUnexpectedValidationResultError(W3CValidatorError):
    def __str__(self):
        return "W3C validation service returned an unexpected result"

class W3CValidatorUnexpectedStatusCodeError(W3CValidatorError):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return "W3C validation service returned an unexpected status code"
