import hashlib

from debian_bundle.changelog import Version

class SourcePackage():
  def __init__(self):
    self.package = None
    self.binary = None
    self.version = None
    self.build_depends = None
    self.build_depends_indep = None

  def asURI(self, base):
    return "%s/source/%s/%s" % (base, self.package, self.version)

class BinaryPackageLite():
  def __init__(self, package=None, version=None):
    self.package = package
    self.version = version

  def asURI(self, base):
    return "%s/binary/%s/%s" % (base, self.package, self.version)

  def __repr__(self):
    return "%s (%s)" % (self.package, self.version)

class BinaryPackage(BinaryPackageLite):
  def __init__(self):
    self.depends = None
    self.recommends = None
    self.build = None

class BinaryPackageBuild():
  def __init__(self):
    self.architecture = None
    self.installedSize = None

  def asURI(self, base):
    return "%s/%s" % (base, self.architecture)

class Architecture():
  def __init__(self, arch):
    self.name = arch

  def asURI(self, base):
    return "%s/arch/%s" % (base, self.name)

  def __repr__(self):
    return str(self.name)

  def __eq__(self, other):
    return self.name.__eq__(other.name)

class VersionNumber(Version):
  def asURI(self, base):
    return "%s/version/%s" % (base, str(self))

class Constraints():
  def __init__(self):
    self.orconstraints = []

  def add(self, orconstraint):
    self.orconstraints.append(orconstraint)

  def get(self, index):
    return self.orconstraints[index]

  def len(self):
    return len(self.orconstraints)

  def __repr__(self):
    return "Constraints: %s" % str(self.orconstraints)

  def __iter__(self):
    return self.orconstraints.__iter__()

class OrConstraint():
  def __init__(self):
    self.constraints = []

  def add(self, constraint):
    self.constraints.append(constraint)

  def get(self, index):
    return self.constraints[index]

  def __repr__(self):
    return "OrConstraint: %s" % str(self.constraints)

class Constraint():
  def __init__(self):
    self.package = None
    self.operator = None
    self.version = None
    self.exceptin = []
    self.onlyin = []

  def asURI(self, base):
    tail = "%s" % self.package
    if self.operator and self.version:
      tail = tail + "%s%s" % (self.operator, self.version)
    # FIMXE: Add *in
    return "%s/constraint/%s" % (base, hashlib.sha1(tail).hexdigest())

  def __repr__(self):
    if self.operator and self.version:
      return "%s (%s %s)" % (self.package, self.operator, self.version)
    else:
      return "%s" % self.package
