#!/bin/bash
#
# Locates the parent VAF project in the folder hierarchy and runs the command in its root directory.
#

DEPTH="$(pwd | tr -c -d / | wc -c)"
MOD=.

while [[ $DEPTH -gt 0 ]]; do
    if [[ -f $MOD/.vafconfig.json ]]; then
        echo "Run $@ in $(realpath $MOD)"
        if [[ $MOD == "." ]]; then
            "$@"
        else
            cd $MOD && "$@"
        fi
        exit $?
    fi
    MOD=$MOD/..
    (( DEPTH-- )) || true
done

echo "No VAF project found in the directory hirachry. Make sure to open a file in a VAF project." >&2
exit 1
