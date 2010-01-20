<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:dc="http://purl.org/dc/elements/1.1/"
                xmlns:dct="http://purl.org/dc/terms/"
                xmlns:atomrdf="http://djpowell.net/schemas/atomrdf/0.3/"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                xmlns:rss="http://purl.org/rss/1.0/"
                
                exclude-result-prefixes="dc dct rss"
                >

  <!-- Pluggable extension support for Atom/RDF -->
  <!-- $Id: atom2rdf-16-extensions.xsl,v 1.2 2006/05/18 13:20:00 Dave Exp $ -->


  <!--
      DEFINES MODES:
      mode="extension" match="*"
      mode="generic-extension" match="*"
      mode="pluggable-extension" match="*"
      mode="query-pluggable-extension" match="*"

      DEFINES NAMES:
      name="Extension"

      CALLS:
      name="getXmlBase"
      name="getElementLang"
  -->

  <xsl:import href="atom2rdf-16-texthelp.xsl" />

  <!-- 
       Provides support for pluggable extensions.  If you want to
       specifically support an extension, import a rule that uses
       mode="query-pluggable-extension", and return 'plugin' to use
       your plugin template instead of the generic behaviour, or
       'both' to use both your plugin template and the generic
       behaviour.  Implement your plugin using
       mode="pluggable-extension".
  -->

  <xsl:import href="baselangutils.xsl" />

  <xsl:template mode="extension" match="*">
    <xsl:param name="defaultBehaviour" select="'generic'" />
    <xsl:param name="context" />
    <xsl:param name="format" />

    <xsl:variable name="extensionValue">
      <xsl:variable name="qpe">
        <xsl:apply-templates mode="query-pluggable-extension" select=".">
          <xsl:with-param name="context" select="$context" />
          <xsl:with-param name="format" select="$format" />
        </xsl:apply-templates>
      </xsl:variable>
      <xsl:choose>
        <xsl:when test="$qpe != ''">
          <xsl:value-of select="$qpe" />
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$defaultBehaviour" />
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <xsl:if test="$extensionValue = 'plugin' or $extensionValue = 'both'">
      <xsl:apply-templates mode="pluggable-extension" select=".">
        <xsl:with-param name="context" select="$context" />
        <xsl:with-param name="format" select="$format" />
      </xsl:apply-templates>
    </xsl:if>

    <xsl:if test="$extensionValue = 'passthrough'">
      <xsl:copy-of select="." />
    </xsl:if>
    
    <xsl:if test="$extensionValue = 'generic' or $extensionValue = 'both'">
      <xsl:apply-templates mode="generic-extension" select="." />
    </xsl:if>
  </xsl:template>

  <xsl:template mode="generic-extension" match="*">
    <xsl:call-template name="Extension" />
  </xsl:template>

  <xsl:template mode="pluggable-extension" match="*">
    <!-- won't be called unless query-pluggable-extension is overridden -->
    <xsl:message terminate="yes">   
      Pluggable extension was found using
      mode="query-pluggable-extension", but failed to override,
      mode="pluggable-extension":
      <xsl:value-of select="name(.)" />
    </xsl:message>
  </xsl:template>

  <!-- default behaviour is unset -->
  <xsl:template mode="query-pluggable-extension" match="*" />

  <!-- Extension Construct -->
  <xsl:template name="Extension">

    <atomrdf:extension>
      <atomrdf:Extension rdf:nodeID="ext-{generate-id()}">

        <xsl:choose>
          <!-- We'll treat Simple and Structured Extension constructs
               the same - everybody else will :).  Instead we shall
               differenciate between extensions with mixed content,
               and those without.  Extensions without mixed content
               will get an atomrdf:extensionText property added to
               simplify access to the data.  This will help a superset
               of Simple Extension constructs.
               
               All extensions will still carry the complete XML in
               atomrdf:extensionXML, and the name of the property in
               atomrdf:propertyNS and atomrdf:propertyName.
          -->

          <!-- if mixed content -->
          <xsl:when test="./*">
            <!-- do nothing special -->
          </xsl:when>
          <xsl:otherwise>
            <!-- add the simple text value of the extension -->
            <atomrdf:extensionText>
              <xsl:value-of select="text()" />
            </atomrdf:extensionText>
          </xsl:otherwise>
        </xsl:choose>
        
        <!-- add atomrdf:contentBase -->
        <xsl:variable name="base">
          <xsl:call-template name="getXmlBase">
            <xsl:with-param name="element" select="." />
            <xsl:with-param name="default" select="$contentbase" />
          </xsl:call-template>
        </xsl:variable>

        <xsl:if test="not($base='')">
          <atomrdf:contentBase rdf:resource="{$base}" />
        </xsl:if>

        <!-- add atomrdf:contentLang -->
        <!-- NOTE: because this can be called from Atom or RSS2, try both
             methods of finding the language -->
        <xsl:variable name="lang">
          <xsl:call-template name="getElementLang">
            <xsl:with-param name="default" select="$contentlang" />
          </xsl:call-template>
        </xsl:variable>

        <xsl:if test="$lang != ''">
          <atomrdf:contentLang>
            <xsl:value-of select="$lang" />
          </atomrdf:contentLang>
        </xsl:if>

        <atomrdf:propertyNS>
          <xsl:value-of select="namespace-uri()" />
        </atomrdf:propertyNS>

        <atomrdf:propertyName>
          <xsl:value-of select="local-name()" />
        </atomrdf:propertyName>

        <!-- add full XML content -->
        <atomrdf:extensionXML rdf:parseType="Literal" >
          <!-- include containing element -->
          <!-- remove xml:base and xml:lang, they're processd above -->
          <xsl:copy>
            <xsl:copy-of select="@*[not((name() = 'xml:base') or (name() = 'xml:lang'))]" />
            <!-- NOTE: urgh QNames (tho safe here) why doesn't
                 not(@xml:base) work?? -->
            <xsl:copy-of select="*|text()" /> 
          </xsl:copy>
        </atomrdf:extensionXML>

      </atomrdf:Extension>
    </atomrdf:extension>

  </xsl:template>

</xsl:stylesheet>
