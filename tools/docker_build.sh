#!/usr/bin/env bash

# Colors for terminal

RST='\033[0m'             # Text Reset
BIGreen='\033[1;92m'      # Green
BIYellow='\033[1;93m'     # Yellow

##############################################################################
# Return absolute path
# Globals:
#   None
# Arguments:
#   Path to resolve
# Returns:
#   None
###############################################################################
realpath () {
  echo $(cd $(dirname "$1"); pwd)/$(basename "$1")
}

# Main
main () {
  openpype_root=$(realpath $(dirname $(dirname "${BASH_SOURCE[0]}")))
  pushd "$openpype_root" > /dev/null || return > /dev/null

  echo -e "${BIYellow}---${RST} Cleaning build directory ..."
  rm -rf "$openpype_root/build" && mkdir "$openpype_root/build" > /dev/null

  version_command="import os;exec(open(os.path.join('$openpype_root', 'openpype', 'version.py')).read());print(__version__);"
  openpype_version="$(python3 <<< ${version_command})"

  echo -e "${BIGreen}>>>${RST} Running docker build ..."
  docker build -t pypeclub/openpype:$openpype_version .

  echo -e "${BIGreen}>>>${RST} Copying build from container ..."
  echo -e "${BIYellow}---${RST} Creating container from pypeclub/openpype:$openpype_version ..."
  id="$(docker create -ti pypeclub/openpype:$openpype_version bash)"
  echo -e "${BIYellow}---${RST} Copying ..."
  docker cp "$id:/opt/openpype/build/exe.linux-x86_64-3.7" "$openpype_root/build"
  echo -e "${BIGreen}>>>${RST} All done, you can delete container:"
  echo -e "${BIYellow}$id${RST}"
}

main
