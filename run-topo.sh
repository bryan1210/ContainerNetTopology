#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <input>"
  exit 1
fi

sudo -E env "PATH=$PATH" "VIRTUAL_ENV=$VIRTUAL_ENV" "PYTHONHOME=" python3 $1
