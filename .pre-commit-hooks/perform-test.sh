#!/bin/bash
CURRENT_DIR=$(pwd)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd $SCRIPT_DIR/../VAF
make test PYTEST_FLAGS="--runslow"
cd $CURRENT_DIR
