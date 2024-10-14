#!/bin/bash 

#######################################################################
#    Apio graphviz package builder                                    #
#######################################################################


# ---------------------------------------------------------------------
# -  Configuring the build.
# ---------------------------------------------------------------------

echo
echo "---> Configuring the build"

# -- Exit on any error
set -e

# -- Set english language for propper pattern matching
export LC_ALL=C

# -- Absolute path to the current dir.
WORK_DIR=$PWD

# -- Base apio package name. Without the "tools-" prefix.
NAME="graphviz"

echo ""
echo "* PACKAGE NAME:"
echo "  tools-$NAME"

# -- The version of the upstream graphviz release.
GRAPHVIZ_VERSION="12.1.2"

echo ""
echo "* GRAPHVIZ VERSION:"
echo "  $GRAPHVIZ_VERSION"

# -- The version for the generated apio package
PACKAGE_VERSION=0.0.1

echo ""
echo "* PACKAGE VERSION:"
echo "  tools-$PACKAGE_VERSION"

#-- This version is stored in a temporal file so that
#-- github actions can read it and figure out the package
#-- name for upload it to the new release
echo "$PACKAGE_VERSION" > "VERSION_BUILD"

# -- Base URL for for the graphviz repo release files.
SRC_URL_BASE="https://gitlab.com/api/v4/projects/4207231/packages/generic/graphviz-releases/$GRAPHVIZ_VERSION"

# -- Print the help message and exit
function print_help_exit {
  echo ""
  echo "Usage: bash build.sh ARCHITECTURE"
  echo ""
  echo "ARCHITECTURES: "
  echo "  * linux_x86_64  : Linux 64-bits"
  echo "  * linux_aarch64 : Linux ARM 64-bits"
  echo "  * windows_amd64 : Windows 64-bits"
  echo "  * darwin        : MAC x64"
  echo "  * darwin_arm64  : MAC arm64"
  echo ""
  echo "Example:"
  echo "bash build.sh linux_x86_64"
  echo ""
  exit 1
}

# --- Check the number of arguments.
if [[  "$#" -ne 1 ]]; then
  echo ""
  echo "Error: expecting exactly one argument."
  print_help_exit
fi

# -- Select architecture specifics.
ARCH=$1

echo ""
echo "* ARCHITECTURE:"
echo "  $ARCH"

if [ "${ARCH}" == "darwin" ]; then
   # -- Darwin.
   SRC_FILE="Darwin_22.6.0_Graphviz-$GRAPHVIZ_VERSION-Darwin.zip"
   EXTRACTION_CMD="unzip"

elif [ "${ARCH}" == "darwin_arm64" ]; then
   # -- Darwin arm64.
   SRC_FILE="Darwin_22.6.0_graphviz-$GRAPHVIZ_VERSION-arm64.tar.gz"
   EXTRACTION_CMD="tar -xvzf"

else
   # -- Unknown architecture.
   print_help_exit 
   echo
   echo "Error: unknown architecture [$ARCH]"
fi

# -- URL of the graphviz release file.
SRC_URL="$SRC_URL_BASE/$SRC_FILE"

echo ""
echo "* SRC URL:"
echo "  $SRC_URL"


# ---------------------------------------------------------------------
# - Create the folders to use for downloading the upstreams package
# - and creating the packages
# ---------------------------------------------------------------------

# --  Folder for storing the upstream packages
UPSTREAM_DIR=$WORK_DIR/_upstream/$ARCH

echo ""
echo "* UPSTREAM DIR:"
echo "  $UPSTREAM_DIR"

mkdir -p "$UPSTREAM_DIR"


# -- Folder for storing the generated packages
PACKAGE_DIR=$WORK_DIR/_packages/$ARCH

echo ""
echo "* PACKAGE DIR:"
echo "  $PACKAGE_DIR"

mkdir -p $PACKAGE_DIR


# -- The generated output package file.
PACKAGE_FILE_NAME=tools-$NAME-$ARCH-$PACKAGE_VERSION.tar.gz
echo ""
echo "* PACKAGE_FILE_NAME:"
echo "  $PACKAGE_FILE_NAME"


# ---------------------------------------------------------------------
# -  Fetching the upsrtream graphviz file.
# ---------------------------------------------------------------------

echo
echo "---> Fetching upstream file."

# -- Change to the upstream folder
cd "$UPSTREAM_DIR"

wget -nv $SRC_URL -O $SRC_FILE


# ---------------------------------------------------------------------
# - Uncompress the upstream file.
# ---------------------------------------------------------------------

echo
echo "---> Uncompressing the upstream file."

$EXTRACTION_CMD $SRC_FILE


# ---------------------------------------------------------------------
# - Copying upstream files.
# ---------------------------------------------------------------------

echo
echo "---> Copying selected files."

mkdir -p $PACKAGE_DIR/bin
install $SOURCE_DIR/bin/* $PACKAGE_DIR/bin


# ---------------------------------------------------------------------
# - Create the package jason meta file.
# ---------------------------------------------------------------------

echo ""
echo "---> Creatign the package json meta file"

PACKAGE_JSON="$PACKAGE_DIR"/package.json

cp -r "$WORK_DIR"/build-data/templates/package-template.json $PACKAGE_JSON

sed -i "" "s/%VERSION%/\"$PACKAGE_VERSION\"/;" "$PACKAGE_DIR"/package.json
sed -i "" "s/%SYSTEM%/\"$ARCH\"/;"     "$PACKAGE_DIR"/package.json


# ---------------------------------------------------------------------
# - Compressing the package file
# ---------------------------------------------------------------------

echo ""
echo "---> Compressing the package file"
cd $PACKAGE_DIR
tar zcf ../$PACKAGE_FILE_NAME ./* 


# ---------------------------------------------------------------------
# - All done
# ---------------------------------------------------------------------
echo
echo "Generated [_packages/$PACKAGE_FILE_NAME]"
echo "All done."
