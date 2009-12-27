class MissingMandatoryFieldException(Exception):
  def __init__(self, fieldname=""):
    self.fieldname = fieldname

  def __str__(self):
    return "Mandatory field '%s' is missing" % self.fieldname

class OptsParsingException(Exception):
  def __init__(self, msg):
    self.msg = msg

  def __str__(self):
    return str(self.msg)
