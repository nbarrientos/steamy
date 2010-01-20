<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:atomrdf="http://djpowell.net/schemas/atomrdf/0.3/"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                xmlns:dc="http://purl.org/dc/elements/1.1/"
                xmlns:content="http://purl.org/rss/1.0/modules/content/"
                xmlns:xhtml="http://www.w3.org/1999/xhtml"
                xmlns:RSS2COMPAT="tag:djpowell.net,2005:ns-rss-compat/"
                xmlns:arlex="http://djpowell.net/schemas/atomrdf-lex/0.1/"
                
                exclude-result-prefixes="atom rdf dc content RSS2COMPAT"
                >

  <!-- RSS 0.91/2.0 support for Atom/RDF -->
  <!-- $Id: atom2rdf-16-rss20.xsl,v 1.3 2006/08/09 20:26:21 Dave Exp $ -->

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

  <xsl:template match="/rss">
    <xsl:apply-templates select="/rss/channel" />
  </xsl:template>

  <!-- RSS 2.0 -->
  <xsl:template match="/rss[@version = '2.0']/channel">
    <rdf:RDF>
      <xsl:call-template name="RSSFeed">
        <xsl:with-param name="format" select="'rss20'" />
      </xsl:call-template>
      <xsl:call-template name="RSSLex" />
    </rdf:RDF>
  </xsl:template>

  <!-- RSS 0.91 -->
  <xsl:template match="/rss[@version = '0.91']/channel">
    <rdf:RDF>
      <xsl:call-template name="RSSFeed">
        <xsl:with-param name="format" select="'rss091'" />
      </xsl:call-template>
      <xsl:call-template name="RSSLex" />
    </rdf:RDF>
  </xsl:template>

  <xsl:template name="RSSLex">
    <arlex:State>
      <arlex:feedInstance rdf:nodeID="fi-{generate-id()}" />
      <arlex:entryInstances rdf:parseType="Collection">
        <xsl:for-each select="/rss/channel/item">
          <atomrdf:EntryInstance rdf:nodeID="ei-{generate-id()}" />
        </xsl:for-each>
      </arlex:entryInstances>
    </arlex:State>
  </xsl:template>

  <!-- === FEED === -->
  <xsl:template name="RSSFeed">
    <xsl:param name="format" />
        <atomrdf:FeedInstance rdf:nodeID="fi-{generate-id()}">

        <atomrdf:feed>
      <atomrdf:Feed>

        <!-- set feed id -->
        <xsl:attribute name="rdf:nodeID">
          <xsl:text>feed-</xsl:text>
          <xsl:value-of select="generate-id()" />
        </xsl:attribute>
      </atomrdf:Feed>
        </atomrdf:feed>
        
          
          <!-- feed title -->
          <xsl:choose>
            <xsl:when test="title">
              <xsl:apply-templates mode="feed-title" select="title" />
            </xsl:when>
            <xsl:when test="dc:title">
              <xsl:apply-templates mode="feed-title" select="dc:title" />
            </xsl:when>
          </xsl:choose>

          <!-- feed subtitle -->
          <xsl:choose>
            <xsl:when test="description">
              <xsl:apply-templates mode="feed-subtitle" select="description" />
            </xsl:when>
            <xsl:when test="dc:description">
              <xsl:apply-templates mode="feed-subtitle" select="dc:description" />
            </xsl:when>
          </xsl:choose>

          <!-- feed language -->
          <xsl:choose>
            <xsl:when test="language">
              <xsl:apply-templates mode="feed-language" select="language" />
            </xsl:when>
            <xsl:when test="dc:language">
              <xsl:apply-templates mode="feed-language" select="dc:language" />
            </xsl:when>
          </xsl:choose>

          <!-- feed author -->
          <xsl:choose>
            <xsl:when test="managingEditor">
              <xsl:apply-templates mode="feed-author" select="managingEditor" />
            </xsl:when>
            <xsl:when test="dc:creator">
              <xsl:apply-templates mode="feed-author" select="dc:creator" />
            </xsl:when>
          </xsl:choose>

          <!-- feed rights -->
          <xsl:choose>
            <xsl:when test="copyright">
              <xsl:apply-templates mode="feed-rights" select="copyright" />
            </xsl:when>
            <xsl:when test="dc:rights">
              <xsl:apply-templates mode="feed-rights" select="dc:rights" />
            </xsl:when>
          </xsl:choose>

          <!-- feed updated -->
          <xsl:choose>
            <xsl:when test="lastBuildDate">
              <xsl:apply-templates mode="feed-updated" select="lastBuildDate" />
            </xsl:when>
            <xsl:when test="dc:date">
              <xsl:apply-templates mode="feed-updated" select="dc:date" />
              </xsl:when>
          </xsl:choose>
            
          <!-- feed category -->
          <xsl:choose>
            <xsl:when test="category">
              <xsl:apply-templates mode="feed-category" select="category" />
            </xsl:when>
            <xsl:when test="dc:subject">
              <xsl:apply-templates mode="feed-category" select="dc:subject" />
            </xsl:when>
          </xsl:choose>

          <!-- NOTE only exclude extensions tested above -->

          <xsl:apply-templates mode="feed" />

          <!-- feed extensions -->
          <xsl:apply-templates mode="extension" select="*[
                           namespace-uri() != ''
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
          </xsl:apply-templates>

        </atomrdf:FeedInstance>

      <xsl:apply-templates mode="entries" select="item">
        <xsl:with-param name="format" select="$format" />
      </xsl:apply-templates>
          
  </xsl:template>

  <xsl:template mode="entries" match="item">
    <xsl:param name="format" />
    
      <atomrdf:EntryInstance rdf:nodeID="ei-{generate-id()}" >
        <atomrdf:entry>
    <atomrdf:Entry>

      <!-- entry id -->
        <xsl:if test="guid">
          <xsl:variable name="lguid" select="translate(guid/text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')" />
          <xsl:choose>
            <xsl:when test="starts-with($lguid, 'http:') or 
                            starts-with($lguid, 'uuid:') or 
                            starts-with($lguid, 'urn:') or 
                            starts-with($lguid, 'tag:') or 
                            starts-with($lguid, 'info:')">
          
              <xsl:attribute name="rdf:about">
                <!-- unlike atom, rss might allow relative GUIDs when
                     permalink="true"?, lets assume so: -->
                <xsl:call-template name="resolveRef">
                  <xsl:with-param name="base" select="$contentbase" />
                  <xsl:with-param name="ref" select="guid/text()" />
                </xsl:call-template>
              </xsl:attribute>
            </xsl:when>
            <xsl:otherwise>
              <!-- entry has a guid, but it isn't a URI -->
              <RSS2COMPAT:guid>
                <xsl:value-of select="guid/text()" />
              </RSS2COMPAT:guid>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:if>
    </atomrdf:Entry>
        </atomrdf:entry>
        
            <xsl:variable name="containingFeedId">
              <xsl:text>feed-</xsl:text>
              <xsl:value-of select="generate-id( /rss/channel )" />            
            </xsl:variable>
            <atomrdf:containingFeed rdf:nodeID="{$containingFeedId}" />
            <xsl:choose>
              <xsl:when test="not(source)">
                <atomrdf:sourceFeed rdf:nodeID="{$containingFeedId}" />
              </xsl:when>
              <xsl:otherwise>
                <xsl:apply-templates mode="source" select="source" />
              </xsl:otherwise>
            </xsl:choose>

        <!-- entry author -->
        <xsl:choose>
          <xsl:when test="author">
            <xsl:apply-templates mode="entry-author" select="author" />
          </xsl:when>
          <xsl:when test="dc:creator">
            <xsl:apply-templates mode="entry-author" select="dc:creator" />
          </xsl:when>
                <xsl:when test="/rss/channel/managingEditor">
                  <xsl:apply-templates mode="feed-author" select="/rss/channel/managingEditor" />
                </xsl:when>
                <xsl:when test="/rss/channel/dc:creator">
                  <xsl:apply-templates mode="feed-author" select="/rss/channel/dc:creator" />
                </xsl:when>
              </xsl:choose>

        <!-- entry rights -->
        <xsl:choose>
          <xsl:when test="dc:rights">
            <xsl:apply-templates mode="entry-rights" select="dc:rights" />
          </xsl:when>
          <!-- copyright is not allowed at entry level -->
                <xsl:when test="/rss/channel/copyright">
                  <xsl:apply-templates mode="feed-rights" select="/rss/channel/copyright" />
                </xsl:when>
                <xsl:when test="/rss/channel/dc:rights">
                  <xsl:apply-templates mode="feed-rights" select="/rss/channel/dc:rights" />
                </xsl:when>
              </xsl:choose>

        <!-- entry title -->
        <xsl:choose>
          <xsl:when test="title">
            <xsl:apply-templates mode="entry-title" select="title" />
          </xsl:when>
          <xsl:when test="dc:title">
            <xsl:apply-templates mode="entry-title" select="dc:title" />
          </xsl:when>
        </xsl:choose>

        <!-- entry summary -->
        <xsl:choose>
          <xsl:when test="description">
            <xsl:apply-templates mode="entry-summary" select="description">
              <xsl:with-param name="format" select="$format" />
            </xsl:apply-templates>
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
        <xsl:choose>
          <xsl:when test="pubDate">
            <xsl:apply-templates mode="entry-updated" select="pubDate" />
          </xsl:when>
          <xsl:when test="dc:date">
            <xsl:apply-templates mode="entry-updated" select="dc:date" />
          </xsl:when>
        </xsl:choose>

        <!-- entry category -->
        <xsl:choose>
          <xsl:when test="category">
            <xsl:apply-templates mode="entry-category" select="category" />
          </xsl:when>
          <xsl:when test="dc:subject">
            <xsl:apply-templates mode="entry-category" select="dc:subject" />
          </xsl:when>
        </xsl:choose>

        <!-- entry language -->
        <xsl:choose>
          <xsl:when test="language">
            <xsl:apply-templates mode="entry-language" select="language" />
          </xsl:when>
          <xsl:when test="dc:language">
            <xsl:apply-templates mode="entry-language" select="dc:language" />
          </xsl:when>
                <xsl:when test="/rss/channel/language">
                  <xsl:apply-templates mode="feed-language" select="/rss/channel/language" />
                </xsl:when>
                <xsl:when test="/rss/channel/dc:language">
                  <xsl:apply-templates mode="feed-language" select="/rss/channel/dc:language" />
                </xsl:when>
              </xsl:choose>
        
        <xsl:apply-templates mode="entry" />

        <!-- NOTE only exclude extensions tested above -->

        <!-- entry extensions -->
        <xsl:apply-templates mode="extension" select="*[
                           namespace-uri() != ''
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
        </xsl:apply-templates>

      </atomrdf:EntryInstance>

  </xsl:template>

  <!-- ALTERNATE FEED PROPERTIES -->

  <xsl:template mode="feed-title" match="title">
    <!-- generally plain text -->
    <atomrdf:title>
      <xsl:call-template name="AmbiguousRSS2Text">
        <xsl:with-param name="type" select="'PlainText'" />
      </xsl:call-template>
    </atomrdf:title>
  </xsl:template>

  <xsl:template mode="feed-subtitle" match="description">
    <!-- urghh - people actually put html in here -->
    <atomrdf:summary>
      <xsl:call-template name="AmbiguousRSS2Text" />
    </atomrdf:summary>
  </xsl:template>

  <xsl:template mode="feed-language" match="language">
    <dc:language>
      <xsl:value-of select="text()" />
    </dc:language>
  </xsl:template>

  <xsl:template mode="feed-author" match="managingEditor">
    <atomrdf:author>
      <xsl:call-template name="FreePerson" />
    </atomrdf:author>
  </xsl:template>

  <xsl:template mode="feed-rights" match="copyright">
    <atomrdf:rights>
      <xsl:call-template name="AmbiguousRSS2Text">
        <xsl:with-param name="nodeId">
          <xsl:text>rights-</xsl:text>
          <xsl:value-of select="generate-id(.)" />
        </xsl:with-param>
        <xsl:with-param name="type" select="'PlainText'" />
      </xsl:call-template>
    </atomrdf:rights>
  </xsl:template>

  <xsl:template mode="feed-updated" match="lastBuildDate">
    <atomrdf:updated>
      <xsl:call-template name="convertRssDate">
        <xsl:with-param name="in" select="text()" />
      </xsl:call-template>
    </atomrdf:updated>
  </xsl:template>

  <xsl:template mode="feed-category" match="category">
    <xsl:call-template name="Rss2Category" />
  </xsl:template>

  <xsl:template mode="feed" match="generator">
    <atomrdf:generator>
      <atomrdf:Generator>
        <atomrdf:generatorName>
          <xsl:value-of select="text()" />
        </atomrdf:generatorName>
      </atomrdf:Generator>
    </atomrdf:generator>
  </xsl:template>

  <!-- NOTE clashes between image and rss:image are unlikely -->
  <xsl:template mode="feed" match="image">
    <atomrdf:logo>
      <atomrdf:Image>
        <atomrdf:imageUri>

          <xsl:attribute name="rdf:resource">
            <!-- resolve image uri -->
            <xsl:call-template name="resolveRef">
              <xsl:with-param name="base" select="$contentbase" />
              <xsl:with-param name="ref" select="url" />
            </xsl:call-template>
          </xsl:attribute>
        </atomrdf:imageUri>

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
          <xsl:value-of select="title" />
        </RSS2COMPAT:imageTitle>

        <RSS2COMPAT:imageLink>
          <xsl:attribute name="rdf:resource">
            <!-- resolve image uri -->
            <xsl:call-template name="resolveRef">
              <xsl:with-param name="base" select="$contentbase" />
              <xsl:with-param name="ref" select="url" />
            </xsl:call-template>
          </xsl:attribute>
        </RSS2COMPAT:imageLink>

        <xsl:if test="description">
          <RSS2COMPAT:imageDescription>
            <xsl:if test="$lang != ''">
              <xsl:attribute name="xml:lang">
                <xsl:value-of select="$lang" />
              </xsl:attribute>
            </xsl:if>
            <xsl:value-of select="description" />
          </RSS2COMPAT:imageDescription>
        </xsl:if>

        <xsl:if test="width">
          <RSS2COMPAT:imageWidth>
            <xsl:value-of select="width" />
          </RSS2COMPAT:imageWidth>
        </xsl:if>

        <xsl:if test="height">
          <RSS2COMPAT:imageHeight>
            <xsl:value-of select="height" />
          </RSS2COMPAT:imageHeight>
        </xsl:if>

      </atomrdf:Image>
    </atomrdf:logo>
  </xsl:template>

  <!-- FEED PROPERTIES -->

  <xsl:template mode="feed" match="link">
    <atomrdf:link>
      <atomrdf:Link>
        <atomrdf:linkRel rdf:resource="http://www.iana.org/assignments/relation/alternate" />

        <atomrdf:linkHref>
          <xsl:attribute name="rdf:resource">
            <xsl:call-template name="resolveRef">
              <xsl:with-param name="base" select="$contentbase" />
              <xsl:with-param name="ref" select="text()" />
            </xsl:call-template>
          </xsl:attribute>
        </atomrdf:linkHref>
        
      </atomrdf:Link>
    </atomrdf:link>
  </xsl:template>

  <xsl:template mode="feed" match="webMaster">
    <RSS2COMPAT:webMaster>
      <xsl:call-template name="FreePerson" />
    </RSS2COMPAT:webMaster>
  </xsl:template>

  <xsl:template mode="feed" match="pubDate">
    <!-- NOTE - outputting pubDate as RSS2COMPAT:pubDate -->
    <RSS2COMPAT:pubDate>
      <xsl:call-template name="convertRssDate">
        <xsl:with-param name="in" select="text()" />
      </xsl:call-template>
    </RSS2COMPAT:pubDate>
  </xsl:template>

  <!-- feed docs (not very useful) -->
  <xsl:template mode="feed" match="docs">
    <RSS2COMPAT:docs>
      <xsl:attribute name="rdf:resource">
        <xsl:value-of select="text()" />
      </xsl:attribute>
    </RSS2COMPAT:docs>
  </xsl:template>
  
  <!-- feed cloud -->
  <xsl:template mode="feed" match="cloud">
    <RSS2COMPAT:cloud>
      <RSS2COMPAT:Cloud>
        <RSS2COMPAT:domain>
          <xsl:value-of select="@domain" />
        </RSS2COMPAT:domain>
        <RSS2COMPAT:port>
          <xsl:value-of select="@port" />
        </RSS2COMPAT:port>
        <RSS2COMPAT:path>
          <xsl:value-of select="@path" />
        </RSS2COMPAT:path>
        <RSS2COMPAT:registerProcedure>
          <xsl:value-of select="@registerProcedure" />
        </RSS2COMPAT:registerProcedure>
        <RSS2COMPAT:protocol>
          <xsl:value-of select="@protocol" />
        </RSS2COMPAT:protocol>
      </RSS2COMPAT:Cloud>
    </RSS2COMPAT:cloud>
  </xsl:template>

  <xsl:template mode="feed" match="ttl">
    <RSS2COMPAT:ttl>
      <xsl:value-of select="text()" />
    </RSS2COMPAT:ttl>
  </xsl:template>

  <xsl:template mode="feed" match="rating">
    <RSS2COMPAT:rating>
      <xsl:value-of select="text()" />
    </RSS2COMPAT:rating>
  </xsl:template>

  <!-- support Netscape's lowercase textinput -->
  <xsl:template mode="feed" match="textInput | textinput">
    <!-- could use rss1's textinput, but it is pretty sucky - reuse of
         property names, no class, etc -->
    <RSS2COMPAT:textInput>
      <RSS2COMPAT:TextInput>
        <xsl:variable name="lang">
          <xsl:call-template name="getRss2Lang">
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
          <xsl:value-of select="title" />
        </RSS2COMPAT:textInputTitle>

        <RSS2COMPAT:textInputDescription>
          <!-- add the xml:lang of description -->
          <xsl:if test="$lang != ''">
            <xsl:attribute name="xml:lang">
              <xsl:value-of select="$lang" />
            </xsl:attribute>
          </xsl:if>
          <xsl:value-of select="description" />
        </RSS2COMPAT:textInputDescription>

        <RSS2COMPAT:textInputName>
          <xsl:value-of select="name" />
        </RSS2COMPAT:textInputName>

        <RSS2COMPAT:textInputLink>
          <xsl:call-template name="resolveRef">
            <xsl:with-param name="base" select="$contentbase" />
            <xsl:with-param name="ref" select="link" />
          </xsl:call-template>
        </RSS2COMPAT:textInputLink>

      </RSS2COMPAT:TextInput>
    </RSS2COMPAT:textInput>
  </xsl:template>


  <xsl:template mode="feed" match="skipHours">
    <xsl:for-each select="hour">
      <xsl:choose>
        <!-- NOTE some RSS versions use 24 instead of 0, use the RSS2
             standard -->
        <xsl:when test="number(text()) = 24">
          <RSS2COMPAT:skipHour>0</RSS2COMPAT:skipHour>
        </xsl:when>
        <xsl:otherwise>
          <RSS2COMPAT:skipHour>
            <xsl:value-of select="string(number(text()))" />
          </RSS2COMPAT:skipHour>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
  </xsl:template>

  <xsl:template mode="feed" match="skipDays">
    <xsl:for-each select="day">
      <xsl:variable name="day1" select="translate(substring(text(), 1, 1), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')" />
      <xsl:variable name="dayT" select="translate(substring(text(), 2), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')" />
      <RSS2COMPAT:skipDay>
        <xsl:value-of select="$day1" />
        <xsl:value-of select="$dayT" />
      </RSS2COMPAT:skipDay>
    </xsl:for-each>
  </xsl:template>

  <!-- ALTERNATE ENTRY PROPERTIES -->

  <xsl:template mode="entry-author" match="author">
    <atomrdf:author>
      <xsl:call-template name="FreePerson" />
    </atomrdf:author>
  </xsl:template>

  <xsl:template mode="entry-title" match="title">
    <!-- urghhh html -->
    <atomrdf:title>
      <xsl:call-template name="AmbiguousRSS2Text" />
    </atomrdf:title>
  </xsl:template>

  <xsl:template mode="entry-summary" match="description">
    <xsl:param name="format" />
    <xsl:choose>
      <xsl:when test="$format = 'rss091'">
        <atomrdf:summary>
          <xsl:call-template name="AmbiguousRSS2Text">
            <xsl:with-param name="type" select="'PlainText'" />
          </xsl:call-template>
        </atomrdf:summary>
      </xsl:when>
      <xsl:otherwise>
        <!-- ambiguous by design -->
        <atomrdf:summary>
          <xsl:call-template name="AmbiguousRSS2Text" />      
        </atomrdf:summary>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template mode="entry-updated" match="pubDate">
    <atomrdf:updated>
      <xsl:call-template name="convertRssDate">
        <xsl:with-param name="in" select="text()" />
      </xsl:call-template>
    </atomrdf:updated>
  </xsl:template>

  <xsl:template mode="entry-category" match="category">
    <xsl:call-template name="Rss2Category" />
  </xsl:template>

  <xsl:template mode="entry" match="link">
    <atomrdf:link>
      <atomrdf:Link>
        <atomrdf:linkRel rdf:resource="http://www.iana.org/assignments/relation/related" />

        <atomrdf:linkHref>
          <xsl:attribute name="rdf:resource">
            <xsl:call-template name="resolveRef">
              <xsl:with-param name="base" select="$contentbase" />
              <xsl:with-param name="ref" select="text()" />
            </xsl:call-template>
          </xsl:attribute>
        </atomrdf:linkHref>
        
      </atomrdf:Link>
    </atomrdf:link>
  </xsl:template>

  <xsl:template mode="entry" match="guid[@permalink != 'false']">
    <atomrdf:link>
      <atomrdf:Link>
        <atomrdf:linkRel rdf:resource="http://www.iana.org/assignments/relation/alternate" />

        <atomrdf:linkHref>
          <xsl:attribute name="rdf:resource">
            <xsl:call-template name="resolveRef">
              <xsl:with-param name="base" select="$contentbase" />
              <xsl:with-param name="ref" select="text()" />
            </xsl:call-template>
          </xsl:attribute>
        </atomrdf:linkHref>

      </atomrdf:Link>
    </atomrdf:link>
  </xsl:template>

  <xsl:template mode="entry" match="comments">
    <atomrdf:link>
      <atomrdf:Link>
        <atomrdf:linkRel>
          <xsl:attribute name="rdf:resource">
            <xsl:value-of select="$NS_RSS2COMPAT" />
            <xsl:text>comments</xsl:text>
          </xsl:attribute>
        </atomrdf:linkRel>

        <atomrdf:linkHref>
          <xsl:attribute name="rdf:resource">
            <xsl:call-template name="resolveRef">
              <xsl:with-param name="base" select="$contentbase" />
              <xsl:with-param name="ref" select="text()" />
            </xsl:call-template>
          </xsl:attribute>
        </atomrdf:linkHref>
        
      </atomrdf:Link>
    </atomrdf:link>
  </xsl:template>

  <xsl:template mode="entry" match="enclosure">
    <atomrdf:link>
      <atomrdf:Link>
        <atomrdf:linkRel rdf:resource="http://www.iana.org/assignments/relation/enclosure" />

        <atomrdf:linkHref>
          <xsl:attribute name="rdf:resource">
            <xsl:call-template name="resolveRef">
              <xsl:with-param name="base" select="$contentbase" />
              <xsl:with-param name="ref" select="@url" />
            </xsl:call-template>
          </xsl:attribute>
        </atomrdf:linkHref>

        <atomrdf:linkType>
          <xsl:value-of select="@type" />
        </atomrdf:linkType>
        
        <atomrdf:linkLength>
          <xsl:value-of select="@length" />
        </atomrdf:linkLength>
        
      </atomrdf:Link>
    </atomrdf:link>
  </xsl:template>

  <xsl:template mode="entry-language" match="language">
    <dc:language>
      <xsl:value-of select="text()" />
    </dc:language>
  </xsl:template>

  <!-- SOURCE PROPERTIES -->

  <xsl:template mode="source" match="source">
    <atomrdf:sourceFeed>
      <!-- TODO needs to point to a Feed, and needs to handle FeedInstance at top level -->
          <atomrdf:FeedInstance>

            <atomrdf:feed>
              <atomrdf:Feed />
            </atomrdf:feed>

            <atomrdf:title>
              <atomrdf:PlainText>
                <atomrdf:textValue>
                  <xsl:value-of select="text()" />
                </atomrdf:textValue>
                <!-- hmm, should we set the lang here - it is coipied from
                     another feed? - let's not -->
              </atomrdf:PlainText>
            </atomrdf:title>
            <atomrdf:link>
              <atomrdf:Link>
                <atomrdf:linkRel rdf:resource="http://www.iana.org/assignments/relation/self" />
                <atomrdf:linkHref>
                  <xsl:value-of select="@url" />
                </atomrdf:linkHref>
              </atomrdf:Link>
            </atomrdf:link>
          </atomrdf:FeedInstance>
    </atomrdf:sourceFeed>
  </xsl:template>

  <!-- FUNCTIONS -->
  
  <xsl:template name="Rss2Category">
    <atomrdf:category>
      <atomrdf:Category>

        <!-- set category id -->
        <xsl:attribute name="rdf:nodeID">
          <xsl:text>cat-</xsl:text>
          <xsl:value-of select="generate-id()" />
        </xsl:attribute>
        
        <atomrdf:categoryTerm>
          <xsl:value-of select="text()" />
        </atomrdf:categoryTerm>

        <!-- NOTE prevent dataloss if domain isn't a url -->
        <xsl:if test="@domain">
          <xsl:choose>
            <xsl:when test="starts-with(@domain, 'http:') or
                            starts-with(@domain, 'uuid:') or
                            starts-with(@domain, 'urn:') or
                            starts-with(@domain, 'tag:') or
                            starts-with(@domain, 'info:')
                            ">
              <atomrdf:categoryScheme>
                <xsl:attribute name="rdf:resource">
                  <xsl:value-of select="@domain" />
                </xsl:attribute>
              </atomrdf:categoryScheme>
            </xsl:when>
            <xsl:otherwise>
              <RSS2COMPAT:categoryDomain>
                <xsl:value-of select="@domain" />
              </RSS2COMPAT:categoryDomain>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:if>

      </atomrdf:Category>
    </atomrdf:category>
  </xsl:template>

</xsl:stylesheet>