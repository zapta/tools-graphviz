#!/bin/bash 

# Build the apio tools-graphviz package for all apio's architectures.
# Generated files are left at _packages directory.

# -- Exit on any error
set -e

# -- Remove build artifacts
./clean.sh

# -- Build 
./build.sh darwin
./build.sh darwin_arm64

echo
echo
ls -al _packages/tools-graphviz*

