class MissingMandatoryFieldException(Exception):
  def __init__(self, fieldname=""):
    self.fieldname = fieldname

  def __str__(self):
    return "Mandatory field '%s' is missing" % self.fieldname

class NoFilesException(Exception):
  def __init__(self):
    pass

class NoBaseURIException(Exception):
  def __init__(self):
    pass
