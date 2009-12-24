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
    regex = re.compile(\
      r"(?P<package>\S+)( \((?P<operator>\S+) (?P<version>\S+)\))?( \[(?P<arches>.+)\])?")
    
    match = regex.match(raw.strip())

    constraint.package = match.group('package')

    if match.group('operator') and match.group('version'):
      constraint.operator = match.group('operator')
      constraint.version = self.parseVersionNumber(match.group('version'))

    if match.group('arches'):
      split = match.group('arches').split()
      for arch in split:
        if arch.startswith("!"):
          constraint.exceptin.append(Architecture(arch[1:]))
        else:
          constraint.onlyin.append(Architecture(arch))

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

  @mandatory('Architecture')
  def parseArchitecture(self, raw):
    arches = []
    for arch in raw['Architecture'].split():
      arches.append(Architecture(arch.strip()))
    
    return arches


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
