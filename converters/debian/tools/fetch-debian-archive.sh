#!/bin/bash

ARCHIVED_DISTS="slink potato woody sarge"
CURRENT_DISTS="etch lenny"
ARCHS="i386"
AREAS="main non-free contrib"
OUTPUT_DIR="dists"

function processDists {
  for dist in $@; do
    echo "Will download $dist (arches: $ARCHS)"
    for area in $AREAS; do
        echo "Area: $area"
        mkdir -p $OUTPUT_DIR/$dist/$area/source
        SOURCES_URL="$BASE_URL/$dist/$area/source/Sources.gz"
        OUTPUT_PATH="$OUTPUT_DIR/$dist/$area/source/Sources.gz"
        processFile $SOURCES_URL $OUTPUT_PATH
        for arch in $ARCHS; do
            mkdir -p $OUTPUT_DIR/$dist/$area/binary-$arch
            PACKAGES_URL="$BASE_URL/$dist/$area/binary-$arch/Packages.gz"
            OUTPUT_PATH="$OUTPUT_DIR/$dist/$area/binary-$arch/Packages.gz"
            processFile $PACKAGES_URL $OUTPUT_PATH
          done
    done
  done
}

function processFile {
  # $1: Download URL $2: Output file
  echo "Downloading file: $1..."
  wget $1 -O $2 &> /dev/null
  local OUTPUT_PATH_UNZIPPED=$(echo $2 |sed -e "s/.gz//")
  echo "Gunzipping and recoding $2 to $OUTPUT_PATH_UNZIPPED..."
  gzip -d $2 -c > $OUTPUT_PATH_UNZIPPED
  iconv -f "ISO-8859-1" -t "UTF-8" $OUTPUT_PATH_UNZIPPED > $OUTPUT_PATH_UNZIPPED.u
  mv $OUTPUT_PATH_UNZIPPED.u $OUTPUT_PATH_UNZIPPED
}
 
BASE_URL="http://ftp.de.debian.org/archive/debian/dists"
processDists $ARCHIVED_DISTS

BASE_URL="http://ftp.de.debian.org/debian/dists"
processDists $CURRENT_DISTS
