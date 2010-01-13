#!/bin/bash
# upload-rdf-virtuoso.sh
#
# Nacho Barrientos Arias <nacho@debian.org>

# License: MIT

URI="http://data.fundacionctic.org/DAV/home/creatic/rdf_sink/"

if [ $# -lt 1 ]
then
  echo "Usage: $0 <input_dir> [virtuoso_dav_uri]"
  exit -1
fi

SRC=$1

if [ ! -z $2 ]
then
    URI=$2
fi

echo "Will upload to $URI"
echo "Username, followed by [ENTER]:"
read user
echo "Password, followed by [ENTER]:"
read passwd

for file in `find $SRC -name "*.rdf"`;
do
  echo "Uploading $file...";
  curl -T $file $URI -u $user:$passwd
done
