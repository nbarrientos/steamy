<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:dc="http://purl.org/dc/elements/1.1/"
                xmlns:dct="http://purl.org/dc/terms/"
                xmlns:atomrdf="http://djpowell.net/schemas/atomrdf/0.3/"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                xmlns:rss="http://purl.org/rss/1.0/"
                
                exclude-result-prefixes="dc dct rss"
                >
  
  <!--
      DEFINES MODES:
      mode="copyXhtml" match="*"

      DEFINES NAMES:
      name="FreePerson"
      name="AmbiguousRSS2Text"
      name="XhtmlRSS2Text"
      name="getElementLang"
      name="getRss2Lang"
      name="getRss1Lang"
      
      CALLS:
      name="getXmlLang"
  -->

  <xsl:import href="baselangutils.xsl" />

  <!-- avoids so many namespace declarations being copied through -
       we'll still use xsl:copy-of for xml content though, cause it
       might contain PIs or something that we don't want to throw away
       -->
  <xsl:template mode="copyXhtml" match="*">
    <xsl:element namespace="{namespace-uri()}" name="{local-name()}">
      <xsl:for-each select="@*">
        <xsl:attribute name="{local-name(.)}" namespace="{namespace-uri(.)}">
          <xsl:value-of select="." />
        </xsl:attribute>
      </xsl:for-each>
      <xsl:apply-templates mode="copyXhtml" />
    </xsl:element>
  </xsl:template>


  <xsl:template name="FreePerson">
    <atomrdf:Person>
      <xsl:attribute name="rdf:nodeID">
        <xsl:text>person-</xsl:text>
        <xsl:value-of select="generate-id(.)" />
      </xsl:attribute>

      <xsl:variable name="personEmail">
        <xsl:choose>
          <!-- form: email@host (full name) -->
          <xsl:when test="substring-before(text(), '(') != ''">
            <xsl:value-of select="normalize-space(substring-before(text(), '('))" />
          </xsl:when>

          <!-- form: full name <email@host> -->
          <xsl:when test="substring-before(text(), '&lt;') != ''">
            <xsl:value-of select="substring-before(substring-after(text(), '&lt;'), '>')" />
          </xsl:when>

          <!-- form: email@host -->
          <xsl:when test="substring-before(text(), '@') != ''">
            <xsl:value-of select="normalize-space(text())" />
          </xsl:when>

          <!-- form: full name -->
          <xsl:otherwise /> <!-- no email -->
        </xsl:choose>
      </xsl:variable>

      <xsl:variable name="personName">
        <xsl:choose>
          <!-- form: email@host (full name) -->
          <xsl:when test="substring-before(text(), '(') != ''">
            <xsl:value-of select="substring-before(substring-after(text(), '('), ')')" />
          </xsl:when>

          <!-- form: full name <email@host> -->
          <xsl:when test="substring-before(text(), '&lt;') != ''">
            <xsl:value-of select="normalize-space(substring-before(text(), '&lt;'))" />
          </xsl:when>

          <!-- form: email@host -->
          <xsl:when test="substring-before(text(), '@') != ''" /> <!-- no name -->

          <!-- form: full name -->
          <xsl:otherwise>
            <xsl:value-of select="normalize-space(text())" />
          </xsl:otherwise>
        </xsl:choose>
      </xsl:variable>

      <!-- process email -->
      <xsl:if test="$personEmail != ''">
        <atomrdf:personEmail>
          <xsl:value-of select="$personEmail" />
        </atomrdf:personEmail>
      </xsl:if>

      <!-- process name -->
      <xsl:if test="$personName != ''">
        <atomrdf:personName>
          <!-- add the xml:lang of atom:name -->
          <xsl:variable name="lang">
            <xsl:call-template name="getElementLang">
              <xsl:with-param name="default" select="$contentlang" />
            </xsl:call-template>
          </xsl:variable>
          <xsl:if test="$lang != ''">
            <xsl:attribute name="xml:lang">
              <xsl:value-of select="$lang" />
            </xsl:attribute>
          </xsl:if>
          <xsl:value-of select="$personName" />
        </atomrdf:personName>
      </xsl:if>

    </atomrdf:Person>
  </xsl:template>



  <!-- process text and html text constructs -->
  <xsl:template name="AmbiguousRSS2Text">
    <xsl:param name="type" select="''" />
    <xsl:param name="nodeId" select="''" />

    <!-- RSS ambiguity: could be HtmlText or PlainText, so just use Text -->   
    <atomrdf:Text>

      <!-- set nodeId if a shared Text node (used by atom:rights only) -->
      <xsl:if test="$nodeId != ''">
        <xsl:attribute name="rdf:nodeID">
          <xsl:value-of select="$nodeId" />
        </xsl:attribute>
      </xsl:if>

      <!-- add explicit type -->
      <xsl:if test="$type != ''">
        <rdf:type>
          <xsl:attribute name="rdf:resource">
            <xsl:value-of select="$NS_ATOMRDF" />
            <xsl:value-of select="$type" />
          </xsl:attribute>
        </rdf:type>
      </xsl:if>

      <!-- preserve xml:lang context -->
      <xsl:variable name="lang">
        <xsl:call-template name="getElementLang">
          <xsl:with-param name="default" select="$contentlang" />
        </xsl:call-template>
      </xsl:variable>
      <xsl:if test="$lang != ''">
        <atomrdf:contentLang>
          <xsl:call-template name="getElementLang">
            <xsl:with-param name="default" select="$contentlang" />
          </xsl:call-template>
        </atomrdf:contentLang>
      </xsl:if>

      <!-- preserve xml:base, in-case this is HtmlText -->
      <xsl:if test="not($contentbase='')">
        <atomrdf:contentBase rdf:resource="{$contentbase}" />
      </xsl:if>

      <atomrdf:textValue>
        <xsl:value-of select="text()" />
      </atomrdf:textValue>

    </atomrdf:Text>
  </xsl:template>

  <!-- process xhtml text constructs -->
  <xsl:template name="XhtmlRSS2Text">
    <atomrdf:XhtmlText>

      <!-- preserve xml:lang context -->
      <xsl:variable name="lang">
        <xsl:call-template name="getElementLang">
          <xsl:with-param name="default" select="$contentlang" />
        </xsl:call-template>
      </xsl:variable>
      <xsl:if test="$lang != ''">
        <atomrdf:contentLang>
          <xsl:call-template name="getElementLang">
            <xsl:with-param name="default" select="$contentlang" />
          </xsl:call-template>
        </atomrdf:contentLang>
      </xsl:if>

      <!-- preserve xml:base, in-case this is HtmlText -->
      <xsl:if test="not($contentbase='')">
        <atomrdf:contentBase rdf:resource="{$contentbase}" />
      </xsl:if>

      <atomrdf:xmlValue rdf:parseType="Literal">
        <xsl:apply-templates mode="copyXhtml" />
      </atomrdf:xmlValue>

    </atomrdf:XhtmlText>
  </xsl:template>


  <xsl:template name="getElementLang">
    <xsl:param name="default" select="''" />
    <xsl:variable name="xlang">
      <xsl:call-template name="getXmlLang">
        <xsl:with-param name="element" select="." />
        <xsl:with-param name="default" select="$default" />
      </xsl:call-template>
    </xsl:variable>    
    <xsl:choose>
      <!-- ATOM -->
      <xsl:when test="$xlang != ''">
        <xsl:value-of select="$xlang" />
      </xsl:when>
      <xsl:otherwise>
        <xsl:variable name="lang2">
          <xsl:call-template name="getRss2Lang">
            <xsl:with-param name="default" select="$default" />
          </xsl:call-template>      
        </xsl:variable>
        <xsl:choose>
          <!-- RSS2 -->
          <xsl:when test="$lang2 != ''">
            <xsl:value-of select="$lang2" />
          </xsl:when>
          <xsl:otherwise>
            <!-- RSS1 -->
            <xsl:call-template name="getRss1Lang">
              <xsl:with-param name="default" select="$default" />
            </xsl:call-template>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="getRss2Lang">
    <xsl:param name="default" />
    <xsl:choose>
      <xsl:when test="ancestor::item/language">
        <xsl:value-of select="ancestor::item/language" />
      </xsl:when>
      <xsl:when test="ancestor::item/dc:language">
        <xsl:value-of select="ancestor::item/dc:language" />
      </xsl:when>
      <xsl:when test="/rss/channel/language">
        <xsl:value-of select="/rss/channel/language" />
      </xsl:when>
      <xsl:when test="/rss/channel/dc:language">
        <xsl:value-of select="/rss/channel/dc:language" />
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$default" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="getRss1Lang">
    <xsl:param name="default" select="''" />
    <xsl:choose>
      <xsl:when test="ancestor::rss:item/language">
        <xsl:value-of select="ancestor::rss:item/language" />
      </xsl:when>
      <xsl:when test="ancestor::rss:item/dc:language">
        <xsl:value-of select="ancestor::rss:item/dc:language" />
      </xsl:when>
      <xsl:when test="/rdf:RDF/rss:channel/rss:language">
        <xsl:value-of select="/rss:rss/rss:channel/rss:language" />
      </xsl:when>
      <xsl:when test="/rdf:RDF/rss:channel/dc:language">
        <xsl:value-of select="/rss:rss/rss:channel/dc:language" />
      </xsl:when>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
