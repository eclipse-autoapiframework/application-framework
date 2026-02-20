#!/bin/bash

# When you modify the tags, be sure to also change the image parameter in the workspace devcontainer template.
docker build -t vaf:latest -t vaf:$(cat ../version.txt) -f eclipse.Dockerfile ..
