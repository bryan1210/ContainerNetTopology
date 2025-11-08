#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <input>"
  exit 1
fi

sudo docker build --platform=linux/amd64 --no-cache -t ot-all-in-one:latest $1/
#sudo docker build --platform=linux/amd64 -t ot-all-in-one:latest $1/