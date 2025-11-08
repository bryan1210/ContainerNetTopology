#!/bin/bash
./mn-c.sh
./build-image.sh "image"
./run-topo.sh "topo.py"