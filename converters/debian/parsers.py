import re

from debian_bundle.changelog import Version

from models import *
from errors import MissingMandatoryFieldException, ParsingException
from decorators import required, optional

class BaseParser():
  def __init__(self):
    pass

  # Common Fields

  @required('Version')
  def parseVersion(self, raw):
    return self.parseVersionNumber(raw['Version'])

  @required('Package')
  def parsePackage(self, raw):
    return raw['Package']

  @required('Section')
  def parseSection(self, raw):
    return Section(raw['Section'])

  @optional('Priority')
  def parsePriority(self, raw):
    return Priority(raw['Priority'])

  @optional('Homepage')
  def parseHomepage(self, raw):
    return raw['Homepage']

  # Tools

  def parseVersionNumber(self, raw):
    return VersionNumber(raw.strip())

  def parseConstraints(self, raw):
    constraints = Constraints()
    orconstraints = re.split(",\s*", raw)

    for orconstraint in orconstraints:
      constraints.add(self.parseOrConstraint(orconstraint))

    return constraints

  def parseOrConstraint(self, raw):
    orconstraint = OrConstraint()
    constraints = re.split("\s*\|\s*", raw)

    for constraint in constraints:
      orconstraint.add(self.parseConstraint(constraint))

    return orconstraint

  def parseConstraint(self, raw):
    constraint = Constraint()
    # Assuming constraint comes from source in good shape. Validation
    # is not necessary.
    regex = re.compile(\
      r"(?P<package>[-a-z0-9+.]+)(\s\((?P<operator>\S{1,2})\s(?P<version>\S+?)\))?(\s\[(?P<arches>.+)\])?")
    
    match = regex.match(raw.strip())

    if match and match.group('package'):
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
    else:
      raise ParsingException("parseConstraint", raw)

    return constraint

  def parseTags(self, raw):
    split = raw.split(", ") # FIXME
    regex = re.compile(\
      r"(?P<facet>[a-zA-Z0-9-]+)::(\{(?P<tags>\S+)\}|(?P<tag>[a-zA-Z0-9-:]+))")
    tags = []

    for rtag in split:
      match = regex.match(rtag)
      if match and match.group('facet'):
        facet = match.group('facet')
        if match.group('tag'):
          tags.append(Tag(facet, match.group('tag')))
        elif match.group('tags'):
          for t in match.group('tags').split(","):
            tags.append(Tag(facet, t))
      else:
        raise ParsingException("parseTags", raw)

    return tags

  def parseContributor(self, raw):
    regex = re.compile(r"(?P<name>.*?)\s*\<(?P<email>\S+)\>")
    match = regex.match(raw)

    if match and match.group("name") and match.group("email"):
      return guessRole(match.group("name"), match.group("email"))
    else:
      raise ParsingException("parseContributor", raw)

  def parseContributors(self, raw):
    split = re.split(",\s*", raw)
    contributors = []

    for contributor in split:
      contributors.append(self.parseContributor(contributor))

    return contributors
    

class SourcesParser(BaseParser):
  def __init__(self):
    pass

  def parseSourcePackage(self, raw):
    sourcePackage = SourcePackage()
    sourcePackage.package = self.parsePackage(raw)
    sourcePackage.binary = self.parseBinary(raw)
    sourcePackage.version = self.parseVersion(raw)
    sourcePackage.buildDepends = self.parseBuildDepends(raw)
    sourcePackage.buildDependsIndep = self.parseBuildDependsIndep(raw)
    sourcePackage.architecture = self.parseArchitecture(raw)
    sourcePackage.directory = self.parseDirectory(raw)
    sourcePackage.files = self.parseFiles(raw, sourcePackage.directory)
    sourcePackage.priority = self.parsePriority(raw)
    sourcePackage.section = self.parseSection(raw)
    sourcePackage.maintainer = self.parseMaintainer(raw)
    sourcePackage.uploaders = self.parseUploaders(raw)
    sourcePackage.homepage = self.parseHomepage(raw)
    return sourcePackage

  def parseBinary(self, raw):
    return [BinaryPackageLite(bin, self.parseVersionNumber(raw['Version'])) \
                for bin in re.split(",\s*", raw['Binary'])] # FIXME

  @required('Architecture')
  def parseArchitecture(self, raw):
    return [Architecture(arch) for arch in raw['Architecture'].split()]
    
  @optional('Build-Depends')
  def parseBuildDepends(self, raw):
    return self.parseConstraints(raw['Build-Depends'])
 
  @optional('Build-Depends-Indep')
  def parseBuildDependsIndep(self, raw):
    return self.parseConstraints(raw['Build-Depends-Indep'])

  @required('Files')
  def parseFiles(self, raw, dir):
    return [File(d['name'], d['md5sum'], d['size'], dir) for d in raw['Files']]

  @required('Directory')
  def parseDirectory(self, raw):
    return Directory(raw['Directory'])

  @required('Maintainer')
  def parseMaintainer(self, raw):
    return self.parseContributor(raw['Maintainer'])

  @optional('Uploaders')
  def parseUploaders(self, raw):
    return self.parseContributors(raw['Uploaders'])

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
    binaryPackage.build = self.parseBinaryPackageBuild(raw, binaryPackage)
    binaryPackage.filename = self.parseFilename(raw)
    binaryPackage.tag = self.parseTag(raw)
    binaryPackage.priority = self.parsePriority(raw)
    binaryPackage.section = self.parseSection(raw)
    return binaryPackage

  def parseBinaryPackageBuild(self, raw, ancestor):
    binaryPackageBuild = BinaryPackageBuild(ancestor)
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

  @required('Architecture')
  def parseArchitecture(self, raw):
    return Architecture(raw['Architecture'])

  @required('Installed-Size')
  def parseInstalledSize(self, raw):
    return raw['Installed-Size']

  @required('Filename')
  def parseFilename(self, raw):
    split = raw['Filename'].rsplit("/", 1)
    return File(split[1], raw['MD5sum'], raw['Size'], Directory(split[0]))

  @optional('Tag') # FIXME
  def parseTag(self, raw):
    return self.parseTags(raw['Tag'])
