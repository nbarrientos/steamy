from errors import MissingMandatoryFieldException
from errors import UnavailableLanguageException

def required(fieldname):
  def decorator(f):
    def wrapper(*args):
      if fieldname in args[1]: # Workaround, kwargs!
        return f(*args) 
      else:
        raise MissingMandatoryFieldException(fieldname)
    return wrapper
  return decorator

def optional(fieldname):
  def decorator(f):
    def wrapper(*args):
      if fieldname in args[1]:
        return f(*args)
      else:
        return None
    return wrapper
  return decorator

def checklang(f):
  def wrapper(self, lang):
    if lang in self.AVAILABLE_LANGS:
      return f(self, lang)
    else:
      raise UnavailableLanguageException(lang)
  return wrapper
