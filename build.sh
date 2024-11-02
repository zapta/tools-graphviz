#!/bin/bash
#######################################################
#      Graphviz Apio package builder (Windows only)   #
#######################################################

# For debugging, echo executed commands.
set -x

# Exit on any error
set -e

# We use the same version number for the upstream and the apio packages.
VERSION="12.1.2"

echo "$VERSION" > "VERSION_BUILD"


# Repository home directory.
HOME=$PWD

# Initialize empty upstream and package directories.
rm -rf $HOME/_upstream/windows_amd64
rm -rf $HOME/_packages/windows_amd64

mkdir -p $HOME/_upstream/windows_amd64
mkdir -p $HOME/_packages/windows_amd64

# Delete leftover package, if any.
rm -rf $HOME/_packages/tools-graphviz-windows_amd64-*

# Fetch upstream package.
cd $HOME/_upstream/windows_amd64
wget https://gitlab.com/api/v4/projects/4207231/packages/generic/graphviz-releases/${VERSION}/windows_10_cmake_Release_Graphviz-${VERSION}-win64.zip

# Unzip upstream package.
unzip windows_10_cmake_Release_Graphviz-${VERSION}-win64.zip

# Collect files.
cd $HOME/_packages/windows_amd64
cp -r $HOME/_upstream/windows_amd64/Graphviz-${VERSION}-win64/* .

# Create package file.
tar zcf $HOME/_packages/tools-graphviz-windows_amd64-${VERSION}.tar.gz ./*

