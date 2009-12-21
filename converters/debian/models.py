class BinaryPackage():
  def __init__(self):
    self.package = None
    self.version = None
    self.depends = []

class Constraints():
  def __init__(self):
    self.orconstraints = []

  def add(self, orconstraint):
    self.orconstraints.append(orconstraint)

  def get(self, index):
    return self.orconstraints[index]

  def __repr__(self):
    return "Constraints: %s" % str(self.orconstraints)

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

  def __repr__(self):
    if self.operator and self.version:
      return "%s (%s %s)" % (self.package, self.operator, self.version)
    else:
      return "%s" % self.package

class VersionNumber():
  def __init__(self, baseURI):
    self.baseURI = baseURI
    self.epoch = None
    self.upstreamVersion = None
    self.debianRevision = None

  def addToGraph(self, graph, packageURI):
    pass # FIXME

  def __str__(self):
    return "VersionNumber(epoch=%d, upstream=%s, debian=%s)" % \
            (self.epoch, self. upstreamVersion, self.debianRevision)
