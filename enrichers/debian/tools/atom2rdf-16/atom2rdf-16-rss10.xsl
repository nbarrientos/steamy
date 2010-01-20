<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:atomrdf="http://djpowell.net/schemas/atomrdf/0.3/"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                xmlns:xhtml="http://www.w3.org/1999/xhtml"
                xmlns:dc="http://purl.org/dc/elements/1.1/"
                xmlns:content="http://purl.org/rss/1.0/modules/content/"
                xmlns:rss="http://purl.org/rss/1.0/"
                xmlns:RSS2COMPAT="tag:djpowell.net,2005:ns-rss-compat/"
                xmlns:arlex="http://djpowell.net/schemas/atomrdf-lex/0.1/"
                
                exclude-result-prefixes="rdf dc content rss RSS2COMPAT"
                >

  <!-- RSS 1.0 support for Atom/RDF -->
  <!-- $Id: atom2rdf-16-rss10.xsl,v 1.2 2006/05/18 13:20:00 Dave Exp $ -->

  <!--
NOTES

Part of the problem with mixing Atom and RSS, or even RSS with DC, is
deciding whether all the information needs to be combined, or whether
some properties just hold redundant duplicate information.

Eg: copyright + dc:rights are likely to be redundant;
    link and atom:link are likely to be relevant

