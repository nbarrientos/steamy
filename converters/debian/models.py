import hashlib
import re

from debian_bundle.changelog import Version

from errors import IndividualNotFoundException

class BasePackage():
  def __init__(self, package=None, version=None):
    self.package = package
    self.version = version

  def __str__(self):
    return "%s (%s)" % (self.package, self.version)

class BaseUnversionedPackage():
  def __init__(self, package):
    self.package = package
  
  def __str__(self):
    return self.package

  def __eq__(self, other):
    return self.package.__eq__(other.package)

class UnversionedSourcePackage(BaseUnversionedPackage):
  def asURI(self, base):
    return "%s/source/%s" % (base, self.package)

  def asLabel(self):
    return "Unversioned Source: %s" % (self.package)

class SourcePackage(BasePackage):
  def asURI(self, base):
    return "%s/source/%s/%s" % (base, self.package, self.version)

  def asLabel(self):
    return "Source: %s (%s)" % (self.package, self.version)

class UnversionedBinaryPackage(BaseUnversionedPackage):
  def asURI(self, base):
    return "%s/binary/%s" % (base, self.package)

  def asLabel(self):
    return "Unversioned Binary: %s" % (self.package)

class BinaryPackage(BasePackage):
  def asURI(self, base):
    return "%s/binary/%s/%s" % (base, self.package, self.version)

  def asLabel(self):
    return "Binary: %s (%s)" % (self.package, self.version)

class BinaryPackageBuild():
  def __init__(self, ancestor = None):
    self.ancestor = ancestor # Cycles are OK in Python! :)

  def asURI(self, base):
    return "%s/binary/%s/%s/%s" % \
            (base, self.ancestor.package, self.ancestor.version, self.architecture)

  def asLabel(self):
    return "BinaryBuild: %s (%s) [%s]" % \
            (self.ancestor.package, self.ancestor.version, self.architecture)

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

  def __str__(self):
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

  def __str__(self):
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

  def asLabel(self):
    label = "Constraint: %s" % self.package
    if self.operator and self.version:
      label = label + " (%s %s)" % (self.operator, self.version)

    for arch in self.exceptin:
      label = label + " !%s" % arch.name

    for arch in self.onlyin:
      label = label + " %s" % arch.name

    return label

  def __str__(self):
    if self.operator and self.version:
      return "%s (%s %s)" % (self.package, self.operator, self.version)
    else:
      return "%s" % self.package

class File():
  def __init__(self, name, md5sum, size, ancestor = None):
    self.name = name
    self.md5sum = md5sum
    self.size = size
    self.ancestor = ancestor

  def asURI(self, base):
    return "%s/path/%s/%s" % \
          (base, self.ancestor.path, self.name)

  def asLabel(self):
    return "File: %s" % self.name

  def __str__(self):
    return "%s %s %s" % (self.md5sum, self.size, self.name)

  def __eq__(self, other):
    return self.md5sum.__eq__(other.md5sum)

class Directory():
  def __init__(self, path):
    self.path = path

  def asLabel(self):
    return "Directory: %s" % self.path

  def asURI(self, base):
    return "%s/path/%s" % (base, self.path)

  def __eq__(self, other):
    return self.path.__eq__(other.path)

class Tag():
  def __init__(self, facet, tag):
    self.facet = facet
    self.tag = tag

  def asURI(self, base):
    return "%s/tag/%s/%s" % (base, self.facet, self.tag)

  def asLabel(self):
    return "Tag: %s::%s" % (self.facet, self.tag)

  def __str__(self):
    return "%s::%s" % (self.facet, self.tag)

  def __eq__(self, other):
    return self.facet.__eq__(other.facet) and self.tag.__eq__(other.tag)

class SimpleDataHolder():
  def __init__(self, name):
    self.name = name

  def __str__(self):
    return str(self.name)

class SimpleDataHolderResources(SimpleDataHolder):
  def __eq__(self, other):
    return self.name.__eq__(other.name)

class SimpleDataHolderIndividuals(SimpleDataHolder):
  def asURI(self, base):
    raise Exception("No URI available, you should treat \
                     this object as an individual")

  def asLabel(self):
    raise Exception("No label available, you should treat \
                     this object as an individual")

class Architecture(SimpleDataHolderResources):
  INSTANCES = ("all")

  def asURI(self, base):
    return "%s/arch/%s" % (base, self.name)

  def asLabel(self):
    return "Architecture: %s" % (self.name)

  def hasIndividual(self):
    return self.name in self.INSTANCES

class Section(SimpleDataHolderResources):
  def asURI(self, base):
    return "%s/section/%s" % (base, self.name)

  def asLabel(self):
    return "Section: %s" % (self.name)

class BaseBox():
  @classmethod
  def get(cls, name):
    if name in cls._I:
      return cls._I[name]
    else:
      raise IndividualNotFoundException(name)

class PriorityBox(BaseBox):
  class Priority(SimpleDataHolderIndividuals):
    pass

  _I = {'required': Priority('required'),\
        'important': Priority('important'),\
        'standard': Priority('standard'),\
        'optional': Priority('optional'),\
        'extra': Priority('extra')}

class AreaBox(BaseBox):
  class Area(SimpleDataHolderIndividuals):
    pass

  _I = {'main': Area('main'),\
        'non-free': Area('non-free'),\
        'contrib': Area('contrib')}

class Contributor():
  def __init__(self, name, email):
    self.name = name
    self.email = email

  def asLabel(self):
    return "Contributor: %s <%s>" % (self.name, self.email)

  def __str__(self):
    return "%s <%s>" % (self.name, self.email)

class Human(Contributor):
  def __init__(self, name, email):
    Contributor.__init__(self, name, email)

  def asURI(self, base):
    return "%s/people/%s" % (base, self.name.replace(" ", "_"))

  def asLabel(self):
    return "Human: %s <%s>" % (self.name, self.email)

  def rdfType(self):
    return "Person"

  def isTeam(self):
    return False

class Team(Contributor):
  def __init__(self, name, email):
    Contributor.__init__(self, name, email)

  def asURI(self, base):
    return "%s/team/%s" % (base, self.name.replace(" ", "_"))

  def asLabel(self):
    return "Team: %s <%s>" % (self.name, self.email)

  def rdfType(self):
    return "Group"

  def isTeam(self):
    return True

# Tools

def guessRole(name, email):
  if teamRating(name, email) > humanRating(name, email) + 1: # FIXME?
    return Team(name, email)
  else:
    return Human(name, email)

def teamRating(name, email):
  mailRegexPool = (".*@lists\.alioth\.debian\.org",\
                   ".*@lists\.debian\.org",\
                   ".*@teams\.debian\.net",\
                   ".*-maintainers@.*")
  nameRegexPool = (".*[tT]eam$", ".*[mM]aintainers.*",\
                   ".*([sS]trike|[tT]ask)\s*Force.*",\
                   ".*[gG]roup", ".*[pP]ackagers",\
                   ".*[pP]arty.*", "^Debian.*")

  return computeRating(name, email, mailRegexPool, nameRegexPool)

def humanRating(name, email):
  mailRegexPool = (".*@debian\.org",\
                   ".*@users.alioth.debian.org",\
                   ".*@gmail\.com") # FIXME

  return computeRating(name, email, mailRegexPool, ())

def computeRating(name, email, eregex, nregex):
  rating = 0

  for regex in nregex:
    if re.match(regex, name):
      rating = rating + 1

  for regex in eregex:
    if re.match(regex, email):
      rating = rating + 1

  return rating
