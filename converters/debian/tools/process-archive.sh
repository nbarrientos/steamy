#!/bin/bash

DATADIR=$1
BASEOUT=$2

BASEURI="http://rdf.debian.net"
DISTRIBUTION="http://rdf.debian.net/distributions/lenny"

areas=(non-free contrib)
#areas=(non-free contrib main)
arches=(i386 amd64 powerpc)
#abc=(a b c d e f g h i j k l m n o p q r s t u v w x y z)
abc=(a b)

function processPackages {
  echo "Area: $1 Architecture: $2 Prefix: $3"
  ./romeo -p $DATADIR/$1/binary-$2/Packages -P $BASEOUT/$1/binary-$2/Packages.$3.rdf \
  -a -t -b $BASEURI -r "^$3.*" \
  -d $DISTRIBUTION
}

function processSources {
  echo "Area: $1 Prefix: $2"
  ./romeo -s $DATADIR/$1/source/Sources -P $BASEOUT/$1/sources/Sources.$2.rdf \
  -a -t -b $BASEURI -r "^$2.*" \
  -d $DISTRIBUTION
}

if [ -z "$1" -o -z "$2" ]
then
  echo "Usage: $0 <archive_dir> <output_dir>"
  exit -1
fi

mkdir -p $BASEOUT

for y in ${areas[@]}
do
  mkdir -p $BASEOUT/$y
  # Packages
  for a in ${arches[@]}
  do
    mkdir -p $BASEOUT/$y/binary-$a
    for l in ${abc[@]}
    do
      processPackages $y $a $l
    done
  done
  # Sources
  mkdir -p $BASEOUT/$y/sources
  for l in ${abc[@]}
  do
    processSources $y $l
  done
done