-->  
  
  <xsl:import href="atom2rdf-16-common.xsl" />

  <xsl:output method="xml" encoding="utf-8" indent="yes" media-type="application/rdf+xml" />

  <!-- FUTURE perhaps allow option of per-site preprocessing stylesheets -->

  <xsl:variable name="NS_RSS10" select="'http://purl.org/rss/1.0/'" />

  <!-- RSS 1.0 -->
  <xsl:template match="/rdf:RDF">
    <xsl:apply-templates select="/rdf:RDF/rss:channel" />
  </xsl:template>

  <xsl:template match="/rdf:RDF/rss:channel">
    <rdf:RDF>
      <xsl:call-template name="RDFFeed" />
      <xsl:call-template name="RDFLex" />
    </rdf:RDF>
  </xsl:template>

  <xsl:template mode="feed" match="rss:items">
    <!-- ignore the item list for a moment, process it as part of the
         entry processing -->
  </xsl:template>

  <xsl:template name="RDFLex">
    <arlex:State>
      <arlex:feedInstance rdf:nodeID="fi-{generate-id()}" />
      <arlex:entryInstances rdf:parseType="Collection">
        <xsl:for-each select="/rdf:RDF/rss:channel/rss:items/rdf:Seq/rdf:li">
          <xsl:variable name="itemUri" select="@rdf:resource" />
          <atomrdf:EntryInstance rdf:nodeID="ei-{generate-id(/rdf:RDF/rss:item[@rdf:about = $itemUri])}" />
        </xsl:for-each>
      </arlex:entryInstances>
    </arlex:State>
  </xsl:template>

  <!-- === FEED === -->
  <xsl:template name="RDFFeed">
    <xsl:variable name="format" select="'rss10'" />
        <atomrdf:FeedInstance rdf:nodeID="fi-{generate-id()}">

          <atomrdf:feed>
      <atomrdf:Feed>

        <!-- set feed id -->
        <xsl:attribute name="rdf:about">
          <xsl:value-of select="@rdf:about" />
        </xsl:attribute>
      </atomrdf:Feed>
          </atomrdf:feed>

          <!-- feed title -->
          <xsl:choose>
            <xsl:when test="rss:title">
              <xsl:apply-templates mode="feed-title" select="rss:title" />
            </xsl:when>
            <xsl:when test="dc:title">
              <xsl:apply-templates mode="feed-title" select="dc:title" />
            </xsl:when>
          </xsl:choose>

          <!-- feed subtitle -->
          <xsl:choose>
            <xsl:when test="rss:description">
              <xsl:apply-templates mode="feed-subtitle" select="rss:description" />
            </xsl:when>
            <xsl:when test="dc:description">
              <xsl:apply-templates mode="feed-subtitle" select="dc:description" />
            </xsl:when>
          </xsl:choose>

          <!-- feed language -->
          <xsl:apply-templates mode="feed-language" select="dc:language" />

          <!-- feed author -->
          <xsl:apply-templates mode="feed-author" select="dc:creator" />

          <!-- feed rights -->
          <xsl:apply-templates mode="feed-rights" select="copyright" />

          <!-- feed updated -->
          <xsl:apply-templates mode="feed-updated" select="dc:date" />

          <!-- feed category -->
          <xsl:apply-templates mode="feed-category" select="dc:subject" />

          <!-- NOTE only exclude extensions tested above -->

          <xsl:apply-templates mode="feed" />

          <!-- feed extensions -->
          <xsl:apply-templates mode="extension" select="*[
                           namespace-uri() != ''
                           and namespace-uri() != $NS_RSS10
                           and not(concat(namespace-uri(), local-name()) = 'http://purl.org/dc/elements/1.1/title')
                           and not(concat(namespace-uri(), local-name()) = 'http://purl.org/dc/elements/1.1/description')
                           and not(concat(namespace-uri(), local-name()) = 'http://purl.org/dc/elements/1.1/creator')
                           and not(concat(namespace-uri(), local-name()) = 'http://purl.org/dc/elements/1.1/language')
                           and not(concat(namespace-uri(), local-name()) = 'http://purl.org/dc/elements/1.1/rights')
                           and not(concat(namespace-uri(), local-name()) = 'http://purl.org/dc/elements/1.1/date')
                           and not(concat(namespace-uri(), local-name()) = 'http://purl.org/dc/elements/1.1/subject')
                           and not(concat(namespace-uri(), local-name()) = 'http://www.w3.org/2005/Atomlink')
                           ]">
            <xsl:with-param name="context" select="'feed'" />
            <xsl:with-param name="format" select="$format" />
            <xsl:with-param name="defaultBehaviour" select="'passthrough'" />
          </xsl:apply-templates>

        </atomrdf:FeedInstance>

      <xsl:apply-templates mode="rss10-entry-set" select="rss:items/rdf:Seq/rdf:li">
        <xsl:with-param name="format" select="$format" />
      </xsl:apply-templates>

  </xsl:template>

  <xsl:template mode="rss10-entry-set" match="rdf:li">
    <xsl:param name="format" />
    <xsl:variable name="itemUri" select="@rdf:resource" />
    <xsl:apply-templates mode="entries" select="/rdf:RDF/rss:item[@rdf:about = $itemUri]">
      <xsl:with-param name="format" select="$format" />
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template mode="entries" match="rss:item">
    <xsl:param name="format" />
    
      <atomrdf:EntryInstance rdf:nodeID="ei-{generate-id()}">

        <atomrdf:entry>
    <atomrdf:Entry>
      <!-- entry id -->
      <xsl:attribute name="rdf:about">
        <xsl:value-of select="@rdf:about" />
      </xsl:attribute>
    </atomrdf:Entry>
        </atomrdf:entry>
        
        <xsl:variable name="containingFeedId">
          <xsl:value-of select="/rdf:RDF/rss:channel/@rdf:about" />
        </xsl:variable>
        <atomrdf:containingFeed rdf:resource="{$containingFeedId}" />
        <atomrdf:sourceFeed rdf:resource="{$containingFeedId}" />

        <!-- entry author -->
        <xsl:choose>
          <xsl:when test="dc:creator">
            <xsl:apply-templates mode="entry-author" select="dc:creator" />
          </xsl:when>
          <xsl:when test="/rdf:RDF/rss:channel/dc:creator">
            <xsl:apply-templates mode="feed-author" select="/rdf:RDF/rss:channel/dc:creator" />
          </xsl:when>
        </xsl:choose>

        <!-- entry rights -->
        <xsl:choose>
          <xsl:when test="dc:rights">
            <xsl:apply-templates mode="entry-rights" select="dc:rights" />
          </xsl:when>
          <xsl:when test="/rdf:RDF/rss:channel/dc:rights">
            <xsl:apply-templates mode="feed-rights" select="/rdf:RDF/rss:channel/dc:rights" />
          </xsl:when>
        </xsl:choose>

        <!-- entry title -->
        <xsl:choose>
          <xsl:when test="rss:title">
            <xsl:apply-templates mode="entry-title" select="rss:title" />
          </xsl:when>
          <xsl:when test="dc:title">
            <xsl:apply-templates mode="entry-title" select="dc:title" />
          </xsl:when>
        </xsl:choose>

        <!-- entry summary -->
        <xsl:choose>
          <xsl:when test="rss:description">
            <xsl:apply-templates mode="entry-summary" select="rss:description" />
          </xsl:when>
          <xsl:when test="dc:description">
            <xsl:apply-templates mode="entry-summary" select="dc:description" />
          </xsl:when>
        </xsl:choose>

        <!-- entry content -->
        <xsl:choose>
          <xsl:when test="content:encoded">
            <xsl:apply-templates mode="entry-content" select="content:encoded" />
          </xsl:when>
          <xsl:when test="xhtml:div">
            <xsl:apply-templates mode="entry-content" select="xhtml:div" />
          </xsl:when>
          <xsl:when test="xhtml:body">
            <xsl:apply-templates mode="entry-content" select="xhtml:body" />
          </xsl:when>
        </xsl:choose>
        
        <!-- entry updated -->
        <xsl:apply-templates mode="entry-updated" select="dc:date" />

        <!-- entry category -->
        <xsl:apply-templates mode="entry-category" select="dc:subject" />

        <!-- entry language -->
        <xsl:choose>
          <xsl:when test="dc:language">
            <xsl:apply-templates mode="entry-language" select="dc:language" />
          </xsl:when>
          <xsl:when test="/rdf:RDF/rss:channel/dc:language">
            <xsl:apply-templates mode="feed-language" select="/rdf:RDF/rss:channel/dc:language" />
          </xsl:when>
        </xsl:choose>
        
        <xsl:apply-templates mode="entry" />

        <!-- NOTE only exclude extensions tested above -->

        <!-- entry extensions -->
        <xsl:apply-templates mode="extension" select="*[
                           namespace-uri() != ''
                           and namespace-uri() != $NS_RSS10
                           and not(concat(namespace-uri(), local-name()) = 'http://purl.org/rss/1.0/modules/content/encoded')
                           and not(concat(namespace-uri(), local-name()) = 'http://www.w3.org/1999/xhtmldiv')
                           and not(concat(namespace-uri(), local-name()) = 'http://www.w3.org/1999/xhtmlbody')
                           and not(concat(namespace-uri(), local-name()) = 'http://purl.org/dc/elements/1.1/title')
                           and not(concat(namespace-uri(), local-name()) = 'http://purl.org/dc/elements/1.1/description')
                           and not(concat(namespace-uri(), local-name()) = 'http://purl.org/dc/elements/1.1/creator')
                           and not(concat(namespace-uri(), local-name()) = 'http://purl.org/dc/elements/1.1/language')
                           and not(concat(namespace-uri(), local-name()) = 'http://purl.org/dc/elements/1.1/rights')
                           and not(concat(namespace-uri(), local-name()) = 'http://purl.org/dc/elements/1.1/date')
                           and not(concat(namespace-uri(), local-name()) = 'http://purl.org/dc/elements/1.1/subject')
                           and not(concat(namespace-uri(), local-name()) = 'http://www.w3.org/2005/Atomlink')
                           ]">
            <xsl:with-param name="context" select="'entry'" />
            <xsl:with-param name="format" select="$format" />
            <xsl:with-param name="defaultBehaviour" select="'passthrough'" />
        </xsl:apply-templates>

      </atomrdf:EntryInstance>

  </xsl:template>

  <!-- ALTERNATE FEED PROPERTIES -->

  <xsl:template mode="feed-title" match="rss:title">
    <atomrdf:title>
      <xsl:call-template name="AmbiguousRSS2Text">
        <xsl:with-param name="type" select="'PlainText'" />
      </xsl:call-template>
    </atomrdf:title>
  </xsl:template>

  <xsl:template mode="feed-subtitle" match="rss:description">
    <atomrdf:subtitle>
      <xsl:call-template name="AmbiguousRSS2Text" />
    </atomrdf:subtitle>
  </xsl:template>

  <xsl:template mode="feed" match="rss:image">
    <atomrdf:logo>
      <atomrdf:Image>
        <xsl:variable name="imageUri" select="@rdf:resource" />

        <atomrdf:imageUri>
          <xsl:attribute name="rdf:resource">
            <!-- resolve image uri -->
            <xsl:call-template name="resolveRef">
              <xsl:with-param name="base">
                <xsl:call-template name="getXmlBase">
                  <xsl:with-param name="element" select="." />
                  <xsl:with-param name="default" select="$contentbase" />
                </xsl:call-template>
              </xsl:with-param>
              <xsl:with-param name="ref" select="$imageUri" />
            </xsl:call-template>
          </xsl:attribute>
        </atomrdf:imageUri>

        <!-- TODO add support for xml:base back to rss elements -->

        <!-- the following really aren't very useful... -->

        <xsl:variable name="lang">
          <xsl:call-template name="getRss2Lang">
            <xsl:with-param name="default" select="$contentlang" />
          </xsl:call-template>
        </xsl:variable>
          
        <RSS2COMPAT:imageTitle>
          <xsl:if test="$lang != ''">
            <xsl:attribute name="xml:lang">
              <xsl:value-of select="$lang" />
            </xsl:attribute>
          </xsl:if>
          <xsl:value-of select="/rdf:RDF/rss:image[@rdf:about=$imageUri]/rss:title" />
        </RSS2COMPAT:imageTitle>

        <!-- TODO should imageLink be a resource? -->
        <RSS2COMPAT:imageLink>
          <xsl:call-template name="resolveRef">
            <xsl:with-param name="base">
              <xsl:call-template name="getXmlBase">
                <xsl:with-param name="element" select="." />
                <xsl:with-param name="default" select="$contentbase" />
              </xsl:call-template>
            </xsl:with-param>
            <xsl:with-param name="ref" select="/rdf:RDF/rss:image[@rdf:about=$imageUri]/rss:link" />
          </xsl:call-template>
        </RSS2COMPAT:imageLink>

        <!-- image extensions -->
        <xsl:apply-templates mode="extension" select="*[namespace-uri() != $NS_RSS10]">
          <xsl:with-param name="context" select="'image'" />
          <xsl:with-param name="format" select="'rss10'" />        
          <xsl:with-param name="defaultBehaviour" select="'passthrough'" />
        </xsl:apply-templates>
        <!-- always rss10, even if this was found in an rss20 feed -
             probably best not to think about that :) -->

      </atomrdf:Image>
    </atomrdf:logo>
  </xsl:template>

  <xsl:template mode="feed" match="rss:link">
    <atomrdf:link>
      <atomrdf:Link>
        <atomrdf:linkRel rdf:resource="http://www.iana.org/assignments/relation/alternate" />

        <atomrdf:linkHref>
          <xsl:attribute name="rdf:resource">
            <xsl:call-template name="resolveRef">
              <xsl:with-param name="base">
                <xsl:call-template name="getXmlBase">
                  <xsl:with-param name="element" select="." />
                  <xsl:with-param name="default" select="$contentbase" />
                </xsl:call-template>
              </xsl:with-param>
              <xsl:with-param name="ref" select="text()" />
            </xsl:call-template>
          </xsl:attribute>
        </atomrdf:linkHref>
        
      </atomrdf:Link>
    </atomrdf:link>
  </xsl:template>


  <xsl:template mode="entry" match="rss:link">
    <atomrdf:link>
      <atomrdf:Link>
        <atomrdf:linkRel rdf:resource="http://www.iana.org/assignments/relation/alternate" />

        <atomrdf:linkHref>
          <xsl:attribute name="rdf:resource">
            <xsl:call-template name="resolveRef">
              <xsl:with-param name="base">
                <xsl:call-template name="getXmlBase">
                  <xsl:with-param name="element" select="." />
                  <xsl:with-param name="default" select="$contentbase" />
                </xsl:call-template>
              </xsl:with-param>
              <xsl:with-param name="ref" select="text()" />
            </xsl:call-template>
          </xsl:attribute>
        </atomrdf:linkHref>
        
      </atomrdf:Link>
    </atomrdf:link>
  </xsl:template>

  <!-- feed textinput -->
  <xsl:template mode="feed" match="rss:textinput">
    <!-- could use rss1's textinput, but it is pretty sucky - reuse of
         property names, no class, etc -->
    
    <RSS2COMPAT:textInput>
      <RSS2COMPAT:TextInput>
        <xsl:variable name="textInputUri" select="@rdf:resource" />

        <xsl:variable name="lang">
          <xsl:call-template name="getRss1Lang">
            <xsl:with-param name="default" select="$contentlang" />
          </xsl:call-template>
        </xsl:variable>

        <RSS2COMPAT:textInputTitle>
          <!-- add the xml:lang of description -->
          <xsl:if test="$lang != ''">
            <xsl:attribute name="xml:lang">
              <xsl:value-of select="$lang" />
            </xsl:attribute>
          </xsl:if>
          <xsl:value-of select="/rdf:RDF/rss:textinput[@rdf:resource=$textInputUri]/rss:title" />
        </RSS2COMPAT:textInputTitle>

        <RSS2COMPAT:textInputDescription>
          <!-- add the xml:lang of description -->
          <xsl:if test="$lang != ''">
            <xsl:attribute name="xml:lang">
              <xsl:value-of select="$lang" />
            </xsl:attribute>
          </xsl:if>
          <xsl:value-of select="/rdf:RDF/rss:textinput[@rdf:resource=$textInputUri]/rss:description" />
        </RSS2COMPAT:textInputDescription>

        <RSS2COMPAT:textInputName>
          <xsl:value-of select="/rdf:RDF/rss:textinput[@rdf:resource=$textInputUri]/rss:name" />
        </RSS2COMPAT:textInputName>

        <!-- TODO rdf:resource? -->
        <RSS2COMPAT:textInputLink>
          <xsl:call-template name="resolveRef">
            <xsl:with-param name="base">
              <xsl:call-template name="getXmlBase">
                <xsl:with-param name="element" select="." />
                <xsl:with-param name="default" select="$contentbase" />
              </xsl:call-template>
            </xsl:with-param>
            <xsl:with-param name="ref" select="/rdf:RDF/rss:textinput[@rdf:resource=$textInputUri]/rss:link" />
          </xsl:call-template>
        </RSS2COMPAT:textInputLink>

        <!-- textInput extensions -->
        <xsl:apply-templates mode="extension" select="*[namespace-uri() != $NS_RSS10]">
          <xsl:with-param name="context" select="'textInput'" />
          <xsl:with-param name="format" select="'rss10'" />        
          <xsl:with-param name="defaultBehaviour" select="'passthrough'" />
        </xsl:apply-templates>
        <!-- always rss10, even if this was found in an rss20 feed -
             probably best not to think about that :) -->

      </RSS2COMPAT:TextInput>
    </RSS2COMPAT:textInput>
  </xsl:template>

  <!-- ALTERNATE ENTRY PROPERTIES -->

  <xsl:template mode="entry-title" match="rss:title">
    <atomrdf:title>
      <xsl:call-template name="AmbiguousRSS2Text">
        <xsl:with-param name="type" select="'PlainText'" />
      </xsl:call-template>
    </atomrdf:title>
  </xsl:template>

  <xsl:template mode="entry-summary" match="rss:description">
    <atomrdf:summary>
      <xsl:call-template name="AmbiguousRSS2Text" />
    </atomrdf:summary>
  </xsl:template>

</xsl:stylesheet>