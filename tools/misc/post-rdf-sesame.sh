#!/bin/bash
# process-distributions.sh
#
# Nacho Barrientos Arias <nacho@debian.org>

# License: MIT

URI="http://localhost:8180/openrdf-sesame/repositories/STEAMY/statements" # FIXME  

if [ $# -lt 2 ]
then
  echo "Usage: $0 <sesame_uri> <input_dir>"
  exit -1
fi

SRC=$2

for file in `find $SRC -name "*.rdf"`;
do
  echo "Uploading $file...";
  curl -H "Content-Type: application/rdf+xml" -d @$file $URI;
done
