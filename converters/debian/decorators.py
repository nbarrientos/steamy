from errors import MissingMandatoryFieldException

def required(fieldname):
  def decorator(f):
    def wrapper(self, raw):
      if fieldname in raw:
        return f(self, raw) 
      else:
        raise MissingMandatoryFieldException(fieldname)
    return wrapper
  return decorator

def optional(fieldname):
  def decorator(f):
    def wrapper(self, raw):
      if fieldname in raw:
        return f(self, raw)
      else:
        return None
    return wrapper
  return decorator
