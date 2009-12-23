import re

from debian_bundle.changelog import Version

from models import *
from errors import MissingMandatoryFieldException
from decorators import mandatory, optional

class BaseParser():
  def __init__(self):
    pass

  # Common Fields

  @mandatory('Version')
  def parseVersion(self, raw):
    return self.parseVersionNumber(raw['Version'])

  @mandatory('Package')
  def parsePackage(self, raw):
    return raw['Package']

  # Tools

  def parseVersionNumber(self, raw):
    return VersionNumber(raw.strip())

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
      constraint.version = self.parseVersionNumber(split[2])

    return constraint


class SourcesParser(BaseParser):
  def __init__(self):
    pass

  def parseSourcePackage(self, raw):
    sourcePackage = SourcePackage()
    sourcePackage.package = self.parsePackage(raw)
    sourcePackage.binary = self.parseBinary(raw)
    sourcePackage.version = self.parseVersion(raw)
    return sourcePackage

  def parseBinary(self, raw):
    binaries = []

    for bin in raw['Binary'].split(","):
      binaries.append(BinaryPackageLite(bin.strip(), self.parseVersionNumber(raw['Version'])))

    return binaries


class PackagesParser(BaseParser):
  def __init__(self):
    pass

  def parseBinaryPackage(self, raw):
    binaryPackage = BinaryPackage()
    binaryPackage.package = self.parsePackage(raw)
    binaryPackage.version = self.parseVersion(raw)
    binaryPackage.depends = self.parseDepends(raw)
    binaryPackage.recommends = self.parseRecommends(raw)
    binaryPackage.architecture = self.parseArchitecture(raw)
    binaryPackage.build = self.parseBinaryPackageBuild(raw)
    return binaryPackage

  def parseBinaryPackageBuild(self, raw):
    binaryPackageBuild = BinaryPackageBuild()
    binaryPackageBuild.architecture = self.parseArchitecture(raw)
    binaryPackageBuild.installedSize = self.parseInstalledSize(raw)
    return binaryPackageBuild

  # Fields

  @optional('Depends')
  def parseDepends(self, raw):
    return self.parseConstraints(raw['Depends'])
 
  @optional('Recommends')
  def parseRecommends(self, raw):
    return self.parseConstraints(raw['Recommends'])

  @mandatory('Architecture')
  def parseArchitecture(self, raw):
    return Architecture(raw['Architecture'])

  @mandatory('Installed-Size')
  def parseInstalledSize(self, raw):
    return raw['Installed-Size']
