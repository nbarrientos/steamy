<Silk>

  <Prefix id="rdfs" namespace="http://www.w3.org/2000/01/rdf-schema#" />
  <Prefix id="deb" namespace="http://idi.fundacionctic.org/steamy/debian.owl#" />
  <Prefix id="rdf" namespace="http://www.w3.org/1999/02/22-rdf-syntax-ns#" />
  <Prefix id="dbpprop" namespace="http://dbpedia.org/property/" />
  <Prefix id="foaf" namespace="http://xmlns.com/foaf/0.1/" />
  <Prefix id="dbpedia-owl" namespace="http://dbpedia.org/ontology/" />

  <DataSource id="dbpedia">
    <EndpointURI>http://dbpedia.org/sparql</EndpointURI>
  </DataSource>

  <DataSource id="debian">
<!--    <EndpointURI>http://localhost:8180/openrdf-sesame/repositories/STEAMY</EndpointURI> -->
    <EndpointURI>http://wopr:8890/sparql</EndpointURI>
    <Graph>http://wopr/debian</Graph>
  </DataSource>

  <Interlink id="packages-projects">
    <LinkType>rdfs:seeAlso</LinkType>

    <TargetDataset dataSource="dbpedia" var="theirs">
      <RestrictTo>
         ?theirs rdf:type dbpedia-owl:Software .
<!--         ?theirs foaf:name "Subversion" -->
      </RestrictTo>
    </TargetDataset>

    <SourceDataset dataSource="debian" var="ours">
      <RestrictTo>
        ?ours rdf:type deb:Source .
        ?ours deb:distribution &lt;http://rdf.debian.net/distribution/lenny&gt; .
<!--        ?ours deb:packageName "subversion" . -->
      </RestrictTo>
    </SourceDataset>

    <LinkCondition>
      <MAX>
        <!-- Source package names -->
        <Compare metric="jaroSimilarity">
          <Param name="str1">
            <Transform function="lowerCase">
                <Param name="string" path="?theirs/dbpprop:name" />
            </Transform>
          </Param>
          <Param name="str2" path="?ours/deb:packageName" />
        </Compare>
        <Compare metric="jaroSimilarity">
          <Param name="str1">
            <Transform function="lowerCase">
                <Param name="string" path="?theirs/foaf:name" />
            </Transform>
          </Param>
          <Param name="str2" path="?ours/deb:packageName" />
        </Compare>
        <Compare metric="jaroSimilarity">
          <Param name="str1">
            <Transform function="lowerCase">
                <Param name="string" path="?theirs/rdfs:label" />
            </Transform>
          </Param>
          <Param name="str2" path="?ours/deb:packageName" />
        </Compare>
        <!-- Homepages -->
        <Compare metric="jaroSimilarity" optional="1">
          <Param name="str1" path="?theirs/foaf:homepage" />
          <Param name="str2" path="?ours/foaf:page" />
        </Compare>
        <Compare metric="jaroSimilarity" optional="1">
          <Param name="str1" path="?theirs/dbpprop:website" />
          <Param name="str2" path="?ours/foaf:page" />
        </Compare>
        <Compare metric="jaroSimilarity" optional="1">
          <Param name="str1" path="?theirs/foaf:page" />
          <Param name="str2" path="?ours/foaf:page" />
        </Compare>
        </MAX>
    </LinkCondition>

    <Thresholds accept="0.8" verify="0.7" />
    <Output acceptedLinks="accepted_links.n3" verifyLinks="verify_links.n3" mode="truncate" />
  </Interlink>

</Silk>
