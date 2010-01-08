import re

from debian_bundle.changelog import Version

from models import *
from errors import ParserError
from errors import PackageDoesNotMatchRegularExpression
from decorators import required, optional


class BaseParser():
  def __init__(self, opts):
    self.opts = opts

  # Common Fields

  @required('Version')
  def parseVersion(self, raw):
    return self.parseVersionNumber(raw['Version'])

  @required('Package')
  def parsePackage(self, raw):
    return raw['Package']

  @optional('Section')
  def parseSection(self, raw):
    return Section(raw['Section'])

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
    regex = re.compile(\
      r"(?P<package>[-a-zA-Z0-9+.]+)(\s\((?P<operator>\S{1,2})\s(?P<version>\S+?)\))?(\s\[(?P<arches>.+)\])?")
    
    match = regex.match(raw.strip())

    if match and match.group('package'):
      constraint.package = UnversionedBinaryPackage(match.group('package'))

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
      raise ParserError("parseConstraint", raw)

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
        raise ParserError("parseTags", raw)

    return tags

  def parseContributor(self, raw):
    regex = re.compile(r"(?P<name>.*?)\s*\<(?P<email>\S+)\>")
    match = regex.match(raw)

    if match and match.group("name") and match.group("email"):
      return guessRole(match.group("name"), match.group("email"))
    else:
      raise ParserError("parseContributor", raw)

  def parseContributors(self, raw):
    split = re.split(",\s*", raw)
    contributors = []

    for contributor in split:
      contributors.append(self.parseContributor(contributor))

    return contributors

  def parseArea(self, raw):
    regex = re.compile(r"^(pool|dists/[a-z]+)/(?P<area>(main|non-free|contrib))/.+?/.+?")
    match = regex.match(raw)

    if match and match.group("area"):
      return AreaBox.get(match.group("area"))
    else:
      raise ParserError("parseArea", raw)

  def parseVcs(self, raw):
    browser = None
    if 'Vcs-Browser' in raw:
      browser = raw['Vcs-Browser']

    if 'Vcs-Git' in raw:
      return GitRepository(browser, raw['Vcs-Git'])
    elif 'Vcs-Svn' in raw:
      return SvnRepository(browser, raw['Vcs-Svn'])
    elif 'Vcs-Bzr' in raw:
      return BzrRepository(browser, raw['Vcs-Bzr'])
    elif 'Vcs-Darcs' in raw:
      return DarcsRepository(browser, raw['Vcs-Darcs'])
    elif 'Vcs-Hg' in raw:
      return HgRepository(browser, raw['Vcs-Hg'])
    elif 'Vcs-Cvs' in raw:
      return CvsRepository(browser, raw['Vcs-Cvs'])
    elif 'Vcs-Arch' in raw:
      return ArchRepository(browser, raw['Vcs-Arch'])
    elif 'Vcs-Mtn' in raw:
      return Repository(browser, raw['Vcs-Mtn'])

    if browser:
      return Repository(browser, None)
    else:
      return None


