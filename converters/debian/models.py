# -*- coding: utf8 -*-

import re
import urllib
import logging

from debian_bundle.changelog import Version
from rdflib import Literal

from errors import IndividualNotFoundError
from decorators import checklang


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


class Labelable():
  def labelAsLiteral(self, lang):
    return Literal(self.asLabel(lang), lang=lang)


class UnversionedSourcePackage(BaseUnversionedPackage, Labelable):
  AVAILABLE_LANGS = ('en',)

  def asURI(self, base):
    return escapeURI(base, "source", self.package)

  @checklang
  def asLabel(self, lang):
    map = {'en': "Unversioned Source"}
    return "%s: %s" % (map[lang], self.package)


class SourcePackage(BasePackage, Labelable):
  AVAILABLE_LANGS = ('en',)

  def asURI(self, base):
    return escapeURI(base, "source", *(self.package, self.version))

  @checklang
  def asLabel(self, lang):
    map = {'en': "Source"}
    return "%s: %s (%s)" % (map[lang], self.package, self.version)


class UnversionedBinaryPackage(BaseUnversionedPackage, Labelable):
  AVAILABLE_LANGS = ('en',)

  def asURI(self, base):
    return escapeURI(base, "binary", self.package)

  @checklang
  def asLabel(self, lang):
    return "Unversioned Binary: %s" % (self.package)


class BinaryPackage(BasePackage, Labelable):
  AVAILABLE_LANGS = ('en',)

  def asURI(self, base):
    return escapeURI(base, "binary", *(self.package, self.version))

  @checklang
  def asLabel(self, lang):
    map = {'en': "Binary"}
    return "%s: %s (%s)" % (map[lang], self.package, self.version)


class BinaryPackageBuild(Labelable):
  AVAILABLE_LANGS = ('en',)

  def __init__(self, ancestor = None):
    self.ancestor = ancestor  # Cycles are OK in Python! :)

  def asURI(self, base):
    return escapeURI(base, "binary",\
            *(self.ancestor.package, self.ancestor.version, self.architecture))

  @checklang
  def asLabel(self, lang):
    map = {'en': "BinaryBuild"}
    return "%s: %s (%s) [%s]" % \
            (map[lang], self.ancestor.package, self.ancestor.version, self.architecture)


class VersionNumber(Version, Labelable):
  AVAILABLE_LANGS = ('en',)

  def asURI(self, base):
    return escapeURI(base, "version", str(self))

  @checklang
  def asLabel(self, lang):
    map = {'en': "Version"}
    return "%s: %s" % (map[lang], str(self))


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


class Constraint(Labelable):
  AVAILABLE_LANGS = ('en',)

  def __init__(self):
    self.package = None
    self.operator = None
    self.version = None
    self.exceptin = []
    self.onlyin = []

  def asURI(self, base):
    postfix = str(self.package)
    if self.operator and self.version:
      postfix = postfix + " %s %s" % (self.operatorAsURI(self.operator), self.version)

    for arch in self.exceptin:
      postfix = postfix + " ExceptIn_%s" % arch.name

    for arch in self.onlyin:
      postfix = postfix + " OnlyIn_%s" % arch.name

    return escapeURI(base, "constraint", postfix)

  @checklang
  def asLabel(self, lang):
    map = {'en': "Constraint"}
    label = "%s: %s" % (map[lang], self.package)
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

  def operatorAsURI(self, op):
    d = {'>>': "StrictlyLater",\
     '>=': "LaterOrEqual",\
     '>': "LaterOrEqual",\
     '=': "Equal",\
     '<': "EarlierOrEqual",\
     '<=': "EarlierOrEqual",\
     "<<": "StrictlyEarlier"}

    if op in d:
      return d[op]
    else:
      raise Exception("Unable to lookup operator %s" % op)


class File(Labelable):
  AVAILABLE_LANGS = ('en',)
  
  def __init__(self, name, md5sum, size, ancestor = None):
    self.name = name
    self.md5sum = md5sum
    self.size = size
    self.ancestor = ancestor

  def asURI(self, base):
    return escapeURI(base, "path", *(self.ancestor.path, self.name))

  @checklang
  def asLabel(self, lang):
    map = {'en': "File"}
    return "%s: %s" % (map[lang], self.name)

  def __str__(self):
    return "%s %s %s" % (self.md5sum, self.size, self.name)

  def __eq__(self, other):
    return self.md5sum.__eq__(other.md5sum)


