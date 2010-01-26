# -*- coding: utf-8 -*-
#
# Nacho Barrientos Arias <nacho@debian.org>
#
#

class W3CValidatorError(Exception):
    pass

class W3CValidatorUnableToConnectError(W3CValidatorError):
    def __str__(self):
        return "Unable to connect to W3C markup validation service"

class W3CValidatorUnexpectedValidationResultError(W3CValidatorError):
    def __str__(self):
        return "W3C validation service returned an unexpected result"

class W3CValidatorUnexpectedStatusCodeError(W3CValidatorError):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return "W3C validation service returned an unexpected status code"

class RSSParsingError(Exception):
    def __init__(self, uri):
        self.uri = uri

    def __str__(self):
        return "'%s' won't be processed due to an undefined reason" % self.uri

class RSSParsingFeedUnavailableError(RSSParsingError):
    def __str__(self):
        return "'%s' not available (Either NOT_FOUND or GONE returned), skipping..." % self.uri

class RSSParsingFeedMalformedError(RSSParsingError):
    def __str__(self):
        return "'%s' is not well-formed XML, skipping..." % self.uri

class RSSParsingUnparseableVersionError(RSSParsingError):
    def __init__(self, version, *args, **kwargs):
        self.version = version
        RSSParsingError.__init__(self, *args, **kwargs)

    def __str__(self):
        return "'%s': untransformable feed version '%s'" % (self.uri, self.version)

class RSSParsingXSLTError(RSSParsingError):
    def __str__(self):
        return "XSL transformation failed"

class RDFDiscoveringError(Exception):
    def __init__(self, uri):
        self.uri = uri

    def __str__(self):
        return "'%s' won't be processed due to an undefined reason" % self.uri

class RDFDiscoveringBrokenLinkError(RDFDiscoveringError):
    def __str__(self):
        return "'%s' is not available, skipping..." % self.uri

class RDFDiscoveringMalformedError(RDFDiscoveringError):
    def __init__(self, reason, *args, **kwargs):
        self.reason = reason
        RDFDiscoveringError.__init__(self, *args, **kwargs)

    def __str__(self):
        return "'%s' malformed (SAX/Rdflib parser error) (%s), skipping..." % \
        (self.uri, self.reason)
