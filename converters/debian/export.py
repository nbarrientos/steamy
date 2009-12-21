class Triplifier():
  def __init__(self, graph, baseUri):
    self.g = graph
    self.baseUri = baseUri

  def triplifyBinaryPackage(self, package):
    pass # FIXME

class Serializer():
  def __init__(self):
    pass

  def serializeToFile(self, graph, file):
    file.write(graph.serialize(format="pretty-xml"))
