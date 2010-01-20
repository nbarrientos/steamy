#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Nacho Barrientos Arias <nacho@debian.org>
#
# License: MIT

import random

from rdflib.Graph import ConjunctiveGraph

from homepages.namespaces import *


class GraphPool():
  def __init__(self, size, prefix, base):
    self.prefix = "%s/%s" % (base, prefix)
    self.pool = [ConjunctiveGraph() for i in range(int(size))]
    for graph in self.pool:
      graph.bind("deb", DEB)
      graph.bind("xhv", XHV)
      graph.bind("earl", EARL)
      graph.bind("dc", DC)
      graph.bind("content", CONTENT)
      graph.bind("r", R)
      graph.bind("rss", RSS)

  def add_triple(self, triple):
    self.pool[self._random_graphno()].add(triple)

  def merge_graph(self, graph):
    self.pool[self._random_graphno()] += graph

  def count_triples(self):
    return sum([len(i) for i in self.pool])

  def __len__(self):
    return len(self.pool)

  def serialize(self):
    for i in range(len(self.pool)): # I'm sorry :(    
      try:
        f = open("%s-%d.rdf" % (self.prefix, i), "w")
        f.write(self.pool[i].serialize())
        f.close()
      except IOError, e:
        logging.error("Serialization failed: %s (does base dir exist?)", e)

  def _random_graphno(self):
    return int(random.uniform(0, len(self.pool)))
