#!/bin/bash

# sphinx-apidoc does not use conf.py. To get some wanted features
# it has been copied to optivis-apidoc in this directory.

# -e creates separate files for each module
# -f forces overwrites of existing files
./optivis-apidoc -o source ../ -f -e