class Directory(Labelable):
  AVAILABLE_LANGS = ('en',)
  
  def __init__(self, path):
    self.path = path

  @checklang
  def asLabel(self, lang):
    map = {'en': "Directory"}
    return "%s: %s" % (map[lang], self.path)

  def asURI(self, base):
    return escapeURI(base, "path", self.path)

  def __eq__(self, other):
    return self.path.__eq__(other.path)


class Tag(Labelable):
  AVAILABLE_LANGS = ('en',)

  def __init__(self, facet, tag):
    self.facet = facet
    self.tag = tag

  def asURI(self, base):
    return escapeURI(base, "tag", *(self.facet, self.tag))

  @checklang
  def asLabel(self, lang):
    map = {'en': "Tag"}
    return "%s: %s::%s" % (map[lang], self.facet, self.tag)

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

  @checklang
  def asLabel(self, lang):
    raise Exception("No label available, you should treat \
                     this object as an individual")


class Architecture(SimpleDataHolderResources, Labelable):
  AVAILABLE_LANGS = ('en',)
  INSTANCES = ("all")

  def asURI(self, base):
    return escapeURI(base, "arch", self.name)

  @checklang
  def asLabel(self, lang):
    map = {'en': "Architecture"}
    return "%s: %s" % (map[lang], self.name)

  def hasIndividual(self):
    return self.name in self.INSTANCES


class Section(SimpleDataHolderResources, Labelable):
  AVAILABLE_LANGS = ('en',)

  def asURI(self, base):
    return escapeURI(base, "section", self.name)

  @checklang
  def asLabel(self, lang):
    map = {'en': "Section"}
    return "%s: %s" % (map[lang], self.name)


class BaseBox():
  @classmethod
  def get(cls, name):
    if name in cls._I:
      return cls._I[name]
    else:
      raise IndividualNotFoundError(name)


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


class Contributor(Labelable):
  AVAILABLE_LANGS = ('en',)

  def __init__(self, name, email):
    self.name = name
    self.email = email

  def rdfType(self):
    return "Agent"

  def asURI(self, base):
    return escapeURI(base, "contributor", self.email)

  @checklang
  def asLabel(self, lang):
    map = {'en': "Contributor"}
    return "%s: %s" % (map[lang], self.email)

  def __str__(self):
    return "%s <%s>" % (self.name, self.email)


class Human(Contributor, Labelable):
  AVAILABLE_LANGS = ('en',)

  def __init__(self, name, email):
    Contributor.__init__(self, name, email)

  def asURI(self, base):
    return escapeURI(base, "people", self.email)

  @checklang
  def asLabel(self, lang):
    map = {'en': "Human"}
    return "%s: %s" % (map[lang], self.email)

  def rdfType(self):
    return "Person"

  def isTeam(self):
    return False


class Team(Contributor, Labelable):
  AVAILABLE_LANGS = ('en',)

  def __init__(self, name, email):
    Contributor.__init__(self, name, email)

  def asURI(self, base):
    return escapeURI(base, "team", self.email)

  @checklang
  def asLabel(self, lang):
    map = {'en': "Team"}
    return "%s: %s" % (map[lang], self.email)

  def rdfType(self):
    return "Group"

  def isTeam(self):
    return True


class Repository(Labelable):
  AVAILABLE_LANGS = ('en',)

  def __init__(self, browser, uri):
    self.browser = browser
    self.uri = uri

  @checklang
  def asLabel(self, lang):
    map = {'en': "Repository"}
    return "%s: %s" % (map[lang], self.uri) if self.uri else map[lang]

  def rdfType(self):
    return "Repository"

  def __str__(self):
      return "Repository: <%s> <%s>" % (self.uri, self.browser)


class ArchRepository(Repository):
  def rdfType(self):
    return "ArchRepository"


class BzrRepository(Repository):
  def rdfType(self):
    return "BazaarRepository"


class CvsRepository(Repository):
  def rdfType(self):
    return "CVSRepository"


class DarcsRepository(Repository):
  def rdfType(self):
    return "DarcsRepository"


class GitRepository(Repository):
  def rdfType(self):
    return "GitRepository"


class HgRepository(Repository):
  def rdfType(self):
    return "HgRepository"


class SvnRepository(Repository):
  def rdfType(self):
    return "SVNRepository"

# Tools

def guessRole(name, email):
  if teamRating(name, email) > humanRating(name, email) + 1: # FIXME?
    logging.debug("Looks like %s is a team" % email)
    return Team(None if not name else name, email)
  else:
    logging.debug("Looks like %s is a human" % email)
    return Human(None if not name else name, email)

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

def escapeURI(base, prefix, *args):
  uri = prefix
  for element in args:
    uri = "%s/%s" % (uri, element)

  return "%s/%s" % (base, urllib.quote_plus(uri, '/'))
