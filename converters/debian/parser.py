import re

from debian_bundle.changelog import Version

from models import *

class Parser():
  def __init__(self):
    pass

  # Full package information

  def parseBinaryPackage(self, raw):
    binaryPackage = BinaryPackage()
    binaryPackage.package = self.parsePackage(raw)
    binaryPackage.version = self.parseVersion(raw)
    binaryPackage.depends = self.parseDepends(raw)
    binaryPackage.recommends = self.parseRecommends(raw)
    return binaryPackage

  # Fields

  def parsePackage(self, raw):
    return raw['Package']

  def parseDepends(self, raw):
    return self.parseConstraints(raw['Depends'])
  
  def parseRecommends(self, raw):
    return self.parseConstraints(raw['Recommends'])

  def parseVersion(self, raw):
    return self.parseVersionNumber(raw['Version'])

  # Tools

  def parseVersionNumber(self, raw):
    return Version(raw.strip())

  def parseConstraints(self, raw):
    constraints = Constraints()
    orconstraints = raw.split(",")

    for orconstraint in orconstraints:
      constraints.add(self.parseOrConstraint(orconstraint))

    return constraints

  def parseOrConstraint(self, raw):
    orconstraint = OrConstraint()
    constraints = raw.strip().split("|")

    for constraint in constraints:
      orconstraint.add(self.parseConstraint(constraint))

    return orconstraint

  def parseConstraint(self, raw):
    constraint = Constraint()
    regex = re.compile("\(|\)")
    split = regex.sub("", raw.strip()).split()

    constraint.package = split[0]

    if len(split) > 1:
      constraint.operator = split[1]
      constraint.version = split[2] #FIXME

    return constraint
