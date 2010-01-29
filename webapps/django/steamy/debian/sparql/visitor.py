# -*- coding: utf-8 -*-
#
# Nacho Barrientos Arias <nacho@debian.org>
#
# License: MIT

from debian.sparql.miniast import *

from debian.config import SPARQL_PREFIXES as PREFIX

class QueryStringVisitor():
    def visit(self, node, *args):
        className = node.__class__.__name__
        implementation = getattr(self, 'visit_' + className)
        return implementation(node, *args)

    def visit_Optional(self, node):
        return "OPTIONAL { %s } ." % self.visit(node.stmt)

    def visit_Variable(self, node):
        return "?%s" % str(node)

    def visit_URIRef(self, node):
        return "<%s>" % str(node)

    def visit_Literal(self, node):
        return '"%s"' % str(node)

    def visit_Limit(self, node):
        return "LIMIT %s" % node.value

    def visit_Offset(self, node):
        return "OFFSET %s" % node.value

    def visit_Orderby(self, node):
        return "ORDER BY %s" % self.visit(node.variable)

    def visit_Triple(self, node):
        out = [self.visit(node.subject), " ", self.visit(node.property), " ",\
                self.visit(node.object), "."]
        return ''.join(out)

    def visit_Optional(self, node):
        triples = [self.visit(triple) for triple in node.stmts]
        return "OPTIONAL{%s}" % ''.join(triples)

    def visit_Filter(self, node):
        return "FILTER(%s)" % self.visit(node.expr)

    def visit_BinaryExpression(self, node):
        return "%s%s%s" % (self.visit(node.lhs), node.operator,\
                            self.visit(node.rhs))

    def visit_UnaryExpression(self, node):
        return "%s%s" % (node.operator, self.visit(node.expr))

    def visit_FunCall(self, node):
        args = [self.visit(arg) for arg in node.args]
        return "%s(%s)" % (node.function, ','.join(args))

    def visit_Union(self, node):
        strs = []
        for graphpattern in node.graphpatterns:
            merged_graphpattern = ''.join([self.visit(triple) for triple in graphpattern])
            strs.append(merged_graphpattern)
        return '{' + '}UNION{'.join(strs) + '}'

    def visit_SelectQuery(self, node, add_prefixes=False):
        prefix = PREFIX if add_prefixes else ""
        select = "SELECT DISTINCT" if node.distinct else "SELECT"
        variables = ''.join(map(self.visit, node.variables))
        ffrom = " FROM %s" % self.visit(node.fromgraph) if node.fromgraph is not None else ""
        where = ''.join(map(self.visit, node.whereclause.stmts))
        modifiers = ' '.join(map(self.visit, node.modifiers))
        orderby = "%s " % self.visit(node.orderby) if node.orderby else ""
        query = [prefix, select, variables, ffrom, " WHERE{", where, "}", orderby, modifiers] 
        return ''.join(query)

    # Tools

    def visit_str(self, node):
        return node

    def visit_unicode(self, node):
        return node