class SourcesParser(BaseParser):
  def parseSourcePackage(self, raw):
    sourcePackage = SourcePackage(self.parsePackage(raw), self.parseVersion(raw))

    if self.opts.regex:
      if not self.opts.cRegex.match(sourcePackage.package):
        raise PackageDoesNotMatchRegularExpression(sourcePackage.package)
    
    sourcePackage.binary = self.parseBinary(raw)
    sourcePackage.buildDepends = self.parseBuildDepends(raw)
    sourcePackage.buildDependsIndep = self.parseBuildDependsIndep(raw)
    sourcePackage.buildConflicts = self.parseBuildConflicts(raw)
    sourcePackage.buildConflictsIndep = self.parseBuildConflictsIndep(raw)
    sourcePackage.architecture = self.parseArchitecture(raw)
    (sourcePackage.directory, sourcePackage.area) = self.parseDirectory(raw)
    sourcePackage.files = self.parseFiles(raw, sourcePackage.directory)
    sourcePackage.priority = self.parsePriority(raw)
    sourcePackage.section = self.parseSection(raw)
    sourcePackage.maintainer = self.parseMaintainer(raw)
    sourcePackage.uploaders = self.parseUploaders(raw)
    sourcePackage.homepage = self.parseHomepage(raw)
    sourcePackage.dmUploadAllowed = self.parseDmUploadAllowed(raw)
    sourcePackage.vcs = self.parseVcs(raw)
    sourcePackage.format = self.parseFormat(raw)
    sourcePackage.standardsVersion = self.parseStandardsVersion(raw)
    sourcePackage.unversionedSource = \
                  UnversionedSourcePackage(sourcePackage.package)
    return sourcePackage

  def parseBinary(self, raw):
    return [BinaryPackage(bin, self.parseVersionNumber(raw['Version'])) \
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

  @optional('Build-Conflicts')
  def parseBuildConflicts(self, raw):
    return self.parseConstraints(raw['Build-Conflicts'])
  
  @optional('Build-Conflicts-Indep')
  def parseBuildConflictsIndep(self, raw):
    return self.parseConstraints(raw['Build-Conflicts-Indep'])

  @required('Files')
  def parseFiles(self, raw, dir):
    return [File(d['name'], d['md5sum'], d['size'], dir) for d in raw['Files']]

  @required('Directory')
  def parseDirectory(self, raw):
    return (Directory(raw['Directory']), self.parseArea(raw['Directory']))

  @required('Maintainer')
  def parseMaintainer(self, raw):
    return self.parseContributor(raw['Maintainer'])

  @optional('Uploaders')
  def parseUploaders(self, raw):
    return self.parseContributors(raw['Uploaders'])

  @optional('Priority')
  def parsePriority(self, raw):
    return PriorityBox.get(raw['Priority'])

  @optional('Format')
  def parseFormat(self, raw):
    return raw['Format']

  @optional('Standards-Version')
  def parseStandardsVersion(self, raw):
    return raw['Standards-Version']

  @optional('Dm-Upload-Allowed')
  def parseDmUploadAllowed(self, raw):
    return True


class PackagesParser(BaseParser):
  def parseBinaryPackage(self, raw):
    binaryPackage = BinaryPackage(self.parsePackage(raw), self.parseVersion(raw))

    if self.opts.regex:
      if not self.opts.cRegex.match(binaryPackage.package):
        raise PackageDoesNotMatchRegularExpression(binaryPackage.package)

    binaryPackage.depends = self.parseDepends(raw)
    binaryPackage.recommends = self.parseRecommends(raw)
    binaryPackage.preDepends = self.parsePreDepends(raw)
    binaryPackage.suggests = self.parseSuggests(raw)
    binaryPackage.breaks = self.parseBreaks(raw)
    binaryPackage.conflicts = self.parseConflicts(raw)
    binaryPackage.provides = self.parseProvides(raw)
    binaryPackage.replaces = self.parseReplaces(raw)
    binaryPackage.enhances = self.parseEnhances(raw)
    binaryPackage.architecture = self.parseArchitecture(raw)
    binaryPackage.build = self.parseBinaryPackageBuild(raw, binaryPackage)
    binaryPackage.filename = self.parseFilename(raw)
    binaryPackage.tag = self.parseTag(raw)
    binaryPackage.priority = self.parsePriority(raw)
    binaryPackage.section = self.parseSection(raw)
    binaryPackage.essential = self.parseEssential(raw)
    binaryPackage.buildEssential = self.parseBuildEssential(raw)
    (binaryPackage.sdescription, binaryPackage.ldescription) = self.parseDescription(raw)
    binaryPackage.unversionedBinary = \
                  UnversionedBinaryPackage(binaryPackage.package)
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

  @optional('Pre-Depends')
  def parsePreDepends(self, raw):
    return self.parseConstraints(raw['Pre-Depends'])

  @optional('Suggests')
  def parseSuggests(self, raw):
    return self.parseConstraints(raw['Suggests'])

  @optional('Breaks')
  def parseBreaks(self, raw):
    return self.parseConstraints(raw['Breaks'])

  @optional('Conflicts')
  def parseConflicts(self, raw):
    return self.parseConstraints(raw['Conflicts'])

  @optional('Provides')
  def parseProvides(self, raw):
    return self.parseConstraints(raw['Provides'])

  @optional('Replaces')
  def parseReplaces(self, raw):
    return self.parseConstraints(raw['Replaces'])

  @optional('Enhances')
  def parseEnhances(self, raw):
    return self.parseConstraints(raw['Enhances'])

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

  @optional('Tag')
  def parseTag(self, raw):
    return self.parseTags(raw['Tag'])

  @required('Priority')
  def parsePriority(self, raw):
    return PriorityBox.get(raw['Priority'])

  @optional('Essential')
  def parseEssential(self, raw):
    return True

  @optional('Build-Essential')
  def parseBuildEssential(self, raw):
    return True
  
  @required('Description')
  def parseDescription(self, raw):
    split = raw['Description'].split("\n",1)
    if len(split) == 1:
      split.append(None)
    return tuple(split)
