#!/bin/bash
CURRENT_DIR=$(pwd)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd $SCRIPT_DIR/../VAF
make format
cd $CURRENT_DIR
