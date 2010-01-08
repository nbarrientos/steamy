class BaseError(Exception):
  pass

class UserOptionsError(BaseError):
  def __init__(self, msg):
    self.msg = msg

  def __str__(self):
    return str(self.msg)

class ParsingError(BaseError):
  pass

class ParserError(ParsingError):
  def __init__(self, method, raw):
    self.method = method
    self.raw = raw

  def __str__(self):
    return "Method '%s' failed parsing: '%s'" % (self.method, self.raw)

class PackageDoesNotMatchRegularExpression(ParsingError):
  def __init__(self, packagename):
    self.packagename = packagename

  def __str__(self):
    return "Package '%s' does not match the regex" % self.packagename

class MissingMandatoryFieldError(ParsingError):
  def __init__(self, fieldname=""):
    self.fieldname = fieldname

  def __str__(self):
    return "Mandatory field '%s' is missing" % self.fieldname

class IndividualNotFoundError(BaseError):
  def __init__(self, individual):
    self.individual = individual

  def __str__(self):
    return "Unable to find individual '%s'" % self.individual

class UnavailableLanguageError(BaseError):
  def __init__(self, lang):
    self.lang = lang

  def __str__(self):
    return "Cannot generate label: '%s' is not available" % self.lang
