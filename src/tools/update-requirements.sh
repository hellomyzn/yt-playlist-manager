#!/bin/bash

PRJ_ROOT=/opt/work

function main() {
    echo "Updating requirements.txt under ${PRJ_ROOT}"
    rm -f "${PRJ_ROOT}/requirements.txt"
    rm -f "${PRJ_ROOT}/requirements-dev.txt"
    poetry export --without-hashes --output "${PRJ_ROOT}/requirements.txt"
    poetry export --without-hashes --output "${PRJ_ROOT}/requirements-dev.txt" --only dev
}

main "${*}"
