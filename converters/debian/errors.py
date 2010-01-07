class OptsParsingException(Exception):
  def __init__(self, msg):
    self.msg = msg

  def __str__(self):
    return str(self.msg)

class ParsingException(Exception):
  pass

class ParsingErrorException(ParsingException):
  def __init__(self, method, raw):
    self.method = method
    self.raw = raw

  def __str__(self):
    return "Method '%s' failed parsing: '%s'" % (self.method, self.raw)

class PackageDoesNotMatchRegularExpressionException(ParsingException):
  def __init__(self, packagename):
    self.packagename = packagename

  def __str__(self):
    return "Package '%s' does not match the regex" % self.packagename

class MissingMandatoryFieldException(ParsingException):
  def __init__(self, fieldname=""):
    self.fieldname = fieldname

  def __str__(self):
    return "Mandatory field '%s' is missing" % self.fieldname

class IndividualNotFoundException(Exception):
  def __init__(self, individual):
    self.individual = individual

  def __str__(self):
    return "Unable to find individual '%s'" % self.individual

class UnavailableLanguageException(Exception):
  def __init__(self, lang):
    self.lang = lang

  def __str__(self):
    return "Cannot generate label: '%s' is not available" % self.lang
