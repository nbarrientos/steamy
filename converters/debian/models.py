class VersionNumber():
  def __init__(self, raw, baseURI):
    self.raw = raw
    self.baseURI = baseURI
    self.epoch = None
    self.upstreamVersion = None
    self.debianRevision = None

  def getEpoch(self):
    if not self.epoch:
      raise Exception("Still not defined, is the model parsed?")

    return self.epoch

  def parse(self, parser):
    pass # FIXME

  def addToGraph(self, graph):
    pass # FIXME

  def __str__(self):
    return "VersionNumber(epoch=%d, upstream=%s, debian=%s)" % \
            (self.epoch, self. upstreamVersion, self.debianRevision)
